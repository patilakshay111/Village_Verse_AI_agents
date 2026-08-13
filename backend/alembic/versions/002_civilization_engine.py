"""civilization engine schema

Revision ID: 002
Revises: 001
Create Date: 2026-06-05

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Villager financial / role fields
    with op.batch_alter_table("villagers") as batch:
        batch.add_column(sa.Column("agent_role", sa.String(64), server_default="villager"))
        batch.add_column(sa.Column("cash", sa.Float(), server_default="0"))
        batch.add_column(sa.Column("bank_balance", sa.Float(), server_default="0"))
        batch.add_column(sa.Column("monthly_income", sa.Float(), server_default="0"))
        batch.add_column(sa.Column("monthly_expenses", sa.Float(), server_default="0"))
        batch.add_column(sa.Column("net_worth", sa.Float(), server_default="0"))
        batch.add_column(sa.Column("reputation", sa.Float(), server_default="50"))
        batch.add_column(sa.Column("skills", sa.Text(), nullable=True))
        batch.add_column(sa.Column("intelligence", sa.Float(), server_default="0.5"))
        batch.add_column(sa.Column("employment_status", sa.String(32), server_default="employed"))
        batch.add_column(sa.Column("active_goal_plan", sa.Text(), nullable=True))

    with op.batch_alter_table("simulation_runs") as batch:
        batch.add_column(sa.Column("civilization_stage", sa.String(64), server_default="Village"))
        batch.add_column(sa.Column("technology_level", sa.Float(), server_default="0.1"))
        batch.add_column(sa.Column("gdp", sa.Float(), server_default="0"))
        batch.add_column(sa.Column("total_wealth", sa.Float(), server_default="0"))
        batch.add_column(sa.Column("unemployment_rate", sa.Float(), server_default="0"))
        batch.add_column(sa.Column("economy_snapshot", sa.Text(), nullable=True))

    op.create_table(
        "markets",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_table(
        "market_prices",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("market_id", sa.String(64), sa.ForeignKey("markets.id"), nullable=False),
        sa.Column("commodity", sa.String(64), nullable=False),
        sa.Column("price", sa.Float(), server_default="0"),
        sa.Column("supply", sa.Float(), server_default="100"),
        sa.Column("demand", sa.Float(), server_default="100"),
        sa.Column("tick_id", sa.Integer(), nullable=True),
    )
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("org_type", sa.String(64), nullable=False),
        sa.Column("owner_id", sa.String(64), sa.ForeignKey("villagers.id"), nullable=True),
        sa.Column("founder_ids", sa.Text(), nullable=True),
        sa.Column("cash", sa.Float(), server_default="0"),
        sa.Column("budget", sa.Float(), server_default="0"),
        sa.Column("reputation", sa.Float(), server_default="50"),
        sa.Column("technology_level", sa.Float(), server_default="0"),
        sa.Column("employee_count", sa.Integer(), server_default="0"),
        sa.Column("status", sa.String(32), server_default="active"),
        sa.Column("founded_tick", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
    )
    op.create_table(
        "businesses",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("business_type", sa.String(64), nullable=False),
        sa.Column("owner_id", sa.String(64), sa.ForeignKey("villagers.id"), nullable=False),
        sa.Column("organization_id", sa.String(64), nullable=True),
        sa.Column("cash", sa.Float(), server_default="0"),
        sa.Column("revenue_monthly", sa.Float(), server_default="0"),
        sa.Column("expenses_monthly", sa.Float(), server_default="0"),
        sa.Column("employee_count", sa.Integer(), server_default="0"),
        sa.Column("status", sa.String(32), server_default="active"),
        sa.Column("founded_tick", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
    )
    op.create_table(
        "assets",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("owner_type", sa.String(32), nullable=False),
        sa.Column("owner_id", sa.String(64), nullable=False),
        sa.Column("asset_type", sa.String(64), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("value", sa.Float(), server_default="0"),
        sa.Column("monthly_revenue", sa.Float(), server_default="0"),
        sa.Column("monthly_cost", sa.Float(), server_default="0"),
        sa.Column("location_id", sa.String(64), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("status", sa.String(32), server_default="active"),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("acquired_tick", sa.Integer(), nullable=True),
    )
    op.create_table(
        "liabilities",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("owner_type", sa.String(32), nullable=False),
        sa.Column("owner_id", sa.String(64), nullable=False),
        sa.Column("liability_type", sa.String(64), nullable=False),
        sa.Column("principal", sa.Float(), server_default="0"),
        sa.Column("balance", sa.Float(), server_default="0"),
        sa.Column("interest_rate", sa.Float(), server_default="0"),
        sa.Column("monthly_payment", sa.Float(), server_default="0"),
        sa.Column("status", sa.String(32), server_default="active"),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("opened_tick", sa.Integer(), nullable=True),
    )
    op.create_table(
        "construction_projects",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("owner_type", sa.String(32), nullable=False),
        sa.Column("owner_id", sa.String(64), nullable=False),
        sa.Column("project_type", sa.String(64), nullable=False),
        sa.Column("location_id", sa.String(64), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("total_cost", sa.Float(), server_default="0"),
        sa.Column("spent", sa.Float(), server_default="0"),
        sa.Column("duration_days", sa.Integer(), server_default="30"),
        sa.Column("progress_pct", sa.Float(), server_default="0"),
        sa.Column("roi_estimate", sa.Float(), server_default="0"),
        sa.Column("status", sa.String(32), server_default="planned"),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("started_tick", sa.Integer(), nullable=True),
    )
    op.create_table(
        "ai_workers",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("worker_type", sa.String(64), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("responsibilities", sa.Text(), nullable=True),
        sa.Column("productivity", sa.Float(), server_default="0.5"),
        sa.Column("monthly_cost", sa.Float(), server_default="0"),
        sa.Column("status", sa.String(32), server_default="active"),
        sa.Column("hired_tick", sa.Integer(), nullable=True),
    )
    op.create_table(
        "software_products",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("problem_solved", sa.Text(), nullable=True),
        sa.Column("mvp_features", sa.Text(), nullable=True),
        sa.Column("revenue_model", sa.String(64), nullable=True),
        sa.Column("development_cost", sa.Float(), server_default="0"),
        sa.Column("monthly_revenue", sa.Float(), server_default="0"),
        sa.Column("status", sa.String(32), server_default="idea"),
        sa.Column("launched_tick", sa.Integer(), nullable=True),
    )
    op.create_table(
        "tool_executions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tick_id", sa.Integer(), nullable=True),
        sa.Column("agent_id", sa.String(64), sa.ForeignKey("villagers.id"), nullable=False),
        sa.Column("tool_name", sa.String(64), nullable=False),
        sa.Column("arguments", sa.Text(), nullable=True),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("success", sa.Boolean(), server_default=sa.false()),
        sa.Column("error_message", sa.String(512), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("tool_executions")
    op.drop_table("software_products")
    op.drop_table("ai_workers")
    op.drop_table("construction_projects")
    op.drop_table("liabilities")
    op.drop_table("assets")
    op.drop_table("businesses")
    op.drop_table("organizations")
    op.drop_table("market_prices")
    op.drop_table("markets")

    with op.batch_alter_table("simulation_runs") as batch:
        batch.drop_column("economy_snapshot")
        batch.drop_column("unemployment_rate")
        batch.drop_column("total_wealth")
        batch.drop_column("gdp")
        batch.drop_column("technology_level")
        batch.drop_column("civilization_stage")

    with op.batch_alter_table("villagers") as batch:
        batch.drop_column("active_goal_plan")
        batch.drop_column("employment_status")
        batch.drop_column("intelligence")
        batch.drop_column("skills")
        batch.drop_column("reputation")
        batch.drop_column("net_worth")
        batch.drop_column("monthly_expenses")
        batch.drop_column("monthly_income")
        batch.drop_column("bank_balance")
        batch.drop_column("cash")
        batch.drop_column("agent_role")
