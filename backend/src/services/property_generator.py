"""
Property Generator Service

Generates complete property data, descriptions, and image briefs.
Part of the property generation pipeline:
1. Generate property data (this service)
2. Generate images (image_generator.py)
3. Store in property pool
"""

import json
import random
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
import structlog

from google import genai
from google.genai import types

from src.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


# =============================================================================
# Perth Suburb Data
# =============================================================================

SUBURBS = {
    "City Beach": {
        "postcode": "6015",
        "median_price": 2800000,
        "price_variance": 0.4,
        "vibe": "Prestigious beachside, family-oriented, Norfolk pines",
        "amenities": ["Beach", "Bold Park", "Empire Village Cafe Strip", "City Beach Oval"],
        "schools": ["Kapinara Primary", "City Beach Primary", "Holy Spirit School"],
        "style_bias": ["contemporary", "luxury", "coastal"]
    },
    "Subiaco": {
        "postcode": "6008",
        "median_price": 1600000,
        "price_variance": 0.35,
        "vibe": "Urban village, cafe culture, heritage character",
        "amenities": ["Subiaco Markets", "Rokeby Road Cafes", "Mueller Park", "Subiaco Oval"],
        "schools": ["Subiaco Primary", "Perth Modern"],
        "style_bias": ["character", "federation", "modern renovation"]
    },
    "Nedlands": {
        "postcode": "6009",
        "median_price": 2200000,
        "price_variance": 0.35,
        "vibe": "Leafy, academic, established families, UWA nearby",
        "amenities": ["UWA Campus", "Nedlands Golf Club", "Broadway Shopping", "Swan River"],
        "schools": ["Nedlands Primary", "Dalkeith Primary", "Hollywood Primary"],
        "style_bias": ["traditional", "grand", "renovated"]
    },
    "Cottesloe": {
        "postcode": "6011",
        "median_price": 3200000,
        "price_variance": 0.4,
        "vibe": "Iconic beach, sunset views, prestigious coastal",
        "amenities": ["Cottesloe Beach", "Indiana Tea House", "Napoleon Street Shops", "Sea View Golf Club"],
        "schools": ["Cottesloe Primary", "North Cottesloe Primary"],
        "style_bias": ["coastal luxury", "beach house", "contemporary"]
    },
    "Claremont": {
        "postcode": "6010",
        "median_price": 2000000,
        "price_variance": 0.35,
        "vibe": "Upmarket shopping, boutiques, refined living",
        "amenities": ["Claremont Quarter", "Lake Claremont", "Claremont Showgrounds", "Freshwater Bay"],
        "schools": ["Claremont Primary", "Scotch College", "MLC", "Christ Church Grammar"],
        "style_bias": ["elegant", "refined", "classic"]
    },
    "Fremantle": {
        "postcode": "6160",
        "median_price": 1100000,
        "price_variance": 0.4,
        "vibe": "Historic port city, arts, maritime, eclectic",
        "amenities": ["Fremantle Markets", "Fishing Boat Harbour", "Cappuccino Strip", "Fremantle Prison"],
        "schools": ["Fremantle Primary", "South Fremantle SHS"],
        "style_bias": ["heritage", "limestone", "artistic"]
    },
}

PROPERTY_TYPES = {
    "house": {"weight": 0.5, "min_beds": 3, "max_beds": 5, "land_multiplier": 1.0},
    "apartment": {"weight": 0.3, "min_beds": 1, "max_beds": 3, "land_multiplier": 0.15},
    "townhouse": {"weight": 0.15, "min_beds": 2, "max_beds": 4, "land_multiplier": 0.4},
    "villa": {"weight": 0.05, "min_beds": 2, "max_beds": 3, "land_multiplier": 0.35},
}

ARCHITECTURAL_STYLES = [
    "Contemporary Australian",
    "Modern Minimalist", 
    "Coastal Contemporary",
    "Federation Revival",
    "Mediterranean Influenced",
    "Hamptons Style",
    "Mid-Century Modern",
    "Traditional Renovated",
]

