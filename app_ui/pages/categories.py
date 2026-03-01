import pandas as pd
import plotly.express as px
import streamlit as st

from app_ui.data import AppData


def render(app_data: AppData) -> None:
    st.title("🏷️ Categories")

    selected_category = st.selectbox("Select Category", app_data.categories_list)

    if selected_category:
        st.subheader(f"Analysis: {selected_category}")
        result_dict = app_data.cf.subcategory(selected_category)

        if result_dict:
            labels = list(result_dict.keys())
            values = list(result_dict.values())

            col1, col2 = st.columns([2, 1])

            with col1:
                fig = px.pie(values=values, names=labels, title=f"{selected_category} Breakdown")
                fig.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.dataframe(
                    pd.DataFrame({"Subcategory": labels, "Amount": values})
                    .sort_values("Amount", ascending=False)
                    .style.format({"Amount": "R {:,.2f}"}),
                    hide_index=True,
                    height=400,
                )

            st.subheader("Recent Transactions")
            category_transactions = app_data.categorised_df[app_data.categorised_df["Category"] == selected_category].tail(20)
            st.dataframe(
                category_transactions[["Date", "Details", "Amount"]].sort_values("Date", ascending=False),
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No data available for this category")

    st.divider()
    st.subheader("📝 Category Management")

    with st.expander("View All Categories"):
        for category, subcategories in app_data.categories_dict.items():
            st.write(f"**{category}**")
            if subcategories:
                for subcategory in subcategories:
                    st.write(f"  • {subcategory}")
            st.write("")
