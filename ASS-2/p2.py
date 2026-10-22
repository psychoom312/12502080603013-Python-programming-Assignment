import re
import sys
from bs4 import BeautifulSoup

def parse_html_file(file_path):
    products = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            soup = BeautifulSoup(content, 'html.parser')
            
            for item in soup.find_all(class_='product-item'):
                name_elem = item.find(class_='product-name')
                price_elem = item.find(class_='product-price')
                rating_elem = item.find(class_='product-rating')
                
                if name_elem and price_elem and rating_elem:
                    name = name_elem.get_text(strip=True)
                    
                    price_text = price_elem.get_text(strip=True)
                    price_digits = re.sub(r'[^\d.]', '', price_text)
                    price = float(price_digits) if price_digits else 0.0
                    
                    rating_text = rating_elem.get_text(strip=True)
                    rating = float(rating_text) if rating_text else 0.0
                    
                    products.append((name, price, rating))
    except Exception:
        pass
    return products

def process_product_ranking():
    input_lines = sys.stdin.read().splitlines()
    if not input_lines:
        return
        
    first_line = input_lines[0].split()
    p = int(first_line[0])
    k = int(first_line[1])
    
    html_paths = input_lines[1:p+1]
    unique_products = {}
    
    for path in html_paths:
        extracted = parse_html_file(path)
        for name, price, rating in extracted:
            if name not in unique_products:
                unique_products[name] = (price, rating)
            else:
                if rating > unique_products[name][1]:
                    unique_products[name] = (price, rating)
                elif rating == unique_products[name][1] and price < unique_products[name][0]:
                    unique_products[name] = (price, rating)

    final_list = []
    for name, (price, rating) in unique_products.items():
        final_list.append((name, price, rating))
        
    final_list.sort(key=lambda x: (-x[2], x[1], x[0]))
    
    for i in range(min(k, len(final_list))):
        name, price, rating = final_list[i]
        if price.is_integer():
            print(f"{name} {int(price)} {rating}")
        else:
            print(f"{name} {price} {rating}")

if __name__ == "__main__":
    process_product_ranking()
