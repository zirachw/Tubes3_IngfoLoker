import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    """Manages MySQL database connections and query execution."""
    
    def __init__(self) -> None:
        """Initialize database connection parameters from environment variables."""
        
        self.host = os.getenv('MYSQL_HOST')
        self.port = int(os.getenv('MYSQL_PORT'))
        self.database = os.getenv('MYSQL_DATABASE')
        self.user = os.getenv('MYSQL_USER')
        self.password = os.getenv('MYSQL_PASSWORD')
        self.connection = None
    
    def connect(self) -> pymysql.connections.Connection:
        """Establish or return existing database connection.
        
        Returns:
            pymysql.connections.Connection: Active database connection
        """

        if not self.connection or not self.connection.open:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
        return self.connection
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """Execute SELECT query and return results.
        
        Args:
            query (str): SQL SELECT query
            params (tuple, optional): Query parameters
            
        Returns:
            list: Query results as list of dictionaries
        """

        connection = self.connect()
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE query.
        
        Args:
            query (str): SQL modification query
            params (tuple, optional): Query parameters
            
        Returns:
            int: Number of affected rows
        """

        connection = self.connect()
        with connection.cursor() as cursor:
            affected_rows = cursor.execute(query, params)
            connection.commit()
            return affected_rows
        
    def clear_data(self) -> None:
        """Clear all data from ATS tables and reset auto-increment counters."""

        self.execute_update("DELETE FROM ApplicationDetail")
        self.execute_update("DELETE FROM ApplicantProfile")
        self.execute_update("ALTER TABLE ApplicationDetail AUTO_INCREMENT = 1")
        self.execute_update("ALTER TABLE ApplicantProfile AUTO_INCREMENT = 1")
    
    def initialize_database(self, init_sql_path: str = "init.sql") -> None:
        """Re-initialize database by executing init.sql file.
        
        Args:
            init_sql_path (str): Path to the init.sql file
        """
        
        try:
            if not os.path.exists(init_sql_path):
                print(f"[Error] - init.sql file not found at: {init_sql_path}")
                return
            
            print(f"[Log] - Initializing database from {init_sql_path}")
            
            with open(init_sql_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            connection = self.connect()
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            with connection.cursor() as cursor:
                for statement in statements:
                    if statement:
                        try:
                            cursor.execute(statement)
                        except Exception as e:
                            print(f"[Warning] - Failed to execute statement: {e}")
                
                connection.commit()
            
            print("[Log] - Database initialization completed successfully")
            
        except Exception as e:
            print(f"[Error] - During database initialization: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def close(self) -> None:
        """Close database connection."""

        if self.connection:
            self.connection.close()
            self.connection = None