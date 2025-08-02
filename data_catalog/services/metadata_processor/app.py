import sys
import os

# Add the project root to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import FastAPI, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import requests
import fitz
import io
import sqlparse
from shared.database import get_db, Base, engine
from shared.models import TableMetadata, ColumnMetadata, LineageMetadata
from services.metadata_processor.processors.excel_processor import process_excel_file
from services.metadata_processor.processors.sql_processor import process_sql_ddl
from services.metadata_processor.processors.starburst_processor import fetch_starburst_metadata
from config.config import settings

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_data_source_config(source_name: str):
    """Helper function to get a data source's config from the central settings."""
    for source in settings.data_sources:
        if source.name == source_name:
            return source
    return None

@app.on_event("startup")
def startup_event():
    print("Metadata Processor Service started.")
    print("Loaded data sources from config:", [source.name for source in settings.data_sources])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "metadata-processor"}

@app.post("/process/excel")
async def upload_excel_metadata(file: UploadFile = File(...)):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Invalid file type.")
    try:
        df = pd.read_excel(file.file)
        table_count, column_count = process_excel_file(df)
        return {"status": "success", "message": f"Processed {table_count} tables and {column_count} columns from Excel file."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/sql-ddl/{source_name}")
async def upload_sql_metadata(source_name: str, file: UploadFile = File(...)):
    if not file.filename.endswith('.sql'):
        raise HTTPException(status_code=400, detail="Invalid file type.")
    
    source_config = get_data_source_config(source_name)
    if not source_config or source_config.type != 'sql_ddl':
        print(f"DEBUG: Source '{source_name}' was not found or type was not 'sql_ddl'. Found source: {source_config}")
        raise HTTPException(status_code=400, detail=f"Source '{source_name}' not configured for SQL DDL.")

    try:
        sql_content = await file.read()
        sql_content = sql_content.decode('utf-8')
        table_count, column_count = process_sql_ddl(sql_content)
        return {"status": "success", "message": f"Processed {table_count} tables and {column_count} columns from SQL DDL."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/starburst/{source_name}")
async def process_starburst_metadata(source_name: str):
    source_config = get_data_source_config(source_name)
    if not source_config or source_config.type != 'starburst':
        raise HTTPException(status_code=400, detail=f"Source '{source_name}' not configured for Starburst.")
    
    try:
        table_count, column_count = fetch_starburst_metadata(source_config.config)
        return {"status": "success", "message": f"Processed {table_count} tables and {column_count} columns from {source_name}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/image-diagram")
async def upload_image_diagram(file: UploadFile = File(...)):
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed types are: {', '.join(allowed_types)}")

    try:
        all_metadata = {"tables": []}
        
        if file.content_type == "application/pdf":
            pdf_data = await file.read()
            pdf_doc = fitz.open(stream=pdf_data, filetype="pdf")
            for page_num in range(len(pdf_doc)):
                page = pdf_doc.load_page(page_num)
                pix = page.get_pixmap(dpi=300)
                image_bytes = pix.tobytes("png")
                
                ai_response = requests.post(
                    f"{settings.services.ai_agent}/extract-metadata-from-diagram",
                    files={"file": (f"page_{page_num}.png", image_bytes, "image/png")}
                )
                ai_response.raise_for_status()
                page_metadata = ai_response.json().get("metadata", {})
                
                if "tables" in page_metadata:
                    all_metadata["tables"].extend(page_metadata["tables"])
            pdf_doc.close()
        else:
            image_data = await file.read()
            ai_response = requests.post(
                f"{settings.services.ai_agent}/extract-metadata-from-diagram",
                files={"file": (file.filename, image_data, file.content_type)}
            )
            ai_response.raise_for_status()
            all_metadata = ai_response.json().get("metadata", {})

        if not all_metadata.get("tables"):
            raise HTTPException(status_code=500, detail="AI Agent failed to extract any table metadata.")
        
        db: Session = next(get_db())
        try:
            table_count = 0
            column_count = 0
            for table_data in all_metadata["tables"]:
                table_metadata = TableMetadata(
                    table_name=table_data["table_name"],
                    schema_name=table_data.get("schema_name", "public"),
                    source="Image Diagram"
                )
                db.add(table_metadata)
                db.commit()
                db.refresh(table_metadata)
                table_count += 1

                for col_data in table_data["columns"]:
                    column_metadata = ColumnMetadata(
                        table_id=table_metadata.id,
                        column_name=col_data["column_name"],
                        data_type=col_data.get("data_type", "UNKNOWN"),
                        description=col_data.get("description", "")
                    )
                    db.add(column_metadata)
                    column_count += 1
            db.commit()
            return {"status": "success", "message": f"Processed {table_count} tables and {column_count} columns from diagram."}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            db.close()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to communicate with AI Agent: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/process/lineage-code/{code_type}/{source_name}")
async def process_lineage_code(code_type: str, source_name: str, file: UploadFile = File(...)):
    if code_type not in ["sql_lineage", "pyspark_sql"]:
        raise HTTPException(status_code=400, detail="Invalid code type. Supported types are 'sql_lineage' and 'pyspark_sql'.")

    file_extension = '.sql' if code_type == 'sql_lineage' else '.py'
    if not file.filename.endswith(file_extension):
        raise HTTPException(status_code=400, detail=f"Invalid file type. Only {file_extension} files are supported for {code_type} lineage.")

    source_config = get_data_source_config(source_name)
    if not source_config or source_config.type != code_type:
        raise HTTPException(status_code=400, detail=f"Source '{source_name}' not configured for {code_type} lineage.")

    try:
        code_content = await file.read()
        
        ai_response = requests.post(
            f"{settings.services.ai_agent}/extract-lineage/{code_type}",
            files={"file": (file.filename, code_content, "text/plain")}
        )
        ai_response.raise_for_status()
        lineage_data = ai_response.json().get("lineage", [])
        
        if not lineage_data:
            return {"status": "success", "message": f"No lineage information could be extracted from the {code_type} file."}
        
        db: Session = next(get_db())
        lineage_count = 0
        try:
            for item in lineage_data:
                # Assuming table names are simple for this example, but they could be complex
                # In a real-world scenario, you might need a more sophisticated lookup
                source_tables = [db.query(TableMetadata).filter_by(table_name=s).first() for s in item.get("source_tables", [])]
                target_table = db.query(TableMetadata).filter_by(table_name=item.get("target_table")).first()

                if target_table:
                    for source_table in source_tables:
                        if source_table:
                            new_lineage = LineageMetadata(
                                source_table_id=source_table.id,
                                target_table_id=target_table.id,
                                transformation_logic=item.get("transformation_logic", "Unknown")
                            )
                            db.add(new_lineage)
                            lineage_count += 1
            db.commit()
            return {"status": "success", "message": f"Extracted and stored {lineage_count} lineage relationships from {code_type}."}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            db.close()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to communicate with AI Agent: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
