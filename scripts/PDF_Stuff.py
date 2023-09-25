"""_summary_."""

import pandas as pd
import numpy as np
from PDFContentConverter import PDFContentConverter
from use_things import UsefulMethods


class ReadPDF():
    """_summary_
    """

    def __init__(self, file_path, dataframe):
        """_summary_

        :param file_path: _description_
        :type file_path: _type_
        :param dataframe: _description_
        :type dataframe: _type_
        """
        self.file_path = file_path
        self.table_list = list()
        self.dataframe = dataframe
        self.df_addon = pd.DataFrame({
            "Transaction Date": [],
            "Transaction Type": [],
            "Amount": []})
        self.um = UsefulMethods()

    def read_pdf_coords_and_sort(self):
        # convert PDF
        converter = PDFContentConverter(self.file_path)
        df = converter.pdf2pandas()  # equivalent to result["content"]
        sorted_df = df.sort_values(by=["y_0", 'x_0', "page"])
        sorted_df["y_0"] = np.ceil(df['y_0'])
        list_of_lines = []
        grouped_by_page = sorted_df.groupby("page")

        for page_group in grouped_by_page.groups.keys():
            grouped_by_y_axis = grouped_by_page.get_group(page_group).groupby("y_0")
            for group in grouped_by_y_axis.groups.keys():
                list_of_lines.append(list(grouped_by_y_axis.get_group(group)["text"]))
        return list_of_lines

    def fnb_to_df(self):
        """_summary_.
        """

        list_of_lines = self.read_pdf_coords_and_sort()
        flattened_list = [item for sublist in list_of_lines for item in sublist]
        credit_account = False if 'FNB PRIVATE WEALTH CREDIT CARD 4483 8100 6210 6000 ' not in flattened_list else True
        headers = ['Date', 'Type', 'Details', 'Amount']
        transactions = [line for line in list_of_lines if self.um.is_valid_date(line[0].strip(), "%d %b") and 4 <= len(line) <= 5]
        if credit_account:
            transactions = [[line[0], line[2], line[1], line[4]] if len(line) == 5 else [line[0], line[2], line[1], line[3]] for line in transactions]
        else:
            transactions = [[line[0], " ", line[1], line[2]] if len(line) == 4 else [line[0], line[2], line[1], line[3]] for line in transactions]
        transactions = [line for line in transactions if "cr" not in line[3].lower()]
        df = pd.DataFrame(transactions, columns=headers)

        print()
        return df

    def discovery_table_to_df(self):
        """_summary_.

        :return: _description_
        :rtype: _type_
        """
        list_of_lines = self.read_pdf_coords_and_sort()
        # FIX MISSING DESCRIPTIONS
        for index, lines in enumerate(list_of_lines):
            if index + 1 != len(list_of_lines):
                next_line = list_of_lines[index+1]
                if all([len(lines) == 1, "Inter account" in lines[0], len(next_line) == 3]):
                    list_of_lines[index+1] = [next_line[0], next_line[1], lines[0], next_line[2]]
            
        headers = ['Date', 'Type', 'Details', 'Amount']
        transactions = [line for line in list_of_lines if self.um.is_valid_date(line[0].strip(), "%d %b %Y") and 4 <= len(line) <= 5]
        transactions = [[line[0], line[1], line[2], line[3]] if len(line) == 4 else [line[0], line[2], line[3], line[4]] for line in transactions]
        print()
        df = pd.DataFrame(transactions, columns=headers)

        return df

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
            if "acc" in self.file_path.lower() and "pdf" in self.file_path:
                df = self.fnb_to_df()
            elif "credit" in self.file_path.lower() and "pdf" in self.file_path:
                df = self.fnb_to_df()
            elif "amy" in self.file_path.lower() and "pdf" in self.file_path:
                df = self.fnb_to_df()
            else:
                df = self.discovery_table_to_df()

            return df
        except Exception as e:
            {self.file_path: str(e)}
    
