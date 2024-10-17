from opensearchpy import OpenSearch

# OpenSearch endpoint
ELASTICSEARCH_ENDPOINT = 'https://search-chatcart-dmyohuhjp4qbxxchek5vbz65uu.aos.us-east-2.on.aws'

es = OpenSearch(
    hosts=[ELASTICSEARCH_ENDPOINT],
    http_auth=('admin', 'Admin123!'), 
    scheme="https",
    port=443,
)

def fetch_and_display_products():
    # Enter the model name
    model_name = input("Enter the product model name you want to search: ")

    # OpenSearch query 
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

def select_product_and_size(product_map):
    # Select a product by ID
    try:
        product_id = int(input("\nEnter the Product ID you want to see: "))
        if product_id in product_map:
            selected_product = product_map[product_id]
            print("\n------------------------------------------")
            print(f"Product ID: {selected_product['product_id']}")
            print(f"Brand: {selected_product['brand']}")
            print(f"Model: {selected_product['model']}")
            print(f"Description: {selected_product['description']}")
            
            # Display available sizes
            sizes = [price['size'] for price in selected_product['prices']]
            print(f"Available sizes: {', '.join(map(str, sizes))}")
            
            # Enter a size and handle input errors
            size_input = input("\nEnter the size you are interested in: ")
            try:
                size = float(size_input)  
                valid_size = False

                for price_info in selected_product['prices']:
                    if price_info['size'] == size:
                        valid_size = True
                        print(f"\nDetails for size {size}:")
                        print(f"Source: {price_info['source']}")
                        print(f"Price: {price_info['price']}")
                        print(f"Stock Level: {price_info['stock_level']}")
                        print(f"Last Update: {price_info['last_update']}")
                
                if not valid_size:
                    print(f"Size {size} is not available for this model.")
            except ValueError:
                print(f"'{size_input}' is not a valid size. Please enter a numeric size.")
        else:
            print("Invalid Product ID.")
    except ValueError:
        print("Invalid input. Please enter a valid Product ID.")

def main():
    # Display products
    product_map = fetch_and_display_products()

    if product_map:
        while True:
            # Select product and size
            select_product_and_size(product_map)
            
            # Ask user if they want to see another product
            choice = input("\nWould you like to see another product? (yes/no): ").strip().lower()
            if choice == 'yes':
                print("\nEnter the Product ID you want to see: ")
                for product_id in product_map:
                    print(f"Product ID: {product_id}, Model: {product_map[product_id]['model']}")
                continue
            else:
                print("Exiting. Thank you!")
                break

if __name__ == "__main__":
    main()
