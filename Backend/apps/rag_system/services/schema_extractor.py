"""
Automatic Schema Extractor - Generates schema documentation from PostgreSQL
This runs ONCE to extract all table information automatically
"""

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from typing import List, Dict
import json


class SchemaExtractor:
    """Extracts schema information from PostgreSQL database"""
    
    def __init__(self, db: Session):
        self.db = db
        self.inspector = inspect(db.bind)
    
    def get_all_tables(self) -> List[str]:
        """Get all table names from database"""
        return self.inspector.get_table_names()
    
    def get_table_columns(self, table_name: str) -> List[Dict]:
        """Get detailed column information for a table"""
        columns = self.inspector.get_columns(table_name)
        
        column_info = []
        for col in columns:
            column_info.append({
                "name": col['name'],
                "type": str(col['type']),
                "nullable": col['nullable'],
                "default": str(col['default']) if col['default'] else None,
                "primary_key": col.get('primary_key', False)
            })
        
        return column_info
    
    def get_foreign_keys(self, table_name: str) -> List[Dict]:
        """Get foreign key relationships"""
        try:
            fks = self.inspector.get_foreign_keys(table_name)
            return fks
        except:
            return []
    
    def get_table_comment(self, table_name: str) -> str:
        """Get table comment/description if exists"""
        try:
            result = self.db.execute(text(f"""
                SELECT obj_description('{table_name}'::regclass, 'pg_class') as comment
            """))
            row = result.fetchone()
            return row[0] if row and row[0] else ""
        except:
            return ""
    
    def get_sample_data(self, table_name: str, limit: int = 3) -> List[Dict]:
        """Get sample rows from table"""
        try:
            result = self.db.execute(text(f"""
                SELECT * FROM {table_name} 
                WHERE deleted = FALSE 
                LIMIT {limit}
            """))
            
            columns = result.keys()
            rows = result.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
        except:
            # If table doesn't have 'deleted' column or query fails
            try:
                result = self.db.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
                columns = result.keys()
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            except:
                return []
    
    def generate_table_documentation(self, table_name: str) -> str:
        """Generate comprehensive documentation for a table"""
        
        # Get table information
        columns = self.get_table_columns(table_name)
        foreign_keys = self.get_foreign_keys(table_name)
        comment = self.get_table_comment(table_name)
        sample_data = self.get_sample_data(table_name, limit=2)
        
        # Build documentation
        doc = f"""
TABLE: {table_name}
{'=' * 80}

"""
        
        if comment:
            doc += f"Description: {comment}\n\n"
        
        # Columns section
        doc += "COLUMNS:\n"
        doc += "-" * 80 + "\n"
        
        primary_keys = [col['name'] for col in columns if col.get('primary_key')]
        
        for col in columns:
            pk_marker = " [PRIMARY KEY]" if col['name'] in primary_keys else ""
            nullable_marker = " [NULLABLE]" if col['nullable'] else " [NOT NULL]"
            
            doc += f"- {col['name']}: {col['type']}{pk_marker}{nullable_marker}\n"
            if col['default']:
                doc += f"  Default: {col['default']}\n"
        
        # Foreign Keys section
        if foreign_keys:
            doc += f"\nRELATIONSHIPS:\n"
            doc += "-" * 80 + "\n"
            for fk in foreign_keys:
                doc += f"- {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}\n"
        
        # Common queries section
        doc += f"\nCOMMON QUERIES:\n"
        doc += "-" * 80 + "\n"
        
        # Count query
        has_deleted = any(col['name'] == 'deleted' for col in columns)
        where_clause = "WHERE deleted = FALSE" if has_deleted else ""
        
        doc += f"""
Count all records:
SELECT COUNT(*) as total FROM {table_name} {where_clause}

List all records:
SELECT * FROM {table_name} {where_clause} LIMIT 100

"""
        
        # Add foreign key JOIN examples
        if foreign_keys:
            doc += "Queries with relationships:\n"
            for fk in foreign_keys[:2]:  # Show first 2 FKs
                ref_table = fk['referred_table']
                doc += f"""
SELECT t.*, r.* 
FROM {table_name} t
LEFT JOIN {ref_table} r ON t.{fk['constrained_columns'][0]} = r.{fk['referred_columns'][0]}
{where_clause}
"""
        
        # Sample data section (for context)
        if sample_data:
            doc += f"\nSAMPLE DATA STRUCTURE (for reference only):\n"
            doc += "-" * 80 + "\n"
            # Show only column names and types from sample
            if sample_data:
                sample = sample_data[0]
                doc += "Example fields: " + ", ".join(sample.keys()) + "\n"
        
        doc += "\n" + "=" * 80 + "\n\n"
        
        return doc
    
    def generate_query_patterns(self) -> str:
        """Generate common query patterns documentation"""
        
        return """
QUERY PATTERNS AND BEST PRACTICES
='=' * 80

COUNTING QUERIES:
1. Count all records in a table:
   SELECT COUNT(*) as total FROM table_name WHERE deleted = FALSE
   
2. Count with grouping:
   SELECT category, COUNT(*) as total 
   FROM table_name 
   WHERE deleted = FALSE 
   GROUP BY category

3. Count distinct values:
   SELECT COUNT(DISTINCT column_name) FROM table_name WHERE deleted = FALSE

FILTERING PATTERNS:
1. Text search (case-insensitive):
   WHERE column_name ILIKE '%search_term%'
   
2. Date range:
   WHERE date_column BETWEEN '2024-01-01' AND '2024-12-31'
   
3. Multiple conditions:
   WHERE condition1 = value1 AND condition2 = value2

4. NULL checks:
   WHERE column_name IS NOT NULL

AGGREGATION QUERIES:
1. Average:
   SELECT AVG(numeric_column) as average FROM table_name WHERE deleted = FALSE
   
2. Sum:
   SELECT SUM(numeric_column) as total FROM table_name WHERE deleted = FALSE
   
3. Max/Min:
   SELECT MAX(column), MIN(column) FROM table_name WHERE deleted = FALSE

SORTING:
1. ORDER BY column_name ASC  (ascending)
2. ORDER BY column_name DESC (descending)
3. ORDER BY date_column DESC LIMIT 10 (most recent 10)

IMPORTANT RULES:
- Always include "deleted = FALSE" for tables with soft delete
- Use ILIKE for case-insensitive text matching in PostgreSQL
- Use COUNT(*) not COUNT(column) for counting all rows
- For counting entities, query the MAIN entity table, not junction tables
- Use LEFT JOIN when you want all records even if relationship doesn't exist
- Use INNER JOIN when you only want records with matching relationships
- Always add LIMIT clause for safety (LIMIT 100 or LIMIT 1000)

JUNCTION TABLES:
- Junction tables (like class_subjects) link multiple tables together
- DO NOT use junction tables for counting main entities
- Example: To count teachers, use teacher_profiles table, NOT class_subjects

='=' * 80
"""
    
    def extract_all_schemas(self) -> List[Dict]:
        """Extract documentation for all tables"""
        
        print("Extracting schemas from PostgreSQL database...")
        
        tables = self.get_all_tables()
        print(f"Found {len(tables)} tables")
        
        schema_docs = []
        
        # Add general query patterns first
        schema_docs.append({
            "content": self.generate_query_patterns(),
            "metadata": {
                "type": "query_patterns",
                "category": "general",
                "table": "all"
            }
        })
        
        # Process each table
        for i, table_name in enumerate(tables, 1):
            print(f"Processing {i}/{len(tables)}: {table_name}")
            
            try:
                doc = self.generate_table_documentation(table_name)
                
                # Determine category based on table name
                category = self._categorize_table(table_name)
                
                schema_docs.append({
                    "content": doc,
                    "metadata": {
                        "type": "schema_documentation",
                        "table": table_name,
                        "category": category
                    }
                })
                
            except Exception as e:
                print(f"  ⚠ Error processing {table_name}: {e}")
                continue
        
        print(f"\n✓ Successfully extracted {len(schema_docs)} schema documents")
        return schema_docs
    
    def _categorize_table(self, table_name: str) -> str:
        """Categorize table based on name"""
        name_lower = table_name.lower()
        
        if 'teacher' in name_lower or 'staff' in name_lower:
            return 'teachers'
        elif 'student' in name_lower:
            return 'students'
        elif 'class' in name_lower or 'course' in name_lower:
            return 'classes'
        elif 'subject' in name_lower:
            return 'subjects'
        elif 'attendance' in name_lower:
            return 'attendance'
        elif 'grade' in name_lower or 'mark' in name_lower or 'exam' in name_lower:
            return 'academics'
        elif 'fee' in name_lower or 'payment' in name_lower:
            return 'finance'
        elif 'user' in name_lower or 'employee' in name_lower:
            return 'users'
        else:
            return 'general'
    
    def save_to_file(self, schema_docs: List[Dict], filename: str = "schema_docs.json"):
        """Save extracted schemas to file for review"""
        with open(filename, 'w') as f:
            json.dump(schema_docs, f, indent=2, default=str)
        print(f"✓ Saved schemas to {filename}")


# Example usage function
def extract_and_save_schemas(db: Session):
    """Main function to extract schemas"""
    extractor = SchemaExtractor(db)
    schema_docs = extractor.extract_all_schemas()
    extractor.save_to_file(schema_docs)
    return schema_docs