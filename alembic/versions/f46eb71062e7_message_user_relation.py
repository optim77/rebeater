"""message user relation

Revision ID: f46eb71062e7
Revises: 840c9fc41892
Create Date: 2025-10-27 18:53:58.703600

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f46eb71062e7'
down_revision: Union[str, Sequence[str], None] = '840c9fc41892'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tworzymy nowe ENUM-y
    message_type_enum = postgresql.ENUM('Email', 'SMS', name='message_type_enum')
    message_type_enum.create(op.get_bind(), checkfirst=True)

    respond_enum = postgresql.ENUM('positiveResponse', 'negativeResponse', 'messageClicked', name='respond_enum')
    respond_enum.create(op.get_bind(), checkfirst=True)

    # Konwersja kolumny messageType na nowy ENUM
    op.execute("""
        ALTER TABLE messages
        ALTER COLUMN "messageType" TYPE message_type_enum
        USING "messageType"::text::message_type_enum
    """)

    # Dodajemy nowe kolumny
    op.add_column('messages', sa.Column('invitation_id', sa.UUID(), nullable=False))
    op.add_column('messages', sa.Column('responded', sa.Enum('positiveResponse', 'negativeResponse', 'messageClicked', name='respond_enum'), nullable=True))
    op.add_column('messages', sa.Column('feedback', sa.String(), nullable=True))
    op.add_column('messages', sa.Column('user_id', sa.UUID(), nullable=False))

    # Constrainty
    op.create_unique_constraint(None, 'messages', ['invitation_id'])
    op.create_foreign_key(None, 'messages', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    # Usuwamy stare tabele, jeśli potrzebne
    op.drop_table('message_recipients')
    op.drop_table('services')


def downgrade() -> None:
    # Usuwamy constrainty
    op.drop_constraint(None, 'messages', type_='foreignkey')
    op.drop_constraint(None, 'messages', type_='unique')

    # Konwersja ENUM na VARCHAR (stary typ)
    op.execute("""
        ALTER TABLE messages
        ALTER COLUMN "messageType" TYPE VARCHAR
        USING "messageType"::text
    """)

    # Usuwamy kolumny
    op.drop_column('messages', 'user_id')
    op.drop_column('messages', 'feedback')
    op.drop_column('messages', 'responded')
    op.drop_column('messages', 'invitation_id')

    # Usuwamy ENUM-y
    respond_enum = postgresql.ENUM('positiveResponse', 'negativeResponse', 'messageClicked', name='respond_enum')
    respond_enum.drop(op.get_bind(), checkfirst=True)

    message_type_enum = postgresql.ENUM('Email', 'SMS', name='message_type_enum')
    message_type_enum.drop(op.get_bind(), checkfirst=True)

    # Odtwarzamy stare tabele
    op.create_table(
        'services',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('name', sa.VARCHAR(length=255), nullable=False),
        sa.Column('description', sa.VARCHAR(length=255), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE')
    )

    op.create_table(
        'message_recipients',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('invitation_id', sa.UUID(), nullable=False, unique=True),
        sa.Column('message_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('sent_at', postgresql.TIMESTAMP(), nullable=True),
        sa.Column('responded', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
