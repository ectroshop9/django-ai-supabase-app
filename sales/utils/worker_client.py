import requests
import secrets
import json
from django.conf import settings

class CloudflareWorkerClient:
    def __init__(self):
        self.worker_url = settings.CLOUDFLARE_WORKER_URL.rstrip('/')
        self.api_secret = settings.CLOUDFLARE_WORKER_SECRET
    
    def create_protected_link(self, file_url, metadata=None):
        """
        إنشاء رابط محمي عبر Cloudflare Worker
        """
        if not settings.CLOUDFLARE_WORKER_ENABLED:
            return {
                "success": False,
                "error": "Cloudflare Worker غير مفعل"
            }
        
        token = secrets.token_urlsafe(32)
        
        payload = {
            "token": token,
            "file_url": file_url,
            "expires_hours": 2,
            "metadata": metadata or {}
        }
        
        try:
            response = requests.post(
                f"{self.worker_url}/_api/store",
                headers={
                    "X-API-Secret": self.api_secret,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "token": token,
                    "download_url": f"{self.worker_url}/d/{token}",
                    "expires_at": data.get("expires_at")
                }
            else:
                return {
                    "success": False,
                    "error": f"خطأ من Worker: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"فشل الاتصال: {str(e)}"
            }
