"""Governance, tender, romance, and daru plotlines — seed hooks and runtime lore."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from app.models.memory import Memory
from app.models.relationship import Relationship
from app.models.rumor import Rumor
from app.models.villager import Villager
from app.prompts.loader import get_prompt_loader

if TYPE_CHECKING:
    pass

# Stable roles applied after random family generation
SARPANCH_NAME = "Vikram Deshmukh"
GRAM_SEVAK_NAME = "Devendra Joshi"
CONTRACTOR_NAME = "Sunil More"
PATIL_ELDER_NAME = "Raghunath Patil"
LOVER_FEMALE_NAME = "Priya Sharma"
LOVER_MALE_NAME = "Kiran Pawar"

PLOT_CATEGORIES = frozenset(
    {"Panchayat", "Tender", "Corruption", "Political", "Romance", "Daru", "Conflict"}
)


def get_lore_summary(max_chars: int = 2200) -> str:
    try:
        text = get_prompt_loader().load_raw("village_lore")
    except FileNotFoundError:
        return ""
    return text[:max_chars] if len(text) > max_chars else text


def get_active_plots() -> dict:
    """Compact plot state injected into world_state for the LLM."""
    return {
        "gram_panchayat": {
            "sarpanch": SARPANCH_NAME,
            "gram_sevak": GRAM_SEVAK_NAME,
            "office": "Gram Panchayat Bhavan",
        },
        "tender_work": {
            "project": "PMGSY road and gutter (₹42 lakh)",
            "site": "Nagar Road Work Site",
            "contractor": CONTRACTOR_NAME,
            "opposition_leader": PATIL_ELDER_NAME,
            "issues": [
                "Low-quality gravel and thin gutter slabs alleged",
                "Patil family blocking work near farm boundary",
                "Rumors of bribes to gram sevak and panchayat approval",
            ],
        },
        "secret_romance": {
            "lovers": [LOVER_FEMALE_NAME, LOVER_MALE_NAME],
            "meeting_places": ["Water Well at dusk", "Community Hall"],
            "risk": "Families would forbid marriage",
        },
        "daru_scene": {
            "location": "Country Liquor Shed",
            "themes": ["masti and songs", "drunk arguments about tender", "occasional fights", "serious worries about money and crops"],
        },
    }


def _pick(
    villagers: list[Villager],
    *,
    family_id: str | None = None,
    gender: str | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
    occupation: str | None = None,
) -> Villager | None:
    pool = villagers
    if family_id:
        pool = [v for v in pool if v.family_id == family_id]
    if gender:
        pool = [v for v in pool if v.gender == gender]
    if min_age is not None:
        pool = [v for v in pool if v.age >= min_age]
    if max_age is not None:
        pool = [v for v in pool if v.age <= max_age]
    if occupation:
        pool = [v for v in pool if v.occupation == occupation]
    if not pool:
        return None
    return max(pool, key=lambda v: v.age)


def _set_villager(
    v: Villager,
    *,
    name: str | None = None,
    occupation: str | None = None,
    location_id: str | None = None,
    traits: list[str] | None = None,
    goals: list[str] | None = None,
    fears: list[str] | None = None,
    hobbies: list[str] | None = None,
    temperament: str | None = None,
) -> None:
    if name:
        v.name = name
    if occupation:
        v.occupation = occupation
    if location_id:
        v.location_id = location_id
    if traits:
        v.personality = json.dumps(traits)
    if goals:
        v.goals = json.dumps(goals)
    if fears:
        v.fears = json.dumps(fears)
    if hobbies:
        v.hobbies = json.dumps(hobbies)
    if temperament:
        v.temperament = temperament


def _relationship(db: Session, a_id: str, b_id: str) -> Relationship | None:
    pair = sorted([a_id, b_id])
    return (
        db.query(Relationship)
        .filter(
            Relationship.agent_a_id == pair[0],
            Relationship.agent_b_id == pair[1],
        )
        .first()
    )


def apply_village_plots(db: Session, villagers: list[Villager]) -> dict[str, str]:
    """Pin named roles, memories, rumors, and secret romance after base seed."""
    ids: dict[str, str] = {}

    sarpanch = _pick(villagers, family_id="deshmukh", gender="Male", min_age=40)
    if sarpanch:
        _set_villager(
            sarpanch,
            name=SARPANCH_NAME,
            occupation="Sarpanch",
            location_id="panchayat",
            traits=["Ambitious", "Clever", "Practical"],
            goals=["Win next panchayat election", "Show road work completed before monsoon"],
            fears=["Anti-corruption complaint", "Deshmukh reputation damage"],
            temperament="Serious",
        )
        ids["sarpanch"] = sarpanch.id

    gram_sevak = _pick(villagers, family_id="joshi", gender="Male", min_age=30, max_age=50)
    if not gram_sevak:
        gram_sevak = _pick(villagers, gender="Male", min_age=28, max_age=45)
    if gram_sevak:
        _set_villager(
            gram_sevak,
            name=GRAM_SEVAK_NAME,
            occupation="Gram Sevak",
            location_id="panchayat",
            traits=["Honest", "Practical", "Introvert"],
            goals=["Keep government job", "Finish tender paperwork correctly"],
            fears=["Transfer order", "Being named in bribe rumor"],
            temperament="Calm",
        )
        ids["gram_sevak"] = gram_sevak.id

    contractor = _pick(villagers, family_id="more", gender="Male", min_age=30)
    if contractor:
        _set_villager(
            contractor,
            name=CONTRACTOR_NAME,
            occupation="Contractor",
            location_id="construction_site",
            traits=["Ambitious", "Clever", "Gossip Lover"],
            goals=["Complete road tender on paper", "Maximize margin on materials"],
            fears=["Work stoppage by Patil family", "Quality inspection"],
            temperament="Fiery",
        )
        ids["contractor"] = contractor.id

    patil_elder = _pick(villagers, family_id="patil", gender="Male", min_age=65)
    if not patil_elder:
        patil_males = [v for v in villagers if v.family_id == "patil" and v.gender == "Male"]
        patil_elder = max(patil_males, key=lambda v: v.age) if patil_males else None
    if patil_elder:
        _set_villager(
            patil_elder,
            name=PATIL_ELDER_NAME,
            occupation="Farmer",
            location_id="farm_lands",
            traits=["Honest", "Fiery", "Practical"],
            goals=["Stop gutter work flooding sugarcane", "Protect Patil land"],
            fears=["Panchayat ignoring farmers", "Cheap contractor work"],
            temperament="Fiery",
        )
        ids["patil_elder"] = patil_elder.id

    priya = _pick(villagers, family_id="sharma", gender="Female", min_age=20, max_age=28)
    if not priya:
        sharma_f = [
            v for v in villagers if v.family_id == "sharma" and v.gender == "Female" and v.age >= 18
        ]
        young = [v for v in sharma_f if v.age <= 30]
        priya = min(young, key=lambda v: abs(v.age - 24)) if young else (max(sharma_f, key=lambda v: v.age) if sharma_f else None)
    kiran = _pick(villagers, family_id="pawar", gender="Male", min_age=22, max_age=32)
    if not kiran:
        pawar_m = [v for v in villagers if v.family_id == "pawar" and v.gender == "Male"]
        kiran = min(pawar_m, key=lambda v: abs(v.age - 26)) if pawar_m else None
    if priya and kiran:
        if kiran.age < 20:
            kiran.age = 24
            kiran.occupation = "Driver"
        _set_villager(
            priya,
            name=LOVER_FEMALE_NAME,
            occupation="Teacher" if priya.age >= 22 else priya.occupation,
            location_id="school",
            traits=["Romantic", "Emotional", "Clever"],
            goals=["Marry Kiran someday", "Keep love secret from Sharma elders"],
            fears=["Family honour scandal", "Village gossip"],
            hobbies=["Reading", "Evening walks near well"],
        )
        _set_villager(
            kiran,
            name=LOVER_MALE_NAME,
            location_id="bus_stop",
            traits=["Romantic", "Friendly", "Emotional"],
            goals=["Save money", "Meet Priya without Pawar family knowing"],
            fears=["Father finding out", "Losing driving job"],
            hobbies=["Cricket", "Bollywood songs"],
        )
        ids["lover_female"] = priya.id
        ids["lover_male"] = kiran.id

        rel = _relationship(db, priya.id, kiran.id)
        if not rel:
            pair = sorted([priya.id, kiran.id])
            rel = Relationship(
                agent_a_id=pair[0],
                agent_b_id=pair[1],
                friendship=72.0,
                trust=68.0,
                respect=55.0,
                romantic_interest=78.0,
                rivalry=5.0,
                last_reason="Secret meetings; not yet public",
            )
            db.add(rel)
        else:
            rel.friendship = max(rel.friendship, 70.0)
            rel.romantic_interest = max(rel.romantic_interest, 75.0)
            rel.trust = max(rel.trust, 65.0)
            rel.last_reason = "Secret love; families must not know"

    if ids.get("sarpanch") and ids.get("contractor"):
        rel = _relationship(db, ids["sarpanch"], ids["contractor"])
        if rel:
            rel.friendship = max(rel.friendship, 45.0)
            rel.trust = max(rel.trust, 40.0)
            rel.last_reason = "Tender allies; village whispers about kickbacks"

    if ids.get("patil_elder") and ids.get("contractor"):
        rel = _relationship(db, ids["patil_elder"], ids["contractor"])
        if rel:
            rel.rivalry = max(rel.rivalry, 55.0)
            rel.respect = min(rel.respect, 25.0)
            rel.friendship = min(rel.friendship, 20.0)
            rel.last_reason = "Road and gutter dispute at farm boundary"

    if ids.get("patil_elder") and ids.get("sarpanch"):
        rel = _relationship(db, ids["patil_elder"], ids["sarpanch"])
        if rel:
            rel.rivalry = max(rel.rivalry, 40.0)
            rel.respect = max(rel.respect, 35.0)
            rel.last_reason = "Panchayat sabha clash over stopping tender work"

    _seed_plot_memories(db, ids)
    _seed_plot_rumors(db, ids)
    db.flush()
    return ids


def _seed_plot_memories(db: Session, ids: dict[str, str]) -> None:
    entries: list[tuple[str, str, float, str]] = []

    if sid := ids.get("sarpanch"):
        entries.append(
            (
                sid,
                "Chaired gram sabha: Patil family demanded halt to gutter work; promised 'quality inspection next week'.",
                0.75,
                "Frustrated",
            )
        )
    if gid := ids.get("gram_sevak"):
        entries.append(
            (
                gid,
                "Contractor's man offered an envelope at the panchayat office — refused but still uneasy about signing sheets.",
                0.85,
                "Fearful",
            )
        )
    if cid := ids.get("contractor"):
        entries.append(
            (
                cid,
                "Using cheaper gravel mix to stay within tender rate; Sunil told workers 'finish before Patil blocks us'.",
                0.8,
                "Hopeful",
            )
        )
    if pid := ids.get("patil_elder"):
        entries.append(
            (
                pid,
                "Told panchayat loudly: 'We will not allow this work' — open gutter will ruin our field drainage.",
                0.9,
                "Angry",
            )
        )
    lf = ids.get("lover_female")
    lm = ids.get("lover_male")
    if lf and lm:
        entries.append(
            (
                lf,
                f"Met {LOVER_MALE_NAME} quietly at the water well after sunset; Sharma family must never know.",
                0.88,
                "Hopeful",
            )
        )
        entries.append(
            (
                lm,
                f"Promised {LOVER_FEMALE_NAME} they will find a way; borrowed friend's bike for secret meeting.",
                0.86,
                "Happy",
            )
        )

    for agent_id, content, importance, emotion in entries:
        db.add(
            Memory(
                agent_id=agent_id,
                content=content,
                emotion=emotion,
                importance=importance,
                participants=json.dumps([]),
                sim_timestamp="Day 1 Morning",
                tick_id=0,
            )
        )


def _seed_plot_rumors(db: Session, ids: dict[str, str]) -> None:
    rumors = [
        (
            "rumor_tender_bribe",
            "Someone says five percent of the road tender went to the panchayat office before work started.",
            ids.get("contractor"),
            0.45,
            0.35,
            0.7,
        ),
        (
            "rumor_secret_lovers",
            "Tea stall talk: a Sharma girl and a Pawar boy were seen talking too long near the water well.",
            ids.get("lover_female"),
            0.55,
            0.5,
            0.55,
        ),
        (
            "rumor_daru_fight",
            "Last Saturday at the country liquor shed, two men nearly fought over the gutter tender — names unclear.",
            None,
            0.4,
            0.6,
            0.5,
        ),
    ]
    for rid, content, source, truth, distortion, importance in rumors:
        if db.query(Rumor).filter(Rumor.rumor_id == rid).first():
            continue
        db.add(
            Rumor(
                rumor_id=rid,
                content=content,
                source_agent_id=source,
                heard_by=json.dumps([]),
                truth_level=truth,
                distortion_level=distortion,
                spread_count=2,
                importance=importance,
                tick_id=0,
            )
        )


def plot_agent_ids(db: Session) -> set[str]:
    """Villager IDs tied to named plot roles (for agent selection)."""
    names = {
        SARPANCH_NAME,
        GRAM_SEVAK_NAME,
        CONTRACTOR_NAME,
        PATIL_ELDER_NAME,
        LOVER_FEMALE_NAME,
        LOVER_MALE_NAME,
    }
    rows = db.query(Villager.id).filter(Villager.name.in_(names)).all()
    return {r[0] for r in rows}
