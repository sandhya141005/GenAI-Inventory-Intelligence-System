from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.analytics_data import InventoryStock, Product, Sale, Store
from app.services.orphanages import match_orphanages

ACTION_ENGINE_CONFIG = {
    "stock_bands": {
        "low_min": 1, "low_max": 9,
        "medium_min": 10, "medium_max": 49,
        "high_min": 50,
    },
    "donate": {
        "min_stock_qty": 50,          
        "non_food_slow_days": 120,    
        "food_slow_days": 60,        
        "food_expiry_buffer_days": 5,
    },
    "clearance": {
        "expiry_tiers": [
            {"max_days_to_expiry": 7, "max_stock_qty": 5, "discount_percent": 70},
            {"max_days_to_expiry": 7, "discount_percent": 50},
            {"max_days_to_expiry": 14, "discount_percent": 40},
            {"max_days_to_expiry": 30, "discount_percent": 20},
        ],
        "slow_mover_tiers": [
            {"min_days_since_last_sold": 45, "discount_percent": 30},
            {"min_days_since_last_sold": 30, "discount_percent": 20},
            {"min_days_since_last_sold": 15, "discount_percent": 10},   
        ],
        "bundle_min_stock_qty": 15,    
        "bundle_min_days_since_last_sold": 20,
    },
   
 
    "food_categories": {
        "bakery",
        "beverages",
        "dairy",
        "food",
        "fresh produce",
        "frozen food",
        "grocery",
        "meat",
        "produce",
        "snacks",
    },
    "no_sales_days": 999,
}


@dataclass(frozen=True)
class InventoryActionInput:
    product_id: int
    store_id: int | None
    product_name: str
    category: str
    current_stock_qty: int
    days_since_last_sold: int
    days_to_expiry: int | None
    price: Decimal
    store_city: str | None
    pickup_location: str


