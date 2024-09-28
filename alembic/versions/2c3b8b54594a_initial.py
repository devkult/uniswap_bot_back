"""initial

Revision ID: 2c3b8b54594a
Revises: 
Create Date: 2024-09-28 04:59:02.090217

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c3b8b54594a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('competitions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('competition_name', sa.String(), nullable=True),
    sa.Column('token_address', sa.String(), nullable=True),
    sa.Column('start_date', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('end_date', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('winner_wallet', sa.String(), nullable=True),
    sa.Column('channel_id', sa.BigInteger(), nullable=True),
    sa.Column('last_processed_timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('competition_swaps',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('competition_id', sa.Integer(), nullable=False),
    sa.Column('wallet_address', sa.String(), nullable=False),
    sa.Column('token_amount', sa.Float(), nullable=False),
    sa.Column('weth_amount', sa.Float(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('pair', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('competition_swaps')
    op.drop_table('competitions')
    # ### end Alembic commands ###
