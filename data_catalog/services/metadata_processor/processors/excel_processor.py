import pandas as pd
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models import TableMetadata, ColumnMetadata

def process_excel_file(df: pd.DataFrame):
    """
    Processes a pandas DataFrame from an Excel file and stores metadata.
    """
    db: Session = SessionLocal()
    table_count = 0
    column_count = 0
    try:
        # Assuming the entire Excel sheet is a single table for this example
        table_name = "excel_data_1"
        schema_name = "public"
        source = "Excel Upload"
        
        table = TableMetadata(table_name=table_name, schema_name=schema_name, source=source)
        db.add(table)
        db.commit()
        db.refresh(table)
        table_count += 1
        
        for column_name, data_type in df.dtypes.items():
            column = ColumnMetadata(
                table_id=table.id,
                column_name=column_name,
                data_type=str(data_type),
                description=f"Column loaded from Excel file. Data type: {str(data_type)}"
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
