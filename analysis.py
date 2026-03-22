# ================================================================
#  Sales Performance Analysis | Superstore Dataset (2020–2023)
#  Author  : YOUR NAME   ← Change this
#  Tools   : Python · Pandas · Matplotlib · Seaborn · SQL(SQLite)
# ================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import sqlite3
import warnings
warnings.filterwarnings('ignore')

# ── Style ────────────────────────────────────────────────────
BG   = '#0d0d1a'; PAN  = '#141428'; TXT  = '#e8e8f0'; SUB  = '#9090b0'
ACC  = ['#00d4ff','#ff6b6b','#ffd93d','#6bcb77','#c77dff','#ff9f43']
plt.rcParams.update({'figure.facecolor':BG,'axes.facecolor':PAN,
    'axes.edgecolor':'#2a2a4a','axes.labelcolor':SUB,'axes.titlecolor':TXT,
    'axes.titleweight':'bold','xtick.color':SUB,'ytick.color':SUB,
    'text.color':TXT,'grid.color':'#1e1e38','grid.linestyle':'--',
    'grid.alpha':0.6,'legend.facecolor':PAN,'legend.edgecolor':'#2a2a4a',
    'font.family':'monospace','axes.titlesize':11,'axes.labelsize':9,
    'xtick.labelsize':8,'ytick.labelsize':8})

# ================================================================
#  1. LOAD REAL DATA
# ================================================================
print("="*60)
print("  📊 SUPERSTORE SALES ANALYSIS  |  2020–2023")
print("="*60)
print("\n[1/5] Loading dataset...")

df = pd.read_csv('superstore_sales.csv', parse_dates=['Order Date'])
df.columns = df.columns.str.strip().str.replace(' ','_').str.replace('-','_')
df.rename(columns={'Order_Date':'Date','Sub_Category':'Sub_Cat'}, inplace=True)
df['Year']    = df['Date'].dt.year
df['Month']   = df['Date'].dt.month
df['MonthName'] = df['Date'].dt.strftime('%b')
df['Quarter'] = 'Q' + df['Date'].dt.quarter.astype(str)
df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)
df['Profitable'] = df['Profit'] > 0

print(f"  ✅ Rows: {len(df):,}  |  Columns: {df.shape[1]}")
print(f"  ✅ Period: {df['Date'].min().date()} → {df['Date'].max().date()}")
print(f"  ✅ Regions: {sorted(df['Region'].unique())}")
print(f"  ✅ Categories: {sorted(df['Category'].unique())}")
print(f"  ✅ Segments: {sorted(df['Segment'].unique())}")

# ================================================================
#  2. SQL QUERIES  (5 professional queries)
# ================================================================
print("\n[2/5] Running SQL queries...")

conn = sqlite3.connect(':memory:')
df.to_sql('sales', conn, index=False, if_exists='replace')

# Q1 — Category revenue + profit
q1 = pd.read_sql("""
    SELECT Category,
           ROUND(SUM(Sales),0)         AS Total_Sales,
           ROUND(SUM(Profit),0)        AS Total_Profit,
           ROUND(AVG(Discount)*100,1)  AS Avg_Discount_Pct,
           COUNT(*)                    AS Orders,
           ROUND(100.0*SUM(CASE WHEN Profit>0 THEN 1 ELSE 0 END)/COUNT(*),1) AS Profit_Rate_Pct
    FROM sales GROUP BY Category ORDER BY Total_Sales DESC
""", conn)

# Q2 — Yearly trend
q2 = pd.read_sql("""
    SELECT Year,
           ROUND(SUM(Sales),0)   AS Sales,
           ROUND(SUM(Profit),0)  AS Profit,
           COUNT(*)               AS Orders,
           ROUND(AVG(Discount)*100,1) AS Avg_Discount
    FROM sales GROUP BY Year ORDER BY Year
""", conn)

# Q3 — Region performance
q3 = pd.read_sql("""
    SELECT Region,
           ROUND(SUM(Sales),0)    AS Sales,
           ROUND(SUM(Profit),0)   AS Profit,
           COUNT(DISTINCT City)   AS Cities,
           COUNT(*)               AS Orders
    FROM sales GROUP BY Region ORDER BY Sales DESC
""", conn)

