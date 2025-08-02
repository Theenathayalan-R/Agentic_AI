import sys
import os
import json
# Add the project root to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
import google.generativeai as genai
from shared.database import get_db, SessionLocal
from shared.models import TableMetadata, ColumnMetadata, UserFeedback
from config.config import settings
from services.ai_agent.agents.definition_agent import generate_business_definition
from services.ai_agent.agents.quality_agent import calculate_data_quality
from services.ai_agent.agents.tag_agent import generate_tags
from services.ai_agent.agents.diagram_agent import process_data_diagram
from services.ai_agent.agents.lineage_agent import extract_lineage

# --- Hardcoded AI Settings for definitive loading ---
class AiSettings(BaseModel):
    gemini_api_key: str = "AIzaSyBF9WHShOcTkC4EYQEk5fz25KEHBC7bEl0"
    model_name: str = "gemini-1.5-flash"
    max_tokens: int = 2000
    temperature: float = 0.7

# Create an instance of the settings class
ai_settings = AiSettings()
# --------------------------------------------------

app = FastAPI()


# --- Configure Gemini API on startup ---
@app.on_event("startup")
def startup_event():
    if settings.ai.gemini_api_key and settings.ai.gemini_api_key != "aaa":
        try:
            genai.configure(api_key=settings.ai.gemini_api_key)
            print("Gemini API key configured successfully.")
        except Exception as e:
            print(f"Error configuring Gemini API: {e}")
            print("AI features may not work as expected.")
    else:
        print("Warning: Gemini API key not configured. AI features will use mock responses.")

# --- Endpoints for AI functionality ---
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-agent"}

class TableSchema(BaseModel):
    table_name: str
    schema_name: str

class FeedbackData(BaseModel):
    table_id: int
    column_id: int | None = None
    feedback: str

# Configure Gemini API Key
if settings.ai.gemini_api_key:
    genai.configure(api_key=settings.ai.gemini_api_key)
else:
    print("Warning: Gemini API key not configured. AI features will use mock responses.")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-agent"}

@app.post("/generate-definitions")
def generate_definitions_endpoint(table_info: TableSchema):
    db: Session = SessionLocal()
    try:
        table = db.query(TableMetadata).filter_by(table_name=table_info.table_name, schema_name=table_info.schema_name).first()
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        
        definition = generate_business_definition(table)
        table.business_definition = definition
        db.commit()
        db.refresh(table)
        
        return {"status": "success", "message": "Business definition generated successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/calculate-quality")
def calculate_quality_endpoint(table_info: TableSchema):
    db: Session = SessionLocal()
    try:
        table = db.query(TableMetadata).filter_by(table_name=table_info.table_name, schema_name=table_info.schema_name).first()
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        
        score = calculate_data_quality(table)
        table.data_quality_score = score
        db.commit()
        db.refresh(table)

        return {"status": "success", "message": "Data quality score calculated."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/generate-tags")
def generate_tags_for_table_endpoint(table_info: TableSchema):
    db: Session = SessionLocal()
    try:
        table = db.query(TableMetadata).filter_by(table_name=table_info.table_name, schema_name=table_info.schema_name).first()
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        
        tags = generate_tags(table)
        table.tags = tags
        db.commit()
        db.refresh(table)
        
        return {"status": "success", "message": "Tags generated successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/submit-feedback")
def submit_user_feedback(feedback_data: FeedbackData, db: Session = Depends(get_db)):
    new_feedback = UserFeedback(
        table_id=feedback_data.table_id,
        column_id=feedback_data.column_id,
        feedback_text=feedback_data.feedback
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    
    return {"status": "success", "message": "Feedback submitted successfully."}

@app.post("/extract-metadata-from-diagram")
async def extract_metadata_from_diagram(file: UploadFile = File(...)):
    """
    Analyzes an image or PDF diagram and extracts table and column metadata.
    """
    try:
        image_data = await file.read()
        mime_type = file.content_type
        
        if not mime_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Only images are supported.")
        
        # Prepare the model and the prompt
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt_text = """
            Extract table and column metadata from the provided database diagram. 
            Provide the output as a JSON object, with a 'tables' array containing objects for each table. 
            Each table object should have 'table_name' and a 'columns' array. 
            Each column object should have 'column_name' and 'data_type'. 
            If a table has no columns, include it with an empty 'columns' array.

            Example JSON structure:
            {
              "tables": [
                {
                  "table_name": "users",
                  "columns": [
                    {"column_name": "id", "data_type": "INT"},
                    {"column_name": "username", "data_type": "VARCHAR"}
                  ]
                }
              ]
            }
            """
        
        # Make the multimodal API call
        response = model.generate_content([
            prompt_text, 
            {"mime_type": mime_type, "data": image_data}
        ])

        # Safely extract and parse the response text
        try:
            # The API response is often in a markdown block, so we clean it.
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[len('```json'):]
            if response_text.endswith('```'):
                response_text = response_text[:-len('```')]
            
            extracted_metadata = json.loads(response_text)
            
            return {"metadata": extracted_metadata}
        except json.JSONDecodeError as e:
            print(f"Error processing image with Gemini API: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Gemini API returned a non-JSON response. Please check the API response format."
            )
        except Exception as e:
            print(f"Unexpected error when processing Gemini response: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred during AI processing.")

    except HTTPException:
        # Re-raise the HTTPException to maintain the original status code
        raise
    except Exception as e:
        print(f"Error processing image with Gemini API: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred when calling the Gemini API: {str(e)}"
        )


@app.post("/extract-lineage/{code_type}")
async def extract_lineage_endpoint(code_type: str, file: UploadFile = File(...)):
    """
    Endpoint to process code (SQL or PySpark) and extract data lineage information.
    """
    if code_type not in ["sql", "pyspark_sql"]:
        raise HTTPException(status_code=400, detail="Invalid code type. Supported types are 'sql' and 'pyspark_sql'.")

    try:
        code_content = await file.read()
        code_content = code_content.decode('utf-8')
        lineage_data = extract_lineage(code_content, code_type)
        return {"status": "success", "lineage": lineage_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
