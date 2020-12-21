"""Adding a course id to reactions

Revision ID: 88dfa540b39a
Revises: fbfc6a3f060e
Create Date: 2020-12-20 15:19:15.908322

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88dfa540b39a'
down_revision = 'fbfc6a3f060e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reactions_course_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'courses', ['reactions_course_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reactions', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('reactions_course_id')

    # ### end Alembic commands ###
