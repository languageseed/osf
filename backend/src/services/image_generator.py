"""
Image Generator Service

Generates property and avatar images using Imagen 3 Fast.
Optimized for speed over quality for demo/hackathon purposes.
"""

import base64
import asyncio
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
import structlog

from google import genai
from google.genai import types

from src.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


# =============================================================================
# Configuration
# =============================================================================

# Use Imagen 3 for hackathon
IMAGEN_MODEL = "imagen-3.0-generate-002"

# Fallback to Gemini native image generation if Imagen not available
GEMINI_IMAGE_MODEL = "gemini-3-flash"


# =============================================================================
# Image Generation
# =============================================================================

async def generate_image(
    prompt: str,
    aspect_ratio: str = "16:9",
    use_gemini_fallback: bool = True,
) -> Optional[bytes]:
    """
    Generate an image using Imagen 3 Fast.
    
    Args:
        prompt: The image generation prompt
        aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4)
        use_gemini_fallback: Fall back to Gemini native if Imagen fails
        
    Returns:
        Image bytes or None if generation fails
    """
    if not settings.google_api_key:
        logger.warning("image_generation_skipped", reason="No API key")
        return None
    
    client = genai.Client(api_key=settings.google_api_key)
    
    # Try Imagen 3 Fast first
    try:
        response = await client.aio.models.generate_images(
            model=IMAGEN_MODEL,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=aspect_ratio,
                output_mime_type="image/jpeg",
            ),
        )
        
        if response.generated_images:
            logger.info("image_generated", model=IMAGEN_MODEL, prompt_length=len(prompt))
            return response.generated_images[0].image.image_bytes
            
    except Exception as e:
        logger.warning("imagen_failed", error=str(e), will_fallback=use_gemini_fallback)
        
        if not use_gemini_fallback:
            return None
    
    # Fallback to Gemini native image generation
    try:
        response = await client.aio.models.generate_content(
            model=GEMINI_IMAGE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
        
        # Extract image from response
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                logger.info("image_generated", model=GEMINI_IMAGE_MODEL, prompt_length=len(prompt))
                return part.inline_data.data
                
    except Exception as e:
        logger.error("gemini_image_failed", error=str(e))
    
    return None


def encode_image_base64(image_bytes: bytes) -> str:
    """Encode image bytes to base64 data URL."""
    encoded = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:image/jpeg;base64,{encoded}"


# =============================================================================
# Property Image Generation
# =============================================================================

def build_isometric_prompt(image_brief: Dict[str, str]) -> str:
    """Build prompt for isometric property render from image brief."""
    
    parts = [
        "45-degree isometric aerial view of a luxury Australian home.",
        "",
        f"BUILDING: {image_brief.get('building', 'Modern single-level home')}",
    ]
    
    if image_brief.get('roof_features'):
        parts.append(f"ROOF: {image_brief['roof_features']}")
    
    if image_brief.get('outdoor_structures'):
        parts.append(f"STRUCTURES: {image_brief['outdoor_structures']}")
    
    if image_brief.get('pool_area'):
        parts.append(f"POOL: {image_brief['pool_area']}")
    
    if image_brief.get('landscaping'):
        parts.append(f"LANDSCAPING: {image_brief['landscaping']}")
    
    if image_brief.get('materials'):
        parts.append(f"MATERIALS: {image_brief['materials']}")
    
    parts.extend([
        "",
        f"STYLE: {image_brief.get('style', 'Photorealistic 3D architectural render')}",
        f"ATMOSPHERE: {image_brief.get('atmosphere', 'Bright daylight, premium luxury feel')}",
        "BACKGROUND: Clean cream/white gradient",
        "",
        "DO NOT include: People, cars, text, watermarks, logos",
    ])
    
    return "\n".join(parts)


def build_floorplan_prompt(floorplan_brief: Dict[str, Any]) -> str:
    """Build prompt for floor plan image from floorplan brief."""
    
    rooms = floorplan_brief.get('rooms', [])
    room_descriptions = []
    
    for room in rooms[:8]:  # Limit to avoid prompt length issues
        name = room.get('name', 'Room')
        area = room.get('area', '')
        wing = room.get('wing', '')
        room_descriptions.append(f"- {name} ({area}) in {wing}")
    
    parts = [
        "Professional architectural floor plan, top-down view, clean technical drawing style.",
        "",
        f"LAYOUT: {floorplan_brief.get('layout_type', 'Single level home')}, {floorplan_brief.get('total_area', '200m²')} total",
        f"ORIENTATION: {floorplan_brief.get('orientation', 'North to rear')}",
        "",
        "ROOMS:",
        *room_descriptions,
        "",
        f"FLOW: {floorplan_brief.get('flow_description', 'Open plan living connecting to outdoor areas')}",
        "",
        "STYLE: Clean architectural line drawing, black lines on white background",
        "INCLUDE: Room labels, door swings, north arrow",
        "",
        "DO NOT include: Furniture, colors, 3D elements, photographs, text other than room labels",
    ]
    
    return "\n".join(parts)


def generate_image_sync(
    prompt: str,
    aspect_ratio: str = "16:9",
) -> Optional[bytes]:
    """Generate an image using Imagen 3 Fast (sync version)."""
    
    if not settings.google_api_key:
        logger.warning("image_generation_skipped", reason="No API key")
        return None
    
    client = genai.Client(api_key=settings.google_api_key)
    
    try:
        # Try Imagen 3 Fast
        response = client.models.generate_images(
            model=IMAGEN_MODEL,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=aspect_ratio,
                output_mime_type="image/jpeg",
            ),
        )
        
        if response.generated_images:
            logger.info("image_generated", model=IMAGEN_MODEL)
            return response.generated_images[0].image.image_bytes
            
    except Exception as e:
        logger.warning("imagen_failed", error=str(e))
        
        # Fallback to Gemini native
        try:
            response = client.models.generate_content(
                model=GEMINI_IMAGE_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )
            
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    logger.info("image_generated", model=GEMINI_IMAGE_MODEL)
                    return part.inline_data.data
                    
        except Exception as e2:
            logger.error("gemini_image_failed", error=str(e2))
    
    return None


