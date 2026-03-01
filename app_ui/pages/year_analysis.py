import pandas as pd
import plotly.express as px
import streamlit as st

from app_ui.data import AppData


def render(app_data: AppData) -> None:
    st.title("📈 Year Analysis")

    unique_years = sorted(app_data.categorised_df["Year"].unique())
    selected_year = st.selectbox("Select Year", unique_years, index=len(unique_years) - 1 if unique_years else 0)

    if not selected_year:
        return

    year_dict = app_data.cf.year(str(selected_year))
    if not year_dict:
        st.warning(f"No data available for {selected_year}")
        return

    year_df = app_data.categorised_df[app_data.categorised_df["Year"] == selected_year]
    total_spent = year_df["Amount"].sum()
    num_transactions = len(year_df)
    avg_transaction = total_spent / num_transactions if num_transactions > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Spent", f"R {total_spent:,.2f}")
    with col2:
        st.metric("Transactions", f"{num_transactions:,}")
    with col3:
        st.metric("Avg Transaction", f"R {avg_transaction:,.2f}")

    st.divider()

    labels = list(year_dict.keys())
    values = list(year_dict.values())

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Category Distribution")
        fig = px.pie(values=values, names=labels, title=f"Spending Distribution - {selected_year}")
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Category Breakdown")
        fig = px.bar(x=values, y=labels, orientation="h", labels={"x": "Amount (R)", "y": "Category"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Category Details")
    detail_df = pd.DataFrame(
        {
            "Category": labels,
            "Amount": values,
            "Percentage": [value / total_spent * 100 for value in values],
        }
    ).sort_values("Amount", ascending=False)

    st.dataframe(
        detail_df.style.format({"Amount": "R {:,.2f}", "Percentage": "{:.1f}%"}),
        hide_index=True,
        use_container_width=True,
    )

    st.divider()
    st.subheader("Category Comparison")
    selected_category = st.selectbox("Select category to compare", app_data.categories_list)

    if not selected_category:
        return

    result_dict = app_data.cf.year_category(str(selected_year), selected_category)
    if not result_dict:
        return

    labels = list(result_dict.keys())
    values = list(result_dict.values())

    fig = px.bar(
        x=labels,
        y=values,
        title=f"{selected_category} - {selected_year}",
        labels={"x": "Subcategory", "y": "Amount (R)"},
    )
    st.plotly_chart(fig, use_container_width=True)
