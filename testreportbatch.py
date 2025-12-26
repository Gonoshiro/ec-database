from src.config import config
from datetime import date, timedelta
from openpyxl import Workbook
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.oauth2 import service_account
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
)

import csv
import os

credentials = service_account.Credentials.from_service_account_file(
    config.GA4_CREDENTIALS_PATH,
    scopes=['https://www.googleapis.com/auth/analytics.readonly']
)

client = BetaAnalyticsDataClient(credentials=credentials)

#タイムスコープ:昨日一日中のデータ
yesterday = date.today() - timedelta(days=1)
date_str = yesterday.strftime("%Y-%m-%d")

#セッション、イベント、ページビュー、コンバージョン、トラフィックソースごとのレポートを定義する
REPORT_DEFINITIONS = [
    {
        "name": "session",
        "dimensions": [
            "date",
            "sessionSourceMedium",
            "deviceCategory",
        ],
        "metrics": [
            "sessions",
            "totalUsers",
        ],
    },
    {
        "name": "event",
        "dimensions": [
            "date",
            "eventName",
        ],
        "metrics": [
            "eventCount",
            "screenPageViews",
            "conversions",
        ],
    },
    {
        "name": "page",
        "dimensions": [
            "date",
            "pagePath",
        ],
        "metrics": [
            "screenPageViews",
        ],
    },
    {
        "name": "conversion",
        "dimensions": [
            "date",
            "eventName",
        ],
        "metrics": [
            "conversions",
            "eventCount",
        ],
    },
    {
        "name": "traffic_source",
        "dimensions": [
            "date",
            "sessionSource",
            "sessionMedium",
            "sessionCampaignName",
        ],
        "metrics": [
            "sessions",
            "totalUsers",
        ],
    },


]

# 実行して、レポートをまとめたxlsxファイルをエキスポートする
xlsx_name = f"ga4_report_{date_str}.xlsx"
xlsx_path = os.path.join(os.getcwd(), xlsx_name)

wb = Workbook()
# デフォルトのシートの削除
wb.remove(wb.active)

for report in REPORT_DEFINITIONS:
    print(f"Running report: {report['name']}")

    request = RunReportRequest(
        property=f"properties/{config.GA4_PROPERTY_ID}",
        date_ranges=[
            DateRange(
                start_date=date_str,
                end_date=date_str,
            )
        ],
        dimensions=[Dimension(name=d) for d in report["dimensions"]],
        metrics=[Metric(name=m) for m in report["metrics"]],
    )

    response = client.run_report(request)

    # =====================
    # レポートごとシート1枚を用意する
    # =====================
    ws = wb.create_sheet(title=report["name"][:31])  

    headers = (
        [h.name for h in response.dimension_headers]
        + [h.name for h in response.metric_headers]
    )

    # ディメンション名とメトリック名
    ws.append(headers)

    # データ
    for row in response.rows:
        dimension_values = [v.value for v in row.dimension_values]
        metric_values = [v.value for v in row.metric_values]
        ws.append(dimension_values + metric_values)

    print(f"  -> Sheet generated: {report['name']}")

#  XLSXファイルの保存
wb.save(xlsx_path)

print(f"All reports finished. XLSX generated: {xlsx_name}")