FEATURES = {
    "outdoor": [
        ("pool", 0.3, "Saltwater swimming pool with glass fencing"),
        ("solar", 0.4, "Rooftop solar panel system"),
        ("alfresco", 0.6, "Covered alfresco entertaining area"),
        ("garden", 0.5, "Established landscaped gardens"),
        ("deck", 0.4, "Timber deck entertaining area"),
        ("boat_parking", 0.1, "Boat or caravan parking"),
        ("outdoor_kitchen", 0.2, "Built-in outdoor kitchen/BBQ"),
        ("spa", 0.1, "Heated spa"),
    ],
    "indoor": [
        ("study", 0.5, "Dedicated home office/study"),
        ("theatre", 0.15, "Home theatre room"),
        ("wine_cellar", 0.08, "Temperature-controlled wine cellar"),
        ("gym", 0.1, "Home gym space"),
        ("ducted_ac", 0.7, "Ducted reverse-cycle air conditioning"),
        ("fireplace", 0.2, "Gas or electric fireplace"),
        ("butler_pantry", 0.25, "Butler's pantry"),
        ("ensuite", 0.8, "Master ensuite bathroom"),
    ],
    "premium": [
        ("marble_floors", 0.2, "Italian marble flooring"),
        ("granite_kitchen", 0.4, "Granite kitchen benchtops"),
        ("smart_home", 0.15, "Smart home automation system"),
        ("security", 0.5, "Security alarm system"),
        ("double_glazing", 0.25, "Double-glazed windows"),
    ]
}

STREET_NAMES = [
    "Ocean", "Beach", "Park", "Garden", "River", "Bay", "Hill", "View",
    "Palm", "Norfolk", "Sunset", "Marine", "Shore", "Cliff", "Grove",
    "Kings", "Queens", "Victoria", "Cambridge", "Oxford", "Wellington"
]

STREET_TYPES = ["Street", "Road", "Avenue", "Crescent", "Drive", "Way", "Place", "Close"]


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class PropertyData:
    """Raw property data."""
    id: str
    address: str
    suburb: str
    state: str = "WA"
    postcode: str = ""
    property_type: str = ""
    bedrooms: int = 0
    bathrooms: int = 0
    parking: int = 0
    land_size: int = 0
    build_area: int = 0
    architectural_style: str = ""
    features_outdoor: List[str] = field(default_factory=list)
    features_indoor: List[str] = field(default_factory=list)
    features_premium: List[str] = field(default_factory=list)
    valuation: int = 0
    gross_yield: float = 0.0
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PropertyListing:
    """Generated property listing with marketing content."""
    property_id: str
    headline: str
    subheadline: str
    quick_stats: Dict[str, Any]
    highlights: List[Dict[str, str]]
    features_description: Dict[str, str]
    lifestyle_description: Dict[str, str]
    property_features: Dict[str, Any]
    rates: Dict[str, float]
    nearby: Dict[str, List[Any]]
    image_brief: Dict[str, str]
    floorplan_brief: Dict[str, Any]
    generated_at: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass 
class GeneratedProperty:
    """Complete generated property with all content."""
    id: str
    status: str  # draft, available, tenanted, archived
    data: PropertyData
    listing: Optional[PropertyListing] = None
    images: Dict[str, str] = field(default_factory=dict)  # base64 encoded
    created_at: str = ""
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "status": self.status,
            "data": self.data.to_dict(),
            "listing": self.listing.to_dict() if self.listing else None,
            "images": self.images,
            "created_at": self.created_at,
        }


# =============================================================================
# Property Data Generator
# =============================================================================

