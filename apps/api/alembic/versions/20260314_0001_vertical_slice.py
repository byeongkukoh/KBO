from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260314_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("team_code", sa.String(length=8), nullable=False),
        sa.Column("team_name", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("team_code"),
    )
    op.create_index("ix_teams_team_code", "teams", ["team_code"], unique=True)

    op.create_table(
        "data_sync_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("game_date", sa.String(length=8), nullable=False),
        sa.Column("game_id", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_data_sync_runs_game_id", "data_sync_runs", ["game_id"], unique=False)

    op.create_table(
        "games",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("kbo_game_id", sa.String(length=32), nullable=False),
        sa.Column("game_date", sa.Date(), nullable=False),
        sa.Column("status_code", sa.String(length=16), nullable=False),
        sa.Column("stadium", sa.String(length=128), nullable=False),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("le_id", sa.Integer(), nullable=False),
        sa.Column("sr_id", sa.Integer(), nullable=False),
        sa.Column("away_team_id", sa.Integer(), nullable=False),
        sa.Column("home_team_id", sa.Integer(), nullable=False),
        sa.Column("away_score", sa.Integer(), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["away_team_id"], ["teams.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["home_team_id"], ["teams.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kbo_game_id"),
    )
    op.create_index("ix_games_kbo_game_id", "games", ["kbo_game_id"], unique=True)

    op.create_table(
        "data_sync_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("external_key", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["run_id"], ["data_sync_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "source_type", "external_key", name="uq_sync_item_run_source_key"),
    )
    op.create_index("ix_data_sync_items_run_id", "data_sync_items", ["run_id"], unique=False)

    op.create_table(
        "inning_scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("inning_no", sa.Integer(), nullable=False),
        sa.Column("away_runs", sa.Integer(), nullable=False),
        sa.Column("home_runs", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", "inning_no", name="uq_inning_scores_game_inning"),
    )
    op.create_index("ix_inning_scores_game_id", "inning_scores", ["game_id"], unique=False)

    op.create_table(
        "game_source_pages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("parser_version", sa.String(length=32), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_game_source_pages_game_id", "game_source_pages", ["game_id"], unique=False)

    op.create_table(
        "team_game_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("runs", sa.Integer(), nullable=False),
        sa.Column("hits", sa.Integer(), nullable=False),
        sa.Column("errors", sa.Integer(), nullable=False),
        sa.Column("walks", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", "team_id", name="uq_team_game_stats_game_team"),
    )
    op.create_index("ix_team_game_stats_game_id", "team_game_stats", ["game_id"], unique=False)
    op.create_index("ix_team_game_stats_team_id", "team_game_stats", ["team_id"], unique=False)

    op.create_table(
        "player_game_batting_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("player_key", sa.String(length=128), nullable=False),
        sa.Column("player_name", sa.String(length=64), nullable=False),
        sa.Column("batting_order", sa.Integer(), nullable=False),
        sa.Column("position_code", sa.String(length=16), nullable=False),
        sa.Column("plate_appearances", sa.Integer(), nullable=False),
        sa.Column("at_bats", sa.Integer(), nullable=False),
        sa.Column("runs", sa.Integer(), nullable=False),
        sa.Column("hits", sa.Integer(), nullable=False),
        sa.Column("doubles", sa.Integer(), nullable=False),
        sa.Column("triples", sa.Integer(), nullable=False),
        sa.Column("home_runs", sa.Integer(), nullable=False),
        sa.Column("runs_batted_in", sa.Integer(), nullable=False),
        sa.Column("walks", sa.Integer(), nullable=False),
        sa.Column("hit_by_pitch", sa.Integer(), nullable=False),
        sa.Column("sacrifice_flies", sa.Integer(), nullable=False),
        sa.Column("strikeouts", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", "team_id", "player_key", name="uq_player_batting_game_team_player"),
    )
    op.create_index("ix_player_game_batting_stats_game_id", "player_game_batting_stats", ["game_id"], unique=False)
    op.create_index("ix_player_game_batting_stats_team_id", "player_game_batting_stats", ["team_id"], unique=False)
    op.create_index("ix_player_game_batting_stats_player_key", "player_game_batting_stats", ["player_key"], unique=False)

    op.create_table(
        "player_game_pitching_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("player_key", sa.String(length=128), nullable=False),
        sa.Column("player_name", sa.String(length=64), nullable=False),
        sa.Column("innings_outs", sa.Integer(), nullable=False),
        sa.Column("batters_faced", sa.Integer(), nullable=False),
        sa.Column("pitches_thrown", sa.Integer(), nullable=False),
        sa.Column("at_bats", sa.Integer(), nullable=False),
        sa.Column("hits_allowed", sa.Integer(), nullable=False),
        sa.Column("home_runs_allowed", sa.Integer(), nullable=False),
        sa.Column("walks_allowed", sa.Integer(), nullable=False),
        sa.Column("strikeouts", sa.Integer(), nullable=False),
        sa.Column("runs_allowed", sa.Integer(), nullable=False),
        sa.Column("earned_runs", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", "team_id", "player_key", name="uq_player_pitching_game_team_player"),
    )
    op.create_index("ix_player_game_pitching_stats_game_id", "player_game_pitching_stats", ["game_id"], unique=False)
    op.create_index("ix_player_game_pitching_stats_team_id", "player_game_pitching_stats", ["team_id"], unique=False)
    op.create_index("ix_player_game_pitching_stats_player_key", "player_game_pitching_stats", ["player_key"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_player_game_pitching_stats_player_key", table_name="player_game_pitching_stats")
    op.drop_index("ix_player_game_pitching_stats_team_id", table_name="player_game_pitching_stats")
    op.drop_index("ix_player_game_pitching_stats_game_id", table_name="player_game_pitching_stats")
    op.drop_table("player_game_pitching_stats")

    op.drop_index("ix_player_game_batting_stats_player_key", table_name="player_game_batting_stats")
    op.drop_index("ix_player_game_batting_stats_team_id", table_name="player_game_batting_stats")
    op.drop_index("ix_player_game_batting_stats_game_id", table_name="player_game_batting_stats")
    op.drop_table("player_game_batting_stats")

    op.drop_index("ix_team_game_stats_team_id", table_name="team_game_stats")
    op.drop_index("ix_team_game_stats_game_id", table_name="team_game_stats")
    op.drop_table("team_game_stats")

    op.drop_index("ix_game_source_pages_game_id", table_name="game_source_pages")
    op.drop_table("game_source_pages")

    op.drop_index("ix_inning_scores_game_id", table_name="inning_scores")
    op.drop_table("inning_scores")

    op.drop_index("ix_data_sync_items_run_id", table_name="data_sync_items")
    op.drop_table("data_sync_items")

    op.drop_index("ix_games_kbo_game_id", table_name="games")
    op.drop_table("games")

    op.drop_index("ix_data_sync_runs_game_id", table_name="data_sync_runs")
    op.drop_table("data_sync_runs")

    op.drop_index("ix_teams_team_code", table_name="teams")
    op.drop_table("teams")
