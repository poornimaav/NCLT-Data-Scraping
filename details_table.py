import os
from selenium.common.exceptions import NoSuchElementException
import logging
import traceback
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
from order_judgement import scrape_order_judgment_table
import logging_utils

def scrape_data_from_details_page(driver, details_page_url):
    logger = logging_utils.setup_logging('test1/scraping_log.log')
    try:
        driver.get(details_page_url)
        
        # Wait for the details table to be present
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, "table-bordered"))
        # )

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Find the details table
        table = soup.find("table", class_="table-bordered")

        details_data = {}

        # Loop through each row and extract the data
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            label = None
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                if i % 2 == 0:
                    # Cell contains a label
                    label = cell_text
                else:
                    # Cell contains a value
                    details_data[label] = cell_text
            
        filing_number = int(details_data.get("Filing Number", 0))
        df = pd.DataFrame([details_data]) 
        csv_filename = "test1/outputs/details.csv"
        serial_number = 1

        if os.path.isfile(csv_filename) and os.path.getsize(csv_filename) > 0:
            existing_df = pd.read_csv(csv_filename)
            last_serial_number = existing_df['S. No'].max()
            if not pd.isna(last_serial_number):
                serial_number = int(last_serial_number) + 1

        if not df.empty:       
            df.insert(0, "S. No", range(serial_number, serial_number + len(df)))

            if not os.path.isfile(csv_filename) or os.path.getsize(csv_filename) == 0:
                df.to_csv(csv_filename, index=False, mode='w', encoding='utf-8')  # Save with header
            else:
                df.to_csv(csv_filename, index=False, mode='a', header=False, encoding='utf-8')  # Append without header
                
            logger.info("Data from details page saved to %s", csv_filename)
        
        else:
            logger.info('No Data Found. Skipping current table')
        # Call another function if needed
        scrape_order_judgment_table(driver, filing_number)
        
    except NoSuchElementException as e:
        logger.error("Error while scraping details page: %s", str(e))

    except Exception as e:
        logger.error("Error while scraping details page: %s", str(e))
      