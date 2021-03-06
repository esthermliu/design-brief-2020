"""Update models

Revision ID: b9af9dd9c27d
Revises: d759151613ab
Create Date: 2020-12-24 13:54:10.035810

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9af9dd9c27d'
down_revision = 'd759151613ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('session',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=True),
    sa.Column('timestamp_start', sa.DateTime(), nullable=True),
    sa.Column('timestamp_end', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('session', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_session_timestamp_end'), ['timestamp_end'], unique=False)
        batch_op.create_index(batch_op.f('ix_session_timestamp_start'), ['timestamp_start'], unique=False)

    with op.batch_alter_table('reactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('session_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'session', ['session_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reactions', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('session_id')

    with op.batch_alter_table('session', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_session_timestamp_start'))
        batch_op.drop_index(batch_op.f('ix_session_timestamp_end'))

    op.drop_table('session')
    # ### end Alembic commands ###
