"""PDF reading utilities.

This module replaces the project-specific `PDFContentConverter` with a
`pdfplumber`-based implementation to extract text and coordinates from
PDF pages and produce the same `transactions` structure used elsewhere.
"""

import pandas as pd
import numpy as np
import pdfplumber
from scripts.utils import UsefulMethods


class ReadPDF:
    """Read bank statement PDFs and convert to tabular transactions.

    The rest of the class (parsing FNB/Discovery formats) is kept intact;
    only `read_pdf_coords_and_sort` is implemented using `pdfplumber`.
    """

    def __init__(self, file_name, file_path):
        self.file_name = file_name
        self.file_path = file_path
        self.table_list = []
        self.dataframe = pd.DataFrame({"Transaction Date": [], "Transaction Type": [], "Amount": []})
        self.um = UsefulMethods()
        self.transactions = self.read_pdf_coords_and_sort()
        self.year = self.get_year(self.transactions)
        self.month = self.get_month(self.transactions)

    def read_pdf_coords_and_sort(self):
        """Extract words with coordinates and group into lines.

        Returns a list where each item is a list of text tokens found on a
        single visual line (grouped by rounded y coordinate and page).
        """
        words = []
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    # extract_words returns dicts with keys: text, x0, x1, top, bottom
                    page_words = page.extract_words()
                    for w in page_words:
                        words.append({
                            "text": w.get("text", ""),
                            "x_0": float(w.get("x0", 0.0)),
                            "y_0": float(w.get("top", 0.0)),
                            "page": page_num,
                        })
        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF with pdfplumber: {e}")

        if not words:
            return []

        df = pd.DataFrame(words)
        # Round / ceil y coordinate to group tokens that are visually on the same line
        df["y_0"] = np.ceil(df["y_0"]).astype(int)
        sorted_df = df.sort_values(by=["page", "y_0", "x_0"])  # order by page, then row

        transactions = []
        grouped_by_page = sorted_df.groupby("page")

        for page_group in grouped_by_page.groups.keys():
            grouped_by_y_axis = grouped_by_page.get_group(page_group).groupby("y_0")
            for group_key in sorted(grouped_by_y_axis.groups.keys(), reverse=False):
                group = grouped_by_y_axis.get_group(group_key)
                tokens = list(group.sort_values("x_0")["text"])
                if tokens:
                    transactions.append(tokens)

        return transactions

    def data_to_df(self, transactions):
        """_summary_.

        :return: _description_
        :rtype: _type_
        """
        # if "Private.txt" in self.file_path:
        #     df = self.txt_private_to_df()
        # elif "Fusion.txt" in self.file_path:
        #     df = self.txt_fusion_to_df()
        try:

            df = pd.DataFrame(
                transactions,
                columns=["Year", "Month", "Date", "Details", "Amount"],
            )
            return df
        except Exception as e:
            raise

    def get_year(self, transactions):
        year = "unknown"
        for i in transactions:
            if i and ("statement date" in " ".join(i).lower()):
                year = i[5]
                if year.isnumeric():
                    return year
            elif (
                isinstance(i, list)
                and len(i) == 1
                and "statement date :" in " ".join(i).lower()
            ):
                year = i[0].strip().split(" ")[-1]

                if year.isnumeric() and int(year) >= 2000:
                    return year
        return year

    def get_month(self, transactions):
        month = "unknown"
        month_list = [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ]
        for i in transactions:
            if i and ("statement date" in " ".join(i).lower()):
                month = i[4]
                if isinstance(month, str) and month.lower() in month_list:
                    return month
            elif (
                isinstance(i, list)
                and len(i) == 1
                and "statement date :" in " ".join(i).lower()
            ):
                month = i[0].strip().split(" ")[-2]
                if isinstance(month, str) and month.lower() in month_list:
                    return month
        return month

class FNBReadPDF(ReadPDF):
    def __init__(self, file_name, file_path):
        super().__init__(file_name, file_path)

    def clean_data_to_df(self) -> pd.DataFrame:
        """_summary_."""

        str_of_list = str(self.transactions)
        credit_account = (
            False
            if "FNB PRIVATE WEALTH CREDIT CARD 4483 8100 6210 6000 "
            not in str_of_list
            else True
        )

        transactions = [
            line
            for line in self.transactions
            if len(line) > 2 and
            self.um.is_valid_date(f"{line[0].strip()} {line[1].strip()}", "%d %b")
        ]

        # create a list of transactions with format: Year, Month, Date, Details, Amount
        if credit_account:
            transactions = [
                [self.year, line[1].split()[0:3], line[0], line[2], line[1], line[:-2]]
                if len(line) == 5
                else [self.year, line[0].split(" ")[1][0:3], line[0], line[2], line[1], line[3]]
                for line in transactions
            ]
        else:
            transactions = [
                [self.year, line[1].strip(" ")[0:3], f"{line[0]} {line[1]} {self.year}", " ".join(line[3:-2]), line[-2]]
                
                for line in transactions if len(line) >= 4
            ]
        transactions = [line for line in transactions if "cr" not in line[4].lower()]

        return_df = self.data_to_df(transactions)
        return return_df

class DiscoveryReadPDF(ReadPDF):
    def __init__(self, file_name, file_path):
        super().__init__(file_name, file_path)

    def clean_data_to_df(self) -> pd.DataFrame:
        """_summary_.

        :return: _description_
        :rtype: _type_
        """

        # FIX MISSING DESCRIPTIONS
        for index, lines in enumerate(self.transactions):
            if index + 1 != len(self.transactions):
                next_line = self.transactions[index + 1]
                if all(
                    [len(lines) == 1, "Inter account" in lines[0], len(next_line) == 3]
                ):
                    self.transactions[index + 1] = [
                        next_line[0],
                        next_line[1],
                        lines[0],
                        next_line[2],
                    ]

        transactions = [
            line
            for line in self.transactions
            if self.um.is_valid_date(line[0].strip(), "%d %b %Y")
            and 4 <= len(line) <= 5
        ]
        transactions = [
            [self.year, line[0].split(" ")[1][0:3], line[0], line[1], line[2], line[3]]
            if len(line) == 4
            else [self.year, line[0].split(" ")[1][0:3], line[0], line[2], line[3], line[4]]
            for line in transactions
        ]

        return_df = self.data_to_df(transactions)
        return return_df

