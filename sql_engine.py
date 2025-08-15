from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use the same database URL as Alembic (configured in alembic.ini)
engine = create_engine('sqlite:///db_tracker_old')
Base = declarative_base()
Session = sessionmaker(bind=engine)