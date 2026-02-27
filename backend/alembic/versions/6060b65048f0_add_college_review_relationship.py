"""add college review relationship

Revision ID: 6060b65048f0
Revises: 74409820399c
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '6060b65048f0'
down_revision: Union[str, Sequence[str], None] = '74409820399c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ================= ENUM CREATION =================

    schooltype_enum = sa.Enum('GOVERNMENT', 'PRIVATE', name='schooltype')
    boardtype_enum = sa.Enum('CBSE', 'ICSE', 'STATE', name='boardtype')
    userrole_enum = sa.Enum('ADMIN', 'STUDENT', 'PROVIDER', name='userrole')

    schooltype_enum.create(op.get_bind(), checkfirst=True)
    boardtype_enum.create(op.get_bind(), checkfirst=True)
    userrole_enum.create(op.get_bind(), checkfirst=True)

    # ================= DROP UNUSED COLUMNS =================

    op.drop_column('coaching', 'type')
    op.drop_column('hostels', 'gender_type')
    op.drop_column('hostels', 'room_types')
    op.drop_column('mess', 'type')

    # ================= ALTER SCHOOL TYPE =================

    op.alter_column(
        'schools',
        'type',
        existing_type=sa.VARCHAR(length=100),
        type_=schooltype_enum,
        existing_nullable=True,
        postgresql_using='type::schooltype'
    )

    op.alter_column(
        'schools',
        'board',
        existing_type=sa.VARCHAR(length=100),
        type_=boardtype_enum,
        existing_nullable=True,
        postgresql_using='board::boardtype'
    )

    # ================= PG RENT CONVERSION =================

    op.alter_column(
        'pg',
        'one_month_rent',
        existing_type=sa.VARCHAR(length=100),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using='one_month_rent::integer'
    )

    op.drop_column('pg', 'gender_type')
    op.drop_column('pg', 'room_types')

    # ================= REVIEWS CHANGE =================

    op.add_column('reviews', sa.Column('college_id', sa.Integer(), nullable=False))
    op.drop_constraint(op.f('reviews_user_id_fkey'), 'reviews', type_='foreignkey')
    op.create_foreign_key(None, 'reviews', 'colleges', ['college_id'], ['id'])
    op.drop_column('reviews', 'entity_type')
    op.drop_column('reviews', 'entity_id')
    op.drop_column('reviews', 'user_id')

    # ================= USERS CHANGE =================

    op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=False))
    op.add_column('users', sa.Column('hashed_password', sa.String(length=255), nullable=False))
    op.add_column('users', sa.Column('role', userrole_enum, nullable=False))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))

    op.alter_column(
        'users',
        'email',
        existing_type=sa.VARCHAR(length=150),
        type_=sa.String(length=255),
        existing_nullable=False
    )

    op.drop_constraint(op.f('users_email_key'), 'users', type_='unique')
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.drop_column('users', 'password')
    op.drop_column('users', 'name')


def downgrade() -> None:

    # ================= USERS ROLLBACK =================

    op.add_column('users', sa.Column('name', sa.VARCHAR(length=100), nullable=False))
    op.add_column('users', sa.Column('password', sa.VARCHAR(length=255), nullable=False))
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.create_unique_constraint(op.f('users_email_key'), 'users', ['email'])

    op.alter_column(
        'users',
        'email',
        existing_type=sa.String(length=255),
        type_=sa.VARCHAR(length=150),
        existing_nullable=False
    )

    op.drop_column('users', 'created_at')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'role')
    op.drop_column('users', 'hashed_password')
    op.drop_column('users', 'full_name')

    # ================= REVIEWS ROLLBACK =================

    op.add_column('reviews', sa.Column('user_id', sa.INTEGER(), nullable=False))
    op.add_column('reviews', sa.Column('entity_id', sa.INTEGER(), nullable=False))
    op.add_column('reviews', sa.Column('entity_type', sa.VARCHAR(length=50), nullable=False))
    op.drop_constraint(None, 'reviews', type_='foreignkey')
    op.create_foreign_key(op.f('reviews_user_id_fkey'), 'reviews', 'users', ['user_id'], ['id'])
    op.drop_column('reviews', 'college_id')

    # ================= PG ROLLBACK =================

    op.add_column('pg', sa.Column('room_types', sa.TEXT(), nullable=True))
    op.add_column('pg', sa.Column('gender_type', sa.VARCHAR(length=50), nullable=False))

    op.alter_column(
        'pg',
        'one_month_rent',
        existing_type=sa.Integer(),
        type_=sa.VARCHAR(length=100),
        existing_nullable=False
    )

    # ================= SCHOOL ROLLBACK =================

    op.alter_column(
        'schools',
        'board',
        existing_type=sa.Enum('CBSE', 'ICSE', 'STATE', name='boardtype'),
        type_=sa.VARCHAR(length=100),
        existing_nullable=True
    )

    op.alter_column(
        'schools',
        'type',
        existing_type=sa.Enum('GOVERNMENT', 'PRIVATE', name='schooltype'),
        type_=sa.VARCHAR(length=100),
        existing_nullable=True
    )

    # ================= ENUM DROP =================

    sa.Enum(name='schooltype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='boardtype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)

    # ================= RESTORE DROPPED COLUMNS =================

    op.add_column('mess', sa.Column('type', sa.VARCHAR(length=50), nullable=True))
    op.add_column('hostels', sa.Column('room_types', sa.TEXT(), nullable=True))
    op.add_column('hostels', sa.Column('gender_type', sa.VARCHAR(length=50), nullable=False))
    op.add_column('coaching', sa.Column('type', sa.VARCHAR(length=50), nullable=True))