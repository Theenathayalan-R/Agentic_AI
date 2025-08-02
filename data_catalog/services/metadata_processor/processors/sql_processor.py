import sqlparse
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models import TableMetadata, ColumnMetadata

def process_sql_ddl(sql_content: str):
    """
    Parses SQL DDL content and stores table and column metadata.
    This is a simplified example that assumes a simple CREATE TABLE syntax.
    """
    db: Session = SessionLocal()
    table_count = 0
    column_count = 0
    try:
        parsed = sqlparse.parse(sql_content)
        for statement in parsed:
            tokens = statement.tokens
            # Find CREATE TABLE statements
            create_token = [t for t in tokens if t.ttype is sqlparse.tokens.DDL and t.value.upper() == 'CREATE']
            if create_token:
                table_token = [t for t in tokens if isinstance(t, sqlparse.sql.Identifier) and t.value.upper() != 'TABLE']
                if not table_token:
                    continue
                table_name = table_token[0].value.strip('"')
                schema_name = "public" # Simplified assumption

                table = TableMetadata(table_name=table_name, schema_name=schema_name, source="SQL DDL")
                db.add(table)
                db.commit()
                db.refresh(table)
                table_count += 1
                
                # Find the column definitions within the parentheses
                paren_tokens = [t for t in tokens if isinstance(t, sqlparse.sql.Parenthesis)]
                if paren_tokens:
                    # Logic to parse columns (simplified)
                    columns_raw = paren_tokens[0].value.strip('()').split(',')
                    for col_str in columns_raw:
                        parts = col_str.strip().split()
                        if len(parts) >= 2:
                            column_name = parts[0].strip('"')
                            data_type = parts[1].strip()
                            column = ColumnMetadata(
                                table_id=table.id,
                                column_name=column_name,
                                data_type=data_type,
                                description=""
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
