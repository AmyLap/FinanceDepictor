from dataclasses import dataclass

import pandas as pd
import streamlit as st

from scripts.category_functions import CategoryFunctions
from scripts.categories_manager import CategoriesManager


@dataclass
class AppData:
    categorised_df: pd.DataFrame
    cf: CategoryFunctions
    cm: CategoriesManager
    categories_dict: dict
    categories_list: list[str]


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_json("logs\\categorised.json")


@st.cache_resource
def get_category_functions(df: pd.DataFrame) -> CategoryFunctions:
    return CategoryFunctions(df)


@st.cache_resource
def get_categories_manager() -> CategoriesManager:
    return CategoriesManager()


def get_app_data() -> AppData:
    categorised_df = load_data()
    cf = get_category_functions(categorised_df)
    cm = get_categories_manager()
    categories_dict = cm.get_categories()
    categories_list = list(categories_dict.keys())

    return AppData(
        categorised_df=categorised_df,
        cf=cf,
        cm=cm,
        categories_dict=categories_dict,
        categories_list=categories_list,
    )
