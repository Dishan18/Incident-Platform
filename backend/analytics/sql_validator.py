"""
SQL Validation Module.
Enforces read-only SELECT queries on the incidents dataset.
"""

import re
import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


def validate_sql(sql_query: str) -> tuple[bool, str]:
    """Validate that the query contains exactly one SELECT statement and is safe to run.

    Parameters
    ----------
    sql_query : str
        The SQL query input.

    Returns
    -------
    tuple[bool, str]
        (is_valid, error_message)
    """
    cleaned_sql = sql_query.strip().rstrip(";").strip()
    if not cleaned_sql:
        return False, "SQL query is empty."

    # 1. Broad keyword block check (pre-parse defense-in-depth)
    forbidden_keywords = [
        "insert", "update", "delete", "drop", "alter", "create",
        "truncate", "merge", "exec", "copy", "grant", "revoke"
    ]
    sql_lower = cleaned_sql.lower()
    for kw in forbidden_keywords:
        pattern = rf"\b{kw}\b"
        if re.search(pattern, sql_lower):
            return False, f"Forbidden SQL operation keyword detected: '{kw}'."

    # 2. Check for system catalogs or schemas
    system_patterns = ["pg_catalog", "information_schema"]
    for pattern in system_patterns:
        if pattern in sql_lower:
            return False, f"Access to system catalog/schema '{pattern}' is forbidden."

    # 3. Parse SQL using sqlglot
    try:
        expressions = sqlglot.parse(cleaned_sql)
        if len(expressions) != 1:
            return False, f"Exactly one statement is allowed. Found {len(expressions)} statements."

        expression = expressions[0]
        if not expression:
            return False, "Failed to parse SQL query."

        # AST-level validation
        forbidden_node_types = {
            exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Alter, exp.Create,
            exp.Merge, exp.Command, exp.Transaction
        }

        for node in expression.walk():
            # Check node class types
            if type(node) in forbidden_node_types:
                return False, f"Forbidden SQL operation class type detected: {type(node).__name__}."

            # Check table access for system objects
            if isinstance(node, exp.Table):
                table_name = node.name.lower() if node.name else ""
                db_name = node.db.lower() if node.db else ""
                if db_name in ["pg_catalog", "information_schema"] or table_name.startswith("pg_"):
                    return False, f"Access to system table or schema is forbidden: '{table_name}'."

        # Enforce that the query must be SELECT, UNION, or Subquery (wrapping select)
        is_select_query = isinstance(expression, (exp.Select, exp.Union, exp.Subquery))
        if not is_select_query:
            # Check if wrapped inside CTE/With block
            if isinstance(expression, exp.Expression) and hasattr(expression, "this") and isinstance(expression.this, (exp.Select, exp.Union)):
                is_select_query = True
            elif expression.__class__.__name__ in ["Select", "Union"]:
                is_select_query = True

        if not is_select_query:
            return False, f"Only SELECT statements are allowed. Found query type: {expression.__class__.__name__}."

    except ParseError as pe:
        return False, f"SQL syntax parsing error: {str(pe)}"
    except Exception as e:
        return False, f"Unexpected validation error: {str(e)}"

    return True, ""
