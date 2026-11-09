import os
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase):
    pass

def database_url():
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    return URL.create("postgresql+psycopg", username=os.environ["POSTGRES_USER"],
                      password=os.environ["POSTGRES_PASSWORD"], host=os.getenv("DB_HOST", "postgres"),
                      port=int(os.getenv("DB_PORT", "5432")), database=os.environ["POSTGRES_DB"])

url = database_url()
sqlite = str(url).startswith("sqlite")
engine = create_engine(url, pool_pre_ping=True,
                       **({"connect_args": {"check_same_thread": False}} if sqlite else
                          {"pool_size": 2, "max_overflow": 1, "pool_timeout": 5,
                           "connect_args": {"connect_timeout": 3}}))
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def get_db():
    with SessionLocal() as session:
        yield session
