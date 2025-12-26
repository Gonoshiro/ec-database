from src.config import config
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.oauth2 import service_account
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
)

import csv

credentials = service_account.Credentials.from_service_account_file(
    config.GA4_CREDENTIALS_PATH,
    scopes=['https://www.googleapis.com/auth/analytics.readonly']
)

client = BetaAnalyticsDataClient(credentials=credentials)

request = RunReportRequest(
    property=f"properties/{config.GA4_PROPERTY_ID}",
    date_ranges=[DateRange(start_date="2025-12-15", end_date="2025-12-17")],
    dimensions=[
        Dimension(name="date"),
        Dimension(name="sessionSourceMedium"),
        Dimension(name="deviceCategory"),
    ],
    metrics=[
        Metric(name="sessions"),
        Metric(name="totalUsers"),
        Metric(name="screenPageViews"),
        Metric(name="conversions"),
        Metric(name="totalRevenue"),
    ],
)

response = client.run_report(request)

# テスト出力
print("date | source / medium | device | sessions | users | pageviews | conversions | revenue")
print("-" * 90)

for row in response.rows:
    print(
        row.dimension_values[0].value, "|",
        row.dimension_values[1].value, "|",
        row.dimension_values[2].value, "|",
        row.metric_values[0].value, "|",
        row.metric_values[1].value, "|",
        row.metric_values[2].value, "|",
        row.metric_values[3].value, "|",
        row.metric_values[4].value,
    )

output_file = "ga4_runreport_standard.csv"

with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    # CSV構造
    writer.writerow([
        "date",
        "sessionSourceMedium",
        "deviceCategory",
        "sessions",
        "totalUsers",
        "screenPageViews",
        "conversions",
        "totalRevenue",
    ])

    # 行当たりのデータ出力
    for row in response.rows:
        writer.writerow([
            row.dimension_values[0].value,  # date
            row.dimension_values[1].value,  # sessionSourceMedium
            row.dimension_values[2].value,  # deviceCategory
            row.metric_values[0].value,     # sessions
            row.metric_values[1].value,     # totalUsers
            row.metric_values[2].value,     # screenPageViews
            row.metric_values[3].value,     # conversions
            row.metric_values[4].value,     # totalRevenue
        ])

print(f"CSV file generated: {output_file}")