"""empty message

Revision ID: ef5a192d32db
Revises: 0944ab3ebaf4
Create Date: 2022-06-08 22:40:19.202335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef5a192d32db'
down_revision = '0944ab3ebaf4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('website', sa.String(length=500), nullable=True))
    op.drop_column('artists', 'website_link')
    op.add_column('venues', sa.Column('website', sa.String(length=150), nullable=True))
    op.drop_column('venues', 'website_link')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('website_link', sa.VARCHAR(length=150), autoincrement=False, nullable=True))
    op.drop_column('venues', 'website')
    op.add_column('artists', sa.Column('website_link', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.drop_column('artists', 'website')
    # ### end Alembic commands ###
