import re
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class SQLExecutionService:
    def __init__(self, db: Session, scope):
        self.db = db
        self.scope = scope
    
    def execute_query(self, sql: str) -> dict[str, Any]:
        """Execute a read-only SQL query and return results."""
        if not self._is_safe_query(sql):
            return {
                "success": False,
                "error": "Query contains unsafe operations. Only SELECT statements are allowed.",
                "rows": [],
                "columns": []
            }
        
        sql_with_params = self._inject_scope_parameters(sql)
        
        try:
            result = self.db.execute(text(sql_with_params))
            
            if result.returns_rows:
                columns = list(result.keys())
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                
                return {
                    "success": True,
                    "rows": rows,
                    "columns": columns,
                    "row_count": len(rows)
                }
            else:
                return {
                    "success": False,
                    "error": "Query did not return any rows",
                    "rows": [],
                    "columns": []
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "rows": [],
                "columns": []
            }
    
    def _is_safe_query(self, sql: str) -> bool:
        """Check if query is read-only."""
        sql_upper = sql.upper().strip()
        
        dangerous_keywords = [
            "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
            "TRUNCATE", "REPLACE", "MERGE", "GRANT", "REVOKE"
        ]
        
        for keyword in dangerous_keywords:
            if re.search(rf'\b{keyword}\b', sql_upper):
                return False
        
        if not sql_upper.startswith("SELECT"):
            return False
        
        return True
    
    def _inject_scope_parameters(self, sql: str) -> str:
        """Replace placeholders with actual scope values."""
        if not self.scope:
            return sql
        
        sql = sql.replace("{realm_id}", str(self.scope.realm_id))
        
        if self.scope.is_store_manager and self.scope.assigned_store_id:
            sql = sql.replace("{assigned_store_id}", str(self.scope.assigned_store_id))
        
        return sql
