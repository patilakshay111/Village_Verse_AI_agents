import json
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.event import Event
from app.models.family import Family
from app.models.location import Location
from app.models.memory import Memory
from app.models.relationship import Relationship
from app.models.story import Story
from app.models.villager import Villager


def list_villagers(
    db: Session,
    *,
    family_id: str | None = None,
    location_id: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[Villager], int]:
    q = db.query(Villager)
    if family_id:
        q = q.filter(Villager.family_id == family_id)
    if location_id:
        q = q.filter(Villager.location_id == location_id)
    total = q.count()
    rows = q.offset(offset).limit(limit).all()
    return rows, total


def get_villager_detail(db: Session, villager_id: str) -> dict[str, Any] | None:
    villager = db.query(Villager).filter(Villager.id == villager_id).first()
    if not villager:
        return None

    memories = (
        db.query(Memory)
        .filter(Memory.agent_id == villager_id)
        .order_by(Memory.importance.desc())
        .limit(10)
        .all()
    )

    rels = (
        db.query(Relationship)
        .filter(
            or_(
                Relationship.agent_a_id == villager_id,
                Relationship.agent_b_id == villager_id,
            )
        )
        .all()
    )

    friends = []
    rivals = []
    for r in rels:
        other_id = r.agent_b_id if r.agent_a_id == villager_id else r.agent_a_id
        other = db.query(Villager).filter(Villager.id == other_id).first()
        if not other:
            continue
        entry = {
            "agent_id": other_id,
            "name": other.name,
            "friendship": r.friendship,
            "rivalry": r.rivalry,
        }
        if r.friendship >= 30:
            friends.append(entry)
        if r.rivalry >= 30:
            rivals.append(entry)

    stories = db.query(Story).order_by(Story.id.desc()).limit(20).all()
    recent = []
    for s in stories:
        participants = json.loads(s.participants or "[]")
        names_match = villager.name in participants or villager_id in participants
        if names_match:
            recent.append(
                {
                    "story_id": s.story_id,
                    "title": s.title,
                    "importance": s.importance,
                }
            )
        if len(recent) >= 5:
            break

    return {
        "villager": villager,
        "memories": memories,
        "friends": friends,
        "rivals": rivals,
        "recent_stories": recent,
    }


def list_stories(
    db: Session,
    *,
    date: str | None = None,
    time_from: str | None = None,
    time_to: str | None = None,
    category: str | None = None,
    villager_id: str | None = None,
    family_id: str | None = None,
    location: str | None = None,
    importance_min: float | None = None,
    q: str | None = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[Story], int]:
    query = db.query(Story)
    if date:
        query = query.filter(Story.date == date)
    if category:
        query = query.filter(Story.category == category)
    if location:
        query = query.filter(Story.location.ilike(f"%{location}%"))
    if importance_min is not None:
        query = query.filter(Story.importance >= importance_min)
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(Story.title.ilike(pattern), Story.summary.ilike(pattern))
        )

    rows = query.order_by(Story.id.desc()).all()

    if villager_id:
        villager = db.query(Villager).filter(Villager.id == villager_id).first()
        if villager:
            rows = [
                s
                for s in rows
                if villager.name in json.loads(s.participants or "[]")
                or villager_id in json.loads(s.participants or "[]")
            ]

    if family_id:
        family = db.query(Family).filter(Family.id == family_id).first()
        if family:
            rows = [
                s
                for s in rows
                if family.name in json.loads(s.families or "[]")
                or family.surname in json.loads(s.families or "[]")
            ]

    if time_from or time_to:
        filtered = []
        for s in rows:
            t = s.time or ""
            if time_from and t < time_from:
                continue
            if time_to and t > time_to:
                continue
            filtered.append(s)
        rows = filtered

    total = len(rows)
    return rows[offset : offset + limit], total


def list_conversations(
    db: Session,
    *,
    tick_id: int | None = None,
    villager_id: str | None = None,
    location_id: str | None = None,
    q: str | None = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[tuple[Conversation, str | None]], int]:
    query = db.query(Conversation, Location.name).outerjoin(
        Location, Conversation.location_id == Location.id
    )
    if tick_id is not None:
        query = query.filter(Conversation.tick_id == tick_id)
    if location_id:
        query = query.filter(Conversation.location_id == location_id)
    if q:
        pattern = f"%{q}%"
        query = query.filter(Conversation.transcript.ilike(pattern))

    rows = query.order_by(Conversation.id.desc()).all()

    if villager_id:
        villager = db.query(Villager).filter(Villager.id == villager_id).first()
        if villager:
            filtered = []
            for conv, loc_name in rows:
                participants = json.loads(conv.participants or "[]")
                if villager.name in participants or villager_id in participants:
                    filtered.append((conv, loc_name))
                elif villager.name.lower() in (conv.transcript or "").lower():
                    filtered.append((conv, loc_name))
            rows = filtered

    total = len(rows)
    return rows[offset : offset + limit], total


def get_conversation(db: Session, conversation_id: int) -> tuple[Conversation, str | None] | None:
    row = (
        db.query(Conversation, Location.name)
        .outerjoin(Location, Conversation.location_id == Location.id)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    return row if row else None


def get_conversation_by_tick(db: Session, tick_id: int) -> tuple[Conversation, str | None] | None:
    row = (
        db.query(Conversation, Location.name)
        .outerjoin(Location, Conversation.location_id == Location.id)
        .filter(Conversation.tick_id == tick_id)
        .order_by(Conversation.id.desc())
        .first()
    )
    return row if row else None


def list_families(db: Session) -> list[Family]:
    return db.query(Family).order_by(Family.name).all()


def get_family_detail(db: Session, family_id: str) -> dict[str, Any] | None:
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        return None
    members = db.query(Villager).filter(Villager.family_id == family_id).all()
    return {"family": family, "members": members}


def list_locations(db: Session) -> list[Location]:
    return db.query(Location).order_by(Location.name).all()
