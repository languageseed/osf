#!/usr/bin/env python3
"""
Pool Status Checker

Check the status of pre-generated property and avatar pools.

Usage:
    python scripts/pool_status.py
"""

import json
import sys
from pathlib import Path


def check_property_pool(path: str = "data/property_pool.json"):
    """Check property pool status."""
    
    pool_file = Path(path)
    
    if not pool_file.exists():
        print(f"  ⚠ Not found: {path}")
        print(f"  Run: python scripts/generate_properties.py --count 50")
        return
    
    pool = json.loads(pool_file.read_text())
    
    properties = pool.get("properties", [])
    
    # Count by status
    status_counts = {}
    for prop in properties:
        status = prop.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Count images
    with_isometric = sum(1 for p in properties if p.get("images", {}).get("isometric"))
    with_floorplan = sum(1 for p in properties if p.get("images", {}).get("floorplan"))
    with_listing = sum(1 for p in properties if p.get("listing"))
    
    # Count by suburb
    suburb_counts = {}
    for prop in properties:
        suburb = prop.get("data", {}).get("suburb", "unknown")
        suburb_counts[suburb] = suburb_counts.get(suburb, 0) + 1
    
    print(f"  Generated: {pool.get('generated_at', 'unknown')}")
    print(f"  Total: {len(properties)}")
    print()
    print(f"  Status:")
    for status, count in status_counts.items():
        print(f"    - {status}: {count}")
    print()
    print(f"  Content:")
    print(f"    - With listing: {with_listing}")
    print(f"    - With isometric: {with_isometric}")
    print(f"    - With floorplan: {with_floorplan}")
    print()
    print(f"  By Suburb:")
    for suburb, count in sorted(suburb_counts.items()):
        print(f"    - {suburb}: {count}")


def check_avatar_pool(path: str = "data/avatars.json"):
    """Check avatar pool status."""
    
    pool_file = Path(path)
    
    if not pool_file.exists():
        print(f"  ⚠ Not found: {path}")
        print(f"  Run: python scripts/generate_avatars.py")
        return
    
    pool = json.loads(pool_file.read_text())
    
    avatars = pool.get("avatars", {})
    
    # Categorize
    participant_roles = []
    service_roles = []
    
    service_prefixes = [
        'plumber', 'electrician', 'gardener', 'cleaner', 'painter', 
        'handyman', 'building', 'real_estate', 'pool', 'security', 
        'hvac', 'locksmith', 'pest', 'roofer', 'conveyancer', 'accountant'
    ]
    
    for role in avatars.keys():
        if any(role.startswith(s) for s in service_prefixes):
            service_roles.append(role)
        else:
            participant_roles.append(role)
    
    print(f"  Generated: {pool.get('generated_at', 'unknown')}")
    print(f"  Total: {len(avatars)}")
    print()
    print(f"  Participant Roles ({len(participant_roles)}):")
    for role in sorted(participant_roles):
        print(f"    - {role}")
    print()
    print(f"  Service Providers ({len(service_roles)}):")
    for role in sorted(service_roles):
        print(f"    - {role}")


def main():
    print()
    print("="*60)
    print("OSF Pool Status")
    print("="*60)
    
    print()
    print("Property Pool:")
    print("-"*40)
    check_property_pool()
    
    print()
    print("Avatar Pool:")
    print("-"*40)
    check_avatar_pool()
    
    print()
    print("="*60)
    print()


if __name__ == "__main__":
    main()
