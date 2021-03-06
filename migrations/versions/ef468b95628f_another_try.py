"""another try

Revision ID: ef468b95628f
Revises: 9e02bf906892
Create Date: 2020-12-19 16:45:15.815698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef468b95628f'
down_revision = '9e02bf906892'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('courses', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['teacher_id'], ['id'])
        batch_op.drop_column('teacher')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('courses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('teacher', sa.VARCHAR(length=140), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###
