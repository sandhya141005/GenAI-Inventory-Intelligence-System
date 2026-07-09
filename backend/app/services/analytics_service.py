from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from math import floor

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased

from app.models.analytics_data import Product, Sale, Store, Transfer, InventoryStock
from app.services.action_engine import SmartInventoryActionEngine


LEAD_TIME_FACTOR = Decimal("3")
HOLDING_COST_RATE = Decimal("0.20")
DEMAND_SPIKE_MULTIPLIER = Decimal("1.50")


class InsufficientStockError(Exception):
    pass


@dataclass(frozen=True)
class InventoryMetric:
    product_id: int
    store_id: int
    sku: str
    product: str
    category: str
    store: str
    inventory: int
    demand: Decimal
    avg_daily_sales: Decimal
    days_of_coverage: Decimal
    revenue_at_risk: Decimal
    holding_cost: Decimal
    inventory_age_days: int
    turnover: Decimal
    stockout_risk: bool
    overstock: bool
    demand_spike: bool
    health: str
    status: str
    inventory_value: Decimal


class AnalyticsService:
    def __init__(self, db: Session, scope=None) -> None:
        self.db = db
        self.scope = scope
        self.today = date.today()
        self.last_30_days = self.today - timedelta(days=30)
        self.previous_30_days = self.today - timedelta(days=60)
        self._metrics_cache: list[InventoryMetric] | None = None

    def overview(self) -> dict:
        metrics = self._inventory_metrics()
        revenue_at_risk = sum((m.revenue_at_risk for m in metrics), Decimal("0"))
        holding_cost = sum((m.holding_cost for m in metrics), Decimal("0"))
        stockout_count = sum(1 for m in metrics if m.stockout_risk)
        overstock_count = sum(1 for m in metrics if m.overstock)
        health_score = self._store_health_score(metrics)
        turnover = self._average_decimal([m.turnover for m in metrics])

        return {
            "summary": {
                "generatedAt": self.today.isoformat(),
                "headline": f"Revenue at risk is {self._currency(revenue_at_risk)} across {stockout_count} stockout-risk positions.",
                "detail": f"{overstock_count} positions are overstocked and the network health score is {health_score}%.",
            },
            "kpis": [
                self._kpi("revenue-at-risk", "Revenue at Risk", revenue_at_risk, "risk" if revenue_at_risk else "good"),
                self._kpi("days-of-coverage", "Avg Days of Coverage", self._average_decimal([m.days_of_coverage for m in metrics]), "watch", suffix="d"),
                self._kpi("stockout-risk", "Stockout Risk", Decimal(stockout_count), "risk" if stockout_count else "good", suffix=""),
                self._kpi("holding-cost", "Holding Cost", holding_cost, "watch" if holding_cost else "good"),
                self._kpi("store-health", "Store Health Score", Decimal(health_score), "good" if health_score >= 80 else "watch", suffix="%"),
                self._kpi("inventory-turnover", "Inventory Turnover", turnover, "good", suffix="x"),
            ],
            "recommendations": self.recommendations()["recommendations"][:4],
            "actionSuggestions": SmartInventoryActionEngine(self.db, self.scope).suggestions()[:12],
        }

    def inventory(self) -> dict:
        return {"items": [self._inventory_item(metric) for metric in self._inventory_metrics()]}

    def recommendations(self) -> dict:
        recommendations: list[dict] = []
        metrics = self._inventory_metrics()

        priority_groups = {"critical": [], "high": [], "medium": [], "low": []}

        for metric in metrics:
            rec = self._generate_recommendation(metric, metrics)
            if rec:
                priority_groups[rec["priority"]].append(rec)

        for priority in ["critical", "high", "medium", "low"]:
            priority_groups[priority].sort(key=lambda r: -r["confidence"])
            recommendations.extend(priority_groups[priority][:10 if priority in ["critical", "high"] else 5])

        return {"recommendations": recommendations[:20]}

    def _generate_recommendation(self, metric: InventoryMetric, all_metrics: list[InventoryMetric]) -> dict | None:
        days = float(metric.days_of_coverage)
        demand_growth = self._calculate_demand_growth(metric)
        has_transfer_source = any(
            m.product_id == metric.product_id and m.store_id != metric.store_id and m.overstock
            for m in all_metrics
        )

        if metric.inventory == 0 and metric.demand > 0:
            return self._rec(
                metric, "Expedite Purchase", "critical", 95,
                "Immediate Replenishment",
                f"Zero stock with active demand of {int(metric.demand)} units/month",
                f"Prevents {self._currency(metric.revenue_at_risk)} revenue loss"
            )

        if days < 5 and metric.stockout_risk and not has_transfer_source and metric.revenue_at_risk > Decimal("1000"):
            return self._rec(
                metric, "Expedite Purchase", "critical", 92,
                "Critical Reorder",
                f"Only {days:.1f} days coverage, {self._currency(metric.revenue_at_risk)} at risk",
                f"Protects {self._currency(metric.revenue_at_risk)} in potential sales"
            )

        if 5 <= days < 10 and metric.stockout_risk and demand_growth > 0.2:
            return self._rec(
                metric, "Increase Safety Stock", "high", 88,
                "Adjust Safety Stock",
                f"Demand increased {demand_growth*100:.0f}%, only {days:.1f} days coverage",
                f"Prevents future stockouts worth {self._currency(metric.revenue_at_risk)}"
            )

        if has_transfer_source and days < 7 and metric.revenue_at_risk > Decimal("5000"):
            return self._rec(
                metric, "Regional Transfer", "high", 90,
                "Transfer Inventory",
                f"Critical shortage, overstock available elsewhere",
                f"Immediate fulfillment of {self._currency(metric.revenue_at_risk)} demand"
            )

        if metric.demand_spike and 10 < days < 30:
            return self._rec(
                metric, "Investigate Demand Spike", "medium", 75,
                "Monitor Demand",
                f"Unusual demand pattern detected, verify before restocking",
                "Early verification prevents overstock if spike is temporary"
            )

        if days > 180 and metric.inventory_value > Decimal("10000"):
            return self._rec(
                metric, "Return Excess Stock", "high", 85,
                "Vendor Return",
                f"Extreme overstock: {days:.0f} days ({self._currency(metric.inventory_value)})",
                f"Recovers {self._currency(metric.inventory_value * Decimal('0.8'))} via vendor credit"
            )

        if 120 < days <= 180 and metric.category in ["Accessories", "Body Parts", "Electrical", "Filters"]:
            return self._rec(
                metric, "Bundle Promotion", "medium", 78,
                "Create Bundle Offer",
                f"Overstock ({days:.0f} days) in promotional category",
                f"Accelerates turnover, saves {self._currency(metric.holding_cost * Decimal('90'))} holding costs"
            )

        if 90 < days <= 120 and metric.inventory_value > Decimal("5000"):
            return self._rec(
                metric, "Clear Aging Inventory", "medium", 80,
                "Markdown Campaign",
                f"{days:.0f} days coverage, high inventory value",
                f"Frees {self._currency(metric.inventory_value * Decimal('0.3'))} working capital"
            )

        if metric.overstock and 60 < days <= 90:
            return self._rec(
                metric, "Reduce Overstock", "medium", 82,
                "Discount or Transfer",
                f"Moderate overstock at {days:.0f} days coverage",
                f"Saves {self._currency(metric.holding_cost * Decimal('60'))} in holding costs"
            )

        imbalance_target = self._find_rebalance_opportunity(metric, all_metrics)
        if imbalance_target and 14 < days < 45:
            return self._rec(
                metric, "Rebalance Inventory", "low", 70,
                "Optimize Distribution",
                f"Transfer {imbalance_target['units']} units to {imbalance_target['target_store']}",
                f"Prevents {self._currency(imbalance_target['revenue_protected'])} stockout elsewhere"
            )

        if 14 <= days <= 45 and metric.turnover > Decimal("0.8") and not metric.stockout_risk and not metric.overstock:
            return self._rec(
                metric, "Monitor Demand Trend", "low", 65,
                "Hold Current Level",
                f"Healthy inventory: {days:.1f} days coverage, {float(metric.turnover):.2f}x turnover",
                "No action required, continue monitoring"
            )

        return None

    def _rec(self, metric: InventoryMetric, rec_type: str, priority: str, confidence: int,
             action: str, reason: str, impact: str) -> dict:
        return {
            "id": f"{rec_type.lower().replace(' ', '-')}-{metric.store_id}-{metric.product_id}",
            "title": f"{rec_type}: {metric.product}",
            "reason": f"{metric.store}: {reason}",
            "impact": impact,
            "priority": priority,
            "confidence": confidence,
            "estimatedSavings": self._currency(max(metric.revenue_at_risk, metric.holding_cost * Decimal("30"))),
            "primaryAction": action,
        }

    def _calculate_demand_growth(self, metric: InventoryMetric) -> float:
        sales_30 = self._sales_totals(self.last_30_days, self.today).get((metric.product_id, metric.store_id), 0)
        sales_prev = self._sales_totals(self.previous_30_days, self.last_30_days - timedelta(days=1)).get((metric.product_id, metric.store_id), 0)
        if sales_prev == 0:
            return 0.0
        return (sales_30 - sales_prev) / sales_prev

    def _find_rebalance_opportunity(self, metric: InventoryMetric, all_metrics: list[InventoryMetric]) -> dict | None:
        if metric.days_of_coverage < 14 or metric.overstock:
            return None

        for target in all_metrics:
            if (target.product_id == metric.product_id and
                target.store_id != metric.store_id and
                target.days_of_coverage < 7 and
                target.stockout_risk):

                transfer_qty = min(
                    int(metric.inventory * 0.3),
                    max(1, int(target.demand * LEAD_TIME_FACTOR) - target.inventory)
                )

                if transfer_qty > 0:
                    return {
                        "units": transfer_qty,
                        "target_store": target.store,
                        "revenue_protected": target.revenue_at_risk
                    }

        return None

    def reports(self) -> dict:
        overview = self.overview()

        content = f"""
    Inventory Decision Report

    Summary:
    {overview["summary"]["headline"]}

    Details:
    {overview["summary"]["detail"]}

    Key Performance Indicators:
    """

        for kpi in overview["kpis"]:
            content += f"""
    {kpi["label"]}: {kpi["value"]}
    Status: {kpi["status"]}
    """

        content += "\nTop Recommendations:\n"

        for rec in self.recommendations()["recommendations"][:5]:
            content += f"""
    - {rec["title"]}
    Reason: {rec["reason"]}
    Impact: {rec["impact"]}
    Confidence: {rec["confidence"]}%
    """

        return {
            "reports": [
                {
                    "id": "inventory-decision-report",
                    "title": "Inventory Decision Report",
                    "summary": overview["summary"]["headline"],
                    "generatedBy": "Decision Intelligence Engine",
                    "lastUpdated": self.today.isoformat(),
                    "content": content
                },
                {
                    "id": "risk-report",
                    "title": "Stockout and Overstock Risk",
                    "summarsy": overview["summary"]["detail"],
                    "generatedBy": "Decision Intelligence Engine",
                    "lastUpdated": self.today.isoformat(),
                    "content": content
                }
            ]
        }

    def charts(self) -> dict:
        revenue_rows = self.db.execute(
            self._sale_scope_filter(
                select(Sale.sale_date, func.coalesce(func.sum(Sale.revenue), 0))
            )
            .where(Sale.sale_date >= self.today - timedelta(days=6))
            .group_by(Sale.sale_date)
            .order_by(Sale.sale_date)
        ).all()
        revenue_by_day = {row[0]: Decimal(row[1] or 0) for row in revenue_rows}
        dates = [self.today - timedelta(days=offset) for offset in range(6, -1, -1)]
        metrics = self._inventory_metrics()
        store_scores = self._store_scores(metrics)
        category_counts: dict[str, int] = defaultdict(int)
        for metric in metrics:
            category_counts[metric.category] += 1
        return {
            "revenueTrend": {"labels": [day.strftime("%a") for day in dates], "values": [float(revenue_by_day.get(day, Decimal("0"))) for day in dates]},
            "storePerformance": {"labels": list(store_scores.keys()), "values": list(store_scores.values())},
            "categoryMix": {"labels": list(category_counts.keys()), "values": list(category_counts.values())},
        }

    def initiate_transfer(
        self,
        product_id: int,
        from_store_id: int,
        to_store_id: int,
        quantity: int,
        transfer_cost: Decimal = Decimal("0"),
    ) -> dict:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        from_stock = self.db.execute(
            self._realm_filter(
                select(InventoryStock).where(
                    InventoryStock.product_id == product_id,
                    InventoryStock.store_id == from_store_id,
                ),
                InventoryStock,
            )
        ).scalar_one_or_none()

        current_qty = int(from_stock.quantity) if from_stock else 0
        if current_qty < quantity:
            raise InsufficientStockError(f"Only {current_qty} units available for product {product_id} at store {from_store_id}")

        if self.scope is not None:
            if getattr(self.scope, "is_store_manager", False):
                allowed_store = getattr(self.scope, "assigned_store_id", None)
                if allowed_store not in {from_store_id, to_store_id}:
                    raise PermissionError("Store managers can only transfer inventory involving their assigned store")
            for store_id in {from_store_id, to_store_id}:
                db_store = self.db.get(Store, store_id)
                if not db_store or db_store.realm_id != self.scope.realm_id:
                    raise PermissionError("Transfer store is outside this realm")

        from_stock.quantity = current_qty - quantity
        from_stock.last_updated = self.today

        to_stock = self.db.execute(
            self._realm_filter(
                select(InventoryStock).where(
                    InventoryStock.product_id == product_id,
                    InventoryStock.store_id == to_store_id,
                ),
                InventoryStock,
            )
        ).scalar_one_or_none()

        if to_stock is None:
            to_stock = InventoryStock(
                product_id=product_id,
                store_id=to_store_id,
                quantity=quantity,
                last_updated=self.today,
                realm_id=getattr(self.scope, "realm_id", None) or from_stock.realm_id,
            )
            self.db.add(to_stock)
        else:
            to_stock.quantity = int(to_stock.quantity or 0) + quantity
            to_stock.last_updated = self.today

        transfer = Transfer(
            realm_id=getattr(self.scope, "realm_id", None),
            from_store_id=from_store_id,
            to_store_id=to_store_id,
            product_id=product_id,
            quantity=quantity,
            transfer_cost=transfer_cost,
            transfer_date=self.today,
        )
        self.db.add(transfer)
        self.db.commit()
        self.db.refresh(transfer)

        product = self.db.get(Product, product_id)
        from_store = self.db.get(Store, from_store_id)
        to_store = self.db.get(Store, to_store_id)

        self._metrics_cache = None

        return {
            "id": f"TR-{transfer.id}",
            "productId": product_id,
            "product": product.name if product else str(product_id),
            "fromStoreId": from_store_id,
            "from": from_store.name if from_store else str(from_store_id),
            "toStoreId": to_store_id,
            "to": to_store.name if to_store else str(to_store_id),
            "units": quantity,
            "transferCost": float(transfer_cost),
            "revenueAtRisk": 0.0,
            "status": "Completed",
            "eta": transfer.transfer_date.isoformat(),
        }

    def transfers(self) -> dict:
        from_store_alias = aliased(Store)
        to_store_alias = aliased(Store)
        rows = self.db.execute(
            select(Transfer, Product, from_store_alias, to_store_alias)
            .join(Product, Product.id == Transfer.product_id)
            .join(from_store_alias, from_store_alias.id == Transfer.from_store_id)
            .join(to_store_alias, to_store_alias.id == Transfer.to_store_id)
            .where(*self._transfer_filters(Transfer))
            .order_by(Transfer.transfer_date.desc().nullslast(), Transfer.id.desc())
        ).all()
        existing = [
            {
                "id": f"TR-{transfer.id}",
                "productId": product.id,
                "product": product.name or product.sku or str(product.id),
                "fromStoreId": from_store.id,
                "from": from_store.name or str(from_store.id),
                "toStoreId": to_store.id,
                "to": to_store.name or str(to_store.id),
                "units": int(transfer.quantity or 0),
                "transferCost": float(transfer.transfer_cost or 0),
                "revenueAtRisk": 0.0,
                "status": "Completed",
                "eta": transfer.transfer_date.isoformat() if transfer.transfer_date else "",
            }
            for transfer, product, from_store, to_store in rows
        ]
        suggestions = [self._transfer_suggestion(metric) for metric in self._inventory_metrics() if metric.demand_spike or metric.stockout_risk]
        return {"transfers": existing + [suggestion for suggestion in suggestions if suggestion]}

    def inventory_aging(self) -> dict:
        items = sorted(self._inventory_metrics(), key=lambda metric: metric.inventory_value, reverse=True)
        return {"items": [self._aging_item(metric) for metric in items]}

    def notices(self) -> dict:
        notices: list[dict] = []
        for index, metric in enumerate(self._inventory_metrics(), start=1):
            if metric.stockout_risk:
                notices.append(
                    {
                        "id": f"stockout-{index}",
                        "category": "Stockout",
                        "title": f"{metric.product} stockout risk",
                        "detail": f"{metric.store}: {metric.inventory} units, {float(metric.days_of_coverage):.1f} days of coverage.",
                        "timestamp": self.today.isoformat(),
                    }
                )
            if metric.overstock:
                notices.append(
                    {
                        "id": f"overstock-{index}",
                        "category": "Recommendation",
                        "title": f"{metric.product} overstock reduction",
                        "detail": f"{metric.store}: inventory exceeds 2x current 30-day demand.",
                        "timestamp": self.today.isoformat(),
                    }
                )
        return {"notices": notices[:20]}

    def _inventory_metrics(self) -> list[InventoryMetric]:
        if self._metrics_cache is not None:
            return self._metrics_cache

        products = {
            product.id: product
            for product in self.db.execute(select(Product)).scalars()
            if self._in_realm(product)
        }
        stores = {
            store.id: store
            for store in self.db.execute(select(Store)).scalars()
            if self._in_realm(store) and self._store_allowed(store.id)
        }
        stock_by_key = {
            (row.product_id, row.store_id): int(row.quantity or 0)
            for row in self.db.execute(self._realm_filter(select(InventoryStock), InventoryStock)).scalars()
        }
        sales_30 = self._sales_totals(self.last_30_days, self.today)
        sales_prev = self._sales_totals(self.previous_30_days, self.last_30_days - timedelta(days=1))

        keys = set(sales_30) | set(sales_prev) | set(stock_by_key)

        metrics: list[InventoryMetric] = []
        for product_id, store_id in sorted(keys):
            product = products.get(product_id)
            if product is None:
                continue
            store = stores.get(store_id)
            if store is None:
                continue
            if self.scope is not None and getattr(self.scope, "is_store_manager", False) and store_id != getattr(self.scope, "assigned_store_id", None):
                continue

            inventory = stock_by_key.get((product_id, store_id), 0)
            demand = Decimal(sales_30.get((product_id, store_id), 0))
            previous_demand = Decimal(sales_prev.get((product_id, store_id), 0))
            price = Decimal(product.price or 0)
            cost = Decimal(product.cost or 0)
            avg_daily_sales = demand / Decimal("30")
            days = Decimal(inventory) / avg_daily_sales if avg_daily_sales > 0 else Decimal("0")
            revenue_at_risk = Decimal(max(0, int(demand) - inventory)) * price
            inventory_value = Decimal(inventory) * price
            holding_cost = Decimal(inventory) * cost * HOLDING_COST_RATE / Decimal("365")
            turnover = demand / Decimal(inventory) if inventory > 0 else Decimal("0")
            stockout_risk =  inventory < (demand/Decimal("30")) * LEAD_TIME_FACTOR
            overstock = Decimal(inventory) > demand * Decimal("2")
            demand_spike = demand > 0 and previous_demand > 0 and demand >= previous_demand * DEMAND_SPIKE_MULTIPLIER
            health = self._health(days, stockout_risk, overstock)
            status = "stockout" if inventory <= 0 else "at-risk" if stockout_risk else "overstock" if overstock else "in-stock"
            metrics.append(
                InventoryMetric(
                    product_id=product.id,
                    store_id=store.id,
                    sku=product.sku or str(product.id),
                    product=product.name or product.sku or str(product.id),
                    category=product.category or "Uncategorized",
                    store=store.name or "Unknown",
                    inventory=inventory,
                    demand=demand,
                    avg_daily_sales=avg_daily_sales,
                    days_of_coverage=days,
                    revenue_at_risk=revenue_at_risk,
                    holding_cost=holding_cost,
                    inventory_age_days=0,
                    turnover=turnover,
                    stockout_risk=stockout_risk,
                    overstock=overstock,
                    demand_spike=demand_spike,
                    health=health,
                    status=status,
                    inventory_value=inventory_value,
                )
            )
        self._metrics_cache = metrics
        return metrics

    def _sales_totals(self, start: date, end: date) -> dict[tuple[int, int], int]:
        rows = self.db.execute(
            self._sale_scope_filter(select(Sale.product_id, Sale.store_id, func.coalesce(func.sum(Sale.quantity), 0)))
            .where(Sale.sale_date >= start, Sale.sale_date <= end, Sale.product_id.is_not(None), Sale.store_id.is_not(None))
            .group_by(Sale.product_id, Sale.store_id)
        ).all()
        return {(int(product_id), int(store_id)): int(total or 0) for product_id, store_id, total in rows}

    def _inventory_item(self, metric: InventoryMetric) -> dict:
        return {
            "sku": metric.sku,
            "product": metric.product,
            "store": metric.store,
            "inventory": metric.inventory,
            "demand": int(metric.demand),
            "daysOfCover": float(metric.days_of_coverage),
            "health": metric.health,
            "revenueAtRisk": float(metric.revenue_at_risk),
            "status": metric.status,
        }

    def _transfer_suggestion(self, metric: InventoryMetric) -> dict | None:
        source = next((m for m in self._inventory_metrics() if m.product_id == metric.product_id and m.store_id != metric.store_id and m.overstock), None)
        if source is None:
            return None
        source_surplus = max(1, source.inventory - int(source.demand * 2))
        target_gap = max(1, int(metric.demand * LEAD_TIME_FACTOR) - metric.inventory)
        units = max(1, floor(min(source_surplus, target_gap)))
        product = self.db.get(Product, metric.product_id)
        transfer_cost = float(units) * 2.5

        # NEW: only worth transferring if 30-day idle holding cost of the surplus exceeds the move cost
        cost = Decimal(product.cost or 0) if product else Decimal("0")
        idle_holding_cost_30d = float(Decimal(units) * cost * HOLDING_COST_RATE / Decimal("365") * Decimal("30"))
        if idle_holding_cost_30d <= transfer_cost:
            return None

        return {
            "id": f"SUG-{source.store_id}-{metric.store_id}-{metric.product_id}",
            "productId": metric.product_id,
            "product": metric.product,
            "fromStoreId": source.store_id,
            "from": source.store,
            "toStoreId": metric.store_id,
            "to": metric.store,
            "units": units,
            "transferCost": round(transfer_cost, 2),
            "revenueAtRisk": float(metric.revenue_at_risk),
            "status": "Recommended",
            "eta": "Rule-based",
        }

    def _aging_item(self, metric: InventoryMetric) -> dict:
        return {
            "product": metric.product,
            "store": metric.store,
            "ageDays": metric.inventory_age_days,
            "value": float(metric.inventory_value),
            "band": "0-30 days",
        }

    def _store_scores(self, metrics: list[InventoryMetric]) -> dict[str, int]:
        grouped: dict[str, list[InventoryMetric]] = defaultdict(list)
        for metric in metrics:
            grouped[metric.store].append(metric)
        return {store: self._store_health_score(items) for store, items in grouped.items()}

    def _store_health_score(self, metrics: list[InventoryMetric]) -> int:
        if not metrics:
            return 100
        penalties = sum((30 if metric.stockout_risk else 0) + (15 if metric.overstock else 0) for metric in metrics)
        return max(0, min(100, 100 - floor(penalties / len(metrics))))

    def _kpi(self, id_: str, label: str, value: Decimal, status: str, suffix: str | None = None) -> dict:
        display = self._currency(value) if suffix is None else f"{float(value):.1f}{suffix}"
        numeric = float(value)
        return {
            "id": id_,
            "label": label,
            "value": display,
            "trend": 0,
            "trendData": [numeric for _ in range(7)],
            "status": status,
            "explanation": {
                "why": "Calculated from PostgreSQL products, stores, sales, inventory_stock, and transfers tables.",
                "action": "Review the generated rule-based recommendations.",
            },
        }

    def _average_decimal(self, values: list[Decimal]) -> Decimal:
        return sum(values, Decimal("0")) / Decimal(len(values)) if values else Decimal("0")

    def _health(self, days: Decimal, stockout_risk: bool, overstock: bool) -> str:
        if overstock:
            return "overstock"
        if stockout_risk or days < 3:
            return "critical"
        if days < 7:
            return "low"
        return "healthy"

    def _currency(self, value: Decimal) -> str:
        return f"INR {float(value):,.0f}"

    def _in_realm(self, row) -> bool:
        return self.scope is None or getattr(row, "realm_id", None) == self.scope.realm_id

    def _store_allowed(self, store_id: int | None) -> bool:
        if self.scope is None or store_id is None:
            return True
        if getattr(self.scope, "is_store_manager", False):
            return store_id == getattr(self.scope, "assigned_store_id", None)
        return True

    def _realm_filter(self, statement, model):
        if self.scope is None:
            return statement
        return statement.where(model.realm_id == self.scope.realm_id)

    def _sale_scope_filter(self, statement):
        statement = self._realm_filter(statement, Sale)
        if self.scope is not None and getattr(self.scope, "is_store_manager", False):
            statement = statement.where(Sale.store_id == self.scope.assigned_store_id)
        return statement

    def _transfer_filters(self, model) -> list:
        filters = []
        if self.scope is not None:
            filters.append(model.realm_id == self.scope.realm_id)
            if getattr(self.scope, "is_store_manager", False):
                filters.append(or_(model.from_store_id == self.scope.assigned_store_id, model.to_store_id == self.scope.assigned_store_id))
        return filters