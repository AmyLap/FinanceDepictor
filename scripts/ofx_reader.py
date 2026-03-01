"""Simple OFX reader that converts OFX transactions into a pandas DataFrame

Produces columns: Year, Month, Date, Type, Details, Amount
Only includes debit (expense) transactions (amount < 0) and stores Amount as positive value.
"""
from datetime import datetime
from typing import List

import pandas as pd

try:
    from ofxparse import OfxParser
except Exception:
    OfxParser = None


def read_ofx_to_df(file_path: str) -> pd.DataFrame:
    """Parse an OFX file and return a DataFrame matching existing pipeline.

    Columns: Year (int), Month (3-letter), Date (ISO string), Type, Details, Amount (float)
    Only debit transactions (amount < 0) are included.
    """
    if OfxParser is None:
        raise RuntimeError("ofxparse is required to parse OFX files. Install with `pip install ofxparse`")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
        ofx = OfxParser.parse(fh)

    txns = []  # type: List[List]
    # ofx.account.statement.transactions contains transactions
    try:
        transactions = ofx.account.statement.transactions
    except Exception:
        transactions = []

    for t in transactions:
        # t.date is datetime.date or datetime
        date_obj = t.date
        if isinstance(date_obj, datetime):
            dt = date_obj
        else:
            dt = datetime.combine(date_obj, datetime.min.time())

        amount = float(t.amount)
        # Include only debits (negative amounts) - treat as expense
        if amount >= 0:
            continue

        year = dt.year
        month = dt.strftime("%b")
        date_str = dt.strftime("%Y-%m-%d")
        txn_type = getattr(t, "type", "")
        details = " ".join(filter(None, [getattr(t, "payee", ""), getattr(t, "memo", "")] )) or ""

        txns.append([year, month, date_str, txn_type, details, abs(amount)])

    df = pd.DataFrame(txns, columns=["Year", "Month", "Date", "Type", "Details", "Amount"]) if txns else pd.DataFrame(columns=["Year", "Month", "Date", "Type", "Details", "Amount"])  # type: ignore
    return df
