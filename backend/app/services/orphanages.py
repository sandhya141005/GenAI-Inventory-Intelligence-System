ORPHANAGE_SEED = [
    {"name": "Sunrise Children's Home", "city": "Chennai", "email": "sunrise.home@example.org"},
    {"name": "Asha Nivas Care Centre", "city": "Chennai", "email": "asha.nivas@example.org"},
    {"name": "Hope Bridge Foundation", "city": "Bangalore", "email": "hope.bridge@example.org"},
    {"name": "Little Stars Home", "city": "Bangalore", "email": "little.stars@example.org"},
    {"name": "Bal Asha Trust", "city": "Mumbai", "email": "balasha.demo@example.org"},
    {"name": "Udaan Children's Shelter", "city": "Delhi", "email": "udaan.shelter@example.org"},
    {"name": "Sahyog Child Care", "city": "Pune", "email": "sahyog.care@example.org"},
    {"name": "New Dawn Home", "city": "Hyderabad", "email": "newdawn.home@example.org"},
    {"name": "Anandam Child Support", "city": "Kolkata", "email": "anandam.support@example.org"},
    {"name": "Prerna Home", "city": "Ahmedabad", "email": "prerna.home@example.org"},
]


def match_orphanages(city: str | None) -> list[dict]:
    if not city:
        return ORPHANAGE_SEED
    matches = [orphanage for orphanage in ORPHANAGE_SEED if orphanage["city"].lower() == city.lower()]
    return matches or ORPHANAGE_SEED