def generate_property_images_sync(
    image_brief: Dict[str, str],
    floorplan_brief: Dict[str, Any],
) -> Dict[str, str]:
    """
    Generate both property images (sync version).
    
    Returns:
        Dict with 'isometric' and 'floorplan' base64 encoded images
    """
    images = {}
    
    # Build prompts
    isometric_prompt = build_isometric_prompt(image_brief)
    floorplan_prompt = build_floorplan_prompt(floorplan_brief)
    
    # Generate isometric
    isometric_bytes = generate_image_sync(isometric_prompt, aspect_ratio="16:9")
    if isometric_bytes:
        images["isometric"] = encode_image_base64(isometric_bytes)
        logger.info("isometric_image_generated")
    else:
        logger.warning("isometric_image_failed")
    
    # Generate floorplan
    floorplan_bytes = generate_image_sync(floorplan_prompt, aspect_ratio="1:1")
    if floorplan_bytes:
        images["floorplan"] = encode_image_base64(floorplan_bytes)
        logger.info("floorplan_image_generated")
    else:
        logger.warning("floorplan_image_failed")
    
    return images


async def generate_property_images(
    image_brief: Dict[str, str],
    floorplan_brief: Dict[str, Any],
) -> Dict[str, str]:
    """
    Generate both property images in parallel.
    
    Returns:
        Dict with 'isometric' and 'floorplan' base64 encoded images
    """
    images = {}
    
    # Build prompts
    isometric_prompt = build_isometric_prompt(image_brief)
    floorplan_prompt = build_floorplan_prompt(floorplan_brief)
    
    # Generate in parallel
    results = await asyncio.gather(
        generate_image(isometric_prompt, aspect_ratio="16:9"),
        generate_image(floorplan_prompt, aspect_ratio="1:1"),
        return_exceptions=True,
    )
    
    isometric_bytes, floorplan_bytes = results
    
    if isinstance(isometric_bytes, bytes):
        images["isometric"] = encode_image_base64(isometric_bytes)
        logger.info("isometric_image_generated")
    else:
        logger.warning("isometric_image_failed", error=str(isometric_bytes))
    
    if isinstance(floorplan_bytes, bytes):
        images["floorplan"] = encode_image_base64(floorplan_bytes)
        logger.info("floorplan_image_generated")
    else:
        logger.warning("floorplan_image_failed", error=str(floorplan_bytes))
    
    return images


