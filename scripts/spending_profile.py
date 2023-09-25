"""_summary_
    """
import os
from PDF_Stuff import ReadPDF
from categories_manager import CategoriesManager

import pandas as pd

documents_directory = os.getcwd() + "\\documents"
cm = CategoriesManager()
df = pd.DataFrame()
pdf_read_error = {}
for file_name in os.listdir(documents_directory):
    document_path = documents_directory + "\\" + file_name
    pdf_reader = ReadPDF(document_path, df)
    next_df = pdf_reader.document_to_df()
    if not isinstance(next_df, dict):
        df = pd.concat([df, next_df])
    else:
        pdf_read_error.update(next_df)
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
        categorised_df = pd.concat([categorised_df, filtered_df])

print()

df_sumed = categorised_df.groupby(by='Category')['Amount'].sum()
print()