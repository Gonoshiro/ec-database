from src.sync.member_sync import member_sync
from src.sync.orders_sync import order_sync
from src.utils.logger import setup_logger
from datetime import datetime, timedelta
import sys

logger = setup_logger('daily_batch')

def main():
    """日次バッチ処理"""
    logger.info("=" * 50)
    logger.info("Daily batch started")
    logger.info("=" * 50)
    
    try:
        # 前日のデータを同期
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        today = datetime.now().strftime('%Y%m%d')
        # 会員データ同期
        logger.info("Syncing member data...")
        member_count = member_sync.sync(date_from=yesterday, date_to=today)
        logger.info(f"⭕Member sync completed: {member_count} records⭕")
        
        # 注文データ同期
        logger.info("Syncing order data...")
        order_count = order_sync.sync(
            start_date=f"{yesterday}000000",
            end_date=f"{today}235959"
        )
        logger.info(f"⭕Order sync completed: {order_count} records⭕")
        
        logger.info("=" * 50)
        logger.info("✅Daily batch completed successfully✅")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌Daily batch failed: {e}❌", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()