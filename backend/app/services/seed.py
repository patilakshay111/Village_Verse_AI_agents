"""Seed Anandgaon with families, villagers, locations, and relationships."""

import json
import random
import uuid

from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.base import Base, SessionLocal, engine, init_db
from app.models.family import Family
from app.models.location import Location
from app.models.relationship import Relationship
from app.models.simulation_run import SimulationRun
from app.models.villager import Villager

LOCATIONS = [
    ("main_chowk", "Main Chowk", "Central gathering place"),
    ("tea_stall", "Tea Stall", "Daily gossip hub"),
    ("temple", "Temple", "Morning prayers and festivals"),
    ("mosque", "Mosque", "Community prayers"),
    ("school", "School", "Children and teachers"),
    ("panchayat", "Gram Panchayat Bhavan", "Sarpanch office, gram sabha, tender files"),
    ("construction_site", "Nagar Road Work Site", "PMGSY road and gutter tender work"),
    ("country_liquor", "Country Liquor Shed", "Evening daru gatherings and masti"),
    ("farm_lands", "Farm Lands", "Agricultural fields"),
    ("market", "Village Market", "Shops and weekly market"),
    ("bus_stop", "Bus Stop", "Transport connection"),
    ("water_well", "Water Well", "Water collection point"),
    ("community_hall", "Community Hall", "Meetings and events"),
    ("playground", "Playground", "Sports and children"),
    ("dairy", "Dairy Collection Center", "Milk collection"),
    ("hospital", "Small Hospital", "Basic healthcare"),
    ("grocery", "Grocery Shop", "Daily essentials"),
]

# family_id, surname, reputation, wealth, influence, primary_trade
FAMILIES = [
    ("patil", "Patil", 72, 65, 80, "Farmer"),
    ("sharma", "Sharma", 68, 58, 55, "Teacher"),
    ("gupta", "Gupta", 60, 70, 45, "Shopkeeper"),
    ("yadav", "Yadav", 55, 52, 50, "Farmer"),
    ("joshi", "Joshi", 75, 48, 60, "Teacher"),
    ("pawar", "Pawar", 58, 62, 48, "Driver"),
    ("kulkarni", "Kulkarni", 70, 55, 65, "Carpenter"),
    ("deshmukh", "Deshmukh", 80, 75, 85, "Politician"),
    ("jadhav", "Jadhav", 62, 60, 52, "Milkman"),
    ("more", "More", 50, 45, 40, "Mechanic"),
]

FIRST_NAMES_M = [
    "Rohit", "Mahesh", "Suresh", "Ajay", "Vikram", "Prakash", "Sunil", "Ramesh",
    "Anil", "Deepak", "Nitin", "Ganesh", "Sanjay", "Raju", "Kiran", "Arun", "Vijay",
]
FIRST_NAMES_F = [
    "Sunita", "Priya", "Kavita", "Meena", "Anita", "Savitri", "Lata", "Pooja",
    "Radha", "Geeta", "Sneha", "Asha", "Usha", "Rekha", "Nirmala", "Swati", "Varsha",
]

TRAITS = [
    "Friendly", "Honest", "Funny", "Religious", "Practical", "Ambitious",
    "Gossip Lover", "Introvert", "Extrovert", "Clever", "Emotional", "Calm",
    "Corrupt", "Romantic", "Fiery",
]
EMOTIONS = ["Happy", "Neutral", "Hopeful", "Proud", "Calm"]

OCCUPATION_LOCATIONS = {
    "Student": "school",
    "Teacher": "school",
    "Farmer": "farm_lands",
    "Doctor": "hospital",
    "Shopkeeper": "market",
    "Driver": "bus_stop",
    "Milkman": "dairy",
    "Mechanic": "market",
    "Carpenter": "market",
    "Electrician": "market",
    "Tailor": "market",
    "Politician": "panchayat",
    "Sarpanch": "panchayat",
    "Gram Sevak": "panchayat",
    "Contractor": "construction_site",
    "Homemaker": "grocery",
    "Retired": "temple",
    "Farm helper": "farm_lands",
}

