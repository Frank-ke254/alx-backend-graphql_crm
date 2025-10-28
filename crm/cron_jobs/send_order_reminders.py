#!/usr/bin/env python3

import requests
from datetime import datetime, timedelta

GRAPHQL_URL = "http://localhost:8000/graphql"

LOG_FILE = "/tmp/order_reminders_log.txt"

query = """
query GetRecentOrders($startDate: DateTime!) {
  orders(filter: { orderDate_Gte: $startDate, status: "PENDING" }) {
    id
    customer {
      email
    }
  }
}
"""

def fetch_pending_orders():
    start_date = (datetime.now() - timedelta(days=7)).isoformat()
    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": {"startDate": start_date}},
        headers={"Content-Type": "application/json"},
        timeout=10
    )

    if response.status_code != 200:
        raise Exception(f"GraphQL query failed with status {response.status_code}: {response.text}")

    data = response.json()
    return data.get("data", {}).get("orders", [])

def log_reminders(orders):
    with open(LOG_FILE, "a") as log:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for order in orders:
            order_id = order["id"]
            email = order["customer"]["email"]
            log.write(f"{timestamp} - Reminder for Order ID {order_id}, Customer: {email}\n")

if __name__ == "__main__":
    try:
        orders = fetch_pending_orders()
        if orders:
            log_reminders(orders)
        print("Order reminders processed!")
    except Exception as e:
        with open(LOG_FILE, "a") as log:
            log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR: {e}\n")
        print("Error occurred during processing.")
