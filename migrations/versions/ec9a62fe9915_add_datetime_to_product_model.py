"""add datetime to product model

Revision ID: ec9a62fe9915
Revises: bced87fb00c8
Create Date: 2024-12-30 14:15:46.644991

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ec9a62fe9915'
down_revision: Union[str, None] = 'bced87fb00c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True))
    op.add_column('products', sa.Column('update_at', postgresql.TIMESTAMP(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'update_at')
    op.drop_column('products', 'created_at')
    # ### end Alembic commands ###
