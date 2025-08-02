import requests
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models import TableMetadata, ColumnMetadata

def fetch_starburst_metadata(starburst_config):
    """
    Connects to a mock Starburst API to fetch and process metadata.
    This function simulates a real API call.
    """
    # Mocking a Starburst API response
    mock_response = {
        "catalog": "mock_starburst_catalog",
        "schema": "finance",
        "tables": [
            {
                "name": "sales",
                "columns": [
                    {"name": "order_id", "type": "bigint", "comment": "Unique order identifier"},
                    {"name": "sale_date", "type": "date", "comment": "Date of sale"}
                ]
            },
            {
                "name": "customers",
                "columns": [
                    {"name": "customer_id", "type": "bigint", "comment": "Unique customer identifier"},
                    {"name": "customer_name", "type": "varchar", "comment": "Name of the customer"}
                ]
            }
        ]
    }
    
    db: Session = SessionLocal()
    table_count = 0
    column_count = 0
    try:
        # Simulate fetching data
        data = mock_response
        source = f"Starburst: {data['catalog']}"
        schema_name = data['schema']
        
        for table_data in data['tables']:
            table_name = table_data['name']
            
            table = TableMetadata(table_name=table_name, schema_name=schema_name, source=source)
            db.add(table)
            db.commit()
            db.refresh(table)
            table_count += 1
            
            for col_data in table_data['columns']:
                column = ColumnMetadata(
                    table_id=table.id,
                    column_name=col_data['name'],
                    data_type=col_data['type'],
                    description=col_data['comment']
                )
                db.add(column)
                column_count += 1
        db.commit()
        return table_count, column_count
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
