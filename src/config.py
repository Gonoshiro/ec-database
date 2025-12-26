import os
from dotenv import load_dotenv

load_dotenv(".env.local")

class Config:
    # Makeshop API
    MAKESHOP_API_TOKEN = os.getenv('MAKESHOP_API_TOKEN')
    MAKESHOP_SHOP_ID = os.getenv('MAKESHOP_SHOP_ID')
    MAKESHOP_API_ENDPOINT = os.getenv('MAKESHOP_API_ENDPOINT', 'https://api.makeshop.jp/graphql')
    MAKESHOP_API_SECRET = os.getenv('MAKESHOP_API_SECRET')
    MAKESHOP_API_KEY = os.getenv('MAKESHOP_API_KEY')
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'ec_database')
    DB_USER = os.getenv('DB_USER', 'ec_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    # GA4
    GA4_PROPERTY_ID = os.getenv('GA4_PROPERTY_ID')
    GA4_CREDENTIALS_PATH = os.getenv('GA4_CREDENTIALS_PATH')
    #ここは要修正 DATABASE_URL = os.getenv('')
    
    # Application
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    @property
    def DATABASE_URL(self):
        return (
            "mssql+pyodbc://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            "?driver=ODBC+Driver+18+for+SQL+Server"
            "&TrustServerCertificate=yes"
        )

config = Config()