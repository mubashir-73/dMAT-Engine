from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


engine = create_engine(
    "postgresql://dmat:dmat@localhost:5432/dmat"
)  # After deployment change localhost to db
Base.metadata.create_all(engine)

inspector = inspect(engine)
existing_tables = inspector.get_table_names()

print("\n🚀 --- DATABASE CONNECTION SUCCESSFUL --- 🚀")
print(f"Tables currently existing in DB: {existing_tables}\n")
