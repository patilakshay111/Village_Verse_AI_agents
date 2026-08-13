"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-05

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "families",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("surname", sa.String(64), nullable=False),
        sa.Column("reputation", sa.Float(), default=50.0),
        sa.Column("wealth", sa.Float(), default=50.0),
        sa.Column("influence", sa.Float(), default=50.0),
        sa.Column("traditions", sa.Text(), nullable=True),
    )
    op.create_table(
        "locations",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_table(
        "simulation_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("current_day", sa.Integer(), default=1),
        sa.Column("current_time", sa.String(32), default="Morning"),
        sa.Column("tick_count", sa.Integer(), default=0),
        sa.Column("status", sa.String(32), default="idle"),
        sa.Column("weather", sa.String(64), default="Clear"),
        sa.Column("last_tick_at", sa.DateTime(), nullable=True),
        sa.Column("last_error", sa.String(512), nullable=True),
    )
    op.create_table(
        "villagers",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("gender", sa.String(16), nullable=False),
        sa.Column("occupation", sa.String(64), nullable=False),
        sa.Column("education", sa.String(64), nullable=True),
        sa.Column("family_id", sa.String(64), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("location_id", sa.String(64), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("personality", sa.Text(), nullable=True),
        sa.Column("humor_style", sa.String(64), nullable=True),
        sa.Column("temperament", sa.String(64), nullable=True),
        sa.Column("goals", sa.Text(), nullable=True),
        sa.Column("fears", sa.Text(), nullable=True),
        sa.Column("dreams", sa.Text(), nullable=True),
        sa.Column("hobbies", sa.Text(), nullable=True),
        sa.Column("financial_status", sa.String(64), nullable=True),
        sa.Column("social_status", sa.String(64), nullable=True),
        sa.Column("daily_schedule", sa.Text(), nullable=True),
        sa.Column("current_emotion", sa.String(32), default="Neutral"),
        sa.Column("emotion_intensity", sa.Float(), default=0.3),
    )
    op.create_table(
        "relationships",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("agent_a_id", sa.String(64), sa.ForeignKey("villagers.id"), nullable=False),
        sa.Column("agent_b_id", sa.String(64), sa.ForeignKey("villagers.id"), nullable=False),
        sa.Column("friendship", sa.Float(), default=0.0),
        sa.Column("trust", sa.Float(), default=0.0),
        sa.Column("respect", sa.Float(), default=0.0),
        sa.Column("rivalry", sa.Float(), default=0.0),
        sa.Column("romantic_interest", sa.Float(), default=0.0),
        sa.Column("family_bond", sa.Float(), default=0.0),
        sa.Column("last_reason", sa.Text(), nullable=True),
    )
    op.create_table(
        "memories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("agent_id", sa.String(64), sa.ForeignKey("villagers.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("emotion", sa.String(32), nullable=True),
        sa.Column("importance", sa.Float(), default=0.5),
        sa.Column("participants", sa.Text(), nullable=True),
        sa.Column("sim_timestamp", sa.String(64), nullable=True),
        sa.Column("tick_id", sa.Integer(), nullable=True),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("event_id", sa.String(64), nullable=False),
        sa.Column("tick_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("importance", sa.Float(), default=0.5),
        sa.Column("affected_agents", sa.Text(), nullable=True),
        sa.Column("expected_consequences", sa.Text(), nullable=True),
        sa.Column("location_id", sa.String(64), sa.ForeignKey("locations.id"), nullable=True),
    )
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tick_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.String(64), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("event_id", sa.String(64), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=False),
        sa.Column("participants", sa.Text(), nullable=True),
        sa.Column("important_moments", sa.Text(), nullable=True),
    )
    op.create_table(
        "stories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("story_id", sa.String(64), nullable=False, unique=True),
        sa.Column("tick_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("full_story", sa.Text(), nullable=True),
        sa.Column("date", sa.String(32), nullable=True),
        sa.Column("time", sa.String(32), nullable=True),
        sa.Column("location", sa.String(128), nullable=True),
        sa.Column("category", sa.String(64), nullable=True),
        sa.Column("importance", sa.Float(), default=0.5),
        sa.Column("participants", sa.Text(), nullable=True),
        sa.Column("families", sa.Text(), nullable=True),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("relationship_changes", sa.Text(), nullable=True),
        sa.Column("future_hooks", sa.Text(), nullable=True),
        sa.Column("related_story_ids", sa.Text(), nullable=True),
    )
    op.create_table(
        "rumors",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("rumor_id", sa.String(64), nullable=False, unique=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_agent_id", sa.String(64), sa.ForeignKey("villagers.id"), nullable=True),
        sa.Column("heard_by", sa.Text(), nullable=True),
        sa.Column("truth_level", sa.Float(), default=0.7),
        sa.Column("distortion_level", sa.Float(), default=0.0),
        sa.Column("spread_count", sa.Integer(), default=1),
        sa.Column("importance", sa.Float(), default=0.3),
        sa.Column("related_event_id", sa.String(64), nullable=True),
        sa.Column("tick_id", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("rumors")
    op.drop_table("stories")
    op.drop_table("conversations")
    op.drop_table("events")
    op.drop_table("memories")
    op.drop_table("relationships")
    op.drop_table("villagers")
    op.drop_table("simulation_runs")
    op.drop_table("locations")
    op.drop_table("families")
