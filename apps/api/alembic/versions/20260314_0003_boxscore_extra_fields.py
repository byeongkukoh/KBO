from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260314_0003"
down_revision: str | None = "20260314_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("player_game_batting_stats", sa.Column("stolen_bases", sa.Integer(), nullable=True))
    op.add_column("player_game_pitching_stats", sa.Column("decision_code", sa.String(length=8), nullable=True))
    op.execute("UPDATE player_game_batting_stats SET stolen_bases = 0 WHERE stolen_bases IS NULL")
    op.alter_column("player_game_batting_stats", "stolen_bases", nullable=False)


def downgrade() -> None:
    op.drop_column("player_game_pitching_stats", "decision_code")
    op.drop_column("player_game_batting_stats", "stolen_bases")
