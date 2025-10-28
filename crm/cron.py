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