EDUCATION_BY_OCCUPATION = {
    "Student": ["Primary", "Secondary"],
    "Teacher": ["Graduate", "Secondary"],
    "Doctor": ["Graduate"],
    "Politician": ["Graduate", "Secondary"],
    "Sarpanch": ["Graduate", "Secondary"],
    "Gram Sevak": ["Graduate", "Secondary"],
    "Contractor": ["Secondary", "Primary"],
    "Farmer": ["Primary", "None", "Secondary"],
    "Shopkeeper": ["Secondary", "Primary"],
    "Driver": ["Primary", "Secondary"],
    "Milkman": ["Primary", "None"],
    "Mechanic": ["Secondary", "Primary"],
    "Carpenter": ["Primary", "Secondary"],
    "Electrician": ["Secondary", "Primary"],
    "Tailor": ["Primary", "Secondary"],
    "Homemaker": ["Primary", "None", "Secondary"],
    "Retired": ["Primary", "Secondary", "None"],
    "Farm helper": ["Primary", "None"],
}


def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _pick_name(gender: str, used: set[str], surname: str) -> str:
    pool = FIRST_NAMES_M if gender == "Male" else FIRST_NAMES_F
    available = [n for n in pool if n not in used]
    if not available:
        available = pool
    first = random.choice(available)
    used.add(first)
    return f"{first} {surname}"


def _occupation_for_age(age: int, gender: str, role: str, family_trade: str) -> str:
    if age < 6:
        return "Student"
    if age <= 17:
        return "Student"
    if age == 18 and random.random() < 0.4:
        return "Student"

    if role == "grandfather":
        if family_trade == "Farmer" and age < 72:
            return "Farmer"
        return "Retired"
    if role == "grandmother":
        return "Homemaker"
    if role == "mother":
        options = ["Homemaker", "Homemaker", family_trade if family_trade in ("Teacher", "Tailor", "Shopkeeper") else "Homemaker"]
        if family_trade == "Teacher":
            options = ["Teacher", "Homemaker", "Homemaker"]
        return random.choice(options)
    if role in ("father", "son_adult", "daughter_adult"):
        if family_trade == "Politician":
            if role == "father":
                return "Sarpanch"
            if role == "son_adult" and age >= 28:
                return random.choice(["Politician", "Teacher", "Shopkeeper"])
            if role == "son_adult":
                return random.choice(["Farmer", "Shopkeeper", "Driver", "Teacher"])
        if role == "son_adult" and gender == "Male":
            return random.choice([family_trade, family_trade, "Farm helper" if family_trade == "Farmer" else family_trade])
        if role == "daughter_adult":
            return random.choice(
                ["Homemaker", "Teacher", "Tailor", "Shopkeeper", family_trade]
                if family_trade not in ("Politician", "Driver", "Mechanic")
                else ["Homemaker", "Teacher", "Tailor"]
            )
        return family_trade

    return family_trade


def _education_for(occupation: str) -> str:
    return random.choice(EDUCATION_BY_OCCUPATION.get(occupation, ["Primary", "Secondary"]))


def _schedule_for(occupation: str) -> dict[str, str]:
    schedules = {
        "Student": {
            "morning": "School",
            "afternoon": "School or homework",
            "evening": "Play or tuition",
            "night": "Rest",
        },
        "Farmer": {
            "morning": "Farm work",
            "afternoon": "Fields or market",
            "evening": "Tea stall",
            "night": "Family",
        },
        "Teacher": {
            "morning": "School",
            "afternoon": "School or papers",
            "evening": "Temple or neighbors",
            "night": "Family",
        },
        "Homemaker": {
            "morning": "Home and water well",
            "afternoon": "Cooking and errands",
            "evening": "Family meal",
            "night": "Home",
        },
        "Retired": {
            "morning": "Temple or chai",
            "afternoon": "Rest in shade",
            "evening": "Tea stall stories",
            "night": "Early sleep",
        },
        "Sarpanch": {
            "morning": "Panchayat office",
            "afternoon": "Village visits or tender site",
            "evening": "Tea stall politics",
            "night": "Family",
        },
        "Gram Sevak": {
            "morning": "Panchayat registers",
            "afternoon": "Road site measurements",
            "evening": "Paperwork at office",
            "night": "Home",
        },
        "Contractor": {
            "morning": "Construction site",
            "afternoon": "Material delivery",
            "evening": "Contractor talks at liquor shed",
            "night": "Accounts",
        },
    }
    return schedules.get(
        occupation,
        {
            "morning": "Work",
            "afternoon": "Village duties",
            "evening": "Tea stall",
            "night": "Family",
        },
    )