def generate_property_data(
    suburb: Optional[str] = None,
    property_type: Optional[str] = None,
    index: int = 0,
) -> PropertyData:
    """Generate random property data based on suburb characteristics."""
    
    # Select suburb
    if suburb is None:
        suburb = random.choice(list(SUBURBS.keys()))
    suburb_data = SUBURBS[suburb]
    
    # Select property type (weighted)
    if property_type is None:
        types = list(PROPERTY_TYPES.keys())
        weights = [PROPERTY_TYPES[t]["weight"] for t in types]
        property_type = random.choices(types, weights=weights)[0]
    type_data = PROPERTY_TYPES[property_type]
    
    # Generate address
    street_num = random.randint(1, 150)
    street_name = random.choice(STREET_NAMES)
    street_type = random.choice(STREET_TYPES)
    address = f"{street_num} {street_name} {street_type}"
    
    # Bedrooms and bathrooms
    bedrooms = random.randint(type_data["min_beds"], type_data["max_beds"])
    bathrooms = max(1, bedrooms - random.randint(0, 1))
    parking = random.randint(1, min(3, bedrooms))
    
    # Land and build size
    base_land = random.randint(400, 1200)
    land_size = int(base_land * type_data["land_multiplier"])
    build_area = int(land_size * random.uniform(0.3, 0.5))
    if property_type == "apartment":
        land_size = 0  # Strata
        build_area = random.randint(60, 180)
    
    # Architectural style (biased by suburb)
    style_pool = ARCHITECTURAL_STYLES.copy()
    for preferred in suburb_data.get("style_bias", []):
        matching = [s for s in style_pool if preferred.lower() in s.lower()]
        if matching:
            style_pool.extend(matching * 2)  # Bias toward preferred
    architectural_style = random.choice(style_pool)
    
    # Features (probability-based)
    features_outdoor = []
    features_indoor = []
    features_premium = []
    
    for feature, prob, _ in FEATURES["outdoor"]:
        if random.random() < prob:
            features_outdoor.append(feature)
    
    for feature, prob, _ in FEATURES["indoor"]:
        if random.random() < prob:
            features_indoor.append(feature)
            
    for feature, prob, _ in FEATURES["premium"]:
        if random.random() < prob:
            features_premium.append(feature)
    
    # Load market data for realistic calibration
    try:
        from src.services.market_data import get_market_data
        market_data = get_market_data()
        wa_yield_house = float(market_data.wa.gross_yield_house) * 100  # 4.5%
        wa_yield_unit = float(market_data.wa.gross_yield_unit) * 100    # 6.0%
        rental_growth = float(market_data.wa.rental_growth_yoy)         # 8%
    except Exception:
        # Fallback values if market data unavailable
        wa_yield_house = 4.5
        wa_yield_unit = 6.0
        rental_growth = 0.08
    
    # Valuation based on suburb median with variance
    variance = suburb_data["price_variance"]
    base_price = suburb_data["median_price"]
    
    # Adjust for bedrooms
    bed_adjustment = (bedrooms - 3) * 0.15
    
    # Adjust for features
    feature_count = len(features_outdoor) + len(features_indoor) + len(features_premium)
    feature_adjustment = feature_count * 0.02
    
    # Calculate final valuation
    multiplier = 1 + bed_adjustment + feature_adjustment + random.uniform(-variance, variance)
    valuation = int(base_price * multiplier)
    
    # Gross yield - calibrated to real WA market data
    # Units typically yield higher than houses
    if property_type == "apartment":
        base_yield = wa_yield_unit + random.uniform(-0.5, 0.5)
    else:
        base_yield = wa_yield_house + random.uniform(-0.5, 0.5)
    
    # Premium properties typically have lower yields
    if valuation > 2500000:
        base_yield -= 0.5
    elif valuation < 800000:
        base_yield += 0.3  # More affordable = higher yield
    
    # Tight rental market boosts potential yield
    if rental_growth > 0.05:
        base_yield += 0.2
    
    gross_yield = round(max(3.0, min(7.0, base_yield)), 1)
    
    return PropertyData(
        id=f"prop_{index + 1:03d}",
        address=address,
        suburb=suburb,
        postcode=suburb_data["postcode"],
        property_type=property_type,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        parking=parking,
        land_size=land_size,
        build_area=build_area,
        architectural_style=architectural_style,
        features_outdoor=features_outdoor,
        features_indoor=features_indoor,
        features_premium=features_premium,
        valuation=valuation,
        gross_yield=gross_yield,
    )


# =============================================================================
# Listing Generator (Gemini)
# =============================================================================

