import os
import json
from typing import Any, List, Optional

from urllib import request
from fastapi import FastAPI, Request
from pydantic import BaseModel

slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
if not slack_webhook_url:
    raise RuntimeError("SLACK_WEBHOOK_URL env variable not set")

api = FastAPI()


class SaleorCustomerUpdatedPayload(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str


@api.post("/customer_updated")
def customer_updated(customers: List[SaleorCustomerUpdatedPayload]):
    for customer in customers:
        message = f"Message from the Saleor Slack App: customer {customer.first_name} {customer.last_name} ({customer.email}) was updated"
        post_to_slack(slack_webhook_url, message)
    pass


def post_to_slack(webhook_url: str, message: str):
    """
    Writes a message to the slack channel associated `webhook_url` using Slack's
    Incoming Webhook API (https://api.slack.com/messaging/webhooks)
    """
    data = json.dumps({"text": message}).encode("utf-8")
    req = request.Request(webhook_url, data)
    req.add_header("Content-Type", "application/json")
    request.urlopen(req)