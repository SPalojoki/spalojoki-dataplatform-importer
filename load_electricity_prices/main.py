import requests
from google.cloud import bigquery
from google.api_core.exceptions import NotFound
import json
from datetime import datetime, timezone
import os

# This should be moved to environment variable
project_id = os.getenv('PROJECT_ID')
table_id = f"{project_id}.analytics__landing.electricity_prices"

client = bigquery.Client()


def fetch_electricity_prices():
    url = "https://api.porssisahko.net/v1/latest-prices.json"
    response = requests.get(url)
    response.raise_for_status()

    return response.json()["prices"]


def create_table_if_not_exists():
    try:
        client.get_table(table_id)
        print(f"Table {table_id} already exists.")
    except NotFound:
        schema = [
            bigquery.SchemaField("start_date", "TIMESTAMP"),
            bigquery.SchemaField("end_date", "TIMESTAMP"),
            bigquery.SchemaField("price", "FLOAT"),
            bigquery.SchemaField("sdp_metadata", "JSON")
        ]
        table = bigquery.Table(table_id, schema=schema)
        client.create_table(table)
        print(f"Table {table_id} created.")
    except Exception as e:
        print(f"An error occurred: {e}")

def insert_data(data):
    rows_to_insert = [
        {
            "start_date": row["startDate"],
            "end_date": row["endDate"],
            "price": row["price"],
            "sdp_metadata": json.dumps({"loaded_at": datetime.now(timezone.utc).isoformat()})
        }
        for row in data
    ]

    errors = client.insert_rows_json(table_id, rows_to_insert)

    if errors:
        print(f"Following errors occurred while inserting data to {table_id}: {errors}")
    else:
        print(f"Data inserted successfully.")


def main(message, context):
    data = fetch_electricity_prices()
    create_table_if_not_exists()
    insert_data(data)
