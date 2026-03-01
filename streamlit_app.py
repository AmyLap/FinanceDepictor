import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import hashlib
import hmac
import secrets
from scripts.category_functions import CategoryFunctions
from scripts.categories_manager import CategoriesManager
from app_ui.auth import guard_authenticated, render_user_sidebar
from app_ui.data import get_app_data
from app_ui.pages import PAGE_NAMES, PAGE_RENDERERS

# Page configuration
st.set_page_config(
    page_title="Finance Depictor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    guard_authenticated()

    app_data = get_app_data()

    render_user_sidebar()
    page = st.sidebar.radio("Navigation", PAGE_NAMES)

    PAGE_RENDERERS[page](app_data)

    st.sidebar.divider()
    st.sidebar.caption("💰 Finance Depictor - Streamlit Edition")


main()
