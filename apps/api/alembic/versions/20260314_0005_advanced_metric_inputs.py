from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260314_0005"
down_revision: str | None = "20260314_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("player_game_batting_stats", sa.Column("intentional_walks", sa.Integer(), nullable=True))
    op.add_column("player_game_pitching_stats", sa.Column("hit_by_pitch_allowed", sa.Integer(), nullable=True))
    op.execute("UPDATE player_game_batting_stats SET intentional_walks = 0 WHERE intentional_walks IS NULL")
    op.execute("UPDATE player_game_pitching_stats SET hit_by_pitch_allowed = 0 WHERE hit_by_pitch_allowed IS NULL")
    op.alter_column("player_game_batting_stats", "intentional_walks", nullable=False)
    op.alter_column("player_game_pitching_stats", "hit_by_pitch_allowed", nullable=False)


def downgrade() -> None:
    op.drop_column("player_game_pitching_stats", "hit_by_pitch_allowed")
    op.drop_column("player_game_batting_stats", "intentional_walks")
