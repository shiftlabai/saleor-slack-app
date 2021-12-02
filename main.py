import os
import json
import time

from typing import List

from urllib import request
from fastapi import FastAPI, Request
from pydantic import BaseModel

slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
if not slack_webhook_url:
    raise RuntimeError("SLACK_WEBHOOK_URL env variable not set")

api = FastAPI()

delay_seconds: float = 1.0
last_request_time: float = 0.0


class SaleorCustomerUpdatedPayload(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str


@api.post("/customer_updated")
def customer_updated(customers: List[SaleorCustomerUpdatedPayload]):
    global last_request_time

    t = time.time()
    if t - last_request_time < delay_seconds:
        # We already handled a call recently, ignore this one. Temporary hack to
        # prevent multiple invocations due to Saleor sending multiple callbacks
        # for the same event.
        return
    last_request_time = t
    for customer in customers:
        message = f"Message from the Saleor Slack App: customer {customer.first_name} {customer.last_name} ({customer.email}) was updated"
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
