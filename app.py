import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Analytics AI", page_icon="📊", layout="wide")
st.title("📊 Sales Data Analytics Dashboard")
st.caption("Upload a sales dataset, explore business metrics, charts, and ask questions.")

uploaded_file = st.sidebar.file_uploader("Upload sales dataset", type=["csv", "xlsx"])
if uploaded_file is None:
    st.info("Upload a CSV or Excel file to begin. You can use the included sales_data.csv.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.lower().endswith(".csv") else pd.read_excel(uploaded_file)
except Exception as exc:
    st.error(f"Could not read the file: {exc}")
    st.stop()

if df.empty:
    st.error("The uploaded dataset is empty.")
    st.stop()

df.columns = [str(c).strip() for c in df.columns]
st.sidebar.header("Map your columns")

def select_column(label, suggestions, required=False):
    options = ["— Not available —"] + list(df.columns)
    selected_index = 0
    lowered = {str(c).strip().lower(): i + 1 for i, c in enumerate(df.columns)}
    for suggestion in suggestions:
        if suggestion in lowered:
            selected_index = lowered[suggestion]
            break
    choice = st.sidebar.selectbox(label, options, index=selected_index)
    if required and choice == "— Not available —":
        st.sidebar.warning(f"Select a {label.lower()}.")
    return None if choice == "— Not available —" else choice

sales_col = select_column("Sales / Revenue column", ["sales", "revenue", "amount", "total sales"], True)
date_col = select_column("Order date column", ["order date", "date", "order_date"])
product_col = select_column("Product column", ["product", "product name", "item"])
region_col = select_column("Region column", ["region", "state", "location", "area"])
category_col = select_column("Category column", ["category", "product category"])
quantity_col = select_column("Quantity column", ["quantity", "qty", "units sold"])
order_col = select_column("Order ID column", ["order id", "order_id", "order number"])

if sales_col is None:
    st.warning("Choose the column containing sales/revenue to continue.")
    st.stop()

data = df.copy()
sales_text = data[sales_col].astype(str).str.replace(",", "", regex=False).str.replace("$", "", regex=False).str.replace("₹", "", regex=False)
data[sales_col] = pd.to_numeric(sales_text, errors="coerce")
data = data.dropna(subset=[sales_col]).copy()
if data.empty:
    st.error("No numeric sales values were found in the selected column.")
    st.stop()

if date_col:
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
if quantity_col:
    data[quantity_col] = pd.to_numeric(data[quantity_col], errors="coerce").fillna(0)

total_revenue = float(data[sales_col].sum())
total_orders = int(data[order_col].nunique()) if order_col else int(len(data))
total_quantity = float(data[quantity_col].sum()) if quantity_col else None
average_order_value = total_revenue / total_orders if total_orders else 0

st.header("Business performance")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total revenue", f"{total_revenue:,.2f}")
k2.metric("Total orders", f"{total_orders:,}")
k3.metric("Quantity sold", f"{total_quantity:,.0f}" if total_quantity is not None else "Not available")
k4.metric("Average order value", f"{average_order_value:,.2f}")

st.divider()
st.header("Sales charts")
chart_count = 0

if date_col:
    dated = data.dropna(subset=[date_col]).copy()
    if not dated.empty:
        dated["Month"] = dated[date_col].dt.to_period("M").astype(str)
        monthly = dated.groupby("Month", as_index=False)[sales_col].sum()
        st.plotly_chart(px.line(monthly, x="Month", y=sales_col, markers=True, title="Monthly sales trend"), use_container_width=True)
        chart_count += 1

if product_col:
    products = data.groupby(product_col, as_index=False)[sales_col].sum().sort_values(sales_col, ascending=False).head(10)
    st.plotly_chart(px.bar(products, x=product_col, y=sales_col, title="Top 10 products by revenue"), use_container_width=True)
    chart_count += 1

if region_col:
    regions = data.groupby(region_col, as_index=False)[sales_col].sum()
    st.plotly_chart(px.pie(regions, names=region_col, values=sales_col, title="Revenue by region"), use_container_width=True)
    chart_count += 1

if category_col:
    categories = data.groupby(category_col, as_index=False)[sales_col].sum().sort_values(sales_col, ascending=False)
    st.plotly_chart(px.bar(categories, x=category_col, y=sales_col, title="Revenue by category"), use_container_width=True)
    chart_count += 1

if chart_count == 0:
    st.info("Select date, product, region, or category columns in the sidebar to display charts.")

st.divider()
st.header("🤖 Ask questions about your sales data")
st.caption("This starter version answers common questions using built-in rules; it does not call a generative AI service.")
question = st.text_input("Ask a question", placeholder="Which product has the highest sales?")

def answer_question(q):
    q = q.lower().strip()
    if any(term in q for term in ["total revenue", "total sales", "overall sales"]):
        return f"Total revenue is {total_revenue:,.2f}."
    if "order" in q and any(term in q for term in ["how many", "total", "number"]):
        return f"Total orders are {total_orders:,}."
    if any(term in q for term in ["average order", "average sales", "average revenue"]):
        return f"Average order value is {average_order_value:,.2f}."
    if quantity_col and any(term in q for term in ["quantity", "units sold"]):
        return f"Total quantity sold is {total_quantity:,.0f}."
    if product_col and "product" in q:
        grouped = data.groupby(product_col)[sales_col].sum()
        if grouped.empty:
            return "There is no product data to analyze."
        if any(term in q for term in ["lowest", "least", "worst"]):
            name, value = grouped.idxmin(), grouped.min()
            return f"Lowest-revenue product: {name} ({value:,.2f})."
        if any(term in q for term in ["highest", "top", "best", "most"]):
            name, value = grouped.idxmax(), grouped.max()
            return f"Top product: {name} ({value:,.2f})."
        return "Try asking which product has the highest or lowest sales."
    if region_col and "region" in q:
        grouped = data.groupby(region_col)[sales_col].sum()
        if grouped.empty:
            return "There is no region data to analyze."
        if any(term in q for term in ["lowest", "least"]):
            return f"Lowest-revenue region: {grouped.idxmin()} ({grouped.min():,.2f})."
        if any(term in q for term in ["highest", "top", "best", "most"]):
            return f"Top region: {grouped.idxmax()} ({grouped.max():,.2f})."
        return grouped.sort_values(ascending=False).to_string()
    if date_col and "month" in q:
        dated = data.dropna(subset=[date_col]).copy()
        if dated.empty:
            return "No valid dates were found."
        dated["Month"] = dated[date_col].dt.to_period("M").astype(str)
        grouped = dated.groupby("Month")[sales_col].sum()
        if any(term in q for term in ["highest", "top", "best", "most"]):
            return f"Best month: {grouped.idxmax()} ({grouped.max():,.2f})."
        return grouped.sort_values(ascending=False).to_string()
    if category_col and "categor" in q:
        grouped = data.groupby(category_col)[sales_col].sum()
        return f"Top category: {grouped.idxmax()} ({grouped.max():,.2f})."
    return "I couldn't match that question. Try asking about total revenue, orders, quantity, top product, top region, category, or best month."

if question:
    st.success(answer_question(question))

st.divider()
st.header("Uploaded data")
st.write(f"Showing {len(data):,} valid rows and {len(data.columns):,} columns.")
st.dataframe(data, use_container_width=True)
st.download_button("Download cleaned dataset", data=data.to_csv(index=False).encode("utf-8"), file_name="cleaned_sales_data.csv", mime="text/csv")
