from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# PostgreSQL bazasiga bog'lanish
engine = create_engine("postgresql://postgres:2004@localhost/delivery_db")

Base = declarative_base()
session = sessionmaker()


def SessionLocal():
    engine = create_engine('postgresql://postgres:2004@localhost/delivery_db', echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
