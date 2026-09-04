"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-03 22:12:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('EDITOR', 'ADMIN', name='userrole'), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Shows table
    op.create_table(
        'shows',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('synopsis', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('section', sa.String(length=100), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'PUBLISHED', 'ARCHIVED', name='contentstatus'), nullable=False),
        sa.Column('poster_url', sa.String(length=512), nullable=True),
        sa.Column('banner_url', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shows_category'), 'shows', ['category'], unique=False)
    op.create_index(op.f('ix_shows_section'), 'shows', ['section'], unique=False)
    op.create_index(op.f('ix_shows_status'), 'shows', ['status'], unique=False)
    op.create_index(op.f('ix_shows_title'), 'shows', ['title'], unique=False)
    op.create_index('idx_shows_section_category', 'shows', ['section', 'category'], unique=False)

    # Seasons table
    op.create_table(
        'seasons',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('show_id', sa.String(length=36), nullable=False),
        sa.Column('season_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'PUBLISHED', 'ARCHIVED', name='contentstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['show_id'], ['shows.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('show_id', 'season_number', name='uq_seasons_show_season_number')
    )
    op.create_index(op.f('ix_seasons_show_id'), 'seasons', ['show_id'], unique=False)

    # Episodes table
    op.create_table(
        'episodes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('season_id', sa.String(length=36), nullable=False),
        sa.Column('episode_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('synopsis', sa.Text(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('content_group', sa.String(length=100), nullable=False),
        sa.Column('language', sa.String(length=50), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'PUBLISHED', 'ARCHIVED', name='contentstatus'), nullable=False),
        sa.Column('poster_url', sa.String(length=512), nullable=True),
        sa.Column('banner_url', sa.String(length=512), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('content_group', 'language', name='uq_episodes_content_group_language')
    )
    op.create_index(op.f('ix_episodes_content_group'), 'episodes', ['content_group'], unique=False)
    op.create_index(op.f('ix_episodes_language'), 'episodes', ['language'], unique=False)
    op.create_index(op.f('ix_episodes_season_id'), 'episodes', ['season_id'], unique=False)
    op.create_index(op.f('ix_episodes_status'), 'episodes', ['status'], unique=False)
    op.create_index('idx_episodes_group_lang', 'episodes', ['content_group', 'language'], unique=False)

    # PublishRuns table
    op.create_table(
        'publish_runs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('published_by_user_id', sa.String(length=36), nullable=True),
        sa.Column('status', sa.Enum('SUCCESS', 'FAILED', name='publishstatus'), nullable=False),
        sa.Column('show_count', sa.Integer(), nullable=False),
        sa.Column('episode_count', sa.Integer(), nullable=False),
        sa.Column('validation_errors', sa.JSON(), nullable=True),
        sa.Column('snapshot_path', sa.String(length=512), nullable=True),
        sa.Column('error_message', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['published_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_publish_runs_published_by_user_id'), 'publish_runs', ['published_by_user_id'], unique=False)
    op.create_index(op.f('ix_publish_runs_status'), 'publish_runs', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('publish_runs')
    op.drop_table('episodes')
    op.drop_table('seasons')
    op.drop_table('shows')
    op.drop_table('users')
