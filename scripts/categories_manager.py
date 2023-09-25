import json
import os


class CategoriesManager():
    """_summary_
    """
    def __init__(self) -> None:
        self._categories = {}
        self.logs_directory = os.getcwd() + "\\logs\\categories.json"

    def get_categories(self):
        """_summary_

        :return: _description_
        :rtype: _type_
        """
        with open(self.logs_directory, 'r') as f:
            self._categories = json.load(f)
        self.save_catgories(copy=True)
        return self._categories

    def save_catgories(self, copy: bool = False):
        """_summary_

        :param copy: _description_, defaults to False
        :type copy: bool, optional
        """
        if copy:
            self.logs_directory = os.getcwd() + "\\logs\\categories_copy.json"
        if self._categories:
            with open(self.logs_directory, 'w') as f:
                json.dump(self._categories, f)

    def add_category(self, category: str):
        """_summary_

        :param category: _description_
        :type category: str
        """
        if not self._categories:
            self.get_categories()
        if category not in self._categories.keys():
            self._categories[category] = []
        else:
            print("Category is already included")

    def remove_category(self, category: str):
        """_summary_

        :param category: _description_
        :type category: str
        """
        if not self._categories:
            self.get_categories()
        if category in self._categories.keys():
            del self._categories[category]
        else:
            print("Category is not in the list of categories")

    def add_key_word_to_category(self, category: str, key_word: str):
        """_summary_

        :param category: _description_
        :type category: str
        :param key_word: _description_
        :type key_word: str
        """
        if not self._categories:
            self.get_categories()
        if category not in self._categories[category]:
            self.add_category(category)
        if key_word not in self.list_of_all_keywords():
            self._categories[category].appendd(key_word)

    def list_of_all_keywords(self):
        """_summary_

        :return: _description_
        :rtype: _type_
        """
        return [key_word.lower() for key_words in self._categories.values() for key_word in key_words]

    def categories(self):
        """_summary_

        :return: _description_
        :rtype: _type_
        """
        return self._categories.keys()

    def detect_uncategorised_descriptions(self, descriptions: list):
        """_summary_

        :param descriptions: _description_
        :type descriptions: list
        :return: _description_
        :rtype: _type_
        """
        if not self._categories:
            self.get_categories()
        uncategorisedd_descriptions = []
        for description in set(descriptions):
            for key_word in self.list_of_all_keywords():
                if key_word in description:
                    continue
            uncategorisedd_descriptions.append(description)
        return uncategorisedd_descriptions