# =============================================================================
# Avatar Image Generation
# =============================================================================

# Character briefs for all roles
CHARACTER_BRIEFS = {
    # Participant Roles
    "investor": {
        "description": "Professional male in tailored navy blue suit, white shirt, red tie. Holding brown leather briefcase. Confident standing pose, looking slightly to the side. Clean-shaven, neat brown hair.",
        "tile": "Polished concrete cube with subtle aggregate texture",
    },
    "investor_female": {
        "description": "Professional female in charcoal blazer and skirt, white blouse. Holding tablet. Confident stance, slight smile. Professional hairstyle.",
        "tile": "Polished concrete cube with subtle aggregate texture",
    },
    "renter": {
        "description": "Young adult male in casual clothes - jeans, hoodie. Holding apartment keys. Friendly, approachable expression.",
        "tile": "Warm wooden hexagonal platform",
    },
    "renter_female": {
        "description": "Young adult female in casual clothes - jeans, sweater. Small box or backpack. Friendly expression.",
        "tile": "Warm wooden hexagonal platform",
    },
    "homeowner": {
        "description": "Middle-aged male in smart casual - chinos, button shirt. Holding house keys. Proud, content expression.",
        "tile": "Natural stone garden tile with grass edge",
    },
    "homeowner_female": {
        "description": "Middle-aged female in smart casual dress. Holding small potted plant. Warm, welcoming expression.",
        "tile": "Natural stone garden tile with grass edge",
    },
    "foundation_partner": {
        "description": "Distinguished professional male in premium business attire. Open handshake gesture. Grey hair, trustworthy demeanor.",
        "tile": "White marble hexagonal platform with subtle veining",
    },
    "governor_ai": {
        "description": "Abstract humanoid figure with smooth metallic blue-silver surface. Subtle glowing circuit patterns. Zen-like pose, hands together. Smooth helmet-like head, no face details.",
        "tile": "Floating circular platform with soft blue glow underneath",
    },
    "market_maker": {
        "description": "Sharp-dressed trader, rolled sleeves, energetic pose pointing. Modern smartwatch, earpiece. Dynamic expression.",
        "tile": "Digital hexagon with subtle LED edge glow",
    },
    
    # Service Providers
    "plumber": {
        "description": "Plumber in blue work overalls, holding large pipe wrench. Tool bag visible. Friendly, capable expression.",
        "tile": "Grey concrete hexagon with subtle water puddle",
    },
    "electrician": {
        "description": "Electrician in dark work pants and company polo. Safety glasses on head, voltage tester in hand. Alert, focused.",
        "tile": "Industrial metal grate platform",
    },
    "gardener": {
        "description": "Gardener in cargo shorts, sun-faded shirt, wide-brim hat. Leather gloves, holding pruning shears. Tanned, friendly.",
        "tile": "Natural grass and soil circular mound",
    },
    "cleaner": {
        "description": "Professional cleaner in neat uniform apron. Carrying cleaning caddy with supplies. Rubber gloves, proud demeanor.",
        "tile": "Sparkling clean white tile platform",
    },
    "painter": {
        "description": "House painter in white overalls with colorful paint splatter. Holding paint roller. Cap backwards, cheerful.",
        "tile": "Paint-splattered drop cloth platform",
    },
    "handyman": {
        "description": "Versatile handyman in jeans and work shirt, variety of tools on belt. Jack-of-all-trades confident look.",
        "tile": "Weathered wooden platform",
    },
    "building_inspector": {
        "description": "Building inspector in smart casual with hi-vis vest. Hard hat, clipboard, measuring tape. Authoritative, thorough.",
        "tile": "Blueprint-patterned platform",
    },
    "real_estate_agent": {
        "description": "Real estate agent in sharp business attire. Holding tablet, small SOLD sticker visible. Confident smile, polished.",
        "tile": "Polished marble hexagon",
    },
    "pool_tech": {
        "description": "Pool technician in shorts and company polo. Holding pool skimmer net. Tanned, relaxed but professional.",
        "tile": "Blue mosaic tile hexagon pool tile style",
    },
    "security_tech": {
        "description": "Security technician in uniform with company logo. Holding alarm panel and drill. Professional, trustworthy.",
        "tile": "Dark grey platform with subtle LED indicator lights",
    },
    "hvac_tech": {
        "description": "HVAC technician in company uniform polo. Carrying refrigerant gauges. Clean-cut, professional service tech.",
        "tile": "Metal vent grate platform",
    },
    "locksmith": {
        "description": "Locksmith in work jacket, large key ring on belt. Holding door lock mechanism. Skilled, trustworthy.",
        "tile": "Metallic brushed steel hexagon",
    },
    "pest_control": {
        "description": "Pest control technician in protective coveralls, spray wand equipment. Mask around neck. Determined.",
        "tile": "Concrete slab with subtle crack detail",
    },
    "roofer": {
        "description": "Roofer in work clothes, safety harness, hard hat. Holding roofing hammer, nail bag. Weathered, tough.",
        "tile": "Terracotta roof tile platform",
    },
    "conveyancer": {
        "description": "Legal professional in business attire, glasses. Holding property documents. Studious, meticulous.",
        "tile": "Dark wood platform with legal book texture",
    },
    "accountant": {
        "description": "Accountant in professional attire. Calculator and neat papers. Organized, intelligent appearance.",
        "tile": "Clean white platform with subtle grid pattern",
    },
}


