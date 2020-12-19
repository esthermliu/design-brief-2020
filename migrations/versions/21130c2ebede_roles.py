"""Roles

Revision ID: 21130c2ebede
Revises: 0745fb85fb1e
Create Date: 2020-12-18 23:01:00.557753

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21130c2ebede'
down_revision = '0745fb85fb1e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('role', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'role')
    # ### end Alembic commands ###
