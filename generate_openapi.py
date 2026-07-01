import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.app import app

def clean_anyof(schema_node):
    if isinstance(schema_node, dict):
        if "anyOf" in schema_node and len(schema_node["anyOf"]) == 2:
            types = [s.get("type") for s in schema_node["anyOf"]]
            if "null" in types:
                # Find the non-null element
                non_null = next((s for s in schema_node["anyOf"] if s.get("type") != "null"), None)
                if non_null:
                    del schema_node["anyOf"]
                    schema_node.update(non_null)
                    schema_node["nullable"] = True
        for k, v in schema_node.items():
            clean_anyof(v)
    elif isinstance(schema_node, list):
        for item in schema_node:
            clean_anyof(item)

def generate_openapi():
    # Get the raw schema from FastAPI
    schema = app.openapi()
    
    # Fix Pydantic v2 anyOf issues for Copilot Studio
    clean_anyof(schema)
    
    # Filter out endpoints that Copilot Studio should NOT see as tools (like the webhook and healthchecks)
    allowed_paths = ["/api/tools/database/schema", "/api/tools/database/query"]
    if "paths" in schema:
        schema["paths"] = {p: path_item for p, path_item in schema["paths"].items() if p in allowed_paths}
    
    # Strip FastAPI's default 422 Validation errors (Copilot Studio hates them)
    if "components" in schema and "schemas" in schema["components"]:
        schema["components"]["schemas"].pop("ValidationError", None)
        schema["components"]["schemas"].pop("HTTPValidationError", None)
        schema["components"]["schemas"].pop("RootResponse", None)
        schema["components"]["schemas"].pop("HealthResponse", None)
    
    for path, path_item in schema.get("paths", {}).items():
        for method, operation in path_item.items():
            if "responses" in operation and "422" in operation["responses"]:
                del operation["responses"]["422"]
                
    # Copilot Studio requires OpenAPI 3.0.x
    schema["openapi"] = "3.0.2"
    schema["info"]["title"] = "SQL Analytics Agent V3"
    
    # Add the servers block as requested by the user
    schema["servers"] = [
        {
            "url": "https://api.example.com",
            "description": "Local development server via dev tunnel or ngrok"
        }
    ]
    
    # Write JSON
    with open("openapi.json", "w") as f:
        json.dump(schema, f, indent=2)
        
    # Write YAML
    import yaml
    with open("openapi.yaml", "w") as f:
        yaml.dump(schema, f, default_flow_style=False, sort_keys=False)
        
    print("OpenAPI schema generated successfully at openapi.json and openapi.yaml!")

if __name__ == "__main__":
    generate_openapi()
