"""launch status version and events

Revision ID: 91fe222cdbfd
Revises: 5dc955ebd659
Create Date: 2024-12-29 16:26:42.993252

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91fe222cdbfd'
down_revision = '5dc955ebd659'
branch_labels = None
depends_on = None

launch_status = sa.Enum('SCHEDULED', 'DELAYED', 'SCRUBBED', 'LAUNCHED', 'SUCCEEDED', 'FAILED', 'CANCELLED', name='launchstatus')


def upgrade():
    op.create_table('launch_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('launch_id', sa.Uuid(), nullable=False),
    sa.Column('changes', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('creator_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['launch_id'], ['launches.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('launch_events', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_launch_events_launch_id'), ['launch_id'], unique=False)

    launch_status.create(op.get_bind())
    with op.batch_alter_table('launches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', launch_status, server_default='SCHEDULED', nullable=False))
        batch_op.add_column(sa.Column('version', sa.Integer(), server_default='1', nullable=False))


def downgrade():
    with op.batch_alter_table('launches', schema=None) as batch_op:
        batch_op.drop_column('version')
        batch_op.drop_column('status')

    launch_status.drop(op.get_bind())

    op.drop_table('launch_events')
