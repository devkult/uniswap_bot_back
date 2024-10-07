"""add prize field

Revision ID: 5688101c26d8
Revises: 655f1502e8f3
Create Date: 2024-10-07 22:01:07.875450

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5688101c26d8'
down_revision: Union[str, None] = '655f1502e8f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('competitions', sa.Column('winner_prize', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('competitions', 'winner_prize')
    # ### end Alembic commands ###
