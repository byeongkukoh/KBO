from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260314_0002"
down_revision: str | None = "20260314_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("games", sa.Column("series_code", sa.String(length=32), nullable=True))
    op.add_column("games", sa.Column("series_name", sa.String(length=32), nullable=True))
    op.execute(
        """
        UPDATE games
        SET series_code = CASE sr_id
            WHEN 1 THEN 'preseason'
            WHEN 0 THEN 'regular'
            WHEN 3 THEN 'postseason'
            WHEN 4 THEN 'postseason'
            WHEN 5 THEN 'postseason'
            WHEN 7 THEN 'postseason'
            ELSE 'other'
        END,
        series_name = CASE sr_id
            WHEN 1 THEN '시범경기'
            WHEN 0 THEN '정규경기'
            WHEN 3 THEN '준플레이오프'
            WHEN 4 THEN '와일드카드'
            WHEN 5 THEN '플레이오프'
            WHEN 7 THEN '한국시리즈'
            ELSE '기타'
        END
        """
    )
    op.alter_column("games", "series_code", nullable=False)
    op.alter_column("games", "series_name", nullable=False)
    op.create_index("ix_games_season_series_date", "games", ["season_id", "series_code", "game_date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_games_season_series_date", table_name="games")
    op.drop_column("games", "series_name")
    op.drop_column("games", "series_code")
