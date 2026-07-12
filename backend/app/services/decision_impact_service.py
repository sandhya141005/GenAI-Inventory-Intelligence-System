# app/services/decision_impact_service.py
from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.analytics_data import Product
from app.services.analytics_service import AnalyticsService, HOLDING_COST_RATE, LEAD_TIME_FACTOR
from app.services.action_engine import SmartInventoryActionEngine

EVAL_HORIZON_DAYS = Decimal("30")  # same 30-day window analytics already uses for demand


class DecisionImpactEvaluationService:
    """
    Measures the business impact of recommendations that already exist.
    Generates nothing new — every number here is either pulled directly
    from AnalyticsService/SmartInventoryActionEngine or derived from their
    existing formulas (HOLDING_COST_RATE, LEAD_TIME_FACTOR, price, cost).
    """

    def __init__(self, db: Session, scope=None) -> None:
        self.db = db
        self.scope = scope
        self.analytics = AnalyticsService(db, scope)
        self.action_engine = SmartInventoryActionEngine(db, scope)
        self._price_cache: dict[int, Decimal] = {}
        self._cost_cache: dict[int, Decimal] = {}

    def evaluate(self) -> dict:
        metrics = self.analytics._inventory_metrics()
        metrics_by_key = {(m.product_id, m.store_id): m for m in metrics}

        # ---------- Dataset Totals ----------
        total_inventory_value = sum(
            (m.inventory_value for m in metrics),
            Decimal("0")
        )

        total_holding_cost = sum(
            (Decimal(m.inventory) * self._cost(m.product_id) * HOLDING_COST_RATE / Decimal("365") * EVAL_HORIZON_DAYS)
            for m in metrics
        )

        total_revenue_at_risk = sum(
            (m.revenue_at_risk for m in metrics),
            Decimal("0")
        )

        transfer_impact = self._evaluate_transfers(metrics_by_key)
        action_impact = self._evaluate_actions(metrics_by_key)

        updated_inventory: dict[tuple[int, int], int] = {}
        updated_inventory.update(transfer_impact["updated_keys"])
        updated_inventory.update(action_impact["updated_keys"])

        revenue_at_risk_before = sum((m.revenue_at_risk for m in metrics), Decimal("0"))
        revenue_protected = transfer_impact["revenue_protected"]
        revenue_risk_reduction_pct = self._pct(revenue_protected, revenue_at_risk_before)

        holding_cost_saved = transfer_impact["holding_cost_saved"] + action_impact["holding_cost_saved"]
        inventory_release_pct = self._pct(
            action_impact["inventory_value_released"],
            total_inventory_value,
        )

        holding_cost_reduction_pct = self._pct(
            holding_cost_saved,
            total_holding_cost,
        )
        stockout_before = sum(1 for m in metrics if m.stockout_risk)
        stockout_after = self._count_flag_after(metrics_by_key, updated_inventory, "stockout")
        stockout_reduction_pct = self._pct(Decimal(stockout_before - stockout_after), Decimal(stockout_before))

        overstock_before = sum(1 for m in metrics if m.overstock)
        overstock_after = self._count_flag_after(metrics_by_key, updated_inventory, "overstock")
        overstock_reduction_pct = self._pct(Decimal(overstock_before - overstock_after), Decimal(overstock_before))

        distressed_value = sum(
            (m.inventory_value for m in metrics if m.stockout_risk or m.overstock), Decimal("0")
        )
        value_recovered = revenue_protected + action_impact["inventory_value_released"] + action_impact["donation_writeoff_value"]
        recovery_rate_pct = self._pct(value_recovered, distressed_value)

        return {
    "revenue": {
        "protected_value": float(revenue_protected),
        "risk_reduction_percent": float(revenue_risk_reduction_pct),
    },

    "cost": {
        "inventory_value_released": float(action_impact["inventory_value_released"]),
        "inventory_release_percent": float(inventory_release_pct),

        "holding_cost_saved": float(holding_cost_saved),
        "holding_cost_reduction_percent": float(holding_cost_reduction_pct),
    },

    "risk": {
        "stockout_risk_reduction_percent": float(stockout_reduction_pct),
        "overstock_reduction_percent": float(overstock_reduction_pct),
    },

    "sustainability": {
        "waste_prevented_units": action_impact["waste_prevented_units"],
        "recovery_rate_percent": float(recovery_rate_pct),
    },

    "dataset": {
        "total_inventory_value": float(total_inventory_value),
        "total_revenue_at_risk": float(total_revenue_at_risk),
        "total_holding_cost": float(total_holding_cost),
        "distressed_inventory_value": float(distressed_value),
    },

    "notes": {
        "evaluation_horizon_days": int(EVAL_HORIZON_DAYS),
        "donation_value_basis": (
            "Donation is valued using inventory cost (write-off/tax benefit basis), "
            "not direct revenue."
        ),
    },
}
        

    # ---------- Transfers ----------
    def _evaluate_transfers(self, metrics_by_key: dict) -> dict:
        revenue_protected = Decimal("0")
        holding_cost_saved = Decimal("0")
        updated_keys: dict[tuple[int, int], int] = {}

        for t in self.analytics.transfers()["transfers"]:
            if t["status"] != "Recommended":
                continue  # only evaluate suggestions, not already-executed transfers

            target_key = (t["productId"], t["toStoreId"])
            target = metrics_by_key.get(target_key)
            if target is None:
                continue

            price = self._price(t["productId"])
            new_inventory = target.inventory + t["units"]
            before_risk = target.revenue_at_risk
            after_risk = max(Decimal("0"), target.demand - Decimal(new_inventory)) * price
            revenue_protected += max(Decimal("0"), before_risk - after_risk)
            updated_keys[target_key] = new_inventory

            source_key = (t["productId"], t["fromStoreId"])
            if source_key in metrics_by_key:
                cost = self._cost(t["productId"])
                holding_cost_saved += Decimal(t["units"]) * cost * HOLDING_COST_RATE / Decimal("365") * EVAL_HORIZON_DAYS
                updated_keys[source_key] = max(0, metrics_by_key[source_key].inventory - t["units"])

        return {
            "revenue_protected": revenue_protected,
            "holding_cost_saved": holding_cost_saved,
            "updated_keys": updated_keys,
        }

    # ---------- Clearance / Bundle / Donate / Discard ----------
    def _evaluate_actions(self, metrics_by_key: dict) -> dict:
        inventory_value_released = Decimal("0")
        holding_cost_saved = Decimal("0")
        waste_prevented_units = 0
        donation_writeoff_value = Decimal("0")
        updated_keys: dict[tuple[int, int], int] = {}

        for s in self.action_engine.suggestions():
            key = (s["product_id"], s["store_id"])
            qty = s["current_stock_qty"]
            cost = self._cost(s["product_id"])
            price = self._price(s["product_id"])
            action = s["action"]

            if action == "CLEARANCE_SALE":
                inventory_value_released += Decimal(qty) * price
                holding_cost_saved += Decimal(qty) * cost * HOLDING_COST_RATE / Decimal("365") * EVAL_HORIZON_DAYS
                updated_keys[key] = 0

            elif action == "DONATE":
                waste_prevented_units += qty
                donation_writeoff_value += Decimal(qty) * cost
                holding_cost_saved += Decimal(qty) * cost * HOLDING_COST_RATE / Decimal("365") * EVAL_HORIZON_DAYS
                updated_keys[key] = 0

            elif action == "DISCARD":
                holding_cost_saved += Decimal(qty) * cost * HOLDING_COST_RATE / Decimal("365") * EVAL_HORIZON_DAYS
                updated_keys[key] = 0

        return {
            "inventory_value_released": inventory_value_released,
            "holding_cost_saved": holding_cost_saved,
            "waste_prevented_units": waste_prevented_units,
            "donation_writeoff_value": donation_writeoff_value,
            "updated_keys": updated_keys,
        }

    # ---------- Helpers ----------
    def _price(self, product_id: int) -> Decimal:
        if product_id not in self._price_cache:
            p = self.db.get(Product, product_id)
            self._price_cache[product_id] = Decimal(p.price or 0) if p else Decimal("0")
        return self._price_cache[product_id]

    def _cost(self, product_id: int) -> Decimal:
        if product_id not in self._cost_cache:
            p = self.db.get(Product, product_id)
            self._cost_cache[product_id] = Decimal(p.cost or 0) if p else Decimal("0")
        return self._cost_cache[product_id]

    def _count_flag_after(self, metrics_by_key: dict, updated: dict, flag: str) -> int:
        count = 0
        for key, m in metrics_by_key.items():
            inv = Decimal(updated.get(key, m.inventory))
            if flag == "stockout" and inv < (m.demand / Decimal("30")) * LEAD_TIME_FACTOR:
                count += 1
            elif flag == "overstock" and inv > m.demand * Decimal("2"):
                count += 1
        return count

    @staticmethod
    def _pct(numerator: Decimal, denominator: Decimal) -> Decimal:
        if denominator <= 0:
            return Decimal("0")
        return (numerator / denominator) * Decimal("100")
