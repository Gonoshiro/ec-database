import os
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
)
from google.oauth2 import service_account
import pandas as pd
import pendulum
from sqlalchemy import create_engine
from loguru import logger

class GA4Sync:
    def __init__(self):
        self.property_id = os.getenv('GA4_PROPERTY_ID')
        self.credentials_path = os.getenv('GA4_CREDENTIALS_PATH')
        self.db_url = os.getenv('DATABASE_URL')
        self.timezone = os.getenv('GA4_TIMEZONE', 'Asia/Tokyo')
        
        # 認証
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        self.client = BetaAnalyticsDataClient(credentials=credentials)
        self.engine = create_engine(self.db_url)
    
    def get_sessions_data(self, date):
        """セッションデータを取得"""
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(
                start_date=date.strftime('%Y-%m-%d'),
                end_date=date.strftime('%Y-%m-%d')
            )],
            dimensions=[
                Dimension(name="date"),
                Dimension(name="sessionSourceMedium"),
                Dimension(name="deviceCategory"),
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="screenPageViews"),
                Metric(name="conversions"),
                Metric(name="totalRevenue"),
            ],
        )
        
        response = self.client.run_report(request)
        return self._parse_response(response)