import re
import sys
import json
import mysql.connector
from mysql.connector import Error

VALID_COLUMNS = {
    "student.student_id", "student.name", "student.spi",
    "course.course_id", "course.course_name", "course.credits",
    "courseregistration.registration_id", "courseregistration.student_id", "courseregistration.course_id"
}

VALID_SORT_DIRECTIONS = {"ASC", "DESC"}

def validate_column(col):
    return col.lower() in VALID_COLUMNS

def build_and_execute_query(db_config, query_json_str):
    try:
        data = json.loads(query_json_str)
        
        columns = data.get("columns", [])
        if not columns or not all(validate_column(col) for col in columns):
            return
            
        projection = ", ".join(columns)
        
        base_sql = f"""SELECT {projection} 
FROM Student student
JOIN CourseRegistration courseregistration ON student.student_id = courseregistration.student_id
JOIN Course course ON courseregistration.course_id = course.course_id"""
        
        where_clauses = []
        params = []
        
        filters = data.get("where", {})
        for col, condition in filters.items():
            if not validate_column(col):
                return
                
            if isinstance(condition, dict):
                for op, val in condition.items():
                    op = op.upper()
                    if op == "=":
                        where_clauses.append(f"{col} = %s")
                        params.append(val)
                    elif op in [">", "<", ">=", "<="]:
                        where_clauses.append(f"{col} {op} %s")
                        params.append(val)
                    elif op == "LIKE":
                        where_clauses.append(f"{col} LIKE %s")
                        params.append(val)
            else:
                where_clauses.append(f"{col} = %s")
                params.append(condition)
                
        if where_clauses:
            base_sql += " WHERE " + " AND ".join(where_clauses)
            
        order_col = data.get("order_column")
        sort_dir = data.get("sort_direction", "ASC").upper()
        
        if order_col:
            if not validate_column(order_col) or sort_dir not in VALID_SORT_DIRECTIONS:
                return
            base_sql += f" ORDER BY {order_col} {sort_dir}"
            
        limit = data.get("limit", 10)
        if not (1 <= limit <= 1000):
            return
            
        base_sql += f" LIMIT {limit}"
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        cursor.execute(base_sql, params)
        results = cursor.fetchall()
        
        print("SQL_OK")
        for row in results:
            print(" ".join(str(val) for val in row))
            
    except (Error, json.JSONDecodeError, ValueError, TypeError):
        return
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    config = {
        'host': 'localhost',
        'database': 'university_db',
        'user': 'root',
        'password': 'password'
    }
    
    if len(sys.argv) > 1:
        build_and_execute_query(config, sys.argv[1])
