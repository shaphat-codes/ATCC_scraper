import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

input_csv = 'cell_line_ids.csv'
output_csv = 'scraped_data.csv'

driver = webdriver.Chrome()

scraped_data = []

skipped_empty_ids_count = 0
scraped_count = 0

not_found_ids = []

expected_fields = [
    "Product category", "Product type", "Organism", "Cell type", 
    "Morphology", "Applications", "Product format", "Storage conditions"
]

try:
    with open(input_csv, mode='r') as file:
        csv_reader = csv.reader(file)
        
        for row in csv_reader:
            product_id = row[0].strip()
            
            if not product_id:
                skipped_empty_ids_count += 1
                continue  # Skip empty IDs

            url = f"https://www.atcc.org/products/{product_id}"
            
            try:
                driver.get(url)
                
                # Adding a small wait to allow page elements to load
                driver.implicitly_wait(1)
                
                # Scraping the cell line name
                cell_line_name = driver.find_element(By.CLASS_NAME, "pdp-page-content__product-name").text
                data_dict = {field: "" for field in expected_fields}
                
                titles = driver.find_elements(By.CLASS_NAME, "product-information__title")
                values = driver.find_elements(By.CLASS_NAME, "product-information__data")
                
                for title, value in zip(titles, values):
                    field_name = title.text.strip()
                    if field_name in data_dict:
                        data_dict[field_name] = value.text.strip()
                
                scraped_row = [cell_line_name, product_id] + [data_dict[field] for field in expected_fields]
                
                scraped_data.append(scraped_row)
                scraped_count += 1

                if scraped_count % 10 == 0:
                    print(f"{scraped_count} / 3549")
            
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                not_found_ids.append(product_id)
                continue  # Skip this ID and move to the next one

finally:
    driver.quit()

with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
    csv_writer = csv.writer(file)
    
    csv_writer.writerow(["cell_line_name", "product_id"] + expected_fields)
    
    csv_writer.writerows(scraped_data)

print(f"Scraping completed. Data saved to {output_csv}.")
print(f"Skipped empty IDs: {skipped_empty_ids_count}")
if not_found_ids:
    print(f"IDs not found on the website: {not_found_ids}")
else:
    print("All valid IDs were found on the website.")
