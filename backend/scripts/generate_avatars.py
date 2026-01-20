#!/usr/bin/env python3
"""
Batch Avatar Generator

Pre-generates character avatars for all roles.
Run this offline before demos to avoid wait times.

Usage:
    python scripts/generate_avatars.py
    python scripts/generate_avatars.py --roles investor,renter,plumber
    python scripts/generate_avatars.py --variants 2
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

from src.services.image_generator import (
    CHARACTER_BRIEFS,
    generate_avatar,
    build_avatar_prompt,
    generate_image_sync,
    encode_image_base64,
)


# Define how many variants per role category
DEFAULT_VARIANTS = {
    # Participant roles - more variants for diversity
    "investor": 2,
    "investor_female": 1,
    "renter": 2,
    "renter_female": 1,
    "homeowner": 2,
    "homeowner_female": 1,
    "foundation_partner": 1,
    "governor_ai": 1,
    "market_maker": 1,
    
    # Service providers - fewer variants needed
    "plumber": 1,
    "electrician": 1,
    "gardener": 1,
    "cleaner": 1,
    "painter": 1,
    "handyman": 1,
    "building_inspector": 1,
    "real_estate_agent": 1,
    "pool_tech": 1,
    "security_tech": 1,
    "hvac_tech": 1,
    "locksmith": 1,
    "pest_control": 1,
    "roofer": 1,
    "conveyancer": 1,
    "accountant": 1,
}


def generate_avatar_sync(role: str) -> str:
    """Generate a single avatar image (sync)."""
    brief = CHARACTER_BRIEFS.get(role)
    if not brief:
        return None
    
    prompt = build_avatar_prompt(role, brief)
    image_bytes = generate_image_sync(prompt, aspect_ratio="1:1")
    
    if image_bytes:
        return encode_image_base64(image_bytes)
    return None


def generate_avatar_pool(
    roles: list = None,
    variants_override: int = None,
    output_path: str = "data/avatars.json",
):
    """Generate avatar pool (sync version)."""
    
    if roles is None:
        roles = list(CHARACTER_BRIEFS.keys())
    
    print(f"\n{'='*60}")
    print(f"OSF Avatar Generator")
    print(f"{'='*60}")
    print(f"Roles: {len(roles)}")
    print(f"Output: {output_path}")
    print(f"{'='*60}\n")
    
    pool = {
        "generated_at": datetime.utcnow().isoformat(),
        "avatars": {},
    }
    
    start_time = time.time()
    total_count = 0
    success_count = 0
    
    for role in roles:
        if role not in CHARACTER_BRIEFS:
            print(f"⚠ Unknown role: {role}, skipping")
            continue
        
        variants = variants_override or DEFAULT_VARIANTS.get(role, 1)
        
        for v in range(variants):
            total_count += 1
            variant_key = f"{role}_{v+1}" if variants > 1 else role
            
            print(f"[{total_count}] Generating {variant_key}...", end=" ", flush=True)
            avatar_start = time.time()
            
            try:
                image = generate_avatar_sync(role)
                
                if image:
                    pool["avatars"][variant_key] = image
                    elapsed = time.time() - avatar_start
                    print(f"✓ {elapsed:.1f}s")
                    success_count += 1
                else:
                    print("✗ No image returned")
                    
            except Exception as e:
                print(f"✗ Error: {e}")
            
            # Small delay between requests
            time.sleep(0.3)
    
    # Save to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(pool, indent=2))
    
    total_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"Complete!")
    print(f"{'='*60}")
    print(f"Avatars generated: {success_count}/{total_count}")
    print(f"Total time: {total_time:.1f}s")
    print(f"Output saved to: {output_path}")
    print(f"{'='*60}\n")


async def list_roles():
    """List all available roles."""
    print("\nAvailable roles:")
    print("-" * 40)
    
    print("\nParticipant Roles:")
    participant_roles = [r for r in CHARACTER_BRIEFS.keys() 
                        if not any(r.startswith(s) for s in 
                                  ['plumber', 'electrician', 'gardener', 'cleaner',
                                   'painter', 'handyman', 'building', 'real_estate',
                                   'pool', 'security', 'hvac', 'locksmith', 'pest',
                                   'roofer', 'conveyancer', 'accountant'])]
    for role in participant_roles:
        print(f"  - {role}")
    
    print("\nService Provider Roles:")
    service_roles = [r for r in CHARACTER_BRIEFS.keys() if r not in participant_roles]
    for role in service_roles:
        print(f"  - {role}")
    
    print()


def main():
    parser = argparse.ArgumentParser(description="Generate avatar pool for OSF simulation")
    parser.add_argument("--roles", type=str, help="Comma-separated list of roles")
    parser.add_argument("--variants", type=int, help="Override variants per role")
    parser.add_argument("--output", type=str, default="data/avatars.json", help="Output file path")
    parser.add_argument("--list", action="store_true", help="List available roles")
    
    args = parser.parse_args()
    
    if args.list:
        asyncio.run(list_roles())
        return
    
    roles = None
    if args.roles:
        roles = [r.strip() for r in args.roles.split(",")]
    
    generate_avatar_pool(
        roles=roles,
        variants_override=args.variants,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
