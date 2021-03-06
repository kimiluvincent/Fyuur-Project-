"""empty message

Revision ID: f1ae5c430eab
Revises: ef2672068e2f
Create Date: 2022-06-08 22:53:03.341424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1ae5c430eab'
down_revision = 'ef2672068e2f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('seeking_venue', sa.String(length=250), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artists', 'seeking_venue')
    # ### end Alembic commands ###
