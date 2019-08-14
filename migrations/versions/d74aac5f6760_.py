"""empty message

Revision ID: d74aac5f6760
Revises: fb98618348b2
Create Date: 2019-08-13 23:56:49.513913

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd74aac5f6760'
down_revision = 'fb98618348b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('first', sa.String(length=80), nullable=False))
    op.add_column('user', sa.Column('last', sa.String(length=80), nullable=False))
    op.drop_constraint('user_first_name_key', 'user', type_='unique')
    op.drop_constraint('user_last_name_key', 'user', type_='unique')
    op.drop_column('user', 'last_name')
    op.drop_column('user', 'first_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('first_name', sa.VARCHAR(length=80), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('last_name', sa.VARCHAR(length=80), autoincrement=False, nullable=False))
    op.create_unique_constraint('user_last_name_key', 'user', ['last_name'])
    op.create_unique_constraint('user_first_name_key', 'user', ['first_name'])
    op.drop_column('user', 'last')
    op.drop_column('user', 'first')
    # ### end Alembic commands ###
