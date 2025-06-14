"""add_summary_to_chapter_table

Revision ID: afb96878a642
Revises: 
Create Date: 2025-05-27 14:43:36.322587

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afb96878a642'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    
    # op.drop_table('project_characters') # Commented out due to "no such table" error. If needed, handle existence.

    with op.batch_alter_table('api_keys', schema=None) as batch_op:
        batch_op.alter_column('encrypted_api_key',
               existing_type=sa.VARCHAR(),
               nullable=True) # Model defines it as nullable=True

    with op.batch_alter_table('chapters', schema=None) as batch_op:
        batch_op.add_column(sa.Column('summary', sa.Text(), nullable=True))
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(),
               nullable=False) # Model implies non-nullable
        batch_op.alter_column('order',
               existing_type=sa.INTEGER(),
               nullable=False, # Model implies non-nullable (has default)
               existing_server_default=sa.text('0'))

    # Create indexes separately
    # It's generally safer to create indexes outside batch mode if they don't involve complex table rebuilds
    # or if the batch_op.create_index syntax for older SQLAlchemy/Alembic is not preferred.
    op.create_index(op.f('ix_chapters_id'), 'chapters', ['id'], unique=False)
    op.create_index(op.f('ix_chapters_title'), 'chapters', ['title'], unique=False)

    with op.batch_alter_table('characters', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(),
               nullable=False) # Model implies non-nullable

    op.create_index(op.f('ix_characters_id'), 'characters', ['id'], unique=False)
    op.create_index(op.f('ix_characters_name'), 'characters', ['name'], unique=False)

    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(),
               nullable=False) # Model implies non-nullable

    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_title'), 'projects', ['title'], unique=False)

    with op.batch_alter_table('scenes', schema=None) as batch_op:
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(),
               nullable=False) # Model implies non-nullable
        batch_op.alter_column('order',
               existing_type=sa.INTEGER(),
               nullable=False, # Model implies non-nullable (has default)
               existing_server_default=sa.text('0'))
               
    op.create_index(op.f('ix_scenes_id'), 'scenes', ['id'], unique=False)
    op.create_index(op.f('ix_scenes_title'), 'scenes', ['title'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_scenes_title'), table_name='scenes')
    op.drop_index(op.f('ix_scenes_id'), table_name='scenes')
    with op.batch_alter_table('scenes', schema=None) as batch_op:
        batch_op.alter_column('order',
                   existing_type=sa.INTEGER(),
                   nullable=True, # Reverting to nullable if that was the original state
                   existing_server_default=sa.text('0'))
        batch_op.alter_column('title',
                   existing_type=sa.VARCHAR(),
                   nullable=True) # Reverting to nullable

    op.drop_index(op.f('ix_projects_title'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.alter_column('title',
                   existing_type=sa.VARCHAR(),
                   nullable=True) # Reverting to nullable

    op.drop_index(op.f('ix_characters_name'), table_name='characters')
    op.drop_index(op.f('ix_characters_id'), table_name='characters')
    with op.batch_alter_table('characters', schema=None) as batch_op:
        batch_op.alter_column('name',
                   existing_type=sa.VARCHAR(),
                   nullable=True) # Reverting to nullable

    op.drop_index(op.f('ix_chapters_title'), table_name='chapters')
    op.drop_index(op.f('ix_chapters_id'), table_name='chapters')
    with op.batch_alter_table('chapters', schema=None) as batch_op:
        batch_op.alter_column('order',
                   existing_type=sa.INTEGER(),
                   nullable=True, # Reverting to nullable
                   existing_server_default=sa.text('0'))
        batch_op.alter_column('title',
                   existing_type=sa.VARCHAR(),
                   nullable=True) # Reverting to nullable
        batch_op.drop_column('summary')

    with op.batch_alter_table('api_keys', schema=None) as batch_op:
        batch_op.alter_column('encrypted_api_key',
                   existing_type=sa.VARCHAR(),
                   nullable=False) # Model was nullable=True, so downgrade makes it non-nullable if that was original state

    # If 'project_characters' was dropped in upgrade and needs to be restored:
    # op.create_table('project_characters',
    # sa.Column('project_id', sa.INTEGER(), nullable=True),
    # sa.Column('character_id', sa.INTEGER(), nullable=True),
    # sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ),
    # sa.ForeignKeyConstraint(['project_id'], ['projects.id'], )
    # )
    # ### end Alembic commands ###