class SmartInventoryActionEngine:
    def __init__(self, db: Session, scope=None) -> None:
        self.db = db
        self.scope = scope
        self.today = date.today()

    def suggestions(self) -> list[dict]:
        suggestions = [
            suggestion
            for item in self._action_inputs()
            if (suggestion := self.evaluate(item))["action"] != "NO_ACTION"
        ]
        suggestions = self._dedupe_donations(suggestions)
        return sorted(
            suggestions,
            key=lambda item: (item["action"], -(item.get("discount_percent") or 0), item["product_name"]),
        )
    def _dedupe_donations(self, suggestions: list[dict]) -> list[dict]:
        donations = [s for s in suggestions if s["action"] == "DONATE"]
        others = [s for s in suggestions if s["action"] != "DONATE"]

        best_per_product: dict[int, dict] = {}
        for s in donations:
            current = best_per_product.get(s["product_id"])
            if current is None or s["current_stock_qty"] > current["current_stock_qty"]:
                best_per_product[s["product_id"]] = s

        return others + list(best_per_product.values())
    def suggestion_for_product(self, product_id: int) -> dict | None:
        item = next((item for item in self._action_inputs() if item.product_id == product_id), None)
        if item is None:
            return None
        suggestion = self.evaluate(item)
        return suggestion if suggestion["action"] != "NO_ACTION" else None
    def _is_bundle_candidate(self, item: InventoryActionInput) -> bool:
        cfg = ACTION_ENGINE_CONFIG["clearance"]
        return (
            item.current_stock_qty >= cfg["bundle_min_stock_qty"]
            and item.current_stock_qty < ACTION_ENGINE_CONFIG["donate"]["min_stock_qty"]
            and item.days_since_last_sold >= cfg["bundle_min_days_since_last_sold"]
            and not self._is_food(item.category)
        )
    def evaluate(self, item: InventoryActionInput) -> dict:
        if (
            item.days_to_expiry is not None
            and item.days_to_expiry <= 0
            and self._is_food(item.category)   # NEW — non-food never gets DISCARD
        ):
            return self._suggestion(item, "DISCARD", "Discard - Expired", None)

        if self._is_donation_candidate(item):
            return self._suggestion(item, "DONATE", "Donate - Orphanage Match", None)

        bundle = self._is_bundle_candidate(item)   # NEW — check before plain clearance
        if bundle:
            return self._suggestion(item, "CLEARANCE_SALE", "Bundle Promotion - Pair with fast movers", None)

        discount = self._clearance_discount(item)
        if discount:
            return self._suggestion(item, "CLEARANCE_SALE", self._clearance_reason(item, discount), discount)

        return self._suggestion(item, "NO_ACTION", "Inventory is within action thresholds", None)
    def _action_inputs(self) -> list[InventoryActionInput]:
        stock_rows = self.db.execute(
            select(Product, Store, InventoryStock.quantity)
            .join(InventoryStock, InventoryStock.product_id == Product.id)
            .join(Store, Store.id == InventoryStock.store_id)
            .where(*self._realm_filters(Product, InventoryStock))
            .where(*self._store_filters(Store))
            .order_by(Product.name)
        ).all()
        last_sale_by_product_store = self._last_sale_dates()

        return [
            InventoryActionInput(
                product_id=product.id,
                store_id=store.id,
                product_name=product.name or product.sku or str(product.id),
                category=product.category or "Uncategorized",
                current_stock_qty=int(quantity or 0),
                days_since_last_sold=self._days_since_last_sold(last_sale_by_product_store.get((product.id, store.id))),
                days_to_expiry=(product.expiry_date - self.today).days if product.expiry_date else None,
                price=Decimal(product.price or 0),
                store_city=store.city,
                pickup_location=store.name or store.city or "Store",
            )
            for product, store, quantity in stock_rows
        ]

    def _is_donation_candidate(self, item: InventoryActionInput) -> bool:
        if item.current_stock_qty < ACTION_ENGINE_CONFIG["donate"]["min_stock_qty"]:
            return False
        if self._is_food(item.category):
            return (
                item.days_since_last_sold >= ACTION_ENGINE_CONFIG["donate"]["food_slow_days"]
                and item.days_to_expiry is not None
                and item.days_to_expiry > ACTION_ENGINE_CONFIG["donate"]["food_expiry_buffer_days"]
            )
        return (
            item.days_since_last_sold >= ACTION_ENGINE_CONFIG["donate"]["non_food_slow_days"]
            and (item.days_to_expiry is None or item.days_to_expiry > 0)
        )

    def _clearance_discount(self, item: InventoryActionInput) -> int | None:
        discounts: list[int] = []
        if item.days_to_expiry is not None and item.days_to_expiry > 0 and self._is_food(item.category):
                for tier in ACTION_ENGINE_CONFIG["clearance"]["expiry_tiers"]:
                    max_stock_qty = tier.get("max_stock_qty")
                    if item.days_to_expiry <= tier["max_days_to_expiry"] and (
                        max_stock_qty is None or item.current_stock_qty <= max_stock_qty
                    ):
                        discounts.append(tier["discount_percent"])
                        break

        for tier in ACTION_ENGINE_CONFIG["clearance"]["slow_mover_tiers"]:
            if item.days_since_last_sold >= tier["min_days_since_last_sold"]:
                discounts.append(tier["discount_percent"])
                break

        return max(discounts) if discounts else None

    def _suggestion(
        self,
        item: InventoryActionInput,
        action: str,
        reason_prefix: str,
        discount_percent: int | None,
    ) -> dict:
        return {
            "product_id": item.product_id,
            "store_id": item.store_id,
            "product_name": item.product_name,
            "category": item.category,
            "action": action,
            "reason": self._reason(item, reason_prefix),
            "discount_percent": discount_percent,
            "suggested_recipient": self._suggested_recipient(item, action),
            "current_stock_qty": item.current_stock_qty,
            "store_city": item.store_city,
            "pickup_location": item.pickup_location,
             "confidence": self._confidence(item), 
        }
    def _confidence(self, item: InventoryActionInput) -> str:
        """
        Confidence = completeness of the data actually backing this suggestion,
        not model certainty. Applicable signals: inventory (always present),
        sales history (do we know when it last sold, or is it a total unknown),
        expiry (only applicable to food).
        """
        signals_present = 1  # inventory row always exists if we got this far
        signals_total = 2    # inventory + sales history

        if item.days_since_last_sold < ACTION_ENGINE_CONFIG["no_sales_days"]:
            signals_present += 1  # we have a real last-sold date, not a "never sold" default

        if self._is_food(item.category):
            signals_total += 1
            if item.days_to_expiry is not None:
                signals_present += 1

        ratio = signals_present / signals_total
        if ratio >= 1.0:
            return "High"
        if ratio >= 0.5:
            return "Medium"
        return "Low"
    def _suggested_recipient(self, item: InventoryActionInput, action: str) -> str | None:
        if action != "DONATE":
            return None
        matches = match_orphanages(item.store_city)
        return matches[0]["name"] if matches else None

    def _reason(self, item: InventoryActionInput, prefix: str) -> str:
        expiry = f", expires in {item.days_to_expiry} days" if item.days_to_expiry is not None else ""
        sold = "no recorded sales" if item.days_since_last_sold >= ACTION_ENGINE_CONFIG["no_sales_days"] else f"not sold in {item.days_since_last_sold} days"
        return f"{prefix}: {sold}, stock of {item.current_stock_qty} units{expiry}"

    def _clearance_reason(self, item: InventoryActionInput, discount: int) -> str:
        return f"Clearance Sale - {discount}% OFF"

    def _days_since_last_sold(self, last_sale_date: date | None) -> int:
        if last_sale_date is None:
            return ACTION_ENGINE_CONFIG["no_sales_days"]
        return max(0, (self.today - last_sale_date).days)

    def _is_food(self, category: str) -> bool:
        return category.strip().lower() in ACTION_ENGINE_CONFIG["food_categories"]

    def _last_sale_dates(self) -> dict[tuple[int, int], date]:
        rows = self.db.execute(
            select(Sale.product_id, Sale.store_id, func.max(Sale.sale_date))
            .where(Sale.product_id.is_not(None), Sale.store_id.is_not(None))
            .where(*self._sale_filters())
            .group_by(Sale.product_id, Sale.store_id)
        ).all()
        return {
            (int(product_id), int(store_id)): last_sale
            for product_id, store_id, last_sale in rows
            if last_sale is not None
        }

    def _realm_filters(self, *models) -> list:
        if self.scope is None:
            return []
        return [model.realm_id == self.scope.realm_id for model in models]

    def _sale_filters(self) -> list:
        filters = self._realm_filters(Sale)
        if self.scope is not None and getattr(self.scope, "is_store_manager", False):
            filters.append(Sale.store_id == self.scope.assigned_store_id)
        return filters

    def _store_filters(self, model) -> list:
        filters = self._realm_filters(model)
        if self.scope is not None and getattr(self.scope, "is_store_manager", False):
            filters.append(model.id == self.scope.assigned_store_id)
        return filters
