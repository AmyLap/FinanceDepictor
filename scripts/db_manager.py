"""Database manager with Streamlit caching for connections and queries.

Replaces the JSON-based cache system with persistent SQLite storage.
Uses `@st.cache_resource` for thread-safe, long-lived DB connections.

Functions:
- get_db(): Get a cached SQLAlchemy engine and session factory.
- file_already_parsed(filename: str) -> bool: Check if a file was already uploaded.
- get_file_transactions(filename: str) -> list: Retrieve cached transactions for a file.
- write_transactions(transactions: list, filename: str, bank: str, account_id: int = 1) -> bool: Store parsed transactions.
"""
from __future__ import annotations

import hashlib
import os
from datetime import date
from typing import Optional

import streamlit as st
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from scripts.db_schema import Base, FileMeta, Transaction


@st.cache_resource
def get_db(db_url: str = "sqlite:///finance.db"):
    """Get a cached SQLAlchemy engine and session factory.
    
    This is cached by Streamlit, so the connection persists across reruns.
    Uses check_same_thread=False for SQLite to allow multi-threaded access.
    """
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {}
    )
    Base.metadata.create_all(engine)  # Ensure tables exist
    return engine, sessionmaker(bind=engine)


def file_already_parsed(filename: str, user_id: int = 1) -> bool:
    """Check if a file has already been uploaded and parsed.
    
    Returns True if a FileMeta record exists for this filename.
    """
    engine, SessionFactory = get_db()
    session = SessionFactory()
    try:
        record = session.query(FileMeta).filter_by(
            filename=filename, user_id=user_id
        ).first()
        return record is not None
    finally:
        session.close()


def get_file_transactions(filename: str, user_id: int = 1) -> Optional[list]:
    """Retrieve cached transactions for a file.
    
    Returns a list of [Year, Month, Date, Type, Details, Amount] rows,
    or None if the file hasn't been parsed.
    """
    engine, SessionFactory = get_db()
    session = SessionFactory()
    try:
        # Find the file record
        file_record = session.query(FileMeta).filter_by(
            filename=filename, user_id=user_id
        ).first()
        if not file_record:
            return None
        
        # Get all transactions for this file
        transactions = session.query(Transaction).filter_by(
            file_id=file_record.id
        ).all()
        
        if not transactions:
            return None
        
        # Convert to list-of-lists format matching [Year, Month, Date, Type, Details, Amount]
        result = []
        for txn in transactions:
            year = txn.date.year if txn.date else "unknown"
            month = txn.date.strftime("%b") if txn.date else "unknown"
            date_str = txn.date.strftime("%d %b %Y") if txn.date else ""
            result.append([
                str(year),
                str(month),
                date_str,
                txn.merchant or "",
                txn.description or "",
                str(txn.amount),
            ])
        
        return result if result else None
    finally:
        session.close()


def write_transactions(
    transactions: list,
    filename: str,
    bank: str = "unknown",
    account_id: int = 1,
    user_id: int = 1,
) -> bool:
    """Store parsed transactions into the database.
    
    Args:
        transactions: List of [Year, Month, Date, Type, Details, Amount] rows.
        filename: Name of the uploaded file (used as unique key).
        bank: Bank identifier (e.g., 'fnb', 'discovery').
        account_id: Account ID to associate transactions with.
        user_id: User ID for multi-tenant tracking.
    
    Returns:
        True on success, False on error.
    """
    engine, SessionFactory = get_db()
    session = SessionFactory()
    try:
        # Check if file was already processed (idempotency)
        existing_file = session.query(FileMeta).filter_by(
            filename=filename, user_id=user_id
        ).first()
        if existing_file:
            # File already in DB; skip to avoid duplicates
            return False
        
        # Create file metadata record
        file_meta = FileMeta(
            user_id=user_id,
            account_id=account_id,
            filename=filename,
            file_type=filename.split(".")[-1] if "." in filename else "unknown",
        )
        session.add(file_meta)
        session.flush()  # Get the file ID
        file_id = file_meta.id
        
        # Insert transactions
        for row in transactions:
            # Unpack: [Year, Month, Date, Type, Details, Amount]
            year_str, month_str, date_str, txn_type, details, amount_str = row
            
            # Parse date
            try:
                if date_str:
                    # Try to parse "DD MMM YYYY" or "DD MMM" format
                    if len(date_str.split()) == 3:
                        txn_date = date.fromisoformat(
                            "-".join(reversed(date_str.replace(" ", "-").split("-")))
                        )
                    else:
                        # Fallback: use year
                        txn_date = date(int(year_str), 1, 1)
                else:
                    txn_date = date(int(year_str), 1, 1)
            except (ValueError, TypeError):
                txn_date = date(2025, 1, 1)  # Safe fallback
            
            try:
                amount = float(amount_str)
            except (ValueError, TypeError):
                amount = 0.0
            
            txn = Transaction(
                file_id=file_id,
                account_id=account_id,
                date=txn_date,
                amount=amount,
                merchant=txn_type or "",
                description=details or "",
                currency="GBP",
            )
            session.add(txn)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error writing transactions to DB: {e}")
        return False
    finally:
        session.close()


__all__ = ["get_db", "file_already_parsed", "get_file_transactions", "write_transactions"]
