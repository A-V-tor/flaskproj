"""refactoring userprofile

Revision ID: 8c0f6679fae0
Revises: f91ca5e55fd7
Create Date: 2022-11-05 09:49:45.573398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c0f6679fae0'
down_revision = 'f91ca5e55fd7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('userprofile', sa.Column('admin', sa.Boolean(), nullable=False))
    op.add_column('userprofile', sa.Column('confirmed', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('userprofile', 'confirmed')
    op.drop_column('userprofile', 'admin')
    # ### end Alembic commands ###
