"""update primary key

Revision ID: 37e7e2e06e1c
Revises: ec9a62fe9915
Create Date: 2024-12-30 19:57:23.492436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37e7e2e06e1c'
down_revision: Union[str, None] = 'ec9a62fe9915'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
