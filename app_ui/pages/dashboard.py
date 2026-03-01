import pandas as pd
import plotly.express as px
import streamlit as st

from app_ui.data import AppData


def render(app_data: AppData) -> None:
    st.title("📊 Financial Dashboard")

    categorised_df = app_data.categorised_df

    col1, col2, col3, col4 = st.columns(4)

    total_transactions = len(categorised_df)
    total_spent = categorised_df["Amount"].sum()
    unique_years = categorised_df["Year"].nunique()
    avg_monthly = total_spent / (unique_years * 12) if unique_years > 0 else 0

    with col1:
        st.metric("Total Transactions", f"{total_transactions:,}")
    with col2:
        st.metric("Total Spent", f"R {total_spent:,.2f}")
    with col3:
        st.metric("Years Tracked", unique_years)
    with col4:
        st.metric("Avg Monthly", f"R {avg_monthly:,.2f}")

    st.divider()

    st.subheader("Spending by Category")
    category_totals = categorised_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(
            x=category_totals.values,
            y=category_totals.index,
            orientation="h",
            labels={"x": "Amount (R)", "y": "Category"},
            title="Total Spending by Category",
        )
        fig.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.dataframe(
            pd.DataFrame({"Category": category_totals.index, "Amount": category_totals.values}).style.format(
                {"Amount": "R {:,.2f}"}
            ),
            hide_index=True,
            height=500,
        )

    st.divider()
    st.subheader("Recent Transactions")
    recent_df = categorised_df.tail(10).sort_values("Date", ascending=False)
    st.dataframe(recent_df[["Date", "Category", "Details", "Amount"]], hide_index=True, use_container_width=True)
