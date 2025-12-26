import requests
from src.api.auth import auth
import logging
from typing import Dict, List, Optional
from datetime import date, datetime  

logger = logging.getLogger(__name__)
#logger = logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


class MakeshopClient:
    def __init__(self):
        self.endpoint = auth.endpoint
        self.headers = auth.get_headers()
        
    def execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """GraphQLクエリを実行"""
        print("QUERY:", query)
        print("VARIABLES:", variables)
        try:
            payload = {'query': query}
            if variables:
                payload['variables'] = variables
            
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def to_api_datetime(self,value: str) -> str:
        return datetime.strptime(value, "%Y%m%d%H%M%S") \
                    .strftime("%Y-%m-%d %H:%M:%S")


    #確定済み取得データ：
    #会員ID：memberId、都道府県：haddressAddr、ポイント:shopPoint、会員加入日：registrationDate、会員グループ指定：groupId、会社名：etc[0]、部署名：etc[1]
    def search_members(
        self,
        page: int = 1,
        limit: int = 1000,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict]:
        """会員情報を取得"""
        query = """
        query searchMember($input: SearchMemberRequest!) {
            searchMember(input: $input) {
                members {
                    memberId
                    haddressAddr
                    shopPoint
                    registrationDate
                    groupId
                    etc
                }
                searchedCount
                page
                limit
            }
        }
        """
        variables = {
            'input': {
                'page': page,
                'limit': limit
            }
        }
        
        if date_from:
            variables['input']['joinDateFrom'] = date_from
        if date_to:
            variables['input']['joinDateTo'] = date_to
        
        result = self.execute_query(query, variables)
        search_member = result.get('data', {}).get('searchMember', {})

        members = search_member.get("members", [])

        for m in members:
            # ---------- registrationDate / modified など、14桁の日付フォーマットの正規化 ----------
            for key in ("registrationDate", "modified"):
                value = m.get(key)
                if isinstance(value, str) and value.isdigit() and len(value) == 14:
                    try:
                        m[key] = datetime.strptime(
                            value, "%Y%m%d%H%M%S"
                        )
                    except ValueError:
                        logger.warning(
                            f"Invalid datetime format for member {m.get('memberId')} "
                            f"{key}: {value}"
                        )
                        m[key] = None

        return search_member
    
    def search_orders(
        self,
        page: int = 1,
        limit: int = 1000,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict]:
        """注文情報を取得"""
        query = """
        query searchOrder($input: SearchOrderRequest!) {
                searchOrder(input: $input) {
                    orders {
                        memberId
                        orderDate
                        systemOrderNumber
                        displayOrderNumber
                        deliveryInfos {
                            deliveryStatus
                            receiverPost
                            receiverPrefecture
                            shippingCharge
                            basketInfos {
                                productCode
                                productName
                                price
                                amount
                                variationName
                                productCustomCode
                                variationCustomCode
                            }
                        }
                        message
                    }
                }
        }
        """
        variables = {
        'input': {
            'page': page,
            'limit': limit
            }
        }
        if date_from:
            variables['input']['startOrderDate'] = date_from
        if date_to:
            variables['input']['endOrderDate'] = date_to
        result = self.execute_query(query, variables)
        search_order = result.get('data', {}).get('searchOrder', {})

        return search_order
#productId がない
    def search_products(
            self,
            page: int = 1, 
            limit: int = 1000, 
            date_from: Optional[str] = None,
            date_to: Optional[str] = None
    ) -> List[Dict]:
        """商品情報を取得"""
        query = """
        query searchProduct($input: SearchProductRequest!) {
            searchProduct(input: $input) {
                products {
                    systemCode
                    customCode
                    productName
                    productGroupCode
                    productGroupName
                    sellPrice
                    consumerPrice
                    taxRate
                    quantity
                    display
                    maker
                    janCode
                    categories {
                        categoryName
                        isMainCategory
                    }
                    createdAt
                    updatedAt
                }
                searchedCount
                page
                limit
            }
        }
        """
        variables = {
            'input': {
                'page': page,
                'limit': limit
            }
        }
        
        result = self.execute_query(query, variables)
        return result.get('data', {}).get('searchProduct', {})

client = MakeshopClient()