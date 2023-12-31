"""do

Revision ID: 90968576fddd
Revises: 
Create Date: 2023-12-09 20:12:18.634112

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90968576fddd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('city',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('other_name', sa.String(), nullable=True),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('birthday', sa.DateTime(), nullable=True),
    sa.Column('city', sa.Integer(), nullable=True),
    sa.Column('additional_info', sa.Text(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.ForeignKeyConstraint(['city'], ['city.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('city')
    # ### end Alembic commands ###
