from elasticsearch import Elasticsearch

ELASTICSEARCH_ENDPOINT = 'https://61e9a807dd8f460d9416993528bac501.us-central1.gcp.cloud.es.io:443'
API_KEY = 'VDZTX0lwSUJGQUxGbHFIcjM1MzE6RXdGUVVjZm5SV09fcWszcFlEaFBWUQ=='

# Initialize Elasticsearch client
es = Elasticsearch(
    ELASTICSEARCH_ENDPOINT,
    api_key=API_KEY
)

# Prompt user for input
search_term = input("Enter the sneaker type you want to search for: ")
min_price = float(input("Enter minimum price: "))
max_price = float(input("Enter maximum price: "))

# Set the size
page_size = 10
page = 0

# Get the total number of results
search_body = {
    "query": {
        "bool": {
            "must": [
                {"match": {"sneaker_type": search_term}}
            ],
            "filter": [
                {"range": {"price": {"gte": min_price, "lte": max_price}}}
            ]
        }
    },
    "from": page * page_size,
    "size": page_size
}

# Get the total number of hits
res = es.search(index='sneaker_data', body=search_body)
total_results = res['hits']['total']['value']
total_pages = (total_results // page_size) + (1 if total_results % page_size > 0 else 0)

print(f"Found {total_results} results across {total_pages} pages.\n")

while True:
    # Elasticsearch query 
    search_body = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"sneaker_type": search_term}}
                ],
                "filter": [
                    {"range": {"price": {"gte": min_price, "lte": max_price}}}
                ]
            }
        },
        "from": page * page_size,  
        "size": page_size         
    }

    # Perform the search
    res = es.search(index='sneaker_data', body=search_body)
    
    # Check if there are no more results
    if not res['hits']['hits']:
        print("No more results.")
        break

    # Print the results for the current page
    print(f"\nPage {page + 1} of {total_pages} - Showing {len(res['hits']['hits'])} results:\n")
    for hit in res['hits']['hits']:
        sneaker_type = hit['_source']['sneaker_type']
        price = hit['_source']['price']
        print(f"Sneaker: {sneaker_type}, Price: ${price}")

    # Ask user if they want to continue to the next page
    if page + 1 >= total_pages:
        print("\nYou have reached the last page.")
        break

    next_page = input("Do you want to see the next page? (yes/no): ").strip().lower()
    if next_page != 'yes':
        break
    
    # Move to the next page
    page += 1







