import pandas as pd
import numpy as np

np.random.seed(42)

# -----------------------------
# CONFIG
# -----------------------------

START_DATE = "2023-01-01"
DAYS = 730                     # 2 years
N_SKUS = 5
N_SUPPLIERS = 4
N_WAREHOUSES = 3

# -----------------------------
# MASTER DATA
# -----------------------------

skus = [f"SKU_{i+1}" for i in range(N_SKUS)]
suppliers = [f"SUP_{i+1}" for i in range(N_SUPPLIERS)]
warehouses = [f"WH_{i+1}" for i in range(N_WAREHOUSES)]
regions = ["North", "South", "East", "West"]

supplier_profiles = {
    "SUP_1": {"lead_mean": 5, "lead_std": 1, "failure_prob": 0.02},
    "SUP_2": {"lead_mean": 8, "lead_std": 2, "failure_prob": 0.05},
    "SUP_3": {"lead_mean": 12, "lead_std": 4, "failure_prob": 0.10},
    "SUP_4": {"lead_mean": 15, "lead_std": 5, "failure_prob": 0.15},
}

# -----------------------------
# GENERATION
# -----------------------------

rows = []
dates = pd.date_range(START_DATE, periods=DAYS, freq="D")

for sku in skus:
    base_demand = np.random.randint(20, 60)
    inventory = np.random.randint(500, 900)

    supplier = np.random.choice(suppliers)
    warehouse = np.random.choice(warehouses)
    region = np.random.choice(regions)

    reorder_point = base_demand * 7
    order_qty = base_demand * 10

    for date in dates:

        # Promotion
        promo = np.random.rand() < 0.1

        # Seasonality (weekly + yearly)
        weekly = 5 * np.sin(2 * np.pi * date.dayofweek / 7)
        yearly = 10 * np.sin(2 * np.pi * date.dayofyear / 365)

        demand = (
            base_demand
            + weekly
            + yearly
            + (15 if promo else 0)
            + np.random.normal(0, 5)
        )

        demand = max(0, int(demand))

        # Supplier lead time
        profile = supplier_profiles[supplier]
        lead_time = max(
            1,
            int(np.random.normal(profile["lead_mean"], profile["lead_std"]))
        )

        # Stockout
        stockout = int(inventory <= demand)

        # Inventory update
        inventory -= demand
        inventory = max(0, inventory)

        # Reorder logic
        order_qty_today = 0
        if inventory <= reorder_point and np.random.rand() > profile["failure_prob"]:
            order_qty_today = order_qty
            inventory += order_qty_today

        rows.append([
            date, sku, warehouse, supplier, region,
            demand, inventory, lead_time,
            reorder_point, order_qty_today,
            round(np.random.uniform(5, 25), 2),
            round(np.random.uniform(10, 40), 2),
            int(promo), stockout
        ])

# -----------------------------
# OUTPUT
# -----------------------------

columns = [
    "Date", "SKU_ID", "Warehouse_ID", "Supplier_ID", "Region",
    "Units_Sold", "Inventory_Level", "Supplier_Lead_Time_Days",
    "Reorder_Point", "Order_Quantity",
    "Unit_Cost", "Unit_Price",
    "Promotion_Flag", "Stockout_Flag"
]

df_synth = pd.DataFrame(rows, columns=columns)

df_synth.to_csv("synthetic_erp_data.csv", index=False)

print("Synthetic ERP data generated:")
print(df_synth.shape)
print("Saved as synthetic_erp_data.csv")

# -----------------------------
# Merge with original Kaggle dataset
# -----------------------------

df_real = pd.read_csv("supply_chain_dataset1.csv")
df_real["Date"] = pd.to_datetime(df_real["Date"])

# Align columns (keep only common columns)
common_cols = df_synth.columns.intersection(df_real.columns)

df_combined = pd.concat(
    [
        df_real[common_cols],
        df_synth[common_cols]
    ],
    ignore_index=True
)

# Sort for time-series consistency
df_combined = df_combined.sort_values(["SKU_ID", "Date"])

# -----------------------------
# Export final dataset
# -----------------------------

df_combined.to_csv("synth_dataset1.csv", index=False)

print("Merged dataset created:")
print(df_combined.shape)
print("Saved as synth_dataset1.csv")
