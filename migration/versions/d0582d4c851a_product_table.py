"""product table

Revision ID: d0582d4c851a
Revises: 089cf1c5719e
Create Date: 2022-11-23 13:24:29.734680

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'd0582d4c851a'
down_revision = '089cf1c5719e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product',
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('product_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('new_arrival', sa.Boolean(), nullable=False),
    sa.Column('flash_sales', sa.Boolean(), nullable=False),
    sa.Column('discount', sa.Float(), nullable=True),
    sa.Column('image', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('product_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('product')
    # ### end Alembic commands ###
