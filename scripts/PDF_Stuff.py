"""_summary_."""

import pandas as pd
import numpy as np
from PDFContentConverter import PDFContentConverter
from use_things import UsefulMethods


class ReadPDF:
    """_summary_"""

    def __init__(self, file_name, file_path, cache):
        """_summary_

        :param file_path: _description_
        :type file_path: _type_
        :param dataframe: _description_
        :type dataframe: _type_
        """
        self.file_name = file_name
        self.file_path = file_path
        self.table_list = []
        self.dataframe = pd.DataFrame(
            {"Transaction Date": [], "Transaction Type": [], "Amount": []}
        )
        self.um = UsefulMethods()
        self.cache = cache

    def read_pdf_coords_and_sort(self):
        # convert PDF
        converter = PDFContentConverter(self.file_path)
        df = converter.pdf2pandas()  # equivalent to result["content"]
        sorted_df = df.sort_values(by=["y_0", "x_0", "page"])
        sorted_df["y_0"] = np.ceil(df["y_0"])
        list_of_lines = []
        grouped_by_page = sorted_df.groupby("page")

        for page_group in grouped_by_page.groups.keys():
            grouped_by_y_axis = grouped_by_page.get_group(page_group).groupby("y_0")
            for group in grouped_by_y_axis.groups.keys():
                list_of_lines.append(list(grouped_by_y_axis.get_group(group)["text"]))
        return list_of_lines

    def fnb_to_df(self, list_of_lines):
        """_summary_."""

        flattened_list = [item for sublist in list_of_lines for item in sublist]
        credit_account = (
            False
            if "FNB PRIVATE WEALTH CREDIT CARD 4483 8100 6210 6000 "
            not in flattened_list
            else True
        )

        transactions = [
            line
            for line in list_of_lines
            if self.um.is_valid_date(line[0].strip(), "%d %b") and 4 <= len(line) <= 5
        ]
        if credit_account:
            transactions = [
                [self.year, line[0].split(" ")[1][0:3], line[0], line[2], line[1], line[4]]
                if len(line) == 5
                else [self.year, line[0].split(" ")[1][0:3], line[0], line[2], line[1], line[3]]
                for line in transactions
            ]
        else:
            transactions = [
                [self.year, line[0].split(" ")[1][0:3], line[0], " ", line[1], line[2]]
                if len(line) == 4
                else [self.year, line[0].split(" ")[1][0:3], line[0], line[2], line[1], line[3]]
                for line in transactions
            ]
        transactions = [line for line in transactions if "cr" not in line[5].lower()]
        return transactions

    def discovery_table_to_df(self, list_of_lines):
        """_summary_.

        :return: _description_
        :rtype: _type_
        """

        # FIX MISSING DESCRIPTIONS
        for index, lines in enumerate(list_of_lines):
            if index + 1 != len(list_of_lines):
                next_line = list_of_lines[index + 1]
                if all(
                    [len(lines) == 1, "Inter account" in lines[0], len(next_line) == 3]
                ):
                    list_of_lines[index + 1] = [
                        next_line[0],
                        next_line[1],
                        lines[0],
                        next_line[2],
                    ]

        transactions = [
            line
            for line in list_of_lines
            if self.um.is_valid_date(line[0].strip(), "%d %b %Y")
            and 4 <= len(line) <= 5
        ]
        transactions = [
            [self.year, line[0].split(" ")[1][0:3], line[0], line[1], line[2], line[3]]
            if len(line) == 4
            else [self.year, line[0].split(" ")[1][0:3], line[0], line[2], line[3], line[4]]
            for line in transactions
        ]

        return transactions

    def document_to_df(self):
        """_summary_.

        :return: _description_
        :rtype: _type_
        """
        # if "Private.txt" in self.file_path:
        #     df = self.txt_private_to_df()
        # elif "Fusion.txt" in self.file_path:
        #     df = self.txt_fusion_to_df()
        try:
            if self.file_name not in self.cache.keys():
                list_of_lines = self.read_pdf_coords_and_sort()
                self.year = self.get_year(list_of_lines)
                self.month = self.get_month(list_of_lines)
                if "discovery" in sum(list_of_lines, [])[0].lower():
                    transactions = self.discovery_table_to_df(list_of_lines)
                else:
                    transactions = self.fnb_to_df(list_of_lines)
                self.cache_data(transactions)

            else:
                transactions = self.cache[self.file_name]

            df = pd.DataFrame(
                transactions,
                columns=["Year", "Month", "Date", "Type", "Details", "Amount"],
            )
            return df
        except Exception as e:
            {self.file_path: str(e)}

    def get_year(self, list_of_lines):
        year = "unknown"
        for i in list_of_lines:
            if len(i) == 2 and ("statement date" in [j.lower().strip() for j in i]):
                year = i[1].split(" ")[2]
                if year.isnumeric() and int(year) >= 2000:
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

    def get_month(self, list_of_lines):
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
        for i in list_of_lines:
            if len(i) == 2 and ("statement date" in [j.lower().strip() for j in i]):
                month = i[1].split(" ")[1]
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

    def cache_data(self, data):
        if self.file_name not in self.cache.keys():
            self.cache[self.file_name] = []

        self.cache[self.file_name] += data
