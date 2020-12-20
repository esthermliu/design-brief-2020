"""empty message

Revision ID: 9e02bf906892
Revises: 90a48257c474
Create Date: 2020-12-19 16:01:54.985848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e02bf906892'
down_revision = '90a48257c474'
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
        batch_op.drop_constraint("name", type_='foreignkey')

    # ### end Alembic commands ###
