import requests
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime

@shared_task
def generate_crm_report():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/crm_report_log.txt"

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql("""
            query {
                allCustomers {
                    totalCount
                }
                allOrders {
                    totalCount
                    edges {
                        node {
                            totalAmount
                        }
                    }
                }
            }
        """)

        result = client.execute(query)

        customers = result.get("allCustomers", {}).get("totalCount", 0)
        orders_data = result.get("allOrders", {})
        orders = orders_data.get("totalCount", 0)

        total_revenue = sum(
            edge["node"]["totalAmount"]
            for edge in orders_data.get("edges", [])
            if edge["node"].get("totalAmount") is not None
        )

        report = f"{timestamp} - Report: {customers} customers, {orders} orders, {total_revenue} revenue"

        with open(log_file, "a") as f:
            f.write(report + "\n")

        print(report)

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - ERROR: {e}\n")
        print(f"{timestamp} - ERROR: {e}")
