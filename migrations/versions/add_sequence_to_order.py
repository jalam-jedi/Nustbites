"""add sequence to order table

Revision ID: add_sequence_to_order
Revises: df51d7376f34
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_sequence_to_order'
down_revision = 'df51d7376f34'
branch_labels = None
depends_on = None

def upgrade():
    # Add sequence column
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sequence', sa.Integer(), nullable=True))
        
    # Set initial sequence values based on existing orders
    op.execute("""
        UPDATE `order` o
        JOIN (
            SELECT id, restaurant_id, 
                   ROW_NUMBER() OVER (PARTITION BY restaurant_id ORDER BY created_at) as seq
            FROM `order`
        ) numbered ON o.id = numbered.id
        SET o.sequence = numbered.seq
    """)
    
    # Make sequence non-nullable after setting values
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.alter_column('sequence',
               existing_type=sa.Integer(),
               nullable=False)

def downgrade():
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('sequence') 