LISTING_SYSTEM_PROMPT = """You are a premium Australian real estate copywriter generating property listings for the OSF Network simulation.

Your output must be valid JSON matching the exact structure provided. Be creative but factual - all numbers must match the input data.

Style: Premium Australian real estate marketing
Tone: Aspirational, sophisticated, lifestyle-focused
Length: Features description 2-3 paragraphs, lifestyle 1-2 paragraphs"""

LISTING_USER_PROMPT = """Generate a complete property listing for:

ADDRESS: {address}, {suburb}, WA {postcode}
TYPE: {property_type} ({bedrooms} bed, {bathrooms} bath, {parking} parking)
LAND: {land_size}m² | BUILD: {build_area}m²
STYLE: {architectural_style}
OUTDOOR FEATURES: {features_outdoor}
INDOOR FEATURES: {features_indoor}
PREMIUM FEATURES: {features_premium}
VALUATION: ${valuation:,}
YIELD: {gross_yield}%

SUBURB INFO:
- Vibe: {suburb_vibe}
- Amenities: {suburb_amenities}
- Schools: {suburb_schools}

Generate JSON with this EXACT structure:
{{
  "headline": "ASPIRATIONAL CAPS HEADLINE (8-12 words)",
  "subheadline": "{address}, {suburb}",
  "quick_stats": {{
    "bedrooms": {bedrooms},
    "bathrooms": {bathrooms},
    "parking": {parking},
    "land_size": "{land_size}m²",
    "build_area": "{build_area}m²",
    "property_type": "{property_type}",
    "status": "Available"
  }},
  "highlights": [
    {{"icon": "icon_name", "title": "Short Title", "description": "One line description"}},
    {{"icon": "icon_name", "title": "Short Title", "description": "One line description"}},
    {{"icon": "icon_name", "title": "Short Title", "description": "One line description"}}
  ],
  "features_description": {{
    "title": "THE FEATURES YOU WILL LOVE",
    "content": "2-3 paragraphs of elegant marketing copy describing the property..."
  }},
  "lifestyle_description": {{
    "title": "THE LIFESTYLE YOU WILL LIVE",
    "content": "1-2 paragraphs about location, amenities, lifestyle benefits..."
  }},
  "property_features": {{
    "building_size": "{build_area}m²",
    "land_size": "{land_size}m²",
    "indoor": ["feature1", "feature2"],
    "outdoor": ["feature1", "feature2"]
  }},
  "rates": {{
    "council": <estimated annual council rates>,
    "water": <estimated annual water rates>
  }},
  "nearby": {{
    "schools": [{{"name": "School Name", "distance": "0.5km", "type": "Government"}}],
    "amenities": ["Amenity 1", "Amenity 2"]
  }},
  "image_brief": {{
    "style": "Photorealistic 3D architectural render, 45-degree isometric aerial view",
    "building": "Detailed description of the building exterior...",
    "roof_features": "Description of roof, solar panels if applicable...",
    "outdoor_structures": "Garage, carport, shed details...",
    "pool_area": "Pool description if applicable, otherwise omit...",
    "landscaping": "Garden, lawn, trees, fencing description...",
    "materials": "Visible materials - tiles, timber, render, stone...",
    "atmosphere": "Lighting, mood, premium feel description"
  }},
  "floorplan_brief": {{
    "layout_type": "Single level / Two storey / Split level",
    "orientation": "North to rear / East facing etc",
    "total_area": "{build_area}m²",
    "rooms": [
      {{"name": "Room Name", "area": "Xm²", "wing": "position", "features": ["feature1"]}}
    ],
    "flow_description": "How the spaces connect and flow...",
    "special_features": ["Feature 1", "Feature 2"]
  }}
}}

IMPORTANT: 
- All numbers must match input exactly
- image_brief must be detailed enough for image generation
- Be creative with marketing copy but factual with stats"""


