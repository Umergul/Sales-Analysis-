"""
Sales Analysis — Sample Superstore dataset.
Dataset: "Superstore Dataset" by Vivek Chowdhury (Kaggle)
         https://www.kaggle.com/datasets/vivek468/superstore-dataset-final

Runs the full analysis end to end:
  1. data loading + cleaning (missing values, date parsing)
  2. KPIs: total sales, profit, profit margin — overall + year-wise
  3. sales breakdown by Category / Region / Segment
  4. monthly sales trend (line chart)
  5. top 10 most profitable + top 10 most loss-making products
  6. printed insights — every number comes from the dataset itself
Charts are saved under charts/.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "sample_superstore.csv")
CHARTS = os.path.join(BASE, "charts")
os.makedirs(CHARTS, exist_ok=True)

# ---------------------------------------------------------------- 1. load
df = pd.read_csv(DATA, encoding="latin1")
print(f"rows x cols (raw): {df.shape}")

# ---------------------------------------------------------------- 2. clean
missing = df.isna().sum()
print("\nmissing values per column (only columns with >0 shown):")
print(missing[missing > 0] if (missing > 0).any() else "none")

df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")
df["Year"] = df["Order Date"].dt.year
df["YearMonth"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()

# drop exact duplicate rows if any
dupes = df.duplicated().sum()
df = df.drop_duplicates()
print(f"duplicate rows removed: {dupes}")
print(f"rows x cols (clean): {df.shape}")

# ------------------------------------------------- 3. KPIs overall + yearly
def kpis(frame):
    sales = frame["Sales"].sum()
    profit = frame["Profit"].sum()
    return sales, profit, (profit / sales * 100 if sales else 0)

sales, profit, margin = kpis(df)
print(f"\nOVERALL  sales=${sales:,.2f}  profit=${profit:,.2f}  margin={margin:.2f}%")

print("\nYEAR-WISE")
yearly = df.groupby("Year").agg(sales=("Sales", "sum"), profit=("Profit", "sum"))
yearly["margin_pct"] = yearly["profit"] / yearly["sales"] * 100
print(yearly.round(2).to_string())

# ------------------------------------------------- 4. breakdowns
print("\nBY CATEGORY")
cat = df.groupby("Category").agg(sales=("Sales", "sum"), profit=("Profit", "sum"))
cat["margin_pct"] = cat["profit"] / cat["sales"] * 100
print(cat.round(2).to_string())

print("\nBY REGION")
reg = df.groupby("Region").agg(sales=("Sales", "sum"), profit=("Profit", "sum"))
reg["margin_pct"] = reg["profit"] / reg["sales"] * 100
print(reg.round(2).to_string())

print("\nBY SEGMENT")
seg = df.groupby("Segment").agg(sales=("Sales", "sum"), profit=("Profit", "sum"))
seg["margin_pct"] = seg["profit"] / seg["sales"] * 100
print(seg.round(2).to_string())

# ------------------------------------------------- 5. monthly trend chart
monthly = df.groupby("YearMonth")["Sales"].sum()
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly.index, monthly.values, marker="o", linewidth=2)
ax.set_title("Monthly Sales Trend — Sample Superstore")
ax.set_xlabel("Month")
ax.set_ylabel("Sales (USD)")
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "monthly_sales_trend.png"), dpi=120)
plt.close(fig)
peak_month = monthly.idxmax().strftime("%b %Y")
print(f"\npeak sales month: {peak_month} (${monthly.max():,.2f})")

# ------------------------------------------------- 6. category profit chart
fig, ax = plt.subplots(figsize=(8, 4.5))
colors = ["#2ca02c" if v >= 0 else "#d62728" for v in cat["profit"]]
ax.bar(cat.index, cat["profit"], color=colors)
ax.set_title("Profit by Category")
ax.set_ylabel("Profit (USD)")
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "profit_by_category.png"), dpi=120)
plt.close(fig)

# ------------------------------------------------- 7. region sales chart
fig, ax = plt.subplots(figsize=(8, 4.5))
reg_sorted = reg.sort_values("sales")
ax.barh(reg_sorted.index, reg_sorted["sales"], color="#1f77b4")
ax.set_title("Sales by Region")
ax.set_xlabel("Sales (USD)")
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "sales_by_region.png"), dpi=120)
plt.close(fig)

# ------------------------------------------------- 8. top / bottom products
prod = df.groupby("Product Name").agg(
    sales=("Sales", "sum"), profit=("Profit", "sum"), orders=("Order ID", "nunique")
).sort_values("profit", ascending=False)

top10 = prod.head(10)
bot10 = prod.tail(10).sort_values("profit")

print("\nTOP 10 MOST PROFITABLE PRODUCTS")
print(top10.round(2).to_string())
print("\nTOP 10 MOST LOSS-MAKING PRODUCTS")
print(bot10.round(2).to_string())

# ------------------------------------------------- 9. insights (from data)
loss_orders = (df.groupby("Order ID")["Profit"].sum() < 0).sum()
total_orders = df["Order ID"].nunique()
discount_corr = df["Discount"].corr(df["Profit"])
best_cat = cat["profit"].idxmax()
worst_cat_margin = cat["margin_pct"].idxmin()
best_region = reg["sales"].idxmax()
top_seg = seg["sales"].idxmax()

print("\n================ INSIGHTS (all numbers computed from the dataset) ================")
print(f"1. Overall the store made ${sales:,.0f} in sales with ${profit:,.0f} profit "
      f"({margin:.1f}% margin) across {total_orders:,} orders.")
print(f"2. {best_cat} is the most profitable category (${cat.loc[best_cat, 'profit']:,.0f} profit), "
      f"while {worst_cat_margin} has the weakest margin ({cat.loc[worst_cat_margin, 'margin_pct']:.1f}%).")
print(f"3. {best_region} leads regional sales at ${reg.loc[best_region, 'sales']:,.0f}; "
      f"the {top_seg} segment drives the most sales (${seg.loc[top_seg, 'sales']:,.0f}).")
print(f"4. {loss_orders:,} of {total_orders:,} orders ({loss_orders/total_orders*100:.1f}%) were loss-making "
      f"in total — discounting pressure is visible (discount-profit correlation: {discount_corr:.2f}).")
print(f"5. The single best month was {peak_month} at ${monthly.max():,.0f} sales; "
      f"the best product earned ${top10['profit'].iloc[0]:,.0f} while the worst lost -${abs(bot10['profit'].iloc[0]):,.0f}.")
print("=================================================================================")
print("\ncharts saved to charts/: monthly_sales_trend.png, profit_by_category.png, sales_by_region.png")
