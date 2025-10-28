import os
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=2,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        query = gql(""" query { hello } """)
        response = client.execute(query)
        if response.get("hello"):
            message += " | GraphQL OK"
        else:
            message += " | GraphQL NO RESPONSE"
    except Exception as e:
        message += f" | GraphQL ERROR: {e}"

    with open(LOG_FILE, "a") as log:
        log.write(message + "\n")

    print(message)

def update_low_stock():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_file = "/tmp/low_stock_updates_log.txt"

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    success
                    message
                    updatedProducts {
                        id
                        name
                        stock
                    }
                }
            }
        """)

        result = client.execute(mutation)
        data = result.get("updateLowStockProducts", {})
        message = data.get("message", "No message returned.")
        updated = data.get("updatedProducts", [])

        with open(log_file, "a") as f:
            f.write(f"\n[{timestamp}] {message}\n")
            for p in updated:
                f.write(f" - {p['name']} (Stock: {p['stock']})\n")

        print(f"[{timestamp}] {message}")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"\n[{timestamp}] ERROR: {e}\n")
        print(f"[{timestamp}] ERROR: {e}")
