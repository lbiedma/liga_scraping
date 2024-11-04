from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

URL = "https://estadisticascabb.gesdeportiva.es/partido/XJjuOZ5-RZfljEiT3iHulg=="

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)

try:
    # Navigate to the URL
    driver.get(URL)
    
    # Wait explicitly for elements to be present (better than time.sleep)
    wait = WebDriverWait(driver, 10)
    
    # First check if there are any iframes and switch to the first one if present
    iframes = wait.until(EC.presence_of_all_elements_located(("tag name", "iframe")))
    # Find first iframe and go there
    driver.switch_to.frame(iframes[0])
    # find iframe whose src contains "estadisticas"
    iframes = wait.until(EC.presence_of_all_elements_located(("tag name", "iframe")))
    iframe = next((iframe for iframe in iframes if "estadisticas" in iframe.get_attribute("src")), None)
    if iframe:
        driver.switch_to.frame(iframe)
        # find table whose class called "table-responsive"
        table_classes = wait.until(EC.presence_of_all_elements_located(("xpath", "//table[contains(@class, 'tabla-estadisticas')]")))
        # get the 2 tables inside
        for idx, table in enumerate(table_classes):
            table = table_classes[0]
            # get header
            header = table.find_element("xpath", "//thead")
            print(header.text)
            # get body
            body = table.find_element("xpath", "//tbody")
                    # Get all rows
            rows = body.find_elements("xpath", ".//tr")

            # Initialize lists to store data
            data = []
            headers = []

            # Get headers first
            header_row = header.find_elements("xpath", ".//tr")[1]
            # get all cells
            header_cells = header_row.find_elements("xpath", ".//th")
            for cell in header_cells:
                if "d-none" not in cell.get_attribute("class"):
                    text = cell.get_attribute('textContent') or cell.get_attribute('innerText') or cell.text
                    headers.append(text.replace("*", "").strip())

            # Get row data
            for row in rows:
                row_data = []
                cells = row.find_elements("xpath", ".//td")
                for cell in cells:
                    if "d-none" not in cell.get_attribute("class"):
                        text = cell.get_attribute('textContent') or cell.get_attribute('innerText') or cell.text
                        row_data.append(text.replace("*", "").strip().split("\n")[-1].strip())
                data.append(row_data)

            # Create DataFrame
            df = pd.DataFrame(data, columns=headers)
            
            # Now you can work with the DataFrame
            print(df)
            # Optionally save to CSV
            df.to_csv(f'liga_data_{idx}.csv', index=False)

finally:
    # Always close the driver
    driver.quit()
