"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('email', sa.String(300), nullable=False, unique=True),
        sa.Column('role', sa.String(50), server_default='admin'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        'sources',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('feed_url', sa.String(500)),
        sa.Column('type', sa.String(50), server_default='rss'),
        sa.Column('active', sa.Boolean(), server_default='true'),
        sa.Column('last_fetched', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        'news_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('source_id', sa.Integer(), sa.ForeignKey('sources.id'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('summary', sa.Text()),
        sa.Column('url', sa.String(1000), nullable=False, unique=True),
        sa.Column('author', sa.String(200)),
        sa.Column('published_at', sa.DateTime(timezone=True)),
        sa.Column('tags', sa.JSON(), server_default='[]'),
        sa.Column('is_duplicate', sa.Boolean(), server_default='false'),
        sa.Column('duplicate_of', sa.Integer(), sa.ForeignKey('news_items.id'), nullable=True),
        sa.Column('impact_score', sa.Float(), server_default='0.5'),
        sa.Column('image_url', sa.String(1000)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_news_items_published_at', 'news_items', ['published_at'])
    op.create_index('ix_news_items_is_duplicate', 'news_items', ['is_duplicate'])
    op.create_index('ix_news_items_source_id', 'news_items', ['source_id'])
    op.create_table(
        'favorites',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('news_item_id', sa.Integer(), sa.ForeignKey('news_items.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        'broadcast_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('favorite_id', sa.Integer(), sa.ForeignKey('favorites.id'), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('message', sa.Text()),
        sa.Column('recipients', sa.JSON(), server_default='[]'),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('broadcast_logs')
    op.drop_table('favorites')
    op.drop_index('ix_news_items_source_id', 'news_items')
    op.drop_index('ix_news_items_is_duplicate', 'news_items')
    op.drop_index('ix_news_items_published_at', 'news_items')
    op.drop_table('news_items')
    op.drop_table('sources')
    op.drop_table('users')