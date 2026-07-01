from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="The SQL query to execute against the CRM database.")

class QueryData(BaseModel):
    columns: List[str] = Field(default_factory=list, description="List of column names returned.")
    rows: List[Dict[str, Any]] = Field(default_factory=list, description="List of rows returned as key-value dictionaries.")

class SchemaData(BaseModel):
    schema_info: str = Field(default="", description="Text representation of the database schema (tables and columns).")

class PipelineRequest(BaseModel):
    period: str = None
    region: str = None
    industry: str = None

class TopAccountsRequest(BaseModel):
    limit: int = 5
    industry: str = None
    region: str = None

class InteractionRequest(BaseModel):
    account_name: str = None
    type: str = None

# --- HR / Employee Data Schemas ---

class HRDepartmentRequest(BaseModel):
    department_name: Optional[str] = Field(default=None, description="Filter by department name, e.g., 'Engineering' or 'Sales'.")

class HRPtoRequest(BaseModel):
    status: Optional[str] = Field(default=None, description="Filter by PTO status, e.g., 'Approved', 'Pending'.")
    department_name: Optional[str] = Field(default=None, description="Filter by department name.")
