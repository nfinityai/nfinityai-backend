"""nfnt_enum

Revision ID: 15174911335c
Revises: 227e5b308147
Create Date: 2024-08-07 08:22:26.823208

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '15174911335c'
down_revision = '227e5b308147'
branch_labels = None
depends_on = None

old_enum = postgresql.ENUM('ETH', 'USDT', name='currencytopayenum')
new_enum = postgresql.ENUM('ETH', 'USDT', 'NFNT', name='currencytopayenum', create_type=False)


def upgrade() -> None:
    # Add new value to the ENUM type
    op.execute("ALTER TYPE currencytopayenum ADD VALUE 'NFNT'")


def downgrade() -> None:
    op.execute("ALTER TYPE currencytopayenum RENAME TO currencytopayenum_old")
    old_enum.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE balance_popups ALTER COLUMN currency_to_pay TYPE currencytopayenum USING currency_to_pay::text::currencytopayenum"
    )
    op.execute("DROP TYPE currencytopayenum_old")
