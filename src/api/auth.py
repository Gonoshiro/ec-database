import requests
from src.config import config
import logging
import time
import json
import hmac
import hashlib


logger = logging.getLogger(__name__)

class MakeshopAuth:
    def __init__(self):
        query = """
            query {
                getShop {
                    shop {
                        shopId
                        shopName
                    }
                }
            }
            """
        self.api_token = config.MAKESHOP_API_TOKEN
        self.api_secret = config.MAKESHOP_API_SECRET   
        self.endpoint = config.MAKESHOP_API_ENDPOINT
        self._debug_delivery_setting_called = False    #事后删除

        

    def generate_signature(self, timestamp):
        return hmac.new(
            self.api_secret.encode('utf-8'),
            timestamp.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def get_headers(self):
        timestamp = str(int(time.time()))
        signature = self.generate_signature(timestamp)

        return {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'x-timestamp': timestamp,
            'x-signature': signature,
            'x-api-key': config.MAKESHOP_API_KEY
        }

    def test_connection(self):
        try:
            response = requests.post(
                self.endpoint,
                headers=self.get_headers(), 
                timeout=30
            )

            response.raise_for_status()
            data = response.json()
            logger.info(f"API connection successful: {data}")
            print("✅ API Authentication Success")
            return True

        except Exception as e:
            logger.error(f"API connection failed: {e}")
            print("❌ API Authentication Failed")
            return False

auth = MakeshopAuth()
