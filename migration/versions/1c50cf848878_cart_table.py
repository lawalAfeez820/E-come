"""cart table

Revision ID: 1c50cf848878
Revises: 73767965ca3d
Create Date: 2022-12-12 12:24:53.316804

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '1c50cf848878'
down_revision = '73767965ca3d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cart',
    sa.Column('user_email', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('product_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('new_arrival', sa.Boolean(), nullable=False),
    sa.Column('flash_sales', sa.Boolean(), nullable=False),
    sa.Column('discount', sa.Float(), nullable=True),
    sa.Column('image', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('cart_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('cart_id'),
    sa.UniqueConstraint('user_email')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('cart')
    # ### end Alembic commands ###
