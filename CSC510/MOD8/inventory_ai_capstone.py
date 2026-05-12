from __future__ import annotations

from pathlib import Path
from math import ceil
from typing import Optional, Union

import numpy as np
import pandas as pd
from sklearn.naive_bayes import GaussianNB


# =========================================================
# CONFIGURATION
# =========================================================

TABLES_DIR = Path(r"C:\Users\culex\Documents\CSU-Global\CSU-Global-MS-AI-ML\CSC510\MOD8\Tables")

ITEMS_FILE = "items.csv"
SUPPLIERS_FILE = "suppliers.csv"
INVENTORY_FILE = "inventory_status.csv"
DEMAND_FILE = "demand_history.csv"
PURCHASE_ORDERS_FILE = "purchase_orders.csv"

SALES_ORDERS_FILE_CANDIDATES = [
    "sales_orders.csv",
    "customer_purchase_orders.csv",
    "customer_orders.csv",
]

LOOKBACK_DAYS = 90
PLAN_DATE = pd.Timestamp.today().normalize()


# =========================================================
# HELPERS
# =========================================================

NumericLike = Union[pd.Series, int, float]


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]+", "_", regex=True)
        .str.strip("_")
    )
    return df


def find_existing_file(folder: Path, candidates: list[str]) -> Optional[Path]:
    for name in candidates:
        p = folder / name
        if p.exists():
            return p
    return None


