# Saleor Slack App

A simple [Saleor app](https://docs.saleor.io/docs/3.0/developer/extending/apps/key-concepts) that posts to a specific Slack channel via a Slack webhook in response to certain events in Saleor.

## Getting started

### Set up Slack

1. Create a temporary Slack channel for testing
2. Create a [Slack App](https://api.slack.com/apps)
3. In the Slack app settings, click **Incoming Webhooks** > **Add New Webhook to Workspace**, and associate the webhook with the channel you created. Make a note of the webhook's URL. (Run the `curl` example code shown in the Slack API console to make sure it's working as you expect.)

### Run the app server

```
export SLACK_WEBHOOK_URL=<URL for your Slack webhook>
uvicorn main:api --reload --port 8081
```

### Set up the app in Saleor

1. Run the Saleor dashboard and go to http://localhost:9000/apps/
2. Next to **Local Apps** click **Create App**
3. Give the app a name and grant it full access to the store
4. Click **Create Webhook**, and enter the following details:
   1. Name: **Customer Updated**
   2. Target URL: http://localhost:8081/customer_updated. (If your Saleor API server is running in Docker, use http://host.docker.internal:8081/customer_updated)
   3. Secret key: <blank>
   4. Events: **Customer updated**
   5. Webhook status: check **"Webhook is active"** (right down at the bottom of the page)

Now go and update a customer record (e.g. change their surname), and you should see notifications appear in your Slack channel.

## Troubleshooting

If your app server (i.e. your `uvicorn` process) isn't being called, check that the Saleor worker is running correctly. In Saleor, the worker process handles processing webhooks, not the main API server.