# Q4 — Segment analysis
q4 = pd.read_sql("""
    SELECT Segment,
           ROUND(SUM(Sales),0)                                          AS Sales,
           ROUND(SUM(Profit),0)                                         AS Profit,
           ROUND(100.0*SUM(Profit)/NULLIF(SUM(Sales),0),1)             AS Profit_Margin_Pct
    FROM sales GROUP BY Segment ORDER BY Sales DESC
""", conn)

# Q5 — Top 5 sub-categories by profit
q5 = pd.read_sql("""
    SELECT Sub_Cat,
           ROUND(SUM(Sales),0)   AS Sales,
           ROUND(SUM(Profit),0)  AS Profit,
           COUNT(*)              AS Orders
    FROM sales GROUP BY Sub_Cat ORDER BY Profit DESC LIMIT 5
""", conn)

print("  ✅ 5 SQL queries completed")

# ================================================================
#  3. KPI SUMMARY
# ================================================================
print("\n[3/5] Computing KPIs...")

total_sales   = df['Sales'].sum()
total_profit  = df['Profit'].sum()
profit_margin = total_profit / total_sales * 100
total_orders  = len(df)
avg_order_val = df['Sales'].mean()
profit_rate   = df['Profitable'].mean() * 100
top_cat       = q1.iloc[0]['Category']
top_region    = q3.iloc[0]['Region']
top_segment   = q4.iloc[0]['Segment']
best_year     = q2.loc[q2['Sales'].idxmax(), 'Year']

yoy = q2.set_index('Year')['Sales']
yoy_growth = ((yoy[2023] - yoy[2022]) / yoy[2022] * 100) if 2022 in yoy and 2023 in yoy else 0

print("\n" + "─"*60)
print("  📌 KEY PERFORMANCE INDICATORS")
print("─"*60)
print(f"  💰 Total Sales Revenue  : ${total_sales:>12,.0f}")
print(f"  💵 Total Profit         : ${total_profit:>12,.0f}")
print(f"  📈 Profit Margin        : {profit_margin:>11.1f}%")
print(f"  📦 Total Orders         : {total_orders:>12,}")
print(f"  🛒 Avg Order Value      : ${avg_order_val:>12,.2f}")
print(f"  ✅ Profitable Orders    : {profit_rate:>11.1f}%")
print(f"  🏆 Top Category         : {top_cat}")
print(f"  🌍 Top Region           : {top_region}")
print(f"  👥 Top Segment          : {top_segment}")
print(f"  📅 Best Year            : {best_year}")
print(f"  📊 YoY Growth (23 vs 22): {yoy_growth:>+10.1f}%")
print("─"*60)

print("\n📋 Category Breakdown (SQL):")
print(q1.to_string(index=False))
print("\n📋 Year-over-Year (SQL):")
print(q2.to_string(index=False))
print("\n📋 Region Performance (SQL):")
print(q3.to_string(index=False))

# ================================================================
#  4. DASHBOARD (2 × 3 grid)
# ================================================================
print("\n[4/5] Building 6-panel dashboard...")

fig = plt.figure(figsize=(20, 11), facecolor=BG)
gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.48, wspace=0.38)
axes = [fig.add_subplot(gs[r, c]) for r in range(2) for c in range(3)]

# ── Panel 1: Yearly Sales vs Profit grouped bar ──────────────
ax = axes[0]
x  = np.arange(len(q2))
w  = 0.38
b1 = ax.bar(x - w/2, q2['Sales']/1000,   w, label='Sales',  color=ACC[0], edgecolor='none')
b2 = ax.bar(x + w/2, q2['Profit']/1000,  w, label='Profit', color=ACC[1], edgecolor='none')
ax.set_xticks(x); ax.set_xticklabels(q2['Year'])
ax.set_title('📅 Yearly Sales vs Profit')
ax.set_ylabel('Amount ($000s)')
ax.legend(fontsize=8)
ax.grid(True, axis='y')
for b in list(b1)+list(b2):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.3,
            f'${b.get_height():.0f}K', ha='center', fontsize=7, color=TXT)

