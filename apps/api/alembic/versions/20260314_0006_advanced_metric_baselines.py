from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260314_0006"
down_revision: str | None = "20260314_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("league_season_batting_contexts", sa.Column("runs_scored", sa.Integer(), nullable=True))
    op.add_column("league_season_pitching_contexts", sa.Column("hit_by_pitch_allowed", sa.Integer(), nullable=True))
    op.execute("UPDATE league_season_batting_contexts SET runs_scored = 0 WHERE runs_scored IS NULL")
    op.execute("UPDATE league_season_pitching_contexts SET hit_by_pitch_allowed = 0 WHERE hit_by_pitch_allowed IS NULL")
    op.alter_column("league_season_batting_contexts", "runs_scored", nullable=False)
    op.alter_column("league_season_pitching_contexts", "hit_by_pitch_allowed", nullable=False)


def downgrade() -> None:
    op.drop_column("league_season_pitching_contexts", "hit_by_pitch_allowed")
    op.drop_column("league_season_batting_contexts", "runs_scored")
