import pandas as pd
import numpy as np

# 1. Create synthetic (fake) transactions
rng = np.random.default_rng(42)
n = 100_000

df = pd.DataFrame({
    "transaction_id": [f"TX{i:07d}" for i in range(n)],
    "customer_id": "C" + pd.Series(rng.integers(1, 5001, n)).astype(str).str.zfill(5),
    "amount": rng.lognormal(mean=9, sigma=1, size=n).round(2),
    "date": pd.Timestamp("2026-09-14") + pd.to_timedelta(rng.integers(0, 7, n), unit="D"),
})

# 2. Rule 1: high-value transactions
threshold = 100000
flagged = df[df["amount"] > threshold]
print("High-value transactions to review:", len(flagged))

# 3. Rule 2: tiered alerts
df["alert"] = np.select(
    [df["amount"] > threshold, df["amount"] > threshold / 2],
    ["REVIEW", "WATCH"],
    default="OK",
)
print(df["alert"].value_counts())

# 4. Rule 3: possible structuring (many near-limit amounts, same customer, same day)
near = df[(df["amount"] >= 40000) & (df["amount"] <= threshold)]
daily = (near.groupby(["customer_id", "date"])
         .agg(txn_count=("amount", "size"), total=("amount", "sum"))
         .reset_index())
structuring = daily[(daily["txn_count"] >= 3) & (daily["total"] > threshold)]
print("Possible structuring cases:", len(structuring))
