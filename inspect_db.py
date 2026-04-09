from database import Base
from models import caffenity_models, credentials_models, arena_models

for table_name, table in Base.metadata.tables.items():
    print(f"Table: {table_name}")
    for column in table.columns:
        print(f"  - {column.name}: {column.type}")
