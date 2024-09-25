import csv
from elasticsearch import Elasticsearch

ELASTICSEARCH_ENDPOINT = 'https://61e9a807dd8f460d9416993528bac501.us-central1.gcp.cloud.es.io:443'
API_KEY = 'VDZTX0lwSUJGQUxGbHFIcjM1MzE6RXdGUVVjZm5SV09fcWszcFlEaFBWUQ=='  

# Initialize Elasticsearch client
es = Elasticsearch(
    ELASTICSEARCH_ENDPOINT,
    api_key=API_KEY
)

index_name = 'sneaker_data'
csv_file_path = 'api/data/temp.csv'


# Helper function
def clean_price(price_str):
    return float(price_str.replace('$', '').replace(',', '').strip())


# Read the CSV file and index each row into Elasticsearch
with open(csv_file_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    
    for i, row in enumerate(reader):
        sneaker_type = row['Sneaker Type']
        price = clean_price(row['Price'])
        
        document = {
            'sneaker_type': sneaker_type,
            'price': price
        }
        
        # Index the document into Elasticsearch
        res = es.index(index=index_name, id=i+1, body=document)
        print(f"Indexed {sneaker_type} with ID {res['_id']}")

# Verify the data is in Elasticsearch
search_res = es.search(index=index_name, body={"query": {"match_all": {}}})
print("Search results:", search_res)
