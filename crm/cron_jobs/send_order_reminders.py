#!/usr/bin/env python3

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta

GRAPHQL_URL = "http://localhost:8000/graphql"

LOG_FILE = "/tmp/order_reminders_log.txt"

query = gql("""
query GetRecentOrders($startDate: DateTime!) {
  orders(filter: { orderDate_Gte: $startDate, status: "PENDING" }) {
    id
    customer {
      email
    }
  }
}
""")

def fetch_pending_orders():
    """Fetch pending orders from the GraphQL API using gql Client."""
    transport = RequestsHTTPTransport(
        url=GRAPHQL_URL,
        verify=True,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    start_date = (datetime.now() - timedelta(days=7)).isoformat()

    result = client.execute(query, variable_values={"startDate": start_date})
    return result.get("orders", [])

def log_reminders(orders):
    """Log order reminders with timestamps."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log:
        for order in orders:
            log.write(f"{timestamp} - Reminder for Order ID {order['id']}, Customer: {order['customer']['email']}\n")

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