def _build_family_members(family: Family, size: int) -> list[dict]:
    """Return list of member specs: role, gender, age, occupation."""
    trade = next(t[5] for t in FAMILIES if t[0] == family.id)
    surname = family.surname
    members: list[dict] = []

    # Household templates by size
    if size >= 5:
        roles = ["grandfather", "grandmother", "father", "mother", "son", "daughter"]
    elif size == 4:
        roles = ["father", "mother", "son", "daughter"]
    else:
        roles = ["father", "mother", "son"]

    # Trim to requested size, prefer keeping parents + kids
    if len(roles) > size:
        priority = ["father", "mother", "son", "daughter", "grandfather", "grandmother"]
        roles = [r for r in priority if r in roles][:size]

    for role in roles:
        if role == "grandfather":
            gender, age = "Male", random.randint(68, 78)
        elif role == "grandmother":
            gender, age = "Female", random.randint(62, 72)
        elif role == "father":
            gender, age = "Male", random.randint(38, 52)
        elif role == "mother":
            gender, age = "Female", random.randint(33, 48)
        elif role == "son":
            if random.random() < 0.55:
                gender, age, role = "Male", random.randint(8, 16), "son"
            else:
                gender, age, role = "Male", random.randint(20, 28), "son_adult"
        elif role == "daughter":
            if random.random() < 0.55:
                gender, age, role = "Female", random.randint(8, 16), "daughter"
            else:
                gender, age, role = "Female", random.randint(19, 26), "daughter_adult"
        else:
            continue

        occupation = _occupation_for_age(age, gender, role, trade)
        members.append(
            {
                "role": role,
                "gender": gender,
                "age": age,
                "occupation": occupation,
            }
        )

    return members


def clear_world(db: Session) -> None:
    from sqlalchemy import delete

    for table in reversed(Base.metadata.sorted_tables):
        db.execute(delete(table))
    db.commit()


def seed_locations(db: Session) -> dict[str, str]:
    mapping = {}
    for loc_id, name, desc in LOCATIONS:
        db.add(Location(id=loc_id, name=name, description=desc))
        mapping[name] = loc_id
    db.flush()
    return mapping


def seed_families(db: Session) -> list[Family]:
    families = []
    for fid, surname, rep, wealth, inf, trade in FAMILIES:
        f = Family(
            id=fid,
            name=f"{surname} Family",
            surname=surname,
            reputation=float(rep),
            wealth=float(wealth),
            influence=float(inf),
            traditions=json.dumps([f"{trade} family", "Festival participation"]),
        )
        db.add(f)
        families.append(f)
    db.flush()
    return families


