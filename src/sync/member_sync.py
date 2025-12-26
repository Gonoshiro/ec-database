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

class MemberSync:
    def __init__(self):
        self.client = client
        self.db = db
    
    def sync(self, date_from: str = None, date_to: str = None):
        """会員データを同期"""
        logger.info(f"Starting member sync: from={date_from}, to={date_to}")
        
        page = 1
        total_synced = 0
        
        while True:
            # APIから会員データ取得
            result = self.client.search_members(
                page=page,
                limit=1000,
                date_from=date_from,
                date_to=date_to
            )
            
            members = result.get('members', [])
            if not members:
                break
            
            # データベースに保存
            session = self.db.get_session()
            try:
                for member in members:
                    self._upsert_member(session, member)
                session.commit()
                total_synced += len(members)
                logger.info(f"Synced page {page}: {len(members)} members")
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to sync members page {page}: {e}")
                raise
            finally:
                session.close()
            
            # 次のページへ
            if len(members) < 1000:
                break
            page += 1
        
        logger.info(f"Member sync completed: {total_synced} members synced")
        return total_synced
    
    def _upsert_member(self, session, member: dict):

        query = text("""
            MERGE INTO members AS target
            USING (
                SELECT
                    :member_id AS member_id,
                    CAST(:prefecture AS NVARCHAR(50)) AS prefecture,
                    :shop_point AS shop_point,
                    :registration_date AS registration_date,
                    :group_id AS group_id,
                    CAST(:company_name AS NVARCHAR(50)) AS company_name,
                    CAST(:department_name AS NVARCHAR(50)) AS department_name
            ) AS source
            ON target.member_id = source.member_id

            WHEN MATCHED THEN
                UPDATE SET
                    prefecture = source.prefecture,
                    shop_point = source.shop_point,
                    registration_date = source.registration_date,
                    group_id = source.group_id,
                    company_name = source.company_name,
                    department_name = source.department_name,
                    updated_at = CURRENT_TIMESTAMP

            WHEN NOT MATCHED THEN
                INSERT (
                    member_id, prefecture, shop_point, registration_date, group_id, company_name, department_name, updated_at
                )
                VALUES (
                    source.member_id, source.prefecture, source.shop_point, source.registration_date, source.group_id,
                    source.company_name, source.department_name, CURRENT_TIMESTAMP
                );
        """)

        session.execute(query, {
            'member_id': member.get('memberId'),
            'prefecture': member.get('haddressAddr'),
            'shop_point': member.get('shopPoint'),
            'registration_date': member.get('registrationDate'),
            'group_id': member.get('groupId'),
            'company_name': (member.get("etc") or [None])[0],
            'department_name': (member.get("etc") or [None,None])[1]
        })

member_sync = MemberSync()