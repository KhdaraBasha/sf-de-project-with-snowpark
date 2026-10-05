# Import python packages
import streamlit as st
import os
import pandas as pd
import altair as alt

from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import (
        col, sum as sf_sum, countDistinct
)

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title = "Customer 360 Order Analytics",
    page_icon = "❄️",
    layout="wide"
)

# 2. GET ACTIVE SESSION LIKE ROLE(), WH, DB ect.
session = get_active_session()

# 3. DASHBOARD TITLE
st.title("❄️ Customer 360 Order Analytics- CLOUDLEARNINGYARD")

st.markdown(
    "**Gold Layer Analytics Dashboards** \n"
    "Built Using **Snowpark + Notebok + Streamlit**"
)

st.divider()

# 4. LOAD GOLD LAYER TABLES --> This part you can replace by creating view and join your DIM and FACT table

fact = session.table(
            "YOUTUBEDEMO.GOLD.FACT_ORDERS"
)

dim_customer = session.table(
            "YOUTUBEDEMO.GOLD.DIM_CUSTOMER"
)

dim_date = session.table(
            "YOUTUBEDEMO.GOLD.DIM_DATE"
)

# 5. JOIN FACT WITH DIM_DATE DIMESION  -- You can create view also to use this

fact_full = (
    fact
    .join(
        dim_date,
        fact["ORDER_DATE_KEY"] == dim_date["DATE_KEY"],
        how="left"
    )
)

# 6. SIDEBAR FILETERS
st.sidebar.title("⧩ Dashboard Filteers")
st.sidebar.markdown("Use the filters below to explore the data.")

# YEAR FILTER
years = [
    r["YEAR_NUMBER"]
    for r in (
        dim_date
        .select("YEAR_NUMBER")
        .distinct()
        .sort("YEAR_NUMBER")
        .collect()
    )
]

selected_years = st.sidebar.multiselect(
    "📅 Order Year",
    years,
    default = years
)

# REGION FILTER
regions = [
    r['REGION_NAME']
    for r in (
        fact
        .select("REGION_NAME")
        .distinct()
        .sort("REGION_NAME")
        .collect()
    )
    if r["REGION_NAME"] is not None
]

selected_regions = st.sidebar.multiselect(
    "🌐 Region",
    regions,
    default=regions
)

# If you want to select only single value then in line 104 use selectbox

# 7. APPLY FILETERS

filtered = fact_full

if selected_years:
    filtered = filtered.filter(
            col("YEAR_NUMBER").isin(selected_years)
    )
    

if selected_regions:
    filtered = filtered.filter(
            col("REGION_NAME").isin(selected_regions)
    )

# 8. FILTER INFORMATION
st.info(
    f"🔍 Showing data for"
    f"**{len(selected_years)} year(s)** across "
    f"**{len(selected_regions)} region(s)**"
)

# KPI CALCULATIONS -- SCORECARDS

kpi_row = (
    filtered
    .agg(
        sf_sum("NET_REVENUE").alias("TOTAL_REVENUE"),
        
        countDistinct("ORDER_KEY").alias("TOTAL_ORDERS"),

        countDistinct("CUSTOMER_KEY").alias("TOTAL_CUSTOMERS"),

        sf_sum("QUANTITY").alias("TOTAL_QUANTITY")
    )
    .collect()[0]
)

# KPI VALUES

total_revenue = float(kpi_row["TOTAL_REVENUE"] or 0)

total_orders = int(kpi_row["TOTAL_ORDERS"] or 0)

total_customers = int(kpi_row["TOTAL_CUSTOMERS"] or 0)

total_quantity = float(kpi_row["TOTAL_QUANTITY"] or 0)

# AVG ORDER VALUE

avg_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0
        )

# 10. KPI CARDS
st.subheader("📊 Business Overview")

st.caption("key performance indicator for the selected data.")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:

    st.metric(
        label = "💰 Total Revenue",
        value = f"${total_revenue:,.2f}"
    )

with c2:
    st.metric(
        label = "🛒 Total Orders",
        value = f"${total_orders:,}"
    )

with c3:
    st.metric(
        label = "👥 Total Customers",
        value = f"${total_customers:,}"
    )

with c4:
    st.metric(
        label = "📦 Total Order Quantity",
        value = f"${total_quantity:,}"
    )

with c5:
    st.metric(
        label = "🧾 Avg Order Value",
        value = f"${avg_order_value:,.2f}"
    )

#   ===============================================================
#   11. TOTAL QUANTITY
#   ===============================================================

st.caption(
    f"📦 Total Quantity Sold: **{total_quantity:,.0f}**"
)

# st.divider()

#   ===============================================================
#   12. REVENUE TREND
#   ===============================================================
st.subheader("📈 Revenue Trend Over Time")
st.caption("Monthly revenue across the selected year!.")

trend_df = (
    filtered
    .group_by(
        "YEAR_NUMBER",
        "MONTH_NUMBER",
        "MONTH_NAME"
    )
    .agg(
        sf_sum("NET_REVENUE")
        .alias("REVENUE")
    )
    .sort(
        "YEAR_NUMBER",
        "MONTH_NUMBER"
    )
    .to_pandas()
)

#   ===============================================================
#   13. CREATE PERIOD COLUMN
#   ===============================================================


# # Write directly to the app
# st.title(f"Example Streamlit App :balloon: {st.__version__}")
# st.write(
#   """Replace this example with your own code!
#   **And if you're new to Streamlit,** check
#   out our easy-to-follow guides at
#   [docs.streamlit.io](https://docs.streamlit.io).
#   """
# )

# st.markdown("""
# - :page_with_curl: [Streamlit open source documentation](https://docs.streamlit.io)
# - :snowflake: [Streamlit in Snowflake documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
# - :books: [Demo repo with templates](https://github.com/Snowflake-Labs/snowflake-demo-streamlit)
# - :memo: [Streamlit in Snowflake release notes](https://docs.snowflake.com/en/release-notes/streamlit-in-snowflake)
# """)

# # Create a database connection to Snowflake
# conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))
# session = conn.session()

# # Use an interactive slider to get user input
# hifives_val = st.slider(
#   "Number of high-fives in Q3",
#   min_value=0,
#   max_value=90,
#   value=60,
#   help="Use this to enter the number of high-fives you gave in Q3",
# )

# #  Create an example dataframe
# #  Note: this is just some dummy data, but you can easily connect to your Snowflake data
# #  It is also possible to query data using raw SQL using session.sql() e.g. session.sql("select * from table")
# created_dataframe = session.create_dataframe(
#   [[50, 25, "Q1"], [20, 35, "Q2"], [hifives_val, 30, "Q3"]],
#   schema=["HIGH_FIVES", "FIST_BUMPS", "QUARTER"],
# )

# # Execute the query and convert it into a Pandas dataframe
# queried_data = created_dataframe.to_pandas()

# # Create a simple bar chart
# # See docs.streamlit.io for more types of charts
# st.subheader("Number of high-fives")
# st.bar_chart(data=queried_data, x="QUARTER", y="HIGH_FIVES")

# st.subheader("Underlying data")
# st.dataframe(queried_data, use_container_width=True)