# ── Panel 2: Category Sales horizontal bar ───────────────────
ax = axes[1]
bars = ax.barh(q1['Category'], q1['Total_Sales']/1000,
               color=ACC[:3], edgecolor='none', height=0.5)
ax.set_title('🏷️ Sales by Category')
ax.set_xlabel('Sales ($000s)')
ax.invert_yaxis()
for bar, p in zip(bars, q1['Profit_Rate_Pct']):
    ax.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
            f'{p}% profitable', va='center', fontsize=8, color=TXT)

# ── Panel 3: Region donut ─────────────────────────────────────
ax = axes[2]
wedges,texts,auto = ax.pie(
    q3['Sales'], labels=q3['Region'], autopct='%1.1f%%',
    colors=ACC[:4], startangle=90,
    wedgeprops=dict(width=0.55, edgecolor=BG, linewidth=2))
for at in auto: at.set_fontsize(8); at.set_color(BG); at.set_fontweight('bold')
ax.set_title('🌍 Sales by Region')

# ── Panel 4: Segment profit margin bar ───────────────────────
ax = axes[3]
colors4 = [ACC[3] if v > 0 else ACC[1] for v in q4['Profit_Margin_Pct']]
b = ax.bar(q4['Segment'], q4['Profit_Margin_Pct'], color=colors4, width=0.45, edgecolor='none')
ax.axhline(0, color='white', lw=0.8, alpha=0.4)
ax.set_title('👥 Profit Margin by Segment')
ax.set_ylabel('Profit Margin %')
ax.grid(True, axis='y')
for bar, v in zip(b, q4['Profit_Margin_Pct']):
    ax.text(bar.get_x()+bar.get_width()/2,
            bar.get_height() + (0.3 if v>=0 else -1),
            f'{v}%', ha='center', fontsize=9, color=TXT)

# ── Panel 5: Discount vs Profit scatter ──────────────────────
ax = axes[4]
colors5 = [ACC[3] if p > 0 else ACC[1] for p in df['Profit']]
ax.scatter(df['Discount']*100, df['Profit'], c=colors5,
           alpha=0.35, s=12, linewidths=0)
ax.axhline(0, color='white', lw=0.8, alpha=0.5)
ax.set_title('🏷️ Discount % vs Profit')
ax.set_xlabel('Discount %')
ax.set_ylabel('Profit ($)')
ax.grid(True)
# custom legend
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=ACC[3],label='Profitable'),
                   Patch(color=ACC[1],label='Loss')], fontsize=8)

# ── Panel 6: Top 5 Sub-Categories profit bar ─────────────────
ax = axes[5]
clr6 = [ACC[3] if v >= 0 else ACC[1] for v in q5['Profit']]
ax.barh(q5['Sub_Cat'], q5['Profit']/1000, color=clr6, edgecolor='none', height=0.5)
ax.set_title('⭐ Top Sub-Categories by Profit')
ax.set_xlabel('Profit ($000s)')
ax.invert_yaxis()
ax.axvline(0, color='white', lw=0.8, alpha=0.4)
ax.grid(True, axis='x')

# ── Title strip ───────────────────────────────────────────────
fig.text(0.5, 0.98, '📊  Superstore Sales Dashboard  |  2020–2023',
         ha='center', fontsize=17, fontweight='bold', color=TXT, family='monospace')
fig.text(0.5, 0.955,
         f'Revenue: ${total_sales:,.0f}   |   Profit: ${total_profit:,.0f}   '
         f'|   Margin: {profit_margin:.1f}%   |   Orders: {total_orders:,}   |   YoY Growth: {yoy_growth:+.1f}%',
         ha='center', fontsize=9.5, color=SUB, family='monospace')

# ================================================================
#  5. SAVE
# ================================================================
print("[5/5] Saving outputs...")
plt.savefig('sales_dashboard.png', dpi=160, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
print("\n" + "="*60)
print("  ✅ FILES SAVED:")
print("     📊 sales_dashboard.png   ← GitHub upload")
print("     📄 superstore_sales.csv  ← GitHub upload")
print("="*60)
conn.close()
plt.show()
