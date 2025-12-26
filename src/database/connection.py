from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.config import config
import logging
import urllib.parse

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # URL encode
        params = urllib.parse.quote_plus(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={config.DB_HOST},{config.DB_PORT};"
            f"DATABASE={config.DB_NAME};"
            f"UID={config.DB_USER};"
            f"PWD={config.DB_PASSWORD};"
            "TrustServerCertificate=yes;"
        )

        self.engine = create_engine(
            f"mssql+pyodbc:///?odbc_connect={params}",
            echo=(config.LOG_LEVEL == 'DEBUG'),
            fast_executemany=True
        )

        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    def test_connection(self):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT @@VERSION"))
                version = result.fetchone()[0]
                logger.info(f"Database connection successful: {version}")
                print("✅ Database connection Success")
                return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            print("❌ Database connection Failed")
            return False


db = Database()
