"""Add relationship

Revision ID: 105b661e12c2
Revises: 8d4b71e13e84
Create Date: 2022-06-20 00:03:51.120589

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '105b661e12c2'
down_revision = '8d4b71e13e84'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'post', 'users', ['user_id'], ['id'])
    op.create_unique_constraint(None, 'users', ['username'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'post', type_='foreignkey')
    op.drop_column('post', 'user_id')
    # ### end Alembic commands ###
