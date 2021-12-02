import base64
import os
import json
import urllib.parse

from typing import List

from urllib import request
from fastapi import FastAPI
from pydantic import BaseModel


slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
if not slack_webhook_url:
    raise RuntimeError("SLACK_WEBHOOK_URL env variable not set")

api = FastAPI()


class SaleorChannel(BaseModel):
    id: str
    slug: str
    currency_code: str


class SaleorAddress(BaseModel):
    id: str
    first_name: str
    last_name: str
    company_name: str
    street_address_1: str
    street_address_2: str
    city: str
    city_area: str
    postal_code: str
    country: str
    country_area: str
    phone: str

    def __str__(self) -> str:
        bits = [
            self.company_name,
            self.street_address_1,
            self.street_address_2,
            self.city,
            self.city_area,
            self.postal_code,
            self.country,
        ]
        address = ", ".join([bit for bit in bits if len(bit) > 0])
        return f"{self.first_name} {self.last_name}, {address}"


class SaleorOrder(BaseModel):
    id: str
    channel: SaleorChannel
    shipping_address: SaleorAddress
    billing_address: SaleorAddress
    user_email: str

    @property
    def url(self) -> str:
        return f"http://localhost:9000/orders/{urllib.parse.quote(self.id)}"

    @property
    def id_number(self) -> int:
        return int(base64.b64decode(self.id).decode("utf-8").split(":")[1])


@api.post("/order_confirmed")
def order_confirmed(orders: List[SaleorOrder]):
    for order in orders:
        message = f"🛒 <{order.url}|Order #{order.id_number}> for customer {order.user_email} has been confirmed. Please check payment has been received before shipping."
        post_to_slack(slack_webhook_url, message)


@api.post("/order_fully_paid")
def order_fully_paid(orders: List[SaleorOrder]):
    for order in orders:
        message = f"💷 <{order.url}|Order #{order.id_number}> for customer {order.user_email} has been fully paid. Please ship to {order.shipping_address}"
        post_to_slack(slack_webhook_url, message)


@api.post("/order_fulfilled")
def order_fulfilled(orders: List[SaleorOrder]):
    for order in orders:
        message = f"📦 <{order.url}|Order #{order.id_number}> for customer {order.user_email} has been fulfilled."
        post_to_slack(slack_webhook_url, message)


def post_to_slack(webhook_url: str, message: str):
    """
    Writes a message to the slack channel associated `webhook_url` using Slack's
    Incoming Webhook API (https://api.slack.com/messaging/webhooks)
    """
    data = json.dumps({"text": message}).encode("utf-8")
    req = request.Request(webhook_url, data)
    req.add_header("Content-Type", "application/json")
    request.urlopen(req)
