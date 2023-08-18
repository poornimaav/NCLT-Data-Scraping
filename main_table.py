import json
import logging
from utilities import automate_input_element, automate_selection
from config_utils import read_config, config
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
import os
from selenium.common.exceptions import NoSuchElementException
from details_table import scrape_data_from_details_page
import traceback
import logging_utils

logger = logging_utils.setup_logging('test1/scraping_log.log')

def scrape_data_from_current_page(driver, config):
   
    try:
        selection_values = {
         "bench": config["bench"],
        "case_year": config["case_year"]
        }

        input_values = {
         "diaryno": config["diaryno"]
        }

        url = config["url"] 
        driver.get(url)

        for element_id, value in selection_values.items():
            automate_selection(driver, element_id, value)
        

        for element_id, value in input_values.items():       
            automate_input_element(driver, element_id, value)

        logger.info("Diary Number: %s", config["diaryno"])

        
        submit_button = driver.find_element(By.CLASS_NAME, "btn-default")
        submit_button.click()

        headers = []  
        serial_number = 1

        response = driver.page_source
        soup = BeautifulSoup(response, 'html.parser')
        data = soup.find('table', class_='table')

        table_data = []
        is_first_row = True
        for row in data.find_all("tr"):
            if is_first_row:
                is_first_row = False
                if not headers:
                    headers = [cell.get_text(strip=True) for cell in row.find_all("th")]
                continue 
                # Skip the first row with the link message
            cells = row.find_all("td")
            row_data = [cell.get_text(strip=True) for cell in cells]
            table_data.append(row_data)

        # Create a DataFrame from the extracted table data
        df1 = pd.DataFrame(table_data)
        csv_filename = "test1/outputs/output.csv"

        if len(headers) == len(df1.columns):
            df1.columns = headers

            if os.path.isfile(csv_filename) and os.path.getsize( csv_filename) > 0:
                existing_df = pd.read_csv(csv_filename)
                last_serial_number = existing_df['S. No'].max()
                if not pd.isna(last_serial_number):
                    serial_number = int(last_serial_number) + 1

            if "S. No" in df1.columns:
                df1.drop("S. No", axis=1, inplace=True)
            
            df1.insert(0, "S. No", range(serial_number, serial_number + len(df1)))
            
            if not os.path.isfile(csv_filename) or os.path.getsize(csv_filename) == 0:
                df1.to_csv(csv_filename, mode='a', index=False, header=True)  # Save with header
            else:
                df1.to_csv(csv_filename, mode='a', index=False, header=False)  # Append without header
            # df1.to_csv('test/output.csv', mode='a', index=False)
            logger.info("Data from main table successfully saved to %s", csv_filename)

            serial_number += len(df1)

            click_pending_status(driver)
            
        else:
            logger.info("No data found. Skipping current table.")

    except Exception as e:
        logger.error("\nError occured while scraping main table: %s", str(e))


def click_pending_status(driver):

    next_url = None
    try:
        # Locate the "Pending" status link within the last column of the table
        status_link = driver.find_element(By.XPATH, "//tbody/tr/td[6]/a")
        next_url = status_link.get_attribute("href")
        status_link.click()
        logger.info("Clicked on status link.")
        scrape_data_from_details_page(driver, next_url)
    
    except NoSuchElementException:
        logger.info("status link not found.")


    except Exception as e:
        logger.error("Error occured while scraping main table: %s", str(e))