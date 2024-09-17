

class CategoryFunctions():

    def __init__(self, categorised_df) -> None:
        self.categorised_df = categorised_df

    def subcategory(self, category):
        categorised_df = self.categorised_df.groupby(['Category', 'Key_Word'])['Amount'].sum().reset_index()
        subcategory = categorised_df[categorised_df['Category'] == category]
        return subcategory.set_index('Key_Word')['Amount'].to_dict()

    def other(self):
        categorised_df = self.categorised_df.groupby(['Category', 'Details'])['Amount'].sum().reset_index()
        subcategory = categorised_df[categorised_df['Category'] == "Other"]
        return subcategory.set_index('Details')['Amount'].to_dict()
    
    def year(self, year):
        grouped = self.categorised_df.groupby(['Year', 'Category'])['Amount'].sum().reset_index()
        year_group = grouped[grouped['Year'] == int(year)]
        year_dict = year_group.set_index('Category')['Amount'].to_dict()
        return year_dict
    
    def year_category(self, a, b):
        if a.isnumeric():
            year = a
            category = b
        else:
            category = a
            year = b
        grouped = self.categorised_df.groupby(['Year', 'Category', 'Key_Word'])['Amount'].sum().reset_index()
        year_group = grouped[grouped['Year'] == int(year)]
        year_subcategory = year_group[year_group['Category'] == category]
        results_dict = year_subcategory.set_index('Key_Word')['Amount'].to_dict()
        return results_dict