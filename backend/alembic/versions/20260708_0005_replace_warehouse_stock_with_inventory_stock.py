''''
"""replace warehouse_stock with per-store inventory_stock"""
from alembic import op
import sqlalchemy as sa
from datetime import date

revision = "20260708_0005"
down_revision = "20260707_0004"

def upgrade():
    op.create_table(
        "inventory_stock",
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), primary_key=True),
        sa.Column("store_id", sa.Integer, sa.ForeignKey("stores.id"), primary_key=True),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_updated", sa.Date, nullable=False, server_default=sa.func.current_date()),
        sa.Column("realm_id", sa.Integer, sa.ForeignKey("realms.id"), nullable=True),
    )

    conn = op.get_bind()

    # ensure every realm has a warehouse store row
    realms = conn.execute(sa.text("SELECT id FROM realms")).fetchall()
    for (realm_id,) in realms:
        existing = conn.execute(
            sa.text("SELECT id FROM stores WHERE realm_id = :r AND store_type = 'warehouse'"),
            {"r": realm_id},
        ).fetchone()
        if existing is None:
            conn.execute(
                sa.text(
                    "INSERT INTO stores (name, city, region, store_type, realm_id) "
                    "VALUES ('Warehouse', 'Central', 'National', 'warehouse', :r)"
                ),
                {"r": realm_id},
            )

    # migrate warehouse_stock rows into inventory_stock, mapped to each realm's warehouse store
    rows = conn.execute(sa.text("SELECT product_id, quantity, realm_id FROM warehouse_stock")).fetchall()
    for product_id, quantity, realm_id in rows:
        wh = conn.execute(
            sa.text("SELECT id FROM stores WHERE realm_id = :r AND store_type = 'warehouse'"),
            {"r": realm_id},
        ).fetchone()
        if wh:
            conn.execute(
                sa.text(
                    "INSERT INTO inventory_stock (product_id, store_id, quantity, last_updated, realm_id) "
                    "VALUES (:p, :s, :q, :d, :r) "
                    "ON CONFLICT (product_id, store_id) DO UPDATE SET quantity = inventory_stock.quantity + EXCLUDED.quantity"
                ),
                {"p": product_id, "s": wh[0], "q": quantity, "d": date.today(), "r": realm_id},
            )

    op.drop_table("warehouse_stock")


def downgrade():
    op.create_table(
        "warehouse_stock",
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), primary_key=True),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("realm_id", sa.Integer, sa.ForeignKey("realms.id"), nullable=True),
    )
    op.drop_table("inventory_stock")
'''
"""replace warehouse_stock with per-store inventory_stock"""
from alembic import op
import sqlalchemy as sa
from datetime import date

revision = "20260708_0005"
down_revision = "20260707_0004"


def upgrade():
    op.create_table(
        "inventory_stock",
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.product_id"), primary_key=True),
        sa.Column("store_id", sa.Integer, sa.ForeignKey("stores.store_id"), primary_key=True),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_updated", sa.Date, nullable=False, server_default=sa.func.current_date()),
        sa.Column("realm_id", sa.Integer, sa.ForeignKey("realms.id"), nullable=True),
    )

    conn = op.get_bind()

    # ensure every realm has a warehouse store row
    realms = conn.execute(sa.text("SELECT id FROM realms")).fetchall()
    for (realm_id,) in realms:
        existing = conn.execute(
            sa.text("SELECT store_id FROM stores WHERE realm_id = :r AND store_type = 'warehouse'"),
            {"r": realm_id},
        ).fetchone()
        if existing is None:
            conn.execute(
                sa.text(
                    "INSERT INTO stores (name, city, region, store_type, realm_id) "
                    "VALUES ('Warehouse', 'Central', 'National', 'warehouse', :r)"
                ),
                {"r": realm_id},
            )

    # migrate warehouse_stock rows into inventory_stock, mapped to each realm's warehouse store
    rows = conn.execute(sa.text("SELECT product_id, quantity, realm_id FROM warehouse_stock")).fetchall()
    for product_id, quantity, realm_id in rows:
        wh = conn.execute(
            sa.text("SELECT store_id FROM stores WHERE realm_id = :r AND store_type = 'warehouse'"),
            {"r": realm_id},
        ).fetchone()
        if wh:
            conn.execute(
                sa.text(
                    "INSERT INTO inventory_stock (product_id, store_id, quantity, last_updated, realm_id) "
                    "VALUES (:p, :s, :q, :d, :r) "
                    "ON CONFLICT (product_id, store_id) DO UPDATE SET quantity = inventory_stock.quantity + EXCLUDED.quantity"
                ),
                {"p": product_id, "s": wh[0], "q": quantity, "d": date.today(), "r": realm_id},
            )

    op.drop_table("warehouse_stock")


def downgrade():
    op.create_table(
        "warehouse_stock",
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.product_id"), primary_key=True),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("realm_id", sa.Integer, sa.ForeignKey("realms.id"), nullable=True),
    )
    op.drop_table("inventory_stock")