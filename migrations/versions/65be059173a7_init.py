"""init

Revision ID: 65be059173a7
Revises: 0607d1c76451
Create Date: 2025-02-27 20:43:26.442714

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '65be059173a7'
down_revision = '0607d1c76451'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('User',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('fs_uniquifier', sa.String(length=255), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('fs_uniquifier'),
    sa.UniqueConstraint('username')
    )
    op.create_table('roles_users',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['Role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], )
    )
    with op.batch_alter_table('Accounts', schema=None) as batch_op:
        batch_op.alter_column('balance',
               existing_type=mysql.INTEGER(),
               type_=sa.Numeric(precision=12, scale=2),
               existing_nullable=False)

    with op.batch_alter_table('Transactions', schema=None) as batch_op:
        batch_op.alter_column('amount',
               existing_type=mysql.INTEGER(),
               type_=sa.Numeric(precision=10, scale=2),
               existing_nullable=False)
        batch_op.alter_column('new_balance',
               existing_type=mysql.INTEGER(),
               type_=sa.Numeric(precision=10, scale=2),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Transactions', schema=None) as batch_op:
        batch_op.alter_column('new_balance',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=mysql.INTEGER(),
               existing_nullable=False)
        batch_op.alter_column('amount',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=mysql.INTEGER(),
               existing_nullable=False)

    with op.batch_alter_table('Accounts', schema=None) as batch_op:
        batch_op.alter_column('balance',
               existing_type=sa.Numeric(precision=12, scale=2),
               type_=mysql.INTEGER(),
               existing_nullable=False)

    op.drop_table('roles_users')
    op.drop_table('User')
    op.drop_table('Role')
    # ### end Alembic commands ###