def generate_property_listing_sync(property_data: PropertyData) -> Optional[PropertyListing]:
    """Generate marketing listing using Gemini (sync version)."""
    
    if not settings.google_api_key:
        logger.warning("listing_generation_skipped", reason="No API key")
        return None
    
    suburb_info = SUBURBS.get(property_data.suburb, {})
    
    prompt = LISTING_USER_PROMPT.format(
        address=property_data.address,
        suburb=property_data.suburb,
        postcode=property_data.postcode,
        property_type=property_data.property_type.title(),
        bedrooms=property_data.bedrooms,
        bathrooms=property_data.bathrooms,
        parking=property_data.parking,
        land_size=property_data.land_size,
        build_area=property_data.build_area,
        architectural_style=property_data.architectural_style,
        features_outdoor=", ".join(property_data.features_outdoor) or "Standard",
        features_indoor=", ".join(property_data.features_indoor) or "Standard",
        features_premium=", ".join(property_data.features_premium) or "None",
        valuation=property_data.valuation,
        gross_yield=property_data.gross_yield,
        suburb_vibe=suburb_info.get("vibe", "Desirable location"),
        suburb_amenities=", ".join(suburb_info.get("amenities", [])),
        suburb_schools=", ".join(suburb_info.get("schools", [])),
    )
    
    try:
        client = genai.Client(api_key=settings.google_api_key)
        
        # Use sync client instead of async
        response = client.models.generate_content(
            model=settings.gemini_model,  # Use flash for speed
            contents=[types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )],
            config=types.GenerateContentConfig(
                system_instruction=LISTING_SYSTEM_PROMPT,
                temperature=0.8,
                max_output_tokens=4000,
                response_mime_type="application/json",
            ),
        )
        
        # Parse response
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        parsed = json.loads(text)
        
        # Handle both array and object responses
        if isinstance(parsed, list):
            data = parsed[0] if parsed else {}
        else:
            data = parsed
        
        return PropertyListing(
            property_id=property_data.id,
            headline=data.get("headline", ""),
            subheadline=data.get("subheadline", ""),
            quick_stats=data.get("quick_stats", {}),
            highlights=data.get("highlights", []),
            features_description=data.get("features_description", {}),
            lifestyle_description=data.get("lifestyle_description", {}),
            property_features=data.get("property_features", {}),
            rates=data.get("rates", {}),
            nearby=data.get("nearby", {}),
            image_brief=data.get("image_brief", {}),
            floorplan_brief=data.get("floorplan_brief", {}),
            generated_at=datetime.utcnow().isoformat(),
        )
        
    except Exception as e:
        logger.error("listing_generation_failed", error=str(e), property_id=property_data.id)
        return None


async def generate_property_listing(property_data: PropertyData) -> Optional[PropertyListing]:
    """Generate marketing listing using Gemini (async wrapper)."""
    # Use sync version to avoid aiohttp issues
    import asyncio
    return await asyncio.get_event_loop().run_in_executor(
        None, generate_property_listing_sync, property_data
    )


# =============================================================================
# Full Property Generation
# =============================================================================

async def generate_complete_property(
    suburb: Optional[str] = None,
    property_type: Optional[str] = None,
    index: int = 0,
    generate_images: bool = False,
) -> GeneratedProperty:
    """Generate a complete property with data, listing, and optionally images."""
    
    # Step 1: Generate property data
    property_data = generate_property_data(suburb, property_type, index)
    
    logger.info("property_data_generated",
               id=property_data.id,
               suburb=property_data.suburb,
               type=property_data.property_type,
               beds=property_data.bedrooms)
    
    # Step 2: Generate listing
    listing = await generate_property_listing(property_data)
    
    if listing:
        logger.info("property_listing_generated",
                   id=property_data.id,
                   headline=listing.headline[:50])
    
    # Step 3: Generate images (if requested - handled by image_generator.py)
    images = {}
    if generate_images and listing:
        # Import here to avoid circular dependency
        from src.services.image_generator import generate_property_images
        images = await generate_property_images(listing.image_brief, listing.floorplan_brief)
    
    return GeneratedProperty(
        id=property_data.id,
        status="draft",
        data=property_data,
        listing=listing,
        images=images,
        created_at=datetime.utcnow().isoformat(),
    )
