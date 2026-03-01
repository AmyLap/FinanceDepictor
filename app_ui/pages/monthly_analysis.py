import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app_ui.data import AppData


def render(app_data: AppData) -> None:
    st.title("📅 Monthly Analysis")

    categorised_df = app_data.categorised_df

    df_summed = categorised_df.groupby(["Year", "Month", "Category"])["Amount"].sum().reset_index()
    unique_years = sorted(df_summed["Year"].unique())

    selected_year = st.selectbox("Select Year", unique_years, index=len(unique_years) - 1 if unique_years else 0)
    year_df = df_summed[df_summed["Year"] == selected_year]

    if year_df.empty:
        st.warning(f"No data available for {selected_year}")
        return

    pivot_df = year_df.pivot(index="Category", columns="Month", values="Amount").fillna(0)

    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    available_months = [month for month in month_order if month in pivot_df.columns]
    pivot_df = pivot_df[available_months]

    fig = go.Figure()

    for category in pivot_df.index:
        fig.add_trace(
            go.Bar(
                name=category,
                x=available_months,
                y=pivot_df.loc[category],
                text=[f"R {value:,.0f}" if value > 0 else "" for value in pivot_df.loc[category]],
                textposition="inside",
            )
        )

    fig.update_layout(
        barmode="stack",
        title=f"Monthly Spending by Category - {selected_year}",
        xaxis_title="Month",
        yaxis_title="Amount (R)",
        height=600,
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Totals")
    monthly_totals = pivot_df.sum(axis=0)
    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(
            pd.DataFrame({"Month": monthly_totals.index, "Total": monthly_totals.values}).style.format(
                {"Total": "R {:,.2f}"}
            ),
            hide_index=True,
            use_container_width=True,
        )

    with col2:
        category_yearly = year_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        st.dataframe(
            pd.DataFrame({"Category": category_yearly.index, "Total": category_yearly.values}).style.format(
                {"Total": "R {:,.2f}"}
            ),
            hide_index=True,
            use_container_width=True,
        )