def build_avatar_prompt(role: str, brief: Dict[str, str]) -> str:
    """Build prompt for character avatar."""
    
    return f"""45 degree isometric view of a character standing on a game board tile.

CHARACTER: {brief['description']}

TILE: {brief['tile']}
- Tile slightly elevated like a game piece base

STYLE: 3D rendered figurine aesthetic, realistic materials and textures
LIGHTING: Soft studio lighting with gentle shadows
BACKGROUND: Clean light grey/white gradient

DO NOT include: Text, logos, watermarks, multiple characters"""


async def generate_avatar(role: str) -> Optional[str]:
    """Generate a single avatar image."""
    
    brief = CHARACTER_BRIEFS.get(role)
    if not brief:
        logger.warning("avatar_brief_not_found", role=role)
        return None
    
    prompt = build_avatar_prompt(role, brief)
    
    image_bytes = await generate_image(prompt, aspect_ratio="1:1")
    
    if image_bytes:
        return encode_image_base64(image_bytes)
    
    return None


async def generate_all_avatars(
    roles: Optional[list] = None,
    variants_per_role: int = 1,
) -> Dict[str, str]:
    """
    Generate avatars for all roles.
    
    Args:
        roles: List of roles to generate, or None for all
        variants_per_role: Number of variants per role (for diversity)
        
    Returns:
        Dict mapping role names to base64 encoded images
    """
    if roles is None:
        roles = list(CHARACTER_BRIEFS.keys())
    
    avatars = {}
    
    for role in roles:
        for variant in range(variants_per_role):
            key = f"{role}_{variant + 1}" if variants_per_role > 1 else role
            
            logger.info("generating_avatar", role=role, variant=variant + 1)
            
            image = await generate_avatar(role)
            
            if image:
                avatars[key] = image
                logger.info("avatar_generated", role=key)
            else:
                logger.warning("avatar_failed", role=key)
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
    
    return avatars


# =============================================================================
# Convenience Functions
# =============================================================================

async def generate_single_property_with_images(
    suburb: Optional[str] = None,
    property_type: Optional[str] = None,
    index: int = 0,
) -> Dict[str, Any]:
    """Generate a complete property with images (convenience function)."""
    
    from src.services.property_generator import generate_complete_property
    
    property = await generate_complete_property(
        suburb=suburb,
        property_type=property_type,
        index=index,
        generate_images=True,
    )
    
    return property.to_dict()
