import streamlit as st
import mysql.connector
import pandas as pd


# Page config
st.set_page_config(
    page_title="Marketing Campaign Analysis",
    layout="wide"
)


# Load data from MySQL
def load_data():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="MySQL71622!",
        database="marketing_analysis"
    )
    query = "SELECT * FROM marketing_customers"
    ds = pd.read_sql(query, conn)
    conn.close()
    return ds


df = load_data()


# Sidebar Filters
st.sidebar.header("Filters")

country = st.sidebar.multiselect(
    "Country",
    options=sorted(df["Country"].unique()),
    default=[]
)

education = st.sidebar.multiselect(
    "Education",
    options=sorted(df["Education"].unique()),
    default=[]
)

marital_status = st.sidebar.multiselect(
    "Marital Status",
    options=sorted(df["Marital_Status"].unique()),
    default=[]
)

st.sidebar.subheader("Age & Income")

# Age slider
age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
age_range = st.sidebar.slider(
    "Age Range",
    min_value=age_min,
    max_value=age_max,
    value=(age_min, age_max)
)

# Income slider
income_min, income_max = int(df["Income"].min()), int(df["Income"].max())
income_range = st.sidebar.slider(
    "Income Range",
    min_value=income_min,
    max_value=income_max,
    value=(income_min, income_max)
)

# Apply filters
df_filtered = df.copy()

if country:
    df_filtered = df_filtered[df_filtered["Country"].isin(country)]

if education:
    df_filtered = df_filtered[df_filtered["Education"].isin(education)]

if marital_status:
    df_filtered = df_filtered[df_filtered["Marital_Status"].isin(marital_status)]

df_filtered = df_filtered[
    (df_filtered["Age"].between(age_range[0], age_range[1])) &
    (df_filtered["Income"].between(income_range[0], income_range[1]))
]

st.title("Marketing Campaign Analysis Dashboard")
st.markdown(
    "This dashboard helps stakeholders understand **customer segments**, "
    "**campaign effectiveness**, and **spending behavior**."
)


# KPIs
st.subheader("Key Performance Indicators")

total_customers = df_filtered.shape[0]
response_rate = df_filtered["Response"].mean() * 100
avg_income = df_filtered["Income"].mean()
avg_spend = df_filtered["Total_Spend"].mean()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Total Customers", f"{total_customers:,}")
kpi2.metric("Response Rate (%)", f"{response_rate:.2f}")
kpi3.metric("Average Income", f"{avg_income:,.0f}")
kpi4.metric("Average Total Spend", f"{avg_spend:,.0f}")


# Campaign Acceptance rate by Campaign
st.subheader("Campaign Acceptance Rate by Campaign")

campaign_cols = [
    "AcceptedCmp1",
    "AcceptedCmp2",
    "AcceptedCmp3",
    "AcceptedCmp4",
    "AcceptedCmp5"
]

campaign_acceptance = df_filtered[campaign_cols].mean()
st.bar_chart(campaign_acceptance)

# Channel Usage by High-Value Customers

st.subheader("Channel Usage by High-Value Customers")

high_value_df = df_filtered[df_filtered["High_Spender"] == 1]

channel_cols = {
    "Web Purchases": "NumWebPurchases",
    "Store Purchases": "NumStorePurchases",
    "Catalog Purchases": "NumCatalogPurchases",
    "Deal Purchases": "NumDealsPurchases",
    "Web Visits / Month": "NumWebVisitsMonth"
}

channel_usage = pd.Series({
    k: high_value_df[v].mean()
    for k, v in channel_cols.items()
})

st.bar_chart(channel_usage)

# Campaign Response by Segment
st.subheader("Campaign Response Rate by Customer Segment")

segment_cols = [
    "High_Income",
    "Young_Customer",
    "Campaign_Responder",
    "High_Web_Engagement",
    "Family_Customer",
    "High_Spender"
]

segment_response = {
    seg.replace("_", " "): df_filtered[df_filtered[seg] == 1]["Response"].mean()
    for seg in segment_cols
}

segment_df = (
    pd.DataFrame.from_dict(segment_response, orient="index", columns=["Response Rate"])
    .fillna(0)
)

st.bar_chart(segment_df)


# Product Spending Analysis
st.subheader("Average Spend by Product Category")

product_cols = [
    "MntWines",
    "MntFruits",
    "MntMeatProducts",
    "MntFishProducts",
    "MntSweetProducts",
    "MntGoldProds"
]

product_spend = df_filtered[product_cols].mean().sort_values(ascending=False)
st.bar_chart(product_spend)


# Channel Usage Analysis
st.subheader("Average Purchases by Channel")

channel_cols = {
    "Web Purchases": "NumWebPurchases",
    "Store Purchases": "NumStorePurchases",
    "Catalog Purchases": "NumCatalogPurchases",
    "Deal Purchases": "NumDealsPurchases"
}

channel_df = pd.DataFrame({
    k: df_filtered[v].mean()
    for k, v in channel_cols.items()
}, index=["Average"]).T

st.bar_chart(channel_df)


# Under-Served Customer Segment
st.subheader("Under-Served Customer Segment")

underserved = df_filtered[
    (df_filtered["Total_Spend"] < df_filtered["Total_Spend"].quantile(0.25)) &
    (df_filtered["NumWebVisitsMonth"] > df_filtered["NumWebVisitsMonth"].quantile(0.75)) &
    (df_filtered["Response"] == 0)
]

st.metric("Number of Under-Served Customers", underserved.shape[0])

st.markdown(
    "These customers visit the website frequently but have low spending "
    "and low campaign response, indicating potential gaps in targeting or messaging."
)

# Optional: small preview table (nice for evaluators)
st.dataframe(
    underserved[
        ["Age", "Income", "Country", "NumWebVisitsMonth", "Total_Spend"]
    ].head(10)
)


# Key Insights and Patterns

st.subheader("Ideal Target Customer Profile")

st.markdown("""
Based on campaign response and spending behavior, ideal target customers typically:
- Have higher income levels
- Spend more on premium products such as wine and meat
- Engage across multiple purchase channels
- Belong to family households
- Show consistent web engagement
""")
