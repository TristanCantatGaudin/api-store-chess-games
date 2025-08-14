from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# In real life the following (especially the password!) should be passed as environment variables:
SQLALCHEMY_DATABASE_URL = "postgresql://tristan:hunter2@localhost:5432/maydatabase"
# change "localhost" with "db" if both DB and app are running in Docker containers

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)