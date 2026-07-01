from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from database.connection import get_db, get_ro_db, engine
from api.schemas import QueryRequest, QueryData, SchemaData, PipelineRequest, TopAccountsRequest, InteractionRequest, HRDepartmentRequest, HRPtoRequest
import services.analytics as analytics
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/database/schema", response_model=SchemaData)
async def get_database_schema(db: Session = Depends(get_db)):
    """
    Returns the database schema (tables and their columns) so the AI knows what to query.
    """
    logger.info("OpenAPI Tool Triggered: get_database_schema")
    try:
        inspector = inspect(engine)
        schema_info = []
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            col_details = [f"{col['name']} ({col['type']})" for col in columns]
            schema_info.append(f"Table: {table_name}\nColumns: {', '.join(col_details)}")
        
        return SchemaData(schema_info="\n\n".join(schema_info))
    except Exception as e:
        logger.error(f"Failed to retrieve schema: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve database schema")

@router.post("/database/query", response_model=QueryData)
def execute_sql_query(payload: QueryRequest, db: Session = Depends(get_ro_db)):
    """
    Executes a SQL query securely and returns the rows.
    In a real production environment, this should enforce READ-ONLY connections.
    """
    logger.info(f"OpenAPI Tool Triggered: execute_sql_query")
    logger.info(f"AI requested execution of SQL: {payload.query}")
    try:
        # Prevent obvious destructive queries
        upper_query = payload.query.upper()
        if not upper_query.startswith(("SELECT", "PRAGMA")):
            raise HTTPException(status_code=403, detail="Only SELECT queries are allowed for Analytics Agent.")
        if any(word in upper_query for word in ["DROP ", "DELETE ", "TRUNCATE ", "ALTER ", "UPDATE ", "INSERT "]):
            raise HTTPException(status_code=403, detail="Data modification queries are forbidden.")
        
        result = db.execute(text(payload.query))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        
        return QueryData(columns=columns, rows=rows)
    except Exception as e:
        logger.error(f"Failed to execute query: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/metadata")
def get_metadata():
    """Returns available metrics, regions, industries, and stages for AI context."""
    return analytics.get_metadata()

@router.post("/pipeline_summary")
def get_pipeline_summary(payload: PipelineRequest):
    """Returns pipeline summary grouped by stage."""
    return analytics.get_pipeline_summary(payload.period, payload.region, payload.industry)

@router.post("/top_accounts")
def get_top_accounts(payload: TopAccountsRequest):
    """Returns top accounts ordered by annual revenue."""
    return analytics.get_top_accounts(payload.limit, payload.industry, payload.region)

@router.post("/interaction_metrics")
def get_interaction_metrics(payload: InteractionRequest):
    """Returns total interactions grouped by type."""
    return analytics.get_interaction_metrics(payload.account_name, payload.type)

@router.get("/sales_trends")
def get_sales_trends():
    """Returns aggregated opportunity amounts grouped by month."""
    return analytics.get_sales_trends()

@router.get("/dashboard_kpis")
def get_dashboard_kpis():
    """Returns high-level business KPIs."""
    return analytics.get_dashboard_kpis()

# --- HR / Employee Data Endpoints ---

@router.post("/hr_headcount")
def get_hr_headcount(payload: HRDepartmentRequest):
    """Returns active employee counts grouped by department."""
    return analytics.get_hr_headcount(payload.department_name)

@router.post("/hr_payroll_summary")
def get_hr_payroll_summary(payload: HRDepartmentRequest):
    """Returns total payroll salary grouped by department."""
    return analytics.get_hr_payroll_summary(payload.department_name)

@router.post("/hr_pto_summary")
def get_hr_pto_summary(payload: HRPtoRequest):
    """Returns PTO summary grouped by time off type."""
    return analytics.get_hr_pto_summary(payload.status, payload.department_name)
