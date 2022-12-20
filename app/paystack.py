from app.config import setting
import requests

class PayStack:

    paystack_secret_key = setting.paystack_secret_key
    base_url = "https://api.paystack.co"

    def verify_payment(self, ref, amount):
        path = f"/transaction/verify/{ref}"

        headers= {
            "Authorization" : f"Bearer {self.paystack_secret_key}",
            "Content-Type" : "application/json"
        }
        full_url= self.base_url + path

        response = requests.get(full_url, headers = headers)
        if response.json()["status"]:
            return response.json()["status"], response.json()["data"]
        return response.json()["status"], response.json()["message"]