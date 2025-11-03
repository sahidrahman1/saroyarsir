"""
Database Configuration and Utilities - Python Implementation
MySQL database connection and utilities
"""
import os
import logging
from contextlib import contextmanager
from typing import Optional, Any, Dict, List
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from urllib.parse import quote_plus
import pymysql

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration management"""
    
    def __init__(self):
        self.database_url = self._build_database_url()
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        
    def _build_database_url(self) -> str:
        """Build database URL; prefer SQLite when forced.
        Falls back to MySQL legacy settings if not forcing SQLite.
        """
        force_sqlite = os.getenv('FORCE_SQLITE', 'true').lower() == 'true' or os.getenv('DB_ENGINE','').lower() == 'sqlite'
        if force_sqlite:
            base_dir = os.getenv('SQLITE_BASE_DIR') or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            db_path = os.path.join(base_dir, 'smartgardenhub.db')
            url = f"sqlite:///{db_path}"
            logger.info(f"Database URL configured (SQLite): {url}")
            return url

        # Legacy MySQL path
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '3306')
        db_name = os.getenv('DB_NAME', 'smartgardenhub')
        db_user = os.getenv('DB_USER', 'root')
        db_password = os.getenv('DB_PASSWORD', '')
        encoded_password = quote_plus(db_password) if db_password else ''
        if encoded_password:
            url = f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4&autocommit=false"
        else:
            url = f"mysql+pymysql://{db_user}@{db_host}:{db_port}/{db_name}?charset=utf8mb4&autocommit=false"
        logger.info(f"Database URL configured (MySQL legacy): mysql+pymysql://{db_user}@{db_host}:{db_port}/{db_name}")
        return url
    
    def initialize_engine(self) -> Engine:
        """Initialize SQLAlchemy engine with connection pooling"""
        if self.engine is None:
            # For SQLite reduce pooling params (they are mostly ignored by SQLite driver)
            if self.database_url.startswith('sqlite:'):
                self.engine = create_engine(
                    self.database_url,
                    connect_args={"check_same_thread": False},
                    echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
                )
            else:
                self.engine = create_engine(
                    self.database_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_timeout=30,
                    pool_recycle=3600,
                    pool_pre_ping=True,
                    echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
                )
            
            # Test connection
            try:
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info("Database connection established successfully")
            except Exception as e:
                logger.error(f"Database connection failed: {e}")
                raise
        
        return self.engine
    
    def get_session_factory(self) -> sessionmaker:
        """Get SQLAlchemy session factory"""
        if self.SessionLocal is None:
            if self.engine is None:
                self.initialize_engine()
            
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
        
        return self.SessionLocal

# Global database configuration instance
db_config = DatabaseConfig()

# Session management utilities
@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    SessionLocal = db_config.get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()

def get_session() -> Session:
    """Get a new database session"""
    SessionLocal = db_config.get_session_factory()
    return SessionLocal()

# Database utility functions
def execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Execute a raw SQL query and return results"""
    with get_db_session() as session:
        result = session.execute(text(query), params or {})
        
        # Convert result to list of dictionaries
        columns = result.keys()
        rows = result.fetchall()
        
        return [dict(zip(columns, row)) for row in rows]

def execute_update(query: str, params: Optional[Dict[str, Any]] = None) -> int:
    """Execute an UPDATE/INSERT/DELETE query and return affected rows"""
    with get_db_session() as session:
        result = session.execute(text(query), params or {})
        session.commit()
        return result.rowcount

def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database"""
    query = """
    SELECT COUNT(*) as count 
    FROM information_schema.tables 
    WHERE table_schema = DATABASE() 
    AND table_name = :table_name
    """
    
    result = execute_query(query, {'table_name': table_name})
    return result[0]['count'] > 0

def get_table_columns(table_name: str) -> List[Dict[str, str]]:
    """Get column information for a table"""
    query = """
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default,
        column_key
    FROM information_schema.columns 
    WHERE table_schema = DATABASE() 
    AND table_name = :table_name
    ORDER BY ordinal_position
    """
    
    return execute_query(query, {'table_name': table_name})

def backup_table(table_name: str, backup_suffix: Optional[str] = None) -> str:
    """Create a backup of a table"""
    if backup_suffix is None:
        from datetime import datetime
        backup_suffix = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    backup_table_name = f"{table_name}_backup_{backup_suffix}"
    
    query = f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name}"
    execute_update(query)
    
    logger.info(f"Table {table_name} backed up to {backup_table_name}")
    return backup_table_name

def drop_table_if_exists(table_name: str) -> bool:
    """Drop a table if it exists"""
    if check_table_exists(table_name):
        execute_update(f"DROP TABLE {table_name}")
        logger.info(f"Table {table_name} dropped")
        return True
    return False

def truncate_table(table_name: str) -> None:
    """Truncate a table (remove all data)"""
    execute_update(f"TRUNCATE TABLE {table_name}")
    logger.info(f"Table {table_name} truncated")

def get_database_info() -> Dict[str, Any]:
    """Get database information"""
    queries = {
        'version': "SELECT VERSION() as version",
        'database': "SELECT DATABASE() as database_name",
        'charset': "SELECT @@character_set_database as charset",
        'collation': "SELECT @@collation_database as collation",
        'tables': """
            SELECT table_name, table_rows, data_length, index_length
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            ORDER BY table_name
        """
    }
    
    info = {}
    for key, query in queries.items():
        try:
            result = execute_query(query)
            if key == 'tables':
                info[key] = result
            else:
                info[key] = result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting {key}: {e}")
            info[key] = None
    
    return info

# Transaction management
@contextmanager
def transaction():
    """Context manager for database transactions"""
    with get_db_session() as session:
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise

# Database health check
def health_check() -> Dict[str, Any]:
    """Perform database health check"""
    try:
        start_time = __import__('time').time()
        
        # Test basic connection
        result = execute_query("SELECT 1 as test, NOW() as timestamp")
        
        end_time = __import__('time').time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Get database info
        db_info = get_database_info()
        
        return {
            'status': 'healthy',
            'response_time_ms': round(response_time, 2),
            'database': db_info.get('database', {}).get('database_name'),
            'version': db_info.get('version', {}).get('version'),
            'charset': db_info.get('charset', {}).get('charset'),
            'table_count': len(db_info.get('tables', [])),
            'timestamp': result[0]['timestamp'].isoformat() if result else None
        }
    
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }

# Migration helpers
def create_migration_table():
    """Create migration tracking table"""
    query = """
    CREATE TABLE IF NOT EXISTS migrations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        filename VARCHAR(255) NOT NULL UNIQUE,
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        checksum VARCHAR(32),
        INDEX idx_filename (filename)
    ) ENGINE=InnoDB
    """
    execute_update(query)

def record_migration(filename: str, checksum: Optional[str] = None):
    """Record a migration as executed"""
    query = """
    INSERT IGNORE INTO migrations (filename, checksum) 
    VALUES (:filename, :checksum)
    """
    execute_update(query, {'filename': filename, 'checksum': checksum})

def is_migration_executed(filename: str) -> bool:
    """Check if a migration has been executed"""
    if not check_table_exists('migrations'):
        return False
    
    query = "SELECT COUNT(*) as count FROM migrations WHERE filename = :filename"
    result = execute_query(query, {'filename': filename})
    return result[0]['count'] > 0

# Initialize database connection on import
try:
    db_config.initialize_engine()
except Exception as e:
    logger.warning(f"Could not initialize database on import: {e}")