from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)

# Initialize the driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
game_dict = {
    "juego_1": "bqwUXlidcU79RV5OYla-Sw==",
    "juego_2": "BmUOzSzEYwJLgsJCHqm_mA==",
    "juego_3": "h2gWgUM2eEWGd9-xKYUqAA==",
    "juego_4": "GHZAqbwWUQq4P5tKvrUTUA==",
    "juego_5": "hIXGa_ebsZ-53yWEA8Qr0Q==",
    "juego_6": "RjSAHUG61dgyS92UHA_rEw==",
}

for key, code in game_dict.items():
    URL = f"https://estadisticascabb.gesdeportiva.es/partido/{code}"

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
                # get header
                header = table.find_element("tag name", "thead")
                # get body
                body = table.find_element("tag name", "tbody")
                # Get all rows
                rows = body.find_elements("tag name", "tr")

                # Initialize lists to store data
                data = []
                headers = []

                # Get headers first
                header_row = header.find_elements("tag name", "tr")[1]
                # get all cells
                header_cells = header_row.find_elements("tag name", "th")
                shot_counter = 0
                for cell in header_cells:
                    if "d-none" not in cell.get_attribute("class"):
                        text = cell.get_attribute('textContent') or cell.get_attribute('innerText') or cell.text
                        text = text.replace("*", "").strip()
                        # if text in ["A/I" and "%"], add prefix
                        shot_types = ["2p", "2p", "3p", "3p", "ft", "ft"]
                        if text in ["A/I", "%"]:
                            # first one is 2 points, second one is 3 points and third one is FT
                            text = f"{shot_types[shot_counter]}_{text}"
                            shot_counter += 1
                        headers.append(text)

                # Get row data
                for row in rows:
                    row_data = []
                    cells = row.find_elements("tag name", "td")
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
                df.to_csv(f'liga_data_{key}_{idx}.csv', index=False)
    except Exception as e:
        print(f"Error scraping {key}: {e}")

driver.quit()
