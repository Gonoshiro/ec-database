from src.config import config
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient

credentials = service_account.Credentials.from_service_account_file(
    config.GA4_CREDENTIALS_PATH,
    scopes=['https://www.googleapis.com/auth/analytics.readonly']
)

client = BetaAnalyticsDataClient(credentials=credentials)

# 验证输出
print("GA4クライアント初期化が成功しました。:", type(client))
