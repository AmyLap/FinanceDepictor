"""Usefull methos to keep around for genral use."""
from datetime import datetime


class UsefulMethods():
    """_summary_"""

    def is_valid_date(self, date_string, date_format):
        """_summary_

        :param date_string: _description_
        :type date_string: _type_
        :param date_format: _description_
        :type date_format: _type_
        :return: _description_
        :rtype: _type_
        """
        try:
            datetime.strptime(date_string, date_format)
            return True
        except ValueError as _e:
            print(_e)
            return False
