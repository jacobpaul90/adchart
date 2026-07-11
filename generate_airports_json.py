#!/usr/bin/env python3
"""
generate_airports_json.py

Builds airports.json for the Airport Diagram Finder website.

The FAA republishes its Digital Terminal Procedures Publication (d-TPP)
on a 28-day cycle. Each cycle, the PDF filenames for every chart --
including airport diagrams -- can change, and they live at a URL that
includes the cycle number (e.g. https://aeronav.faa.gov/d-tpp/2606/00117ad.pdf).

This script downloads the FAA's current d-TPP XML metadata catalog,
pulls out just the "APD" (Airport Diagram) record for every airport,
and writes a small JSON lookup table that the website reads directly.

Run this every ~28 days (whenever the FAA publishes a new cycle) and
re-upload the resulting airports.json to your web host.

Usage:
    python3 generate_airports_json.py
"""

import json
import sys
import urllib.request
import xml.etree.ElementTree as ET

# FAA's "always current" alias for the d-TPP metadata catalog. If this
# URL ever stops working, check the "d-TPP Metafile XML" links on:
# https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/dtpp/search/
SOURCE_URL = "https://nfdc.faa.gov/webContent/dtpp/current.xml"

OUTPUT_FILE = "airports.json"


def fetch_xml(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "airport-diagram-finder/1.0 (+personal project)"},
    )
    print("Downloading {} ...".format(url))
    with urllib.request.urlopen(req, timeout=180) as resp:
        return resp.read()


def build_lookup(xml_bytes):
    root = ET.fromstring(xml_bytes)
    cycle = root.attrib.get("cycle", "")
    print("Current FAA chart cycle: {}".format(cycle or "unknown"))

    airports = {}
    matched = 0

    for airport in root.iter("airport_name"):
        icao = (airport.attrib.get("icao_ident") or "").strip().upper()
        faa_id = (airport.attrib.get("apt_ident") or "").strip().upper()
        name = (airport.attrib.get("ID") or "").strip().title()

        for record in airport.findall("record"):
            chart_code = (record.findtext("chart_code") or "").strip()
            if chart_code != "APD":
                continue

            pdf_name = (record.findtext("pdf_name") or "").strip()
            if not pdf_name or not cycle:
                continue

            anchor = faa_id or icao
            pdf_url = "https://aeronav.faa.gov/d-tpp/{}/{}#nameddest=({})".format(
                cycle, pdf_name.lower(), anchor
            )
            entry = {"name": name, "pdf": pdf_url}

            if icao:
                airports[icao] = entry
            if faa_id:
                airports[faa_id] = entry

            matched += 1
            break  # one diagram per airport is enough

    print("Found airport diagrams for {} airports.".format(matched))
    return {"cycle": cycle, "airports": airports}


def main():
    try:
        xml_bytes = fetch_xml(SOURCE_URL)
    except Exception as exc:
        print("ERROR: could not download FAA metadata: {}".format(exc), file=sys.stderr)
        sys.exit(1)

    try:
        data = build_lookup(xml_bytes)
    except ET.ParseError as exc:
        print("ERROR: could not parse FAA XML: {}".format(exc), file=sys.stderr)
        sys.exit(1)

    if not data["airports"]:
        print("ERROR: no airport diagrams were found -- refusing to overwrite "
              "airports.json with empty data.", file=sys.stderr)
        sys.exit(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"), ensure_ascii=False)

    print("Wrote {} ({} airports, cycle {}).".format(
        OUTPUT_FILE, len(data["airports"]), data["cycle"]))


if __name__ == "__main__":
    main()
