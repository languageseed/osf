#!/usr/bin/env python3
"""
Batch Property Generator

Pre-generates a pool of properties with descriptions and images.
Run this offline before demos to avoid wait times.

Usage:
    python scripts/generate_properties.py --count 50
    python scripts/generate_properties.py --count 20 --suburbs "City Beach,Subiaco"
    python scripts/generate_properties.py --count 10 --no-images  # Descriptions only
"""

import asyncio
import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.property_generator import (
    generate_property_data,
    generate_property_listing_sync,
    GeneratedProperty,
    SUBURBS,
)
from src.services.image_generator import generate_property_images_sync


def generate_property_pool(
    count: int = 50,
    suburbs: list = None,
    include_images: bool = True,
    output_path: str = "data/property_pool.json",
):
    """Generate a pool of properties (sync version for reliability)."""
    
    if suburbs is None:
        suburbs = list(SUBURBS.keys())
    
    print(f"\n{'='*60}")
    print(f"OSF Property Pool Generator")
    print(f"{'='*60}")
    print(f"Count: {count}")
    print(f"Suburbs: {', '.join(suburbs)}")
    print(f"Include Images: {include_images}")
    print(f"Output: {output_path}")
    print(f"{'='*60}\n")
    
    pool = {
        "generated_at": datetime.utcnow().isoformat(),
        "count": count,
        "include_images": include_images,
        "properties": [],
    }
    
    start_time = time.time()
    
    for i in range(count):
        suburb = suburbs[i % len(suburbs)]
        
        print(f"[{i+1}/{count}] Generating property in {suburb}...", end=" ", flush=True)
        prop_start = time.time()
        
        try:
            # Step 1: Generate property data
            property_data = generate_property_data(suburb=suburb, index=i)
            
            # Step 2: Generate listing with Gemini (sync)
            listing = generate_property_listing_sync(property_data)
            
            if not listing:
                print("⚠ No listing (API key missing?)")
                # Still save the property data
                pool["properties"].append({
                    "id": property_data.id,
                    "status": "draft",
                    "data": property_data.to_dict(),
                    "listing": None,
                    "images": {},
                })
                continue
            
            # Step 3: Generate images (if enabled)
            images = {}
            if include_images and listing.image_brief:
                images = generate_property_images_sync(
                    listing.image_brief,
                    listing.floorplan_brief,
                )
            
            # Package property
            property_entry = {
                "id": property_data.id,
                "status": "draft",
                "data": property_data.to_dict(),
                "listing": listing.to_dict(),
                "images": images,
            }
            
            pool["properties"].append(property_entry)
            
            elapsed = time.time() - prop_start
            
            status_parts = []
            if listing:
                status_parts.append("listing")
            if images.get("isometric"):
                status_parts.append("isometric")
            if images.get("floorplan"):
                status_parts.append("floorplan")
            
            print(f"✓ [{', '.join(status_parts)}] {elapsed:.1f}s")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Save to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(pool, indent=2))
    
    total_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"Complete!")
    print(f"{'='*60}")
    print(f"Properties generated: {len(pool['properties'])}")
    print(f"Total time: {total_time:.1f}s ({total_time/count:.1f}s per property)")
    print(f"Output saved to: {output_path}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Generate property pool for OSF simulation")
    parser.add_argument("--count", type=int, default=50, help="Number of properties to generate")
    parser.add_argument("--suburbs", type=str, help="Comma-separated list of suburbs")
    parser.add_argument("--no-images", action="store_true", help="Skip image generation")
    parser.add_argument("--output", type=str, default="data/property_pool.json", help="Output file path")
    
    args = parser.parse_args()
    
    suburbs = None
    if args.suburbs:
        suburbs = [s.strip() for s in args.suburbs.split(",")]
        # Validate suburbs
        for s in suburbs:
            if s not in SUBURBS:
                print(f"Error: Unknown suburb '{s}'")
                print(f"Valid suburbs: {', '.join(SUBURBS.keys())}")
                sys.exit(1)
    
    generate_property_pool(
        count=args.count,
        suburbs=suburbs,
        include_images=not args.no_images,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
