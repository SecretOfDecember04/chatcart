from elasticsearch import Elasticsearch

cloud_id = '58822d2467104f0ea020844c565f84aa:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDc0NTM4M2Q1NDQxMzRiN2JiOWVjYWZjMWY0ZTRiYzU3JGVmY2M0ZjE5YTc1ZDRmYjA4OGNmMDBjZjgzNjhiMjBh' 
api_key = 'WGRPbm1KSUJYWmVHWDV4Yk9lT2M6UlZURmFycl9RV1NWVWFPT3pmMUhTQQ==' 

# Elasticsearch connection (using Cloud ID and API key)
es = Elasticsearch(
    cloud_id=cloud_id,
    api_key=api_key
)

def fetch_and_display_products_by_model(model_name):
    # ElasticSearch query 
    query = {
        "query": {
            "query_string": {
                "query": f"*{model_name}*",  
                "fields": ["model"],  
                "default_operator": "AND"
            }
        },
        "size": 1000,
        "sort": [
        {"product_id": {"order": "asc"}}  
    ]  
    }

    # Execute the search query
    response = es.search(body=query, index="products")

    # Check hits
    if response['hits']['total']['value'] > 0:
        print(f"\nFound {response['hits']['total']['value']} products matching '{model_name}':\n")
        
        # Display all products by ID
        products = response['hits']['hits']
        product_map = {}
        for product in products:
            product_source = product['_source']
            product_map[product_source['product_id']] = product_source
            print(f"Product ID: {product_source['product_id']}, Brand: {product_source['brand']}, Model: {product_source['model']}")
        
        return product_map
    else:
        print(f"No products found with model name containing '{model_name}'.")
        return {}


def select_product_and_size(product_map, product_id):
    # Check if the product ID exists in the map
    if product_id in product_map:
        selected_product = product_map[product_id]
        print("\n------------------------------------------")
        print(f"Product ID: {selected_product['product_id']}")
        print(f"Brand: {selected_product['brand']}")
        print(f"Model: {selected_product['model']}")
        print(f"Description: {selected_product['description']}")
        
        # Display available sizes and corresponding price details
        print(f"Available sizes for product {product_id}:")
        for price_info in selected_product['prices']:
            print(f"\nSize: {price_info['size']}")
            print(f"Source: {price_info['source']}")
            print(f"Price: {price_info['price']}")
            print(f"Stock Level: {price_info['stock_level']}")
            print(f"Last Update: {price_info['last_update']}")
        
    else:
        print("Invalid Product ID or product not found.")
