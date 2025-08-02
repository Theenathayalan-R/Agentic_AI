import google.generativeai as genai
import json
from config.config import settings

def extract_lineage(code_content: str, code_type: str):
    """
    Uses the Gemini API to analyze SQL or PySpark code to extract
    data lineage information (source tables -> target tables).
    """
    if not settings.ai.gemini_api_key:
        return [
            {"source_tables": ["mock_source_table"], "target_table": "mock_target_table", "transformation_logic": "Mock transformation"}
        ]
    
    prompt = f"""
    You are a data lineage expert. Analyze the following {code_type} code and
    identify the data lineage. For each query or transformation, identify the
    source tables and the target table (if one is being created or updated).
    Also, provide a brief description of the transformation logic.
    Respond with a JSON array of objects. Each object should have 'source_tables' (an array of strings),
    'target_table' (a string), and 'transformation_logic' (a string).
    If a target table cannot be identified, omit the object.
    
    Code:
    ```
    {code_content}
    ```
    
    JSON Output:
    """

    # Using the text-based gemini-1.5-flash model
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip())
    except Exception as e:
        print(f"Error extracting lineage with Gemini API: {e}")
        return []