def first_existing_col(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def first_existing_date_col(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    """
    Return the first matching date-like column from a list of candidates.
    """
    return first_existing_col(df, candidates)


def as_series(value: NumericLike, index: pd.Index) -> pd.Series:
    if isinstance(value, pd.Series):
        return value
    return pd.Series([value] * len(index), index=index)


def to_int_series(value: NumericLike, index: pd.Index) -> pd.Series:
    s = as_series(value, index)
    return pd.to_numeric(s, errors="coerce").fillna(0).astype(int)


def to_float_series(value: NumericLike, index: pd.Index) -> pd.Series:
    s = as_series(value, index)
    return pd.to_numeric(s, errors="coerce").fillna(0.0).astype(float)


def classify_variability(avg_daily_demand: float, demand_std_dev: float) -> str:
    if avg_daily_demand <= 0:
        return "low"
    ratio = demand_std_dev / avg_daily_demand
    if ratio < 0.50:
        return "low"
    if ratio < 1.00:
        return "med"
    return "high"


def classify_lead_time(days: float) -> str:
    if days <= 45:
        return "short"
    if days <= 90:
        return "medium"
    return "long"


def classify_supplier_reliability(score: float) -> str:
    return "high" if score >= 0.85 else "low"


def choose_recommended_action(row: pd.Series) -> str:
    inbound_too_late = (
        row["days_until_next_po_arrival"] > row["days_of_supply"]
        if pd.notna(row["days_until_next_po_arrival"])
        else True
    )

    if (
        row["stockout_risk_class"] == "High"
        and inbound_too_late
        and row["net_available_inventory"] < row["lead_time_demand"]
    ):
        return "EXPEDITE"

    if (
        row["net_available_inventory"] <= row["reorder_point"]
        or row["days_of_supply"] <= row["avg_lead_time_days"]
        or row["stockout_risk_class"] == "High"
    ):
        return "REORDER"

    if (
        str(row["criticality_level"]).lower() == "high"
        and row["supplier_reliability_class"] == "low"
        and row["stockout_risk_class"] == "Low"
    ):
        return "REVIEW"

    return "WAIT"


def recommended_order_qty(row: pd.Series) -> tuple[int, int]:
    target_qty = max(
        0.0,
        float(row["lead_time_demand"]) + float(row["safety_stock"]) - float(row["net_available_inventory"]),
    )

    moq = max(int(row["moq"]), 1)

    if target_qty <= 0:
        return 0, 0

    multiple = int(ceil(target_qty / moq))
    qty = multiple * moq
    return qty, multiple


def build_explanation(row: pd.Series) -> str:
    action = row["recommended_action"]

    if action == "EXPEDITE":
        return (
            f"Expedite recommended because stockout risk is {row['stockout_risk_class']} "
            f"({row['stockout_risk_probability']:.2f}), net available inventory is below lead-time demand, "
            f"and existing inbound supply arrives too late."
        )

    if action == "REORDER":
        return (
            f"Reorder recommended because net available inventory ({row['net_available_inventory']}) "
            f"is at or below the reorder trigger, stockout risk is {row['stockout_risk_class']} "
            f"({row['stockout_risk_probability']:.2f}), and MOQ rules require an order quantity of "
            f"{row['recommended_order_qty']} units."
        )

    if action == "REVIEW":
        return (
            f"Review recommended because the item is high criticality and supplier reliability is low, "
            f"although current stockout risk remains below the automatic reorder threshold."
        )

    return (
        f"Wait recommended because available and inbound supply are sufficient for projected demand, "
        f"and current stockout risk is {row['stockout_risk_class']} ({row['stockout_risk_probability']:.2f})."
    )


# =========================================================
# LOAD FILES
# =========================================================

def load_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sales_path = find_existing_file(TABLES_DIR, SALES_ORDERS_FILE_CANDIDATES)
    if sales_path is None:
        raise FileNotFoundError(
            f"Could not find a sales orders file in {TABLES_DIR}. "
            f"Tried: {SALES_ORDERS_FILE_CANDIDATES}"
        )

    items = pd.read_csv(TABLES_DIR / ITEMS_FILE)
    suppliers = pd.read_csv(TABLES_DIR / SUPPLIERS_FILE)
    inventory = pd.read_csv(TABLES_DIR / INVENTORY_FILE)
    demand = pd.read_csv(TABLES_DIR / DEMAND_FILE)
    purchase_orders = pd.read_csv(TABLES_DIR / PURCHASE_ORDERS_FILE)
    sales_orders = pd.read_csv(sales_path)

    return items, suppliers, inventory, demand, purchase_orders, sales_orders


# =========================================================
# CLEAN TABLES
# =========================================================

def clean_items(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)

    item_col = first_existing_col(df, ["item_id", "internal_id", "item"])
    supplier_col = first_existing_col(df, ["supplier_id"])

    if item_col is None or supplier_col is None:
        raise ValueError("items.csv must contain item_id/internal_id and supplier_id.")

    df = df.rename(columns={item_col: "item_id", supplier_col: "supplier_id"})

    optional_map = {
        first_existing_col(df, ["item_name", "name", "description"]): "item_name",
        first_existing_col(df, ["category"]): "category",
        first_existing_col(df, ["criticality_level", "criticality"]): "criticality_level",
        first_existing_col(df, ["holding_cost"]): "holding_cost",
        first_existing_col(df, ["stockout_penalty"]): "stockout_penalty",
        first_existing_col(df, ["moq", "minimum_order_quantity"]): "moq",
    }
    optional_map = {k: v for k, v in optional_map.items() if k is not None}
    df = df.rename(columns=optional_map)

    df["item_id"] = to_int_series(df["item_id"], df.index)
    df["supplier_id"] = to_int_series(df["supplier_id"], df.index)
    df["holding_cost"] = to_float_series(df.get("holding_cost", 0.0), df.index)
    df["stockout_penalty"] = to_float_series(df.get("stockout_penalty", 0.0), df.index)
    df["moq"] = to_int_series(df.get("moq", 1), df.index)

    if "item_name" not in df.columns:
        df["item_name"] = "Unknown Item"
    if "category" not in df.columns:
        df["category"] = "Unknown"
    if "criticality_level" not in df.columns:
        df["criticality_level"] = "low"

    return df[
        [
            "item_id",
            "item_name",
            "category",
            "criticality_level",
            "holding_cost",
            "stockout_penalty",
            "moq",
            "supplier_id",
        ]
    ]


def clean_suppliers(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)

    supplier_col = first_existing_col(df, ["supplier_id"])
    if supplier_col is None:
        raise ValueError("suppliers.csv must contain supplier_id.")

    df = df.rename(columns={supplier_col: "supplier_id"})

    optional_map = {
        first_existing_col(df, ["supplier_name", "name"]): "supplier_name",
        first_existing_col(df, ["reliability_score"]): "reliability_score",
        first_existing_col(df, ["average_lead_time_days", "avg_lead_time_days", "lead_time_days"]): "avg_lead_time_days",
        first_existing_col(df, ["variability_index"]): "variability_index",
    }
    optional_map = {k: v for k, v in optional_map.items() if k is not None}
    df = df.rename(columns=optional_map)

    df["supplier_id"] = to_int_series(df["supplier_id"], df.index)
    df["reliability_score"] = to_float_series(df.get("reliability_score", 0.85), df.index)
    df["avg_lead_time_days"] = to_float_series(df.get("avg_lead_time_days", 45.0), df.index)
    df["variability_index"] = to_float_series(df.get("variability_index", 0.0), df.index)

    if "supplier_name" not in df.columns:
        df["supplier_name"] = "Unknown Supplier"

    return df[
        [
            "supplier_id",
            "supplier_name",
            "reliability_score",
            "avg_lead_time_days",
            "variability_index",
        ]
    ]


def clean_inventory(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)

    item_col = first_existing_col(df, ["item_id", "internal_id"])
    if item_col is None:
        raise ValueError("inventory_status.csv must contain item_id/internal_id.")

    df = df.rename(columns={item_col: "item_id"})

    optional_map = {
        first_existing_col(df, ["current_on_hand", "on_hand", "qty_on_hand"]): "current_on_hand",
        first_existing_col(df, ["safety_stock"]): "safety_stock",
        first_existing_col(df, ["reorder_point"]): "reorder_point",
        first_existing_col(df, ["last_updated"]): "last_updated",
    }
    optional_map = {k: v for k, v in optional_map.items() if k is not None}
    df = df.rename(columns=optional_map)

    df["item_id"] = to_int_series(df["item_id"], df.index)
    df["current_on_hand"] = to_int_series(df.get("current_on_hand", 0), df.index)
    df["safety_stock"] = to_int_series(df.get("safety_stock", 0), df.index)
    df["reorder_point"] = to_int_series(df.get("reorder_point", 0), df.index)

    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")

    return df[
        [
            "item_id",
            "current_on_hand",
            "safety_stock",
            "reorder_point",
        ]
    ]


def clean_demand(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)

    item_col = first_existing_col(df, ["item_id", "internal_id"])
    date_col = first_existing_col(df, ["date"])
    qty_col = first_existing_col(df, ["quantity", "qty", "units_sold"])

    if item_col is None or date_col is None or qty_col is None:
        raise ValueError("demand_history.csv must contain item_id/internal_id, date, and quantity.")

    df = df.rename(columns={item_col: "item_id", date_col: "date", qty_col: "quantity"})
    df["item_id"] = to_int_series(df["item_id"], df.index)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["quantity"] = to_float_series(df["quantity"], df.index)

    return df[["item_id", "date", "quantity"]].dropna(subset=["date"])


def clean_orders(df: pd.DataFrame, order_type: str) -> pd.DataFrame:
    """
    Generic cleaner for both sales orders and purchase orders.
    Uses flexible date-column detection so PO arrival dates populate more reliably.
    """
    df = standardize_columns(df)

    item_col = first_existing_col(df, ["item_id", "internal_id"])
    qty_col = first_existing_col(df, ["qty_ordered", "quantity", "qty", "order_quantity"])
    status_col = first_existing_col(df, ["status", "document_status", "po_status", "so_status"])

    # Broader arrival-date detection for purchase orders
    if order_type == "purchase_orders":
        expected_arrival_col = first_existing_date_col(
            df,
            [
                "expected_arrival",
                "expected_receipt_date",
                "expected_arrival_date",
                "promised_date",
                "eta",
                "estimated_arrival",
                "receipt_date",
                "due_date",
                "need_by_date",
                "ship_date",
            ],
        )
    else:
        expected_arrival_col = first_existing_date_col(
            df,
            [
                "due_date",
                "ship_date",
                "expected_ship_date",
                "promised_date",
                "requested_date",
            ],
        )

    order_date_col = first_existing_date_col(
        df,
        [
            "order_date",
            "date",
            "created_date",
            "transaction_date",
            "document_date",
        ],
    )

    if item_col is None or qty_col is None:
        raise ValueError(f"{order_type} file must contain item_id/internal_id and quantity.")

    rename_map = {item_col: "item_id", qty_col: "qty_ordered"}

    if status_col:
        rename_map[status_col] = "status"
    if expected_arrival_col:
        rename_map[expected_arrival_col] = "expected_arrival"
    if order_date_col:
        rename_map[order_date_col] = "order_date"

    df = df.rename(columns=rename_map)

    df["item_id"] = to_int_series(df["item_id"], df.index)
    df["qty_ordered"] = to_float_series(df["qty_ordered"], df.index)

    if "status" not in df.columns:
        df["status"] = "open"

    if "expected_arrival" in df.columns:
        df["expected_arrival"] = pd.to_datetime(df["expected_arrival"], errors="coerce")
    else:
        df["expected_arrival"] = pd.NaT

    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    else:
        df["order_date"] = pd.NaT

    return df[["item_id", "qty_ordered", "status", "expected_arrival", "order_date"]]


# =========================================================
# FEATURE ENGINEERING
# =========================================================

def build_inventory_features(
    items: pd.DataFrame,
    suppliers: pd.DataFrame,
    inventory: pd.DataFrame,
    demand: pd.DataFrame,
    sales_orders: pd.DataFrame,
    purchase_orders: pd.DataFrame,
) -> pd.DataFrame:

    recent_cutoff = PLAN_DATE - pd.Timedelta(days=LOOKBACK_DAYS)
    demand_recent = demand[demand["date"] >= recent_cutoff].copy()

    demand_agg = (
        demand_recent.groupby("item_id", as_index=False)
        .agg(
            total_recent_demand=("quantity", "sum"),
            avg_daily_demand=("quantity", "mean"),
            demand_std_dev=("quantity", "std"),
        )
    )

    demand_agg["demand_std_dev"] = demand_agg["demand_std_dev"].fillna(0.0)
    demand_agg["avg_daily_demand"] = demand_agg["avg_daily_demand"].fillna(0.0)
    demand_agg["total_recent_demand"] = demand_agg["total_recent_demand"].fillna(0.0)

    # Sales orders
    so_open = sales_orders.copy()
    so_open["status"] = so_open["status"].astype(str).str.lower()
    so_open = so_open[~so_open["status"].isin(["closed", "complete", "completed", "cancelled", "canceled"])]

    sales_agg = (
        so_open.groupby("item_id", as_index=False)
        .agg(open_sales_order_qty=("qty_ordered", "sum"))
    )

    # Purchase orders
    po_open = purchase_orders.copy()
    po_open["status"] = po_open["status"].astype(str).str.lower()
    po_open = po_open[~po_open["status"].isin(["closed", "received", "complete", "completed", "cancelled", "canceled"])]

    purchase_qty_agg = (
        po_open.groupby("item_id", as_index=False)
        .agg(open_purchase_order_qty=("qty_ordered", "sum"))
    )

    purchase_eta_agg = (
        po_open.dropna(subset=["expected_arrival"])
        .groupby("item_id", as_index=False)
        .agg(next_po_arrival_date=("expected_arrival", "min"))
    )

    # Merge source tables
    features = items.merge(suppliers, on="supplier_id", how="left")
    features = features.merge(inventory, on="item_id", how="left")
    features = features.merge(demand_agg, on="item_id", how="left")
    features = features.merge(sales_agg, on="item_id", how="left")
    features = features.merge(purchase_qty_agg, on="item_id", how="left")
    features = features.merge(purchase_eta_agg, on="item_id", how="left")

    numeric_fill_zero = [
        "current_on_hand",
        "safety_stock",
        "reorder_point",
        "avg_daily_demand",
        "demand_std_dev",
        "total_recent_demand",
        "open_sales_order_qty",
        "open_purchase_order_qty",
        "holding_cost",
        "stockout_penalty",
        "moq",
        "avg_lead_time_days",
        "reliability_score",
        "variability_index",
    ]
    for col in numeric_fill_zero:
        if col in features.columns:
            features[col] = features[col].fillna(0)

    features["snapshot_date"] = PLAN_DATE

    # Core formulas
    features["net_available_inventory"] = (
        features["current_on_hand"]
        + features["open_purchase_order_qty"]
        - features["open_sales_order_qty"]
    )

    features["days_of_supply"] = features.apply(
        lambda r: 999.0 if r["avg_daily_demand"] <= 0 else r["net_available_inventory"] / r["avg_daily_demand"],
        axis=1,
    )

    features["lead_time_demand"] = features["avg_daily_demand"] * features["avg_lead_time_days"]

    features["days_until_next_po_arrival"] = (
        features["next_po_arrival_date"] - PLAN_DATE
    ).dt.days

    # Classes
    features["demand_variability_class"] = features.apply(
        lambda r: classify_variability(float(r["avg_daily_demand"]), float(r["demand_std_dev"])),
        axis=1,
    )
    features["lead_time_class"] = features["avg_lead_time_days"].apply(classify_lead_time)
    features["supplier_reliability_class"] = features["reliability_score"].apply(classify_supplier_reliability)

    # Training target for Naive Bayes
    features["risk_target"] = np.where(
        (
            (features["net_available_inventory"] < features["lead_time_demand"])
            | (features["days_of_supply"] < features["avg_lead_time_days"])
            | (
                features["criticality_level"].astype(str).str.lower().eq("high")
                & features["supplier_reliability_class"].eq("low")
            )
        ),
        1,
        0,
    )

    model_features = features[
        [
            "avg_daily_demand",
            "demand_std_dev",
            "current_on_hand",
            "open_sales_order_qty",
            "open_purchase_order_qty",
            "net_available_inventory",
            "days_of_supply",
            "avg_lead_time_days",
            "reliability_score",
            "lead_time_demand",
        ]
    ].copy()

    X = model_features.fillna(0.0).to_numpy(dtype=float)
    y = features["risk_target"].to_numpy(dtype=int)

    if len(np.unique(y)) > 1:
        nb = GaussianNB()
        nb.fit(X, y)
        prob_high = nb.predict_proba(X)[:, 1]
    else:
        prob_high = np.where(y == 1, 1.0, 0.0)

    features["stockout_risk_probability"] = prob_high
    features["stockout_risk_class"] = np.where(features["stockout_risk_probability"] >= 0.60, "High", "Low")

    features["forecast_demand_next_period"] = features["avg_daily_demand"] * 30

    features["feature_notes"] = np.where(
        features["stockout_risk_class"] == "High",
        "High projected stockout exposure based on inventory position and lead-time demand.",
        "Inventory position currently adequate relative to projected demand and replenishment window.",
    )

    final_cols = [
        "item_id",
        "snapshot_date",
        "item_name",
        "category",
        "criticality_level",
        "supplier_id",
        "supplier_name",
        "current_on_hand",
        "safety_stock",
        "reorder_point",
        "moq",
        "holding_cost",
        "stockout_penalty",
        "avg_lead_time_days",
        "reliability_score",
        "variability_index",
        "avg_daily_demand",
        "demand_std_dev",
        "total_recent_demand",
        "demand_variability_class",
        "open_sales_order_qty",
        "open_purchase_order_qty",
        "next_po_arrival_date",
        "days_until_next_po_arrival",
        "net_available_inventory",
        "days_of_supply",
        "lead_time_demand",
        "lead_time_class",
        "supplier_reliability_class",
        "stockout_risk_class",
        "stockout_risk_probability",
        "forecast_demand_next_period",
        "feature_notes",
    ]

    return features[final_cols].copy()


# =========================================================
# REORDER PLAN
# =========================================================

def build_reorder_plan(features: pd.DataFrame) -> pd.DataFrame:
    plan = features.copy()

    plan["plan_date"] = PLAN_DATE
    plan["recommended_action"] = plan.apply(choose_recommended_action, axis=1)

    qty_multiple = plan.apply(recommended_order_qty, axis=1)
    plan["recommended_order_qty"] = [x[0] for x in qty_multiple]
    plan["recommended_order_multiple"] = [x[1] for x in qty_multiple]

    plan["expected_arrival_date"] = np.where(
        plan["recommended_action"].isin(["REORDER", "EXPEDITE"]),
        PLAN_DATE + pd.to_timedelta(plan["avg_lead_time_days"], unit="D"),
        plan["next_po_arrival_date"],
    )
    plan["expected_arrival_date"] = pd.to_datetime(plan["expected_arrival_date"], errors="coerce")

    plan["projected_days_of_supply"] = plan.apply(
        lambda r: 999.0 if r["avg_daily_demand"] <= 0 else (r["net_available_inventory"] + r["recommended_order_qty"]) / r["avg_daily_demand"],
        axis=1,
    )

    plan["expected_holding_cost"] = plan["recommended_order_qty"] * plan["holding_cost"]

    plan["expected_stockout_penalty"] = plan.apply(
        lambda r: max(0.0, r["lead_time_demand"] - r["net_available_inventory"]) * r["stockout_penalty"],
        axis=1,
    )

    plan["expected_total_cost"] = plan["expected_holding_cost"] + plan["expected_stockout_penalty"]

    plan["algorithm_used"] = "Naive Bayes + Rule-Based Planning"

    plan["reason_code"] = np.select(
        [
            plan["recommended_action"] == "EXPEDITE",
            plan["recommended_action"] == "REORDER",
            plan["recommended_action"] == "REVIEW",
        ],
        [
            "HIGH_RISK_LATE_INBOUND",
            "REORDER_TRIGGER",
            "HIGH_CRITICALITY_LOW_RELIABILITY",
        ],
        default="SUFFICIENT_COVERAGE",
    )

    plan["constraint_flags"] = plan.apply(
        lambda r: "; ".join(
            [
                flag
                for flag in [
                    "MOQ_APPLIED" if r["recommended_order_qty"] > 0 else "",
                    "LOW_RELIABILITY_SUPPLIER" if r["supplier_reliability_class"] == "low" else "",
                    "HIGH_CRITICALITY" if str(r["criticality_level"]).lower() == "high" else "",
                    "OPEN_PO_EXISTS" if r["open_purchase_order_qty"] > 0 else "",
                    "OPEN_SO_EXISTS" if r["open_sales_order_qty"] > 0 else "",
                ]
                if flag
            ]
        ),
        axis=1,
    )

    plan["approval_status"] = "Pending"
    plan["review_notes"] = ""
    plan["explanation"] = plan.apply(build_explanation, axis=1)

    plan = plan.reset_index(drop=True)
    plan["plan_id"] = plan.index + 1

    final_cols = [
        "plan_id",
        "plan_date",
        "item_id",
        "item_name",
        "current_on_hand",
        "net_available_inventory",
        "stockout_risk_class",
        "stockout_risk_probability",
        "recommended_action",
        "recommended_order_qty",
        "recommended_order_multiple",
        "expected_arrival_date",
        "projected_days_of_supply",
        "expected_holding_cost",
        "expected_stockout_penalty",
        "expected_total_cost",
        "algorithm_used",
        "reason_code",
        "explanation",
        "constraint_flags",
        "approval_status",
        "review_notes",
    ]

    return plan[final_cols].copy()


# =========================================================
# MAIN
# =========================================================

def main() -> None:
    print("Loading source tables...")
    items_raw, suppliers_raw, inventory_raw, demand_raw, purchase_orders_raw, sales_orders_raw = load_tables()

    print("Cleaning source tables...")
    items = clean_items(items_raw)
    suppliers = clean_suppliers(suppliers_raw)
    inventory = clean_inventory(inventory_raw)
    demand = clean_demand(demand_raw)
    purchase_orders = clean_orders(purchase_orders_raw, "purchase_orders")
    sales_orders = clean_orders(sales_orders_raw, "sales_orders")

    print("Building inventory_features...")
    inventory_features = build_inventory_features(
        items=items,
        suppliers=suppliers,
        inventory=inventory,
        demand=demand,
        sales_orders=sales_orders,
        purchase_orders=purchase_orders,
    )

    print("Building reorder_plan...")
    reorder_plan = build_reorder_plan(inventory_features)

    inventory_features_path = TABLES_DIR / "inventory_features.csv"
    reorder_plan_path = TABLES_DIR / "reorder_plan.csv"

    inventory_features.to_csv(inventory_features_path, index=False)
    reorder_plan.to_csv(reorder_plan_path, index=False)

    print("\nDone.")
    print(f"inventory_features saved to: {inventory_features_path}")
    print(f"reorder_plan saved to:      {reorder_plan_path}")

    print("\nPreview: inventory_features")
    print(inventory_features.head(10).to_string(index=False))

    print("\nPreview: reorder_plan")
    print(reorder_plan.head(10).to_string(index=False))


if __name__ == "__main__":
    main()