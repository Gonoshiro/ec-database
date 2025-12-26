import logging
logging.basicConfig(level=logging.INFO, force=True)
for name in (
    "sqlalchemy",
    "sqlalchemy.engine",
    "sqlalchemy.engine.Engine",
):
    logger_ = logging.getLogger(name)
    logger_.handlers.clear()
    logger_.setLevel(logging.WARNING)
    logger_.propagate = False
from src.api.makeshop_client import client
from src.database.connection import db
from sqlalchemy import text, bindparam, Unicode
from datetime import datetime
logger = logging.getLogger(__name__)


class OrderSync:
    def __init__(self):
        self.client = client
        self.db = db
    
    def sync(self, start_date: str = None, end_date: str = None):
        """注文データを同期"""
        logger.info(f"Starting order sync: from={start_date}, to={end_date}")
        
        page = 1
        total_synced = 0
        
        while True:
            # APIから注文データ取得
            result = self.client.search_orders(
                page=page,
                limit=1000,
                date_from=start_date,
                date_to=end_date
            )
            orders = result.get('orders', [])
            if not orders:
                break
            
            # データベースに保存
            session = self.db.get_session()
            try:
                for order in orders:
                    self._upsert_order(session, order)
                session.commit()
                total_synced += len(orders)
                logger.info(f"Synced page {page}: {len(orders)} orders")
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to sync orders page {page}: {e}")
                raise
            finally:
                session.close()
            
            # 次のページへ
            if len(orders) < 1000:
                break
            page += 1
        
        logger.info(f"order sync completed: {total_synced} orders synced")
        return total_synced
    
    def _upsert_order(self, session, order: dict):

        query = text("""
            MERGE INTO orders AS target
            USING (
                SELECT
                    :system_order_number AS system_order_number,
                    :order_date AS order_date,
                    :display_order_number AS display_order_number,
                    CAST(:delivery_status AS NVARCHAR(50)) AS delivery_status,
                    CAST(:member_id AS NVARCHAR(50)) AS member_id,
                    :receiver_post AS receiver_post,
                    CAST(:receiver_address AS NVARCHAR(50)) AS receiver_address,
                    CAST(:product_name AS NVARCHAR(50)) AS product_name,
                    :product_sell_price AS product_sell_price,
                    :amount AS amount,
                    CAST(:variation_name AS NVARCHAR(50)) AS variation_name,
                    CAST(:product_custom_code AS NVARCHAR(50)) AS product_custom_code,
                    CAST(:variation_custom_code AS NVARCHAR(50)) AS variation_custom_code,
                    :shipping_charge AS shipping_charge,
                    CAST(:message AS NVARCHAR(50)) AS message
            ) AS source
            ON target.system_order_number = source.system_order_number

            WHEN MATCHED THEN
                UPDATE SET
                    order_date = source.order_date,
                    display_order_number = source.display_order_number, 
                    delivery_status = source.delivery_status,
                    member_id = source.member_id,
                    receiver_post = source.receiver_post,
                    receiver_address = source.receiver_address,
                    product_name = source.product_name,
                    product_sell_price = source.product_sell_price,
                    amount = source.amount,
                    variation_name = source.variation_name,
                    product_custom_code = source.product_custom_code,
                    variation_custom_code = source.variation_custom_code,
                    shipping_charge = source.shipping_charge,
                    message = source.message,
                    updated_at = CURRENT_TIMESTAMP

            WHEN NOT MATCHED THEN
                INSERT (
                    system_order_number, order_date, display_order_number, delivery_status, member_id, 
                    receiver_post, receiver_address, product_name, product_sell_price, 
                    amount, variation_name, product_custom_code, variation_custom_code, 
                    shipping_charge, message, updated_at
                )
                VALUES (
                    source.system_order_number, source.order_date, source.display_order_number, 
                    source.delivery_status, source.member_id, 
                    source.receiver_post, source.receiver_address, 
                    source.product_name, source.product_sell_price, source.amount, 
                    source.variation_name, source.product_custom_code, source.variation_custom_code, source.shipping_charge, 
                    source.message, CURRENT_TIMESTAMP
                );
        """)
        print(type(order))
        session.execute(query, {
            'system_order_number': order.get('systemOrderNumber'),
            'order_date': order.get('orderDate'),
            'display_order_number': order.get('displayOrderNumber'),
            'delivery_status': order.get("deliveryInfos", [{}])[0].get("deliveryStatus"),
            'member_id': order.get('memberId'),
            'receiver_post': order.get("deliveryInfos", [{}])[0].get("receiverPost"),
            'receiver_address': order.get("deliveryInfos", [{}])[0].get("receiverPrefecture"),
            'product_name': order.get("deliveryInfos", [{}])[0].get("basketInfos", [{}])[0].get("productName"),
            'product_sell_price': order.get("deliveryInfos", [{}])[0].get("basketInfos", [{}])[0].get("price"),
            'amount': order.get("deliveryInfos", [{}])[0].get("basketInfos", [{}])[0].get("amount"),
            'variation_name': order.get("deliveryInfos", [{}])[0].get("basketInfos", [{}])[0].get("variationName"),
            'product_custom_code': order.get("deliveryInfos", [{}])[0].get("basketInfos", [{}])[0].get("productCustomCode"),
            'variation_custom_code': order.get("deliveryInfos", [{}])[0].get("basketInfos", [{}])[0].get("variationCustomCode"),
            'shipping_charge': order.get("deliveryInfos", [{}])[0].get("shippingCharge"),
            'message': order.get('message').split('||', 1)[0]
        })

order_sync = OrderSync()