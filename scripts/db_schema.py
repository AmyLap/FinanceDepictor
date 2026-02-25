"""SQLAlchemy models and DB helper for FinanceDepictor.

Usage:
    pip install sqlalchemy
    from scripts.db_schema import create_db, seed_sample
    create_db('sqlite:///finance.db')
    seed_sample('sqlite:///finance.db')
"""
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    bank_name = Column(String)
    account_mask = Column(String)
    account_type = Column(String)
    currency = Column(String, default='GBP')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship('User')


class FileMeta(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    account_id = Column(Integer, ForeignKey('accounts.id'))
    filename = Column(String, nullable=False)
    original_name = Column(String)
    file_type = Column(String)
    checksum = Column(String)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship('User')
    account = relationship('Account')


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    is_system = Column(Integer, default=0)


class Rule(Base):
    __tablename__ = 'rules'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    pattern = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    priority = Column(Integer, default=100)
    active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'))
    account_id = Column(Integer, ForeignKey('accounts.id'))
    external_id = Column(String)
    date = Column(Date, nullable=False)
    posted_date = Column(Date)
    amount = Column(Numeric, nullable=False)
    currency = Column(String, default='GBP')
    description = Column(Text)
    merchant = Column(String)
    normalized_description = Column(Text)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category_confidence = Column(Float, default=0.0)
    categorized_by = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime)


class TransactionCategoryHistory(Base):
    __tablename__ = 'transaction_category_history'
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    previous_category_id = Column(Integer, ForeignKey('categories.id'))
    new_category_id = Column(Integer, ForeignKey('categories.id'))
    changed_by = Column(String)
    changed_at = Column(DateTime, default=datetime.datetime.utcnow)


def create_db(db_url: str = 'sqlite:///finance.db'):
    """Create DB and tables using SQLAlchemy."""
    engine = create_engine(db_url, connect_args={"check_same_thread": False} if db_url.startswith('sqlite') else {})
    Base.metadata.create_all(engine)
    return engine


def seed_sample(db_url: str = 'sqlite:///finance.db'):
    """Insert minimal sample data for development/testing."""
    engine = create_engine(db_url, connect_args={"check_same_thread": False} if db_url.startswith('sqlite') else {})
    Session = sessionmaker(bind=engine)
    session = Session()

    # add couple of categories
    groceries = Category(name='Groceries')
    utilities = Category(name='Utilities')
    session.add_all([groceries, utilities])
    session.commit()

    # add a sample user and account
    user = User(name='Household', email='household@example.com')
    session.add(user)
    session.commit()
    account = Account(user_id=user.id, bank_name='Example Bank', account_mask='****1234')
    session.add(account)
    session.commit()

    session.close()


if __name__ == '__main__':
    create_db()
    print('Database initialized (default: sqlite:///finance.db)')