def seed_villagers(db: Session, families: list[Family], loc_map: dict[str, str]) -> list[Villager]:
    villagers: list[Villager] = []
    target = get_settings().seed_villagers
    count = 0

    for family in families:
        remaining = target - count
        if remaining <= 0:
            break
        size = min(random.randint(3, 5), remaining)
        used_names: set[str] = set()
        specs = _build_family_members(family, size)

        for spec in specs:
            if count >= target:
                break
            occupation = spec["occupation"]
            loc_key = OCCUPATION_LOCATIONS.get(occupation, "main_chowk")
            loc_id = loc_map.get(
                next(name for lid, name, _ in LOCATIONS if lid == loc_key),
                loc_key,
            )

            wealth_band = "Poor" if family.wealth < 50 else "Middle" if family.wealth < 65 else "Comfortable"

            v = Villager(
                id=_uid(family.id),
                name=_pick_name(spec["gender"], used_names, family.surname),
                age=spec["age"],
                gender=spec["gender"],
                occupation=occupation,
                education=_education_for(occupation),
                family_id=family.id,
                location_id=loc_id,
                personality=json.dumps(random.sample(TRAITS, k=3)),
                humor_style=random.choice(["Dry", "Playful", "Warm", "Sarcastic"]),
                temperament=random.choice(["Calm", "Cheerful", "Serious", "Fiery"]),
                goals=json.dumps(
                    ["Support family", "Children's education"]
                    if occupation == "Homemaker"
                    else [f"Excel as {occupation}", "Improve family standing"]
                ),
                fears=json.dumps(["Crop failure", "Health problems"] if occupation == "Farmer" else ["Financial trouble", "Family conflict"]),
                dreams=json.dumps(["Peaceful village life", "Children succeed"]),
                hobbies=json.dumps(
                    ["Cricket", "Farming"] if occupation in ("Farmer", "Farm helper") else ["Cricket", "Tea with friends"]
                ),
                financial_status=wealth_band,
                social_status="Respected" if family.reputation >= 70 else "Average",
                daily_schedule=json.dumps(_schedule_for(occupation)),
                current_emotion=random.choice(EMOTIONS),
                emotion_intensity=round(random.uniform(0.25, 0.65), 2),
            )
            db.add(v)
            villagers.append(v)
            count += 1

    db.flush()
    return villagers


def seed_relationships(db: Session, villagers: list[Villager]) -> None:
    by_family: dict[str, list[Villager]] = {}
    for v in villagers:
        by_family.setdefault(v.family_id, []).append(v)

    for members in by_family.values():
        for i, a in enumerate(members):
            for b in members[i + 1 :]:
                pair = sorted([a.id, b.id])
                db.add(
                    Relationship(
                        agent_a_id=pair[0],
                        agent_b_id=pair[1],
                        family_bond=85.0,
                        friendship=55.0,
                        trust=65.0,
                    )
                )

    ids = [v.id for v in villagers]
    attempts = 0
    added = 0
    while added < min(25, len(ids)) and attempts < 80:
        attempts += 1
        a, b = random.sample(ids, 2)
        if a == b:
            continue
        va = next(v for v in villagers if v.id == a)
        vb = next(v for v in villagers if v.id == b)
        if va.family_id == vb.family_id:
            continue
        pair = sorted([a, b])
        exists = (
            db.query(Relationship)
            .filter(
                Relationship.agent_a_id == pair[0],
                Relationship.agent_b_id == pair[1],
            )
            .first()
        )
        if exists:
            continue
        friendship = random.uniform(10, 60)
        db.add(
            Relationship(
                agent_a_id=pair[0],
                agent_b_id=pair[1],
                friendship=friendship,
                trust=random.uniform(20, 55),
                respect=random.uniform(15, 50),
                rivalry=random.uniform(0, 20) if friendship > 30 else random.uniform(10, 35),
            )
        )
        added += 1

    db.flush()


def seed_simulation(db: Session) -> SimulationRun:
    sim = SimulationRun(current_day=1, current_time="Morning", status="idle")
    db.add(sim)
    db.flush()
    return sim


def run_seed(db: Session | None = None, reset: bool = True) -> dict:
    own_session = db is None
    db = db or SessionLocal()
    try:
        if reset:
            init_db()
            clear_world(db)
        loc_map = seed_locations(db)
        families = seed_families(db)
        villagers = seed_villagers(db, families, loc_map)
        seed_relationships(db, villagers)
        from app.services.village_plots import apply_village_plots

        apply_village_plots(db, villagers)
        from app.services.civilization_seed import seed_civilization_basics

        civ = seed_civilization_basics(db)
        seed_simulation(db)
        db.commit()
        return {
            "families": len(families),
            "villagers": len(villagers),
            "locations": len(LOCATIONS),
            "civilization": civ,
        }
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    init_db()
    result = run_seed()
    print(f"Seeded: {result}")
