"""_summary_
    """
import os
from PDF_Stuff import ReadPDF
from categories_manager import CategoriesManager, CacheManager

import pandas as pd

documents_directory = os.getcwd() + "\\documents"
cm = CategoriesManager()
df = pd.DataFrame()
pdf_read_error = {}


manage_cache = CacheManager()
cache = manage_cache.get_cache()

for file_name in os.listdir(documents_directory):
    document_path = documents_directory + "\\" + file_name
    pdf_reader = ReadPDF(file_name, document_path, cache)
    next_df = pdf_reader.document_to_df()
    cache = pdf_reader.cache
    manage_cache.save_cache()
    if not isinstance(next_df, dict):
        df = pd.concat([df, next_df])
    else:
        pdf_read_error.update(next_df)


manage_cache.save_cache()
print()

df['Amount'] = df["Amount"].apply(lambda x: x.replace("R", "").replace("-", "").replace(" ", "").replace("\xa0", "").replace(",", "").strip() if isinstance(x, str) else x)
df["Amount"] = df["Amount"].apply(lambda x: float(x) if x.replace(".", "").replace(",", "").isnumeric() else x)

categories = cm.get_categories()
uncategorise_keywords = cm.detect_uncategorised_descriptions(list(df["Details"].str.lower().str.strip()))
categorised_df = pd.DataFrame()
for category, key_words in categories.items():
    if key_words:
        filtered_df = df[df['Details'].str.contains('|'.join(key_words), case=False)]
        filtered_df["Category"] = category
        sub_cat_df = pd.DataFrame()
        for key_word in key_words:
            sub_filtered_df = filtered_df[filtered_df['Details'].str.contains(key_word, case=False)]
            sub_filtered_df["Key_Word"] = key_word
            sub_cat_df = pd.concat([sub_cat_df, sub_filtered_df])
        categorised_df = pd.concat([categorised_df, sub_cat_df])
# Category other
filtered_df = df[df['Details'].str.contains('|'.join(uncategorise_keywords), case=False)]
filtered_df["Category"] = "Other"
categorised_df = pd.concat([categorised_df, filtered_df])
print()


categorised_df['Month'] = categorised_df['Date'].str.extract(r'(\b[A-Za-z]{3}\b)')
df_sumed = categorised_df.groupby(['Month', 'Category'])['Amount'].sum().reset_index()

records_dict = categorised_df.to_dict(orient="records")


print()

