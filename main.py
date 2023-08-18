import logging
from selenium import webdriver
import traceback
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from main_table import scrape_data_from_current_page
from config_utils import read_config, config,  write_config
import time
import logging_utils

if __name__ == "__main__":
    logger = logging_utils.setup_logging('scraping_log.log')
    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=options)
        start_diary_number = int(config["diaryno"])  # Convert to integer
        end_diary_number = start_diary_number + 2
        
        count = 1
        total_time = 0
        for diary_number in range(start_diary_number, end_diary_number):
            config["diaryno"] = str(diary_number)
            write_config(config) 
            logger.info("Starting iteration %d", count)
            
            start_time = time.time()# Update the config diaryno
            scrape_data_from_current_page(driver, config)
            end_time = time.time()
            
            loop_time = end_time - start_time
            logger.info("Iteration %d completed in %s seconds", count, loop_time)
            count+=1
            total_time += loop_time

        driver.quit()
        
           
    except WebDriverException as e:
        if "ERR_INTERNET_DISCONNECTED" in str(e):
            logger.error("Internet connection lost. Please check your connection.")
        else:
            logger.error("An error occurred: ", str(e))

    except KeyboardInterrupt:
        logger.error("Script interrupted by the user.")
        driver.quit()

    except Exception as e:
        logger.error("An error occurred: %s", str(e))

    logger.info("Total time taken for all iterations: %s seconds", total_time)