"""add total_orders to restaurant

Revision ID: add_total_orders
Revises: 63c261580b0b
Create Date: 2024-03-19 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_total_orders'
down_revision = '63c261580b0b'
branch_labels = None
depends_on = None

def upgrade():
    # Add total_orders column
    with op.batch_alter_table('restaurant', schema=None) as batch_op:
        batch_op.add_column(sa.Column('total_orders', sa.Integer(), nullable=False, server_default='0'))

def downgrade():
    # Remove total_orders column
    with op.batch_alter_table('restaurant', schema=None) as batch_op:
        batch_op.drop_column('total_orders') 