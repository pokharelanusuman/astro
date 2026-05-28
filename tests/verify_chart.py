#!/usr/bin/env python3
"""Automated verification script for /api/calculate endpoint.

Usage:
  python3 tests/verify_chart.py --host http://localhost:5000

Tests the Biratnagar example (1992-12-17 04:55) for both tropical and sidereal modes.
Asserts:
 - Tropical: Ascendant in Sagittarius (240°-270°)
 - Sidereal: Ascendant in Scorpio (210°-240°)
 - Timezone resolves to Kathmandu
 - planet_map contains 12 house keys
 - Input place preserved in response
"""
import sys
import argparse
import requests


def fail(msg):
    print("FAIL:", msg)
    sys.exit(2)


def test_zodiac_mode(url, payload, mode, expected_range):
    """Test chart calculation with specific zodiac mode.
    
    Args:
        url: API endpoint URL
        payload: Base payload (will add zodiac_mode)
        mode: 'tropical' or 'sidereal'
        expected_range: (min_deg, max_deg) for ascendant
    """
    test_payload = {**payload, 'zodiac_mode': mode}
    
    print(f"\nTesting {mode.upper()} mode...")
    try:
        resp = requests.post(url, json=test_payload, timeout=15)
    except Exception as e:
        fail(f"Request failed for {mode}: {e}")

    if resp.status_code != 200:
        fail(f"HTTP {resp.status_code} for {mode}: {resp.text}")

    data = resp.json()
    if data.get('status') != 'success':
        fail(f"API returned error for {mode}: {data}")

    chart = data.get('data') or {}

    asc = chart.get('ascendant_degree')
    if asc is None:
        fail(f'ascendant_degree missing for {mode}')

    try:
        asc = float(asc)
    except Exception:
        fail(f'invalid ascendant_degree for {mode}: {asc}')

    min_deg, max_deg = expected_range
    if not (min_deg <= asc < max_deg):
        fail(f'{mode}: Ascendant not in expected range ({min_deg}°-{max_deg}°), got {asc}°')

    # Verify zodiac_mode in response
    if chart.get('zodiac_mode') != mode:
        fail(f'{mode}: zodiac_mode mismatch in response, got {chart.get("zodiac_mode")}')

    tz = chart.get('timezone', '') or ''
    if 'kathmandu' not in tz.lower():
        fail(f"{mode}: Resolved timezone is not Kathmandu: '{tz}'")

    planet_map = chart.get('planet_map') or chart.get('house_mapping')
    if not planet_map:
        fail(f'{mode}: planet_map / house_mapping missing')

    if len(planet_map) < 12:
        fail(f'{mode}: planet_map has fewer than 12 houses: {len(planet_map)}')

    place_in = chart.get('birth_data', {}).get('input_place') or chart.get('location') or ''
    if 'biratnagar' not in str(place_in).lower():
        fail(f"{mode}: Input place not preserved: '{place_in}'")

    print(f"✓ {mode.upper()}: Ascendant {asc:.2f}° (expected {min_deg}°-{max_deg}°), TZ: {tz}, Place: {place_in}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', '-H', default='http://localhost:5000')
    args = parser.parse_args()

    url = args.host.rstrip('/') + '/api/calculate'
    payload = {
        'year': 1992,
        'month': 12,
        'day': 17,
        'time': '04:55',
        'place': 'Biratnagar'
    }

    print(f"Posting test payloads to {url}")
    print(f"Base payload: {payload}\n")

    # Test tropical mode: Sagittarius (240°-270°)
    test_zodiac_mode(url, payload, 'tropical', (240.0, 270.0))

    # Test sidereal mode: Scorpio (210°-240°)
    test_zodiac_mode(url, payload, 'sidereal', (210.0, 240.0))

    print('\n✓ PASS: All checks succeeded for both tropical and sidereal modes')
    return 0


if __name__ == '__main__':
    sys.exit(main())
