from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260314_0004"
down_revision: str | None = "20260314_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "league_season_batting_contexts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("series_code", sa.String(length=32), nullable=False),
        sa.Column("plate_appearances", sa.Integer(), nullable=False),
        sa.Column("at_bats", sa.Integer(), nullable=False),
        sa.Column("hits", sa.Integer(), nullable=False),
        sa.Column("doubles", sa.Integer(), nullable=False),
        sa.Column("triples", sa.Integer(), nullable=False),
        sa.Column("home_runs", sa.Integer(), nullable=False),
        sa.Column("stolen_bases", sa.Integer(), nullable=False),
        sa.Column("strikeouts", sa.Integer(), nullable=False),
        sa.Column("walks", sa.Integer(), nullable=False),
        sa.Column("hit_by_pitch", sa.Integer(), nullable=False),
        sa.Column("sacrifice_flies", sa.Integer(), nullable=False),
        sa.Column("batting_avg", sa.Float(), nullable=True),
        sa.Column("obp", sa.Float(), nullable=True),
        sa.Column("slg", sa.Float(), nullable=True),
        sa.Column("ops", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("season_id", "series_code", name="uq_league_batting_context_season_series"),
    )
    op.create_table(
        "league_season_pitching_contexts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("series_code", sa.String(length=32), nullable=False),
        sa.Column("innings_outs", sa.Integer(), nullable=False),
        sa.Column("hits_allowed", sa.Integer(), nullable=False),
        sa.Column("walks_allowed", sa.Integer(), nullable=False),
        sa.Column("strikeouts", sa.Integer(), nullable=False),
        sa.Column("earned_runs", sa.Integer(), nullable=False),
        sa.Column("era", sa.Float(), nullable=True),
        sa.Column("whip", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("season_id", "series_code", name="uq_league_pitching_context_season_series"),
    )
    op.create_table(
        "advanced_metric_constants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("series_code", sa.String(length=32), nullable=False),
        sa.Column("metric_code", sa.String(length=64), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("season_id", "series_code", "metric_code", name="uq_metric_constant_season_series_metric"),
    )
    op.create_index("ix_league_batting_context_season", "league_season_batting_contexts", ["season_id", "series_code"], unique=False)
    op.create_index("ix_league_pitching_context_season", "league_season_pitching_contexts", ["season_id", "series_code"], unique=False)
    op.create_index("ix_metric_constants_season", "advanced_metric_constants", ["season_id", "series_code"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_metric_constants_season", table_name="advanced_metric_constants")
    op.drop_index("ix_league_pitching_context_season", table_name="league_season_pitching_contexts")
    op.drop_index("ix_league_batting_context_season", table_name="league_season_batting_contexts")
    op.drop_table("advanced_metric_constants")
    op.drop_table("league_season_pitching_contexts")
    op.drop_table("league_season_batting_contexts")
