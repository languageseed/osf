"""
Property and Avatar Pool API

Endpoints for accessing pre-generated property and avatar pools.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/pool", tags=["Asset Pools"])


# =============================================================================
# Data Models
# =============================================================================

class PoolStatus(BaseModel):
    """Pool status summary."""
    exists: bool
    count: int
    generated_at: Optional[str]
    available: int
    enabled: int


class PropertySummary(BaseModel):
    """Property summary for listing."""
    id: str
    status: str
    address: str
    suburb: str
    property_type: str
    bedrooms: int
    bathrooms: int
    valuation: int
    headline: Optional[str]
    has_images: bool
    # Include images for frontend display
    images: Optional[Dict[str, str]] = None
    # Include listing highlights
    highlights: Optional[List[Dict[str, str]]] = None


class PropertyDetail(BaseModel):
    """Full property detail."""
    id: str
    status: str
    data: Dict[str, Any]
    listing: Optional[Dict[str, Any]]
    images: Dict[str, str]


class AvatarInfo(BaseModel):
    """Avatar info."""
    role: str
    image: str


# =============================================================================
# Pool Loading
# =============================================================================

PROPERTY_POOL_PATH = Path("data/property_pool.json")
AVATAR_POOL_PATH = Path("data/avatars.json")

# In-memory cache
_property_pool = None
_avatar_pool = None


def load_property_pool() -> dict:
    """Load property pool from disk."""
    global _property_pool
    
    if _property_pool is not None:
        return _property_pool
    
    if not PROPERTY_POOL_PATH.exists():
        return {"properties": [], "generated_at": None}
    
    try:
        _property_pool = json.loads(PROPERTY_POOL_PATH.read_text())
        logger.info("property_pool_loaded", count=len(_property_pool.get("properties", [])))
        return _property_pool
    except Exception as e:
        logger.error("property_pool_load_failed", error=str(e))
        return {"properties": [], "generated_at": None}


def load_avatar_pool() -> dict:
    """Load avatar pool from disk."""
    global _avatar_pool
    
    if _avatar_pool is not None:
        return _avatar_pool
    
    if not AVATAR_POOL_PATH.exists():
        return {"avatars": {}, "generated_at": None}
    
    try:
        _avatar_pool = json.loads(AVATAR_POOL_PATH.read_text())
        logger.info("avatar_pool_loaded", count=len(_avatar_pool.get("avatars", {})))
        return _avatar_pool
    except Exception as e:
        logger.error("avatar_pool_load_failed", error=str(e))
        return {"avatars": {}, "generated_at": None}


def save_property_pool():
    """Save property pool to disk."""
    global _property_pool
    if _property_pool:
        PROPERTY_POOL_PATH.write_text(json.dumps(_property_pool, indent=2))


def reload_pools():
    """Force reload pools from disk."""
    global _property_pool, _avatar_pool
    _property_pool = None
    _avatar_pool = None
    load_property_pool()
    load_avatar_pool()


# =============================================================================
# Property Pool Endpoints
# =============================================================================

@router.get("/properties/status", response_model=PoolStatus)
async def get_property_pool_status():
    """Get property pool status."""
    pool = load_property_pool()
    properties = pool.get("properties", [])
    
    available = sum(1 for p in properties if p.get("status") == "draft")
    enabled = sum(1 for p in properties if p.get("status") != "draft")
    
    return PoolStatus(
        exists=PROPERTY_POOL_PATH.exists(),
        count=len(properties),
        generated_at=pool.get("generated_at"),
        available=available,
        enabled=enabled,
    )


@router.get("/properties", response_model=List[PropertySummary])
async def list_properties(
    status: Optional[str] = Query(None, description="Filter by status"),
    suburb: Optional[str] = Query(None, description="Filter by suburb"),
    limit: int = Query(50, ge=1, le=100),
):
    """List properties in the pool."""
    pool = load_property_pool()
    properties = pool.get("properties", [])
    
    # Filter
    if status:
        properties = [p for p in properties if p.get("status") == status]
    if suburb:
        properties = [p for p in properties if p.get("data", {}).get("suburb") == suburb]
    
    # Build summaries
    summaries = []
    for prop in properties[:limit]:
        data = prop.get("data", {})
        listing = prop.get("listing", {})
        images = prop.get("images", {})
        
        summaries.append(PropertySummary(
            id=prop.get("id", ""),
            status=prop.get("status", "draft"),
            address=data.get("address", ""),
            suburb=data.get("suburb", ""),
            property_type=data.get("property_type", ""),
            bedrooms=data.get("bedrooms", 0),
            bathrooms=data.get("bathrooms", 0),
            valuation=data.get("valuation", 0),
            headline=listing.get("headline") if listing else None,
            has_images=bool(images.get("isometric")),
            images=images if images else None,
            highlights=listing.get("highlights") if listing else None,
        ))
    
    return summaries


@router.get("/properties/{property_id}", response_model=PropertyDetail)
async def get_property(property_id: str):
    """Get full property details."""
    pool = load_property_pool()
    
    for prop in pool.get("properties", []):
        if prop.get("id") == property_id:
            return PropertyDetail(
                id=prop.get("id"),
                status=prop.get("status", "draft"),
                data=prop.get("data", {}),
                listing=prop.get("listing"),
                images=prop.get("images", {}),
            )
    
    raise HTTPException(404, f"Property {property_id} not found")


@router.post("/properties/{property_id}/enable")
async def enable_property(property_id: str):
    """Enable a property (change status from draft to available)."""
    pool = load_property_pool()
    
    for prop in pool.get("properties", []):
        if prop.get("id") == property_id:
            if prop.get("status") == "draft":
                prop["status"] = "available"
                save_property_pool()
                logger.info("property_enabled", id=property_id)
                return {"status": "enabled", "property_id": property_id}
            else:
                return {"status": "already_enabled", "property_id": property_id}
    
    raise HTTPException(404, f"Property {property_id} not found")


@router.post("/properties/enable-next")
async def enable_next_property(suburb: Optional[str] = None):
    """Enable the next available draft property."""
    pool = load_property_pool()
    
    for prop in pool.get("properties", []):
        if prop.get("status") == "draft":
            if suburb and prop.get("data", {}).get("suburb") != suburb:
                continue
            
            prop["status"] = "available"
            save_property_pool()
            
            remaining = sum(1 for p in pool["properties"] if p.get("status") == "draft")
            
            logger.info("next_property_enabled", id=prop["id"])
            
            return {
                "property_id": prop["id"],
                "suburb": prop.get("data", {}).get("suburb"),
                "remaining_in_pool": remaining,
            }
    
    raise HTTPException(404, "No draft properties available")


# =============================================================================
# Avatar Pool Endpoints
# =============================================================================

@router.get("/avatars/status", response_model=PoolStatus)
async def get_avatar_pool_status():
    """Get avatar pool status."""
    pool = load_avatar_pool()
    avatars = pool.get("avatars", {})
    
    return PoolStatus(
        exists=AVATAR_POOL_PATH.exists(),
        count=len(avatars),
        generated_at=pool.get("generated_at"),
        available=len(avatars),
        enabled=len(avatars),  # All avatars are always "enabled"
    )


@router.get("/avatars")
async def list_avatars(
    category: Optional[str] = Query(None, description="Filter: participant or service"),
):
    """List all available avatars."""
    pool = load_avatar_pool()
    avatars = pool.get("avatars", {})
    
    service_prefixes = [
        'plumber', 'electrician', 'gardener', 'cleaner', 'painter', 
        'handyman', 'building', 'real_estate', 'pool', 'security', 
        'hvac', 'locksmith', 'pest', 'roofer', 'conveyancer', 'accountant'
    ]
    
    result = {}
    
    for role, image in avatars.items():
        is_service = any(role.startswith(s) for s in service_prefixes)
        
        if category == "participant" and is_service:
            continue
        if category == "service" and not is_service:
            continue
        
        result[role] = {
            "role": role,
            "category": "service" if is_service else "participant",
            "image": image,
        }
    
    return result


@router.get("/avatars/{role}")
async def get_avatar(role: str):
    """Get a specific avatar."""
    pool = load_avatar_pool()
    avatars = pool.get("avatars", {})
    
    if role in avatars:
        return {"role": role, "image": avatars[role]}
    
    raise HTTPException(404, f"Avatar for role '{role}' not found")


# =============================================================================
# Pool Management
# =============================================================================

@router.post("/reload")
async def reload_all_pools():
    """Reload pools from disk (use after regenerating)."""
    reload_pools()
    
    prop_pool = load_property_pool()
    avatar_pool = load_avatar_pool()
    
    return {
        "properties_loaded": len(prop_pool.get("properties", [])),
        "avatars_loaded": len(avatar_pool.get("avatars", {})),
    }
