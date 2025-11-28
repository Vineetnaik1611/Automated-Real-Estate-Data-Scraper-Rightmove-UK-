from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import csv
import time
import random
import re
import os

class RightmoveScraper:
    def __init__(self):
        self.results = []
        chrome_options = Options()
        #chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.driver.set_page_load_timeout(30)

    def fetch(self, url, retries=3, delay=5):
        print(f"Fetching URL: {url}")
        attempt = 0
        while attempt < retries:
            try:
                self.driver.get(url)
                time.sleep(random.uniform(1, 3))
                try:
                    accept_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]'))
                    )
                    accept_button.click()
                    print("Accepted cookies")
                except:
                    print("No cookie popup found")

                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.PropertyPrice_price__VL65t'))
                )
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                return self.driver.page_source
            except TimeoutException:
                print(f"Timeout (attempt {attempt + 1}/{retries})")
                attempt += 1
                time.sleep(delay)
            except Exception as e:
                print(f"Error: {str(e)}")
                attempt += 1
                time.sleep(delay)
        raise Exception(f"Failed after {retries} attempts")

    def parse(self, html):
        print("Parsing HTML...")
        soup = BeautifulSoup(html, 'lxml')
        prices = soup.find_all('div', class_='PropertyPrice_price__VL65t')
        addresses = soup.find_all('address', class_='PropertyAddress_address__LYRPq')
        descriptions = soup.find_all('p', class_='PropertyCardSummary_summary__oIv57')
        bedrooms = soup.find_all('span', class_='PropertyInformation_bedroomsCount___2b5R')
        bathrooms = soup.find_all('span', {'aria-label': True})
        links = soup.select("a.propertyCard-link")

        for price_element, address_element, description_element, bedroom_element, bathroom_element, link_element in zip(
            prices, addresses, descriptions, bedrooms, bathrooms, links):
            try:
                price = price_element.get_text(strip=True)
                address = address_element.get_text(strip=True)
                description = description_element.get_text(strip=True)
                bedroom = bedroom_element.get_text(strip=True)
                bathroom = 'N/A'
                aria_label = bathroom_element.get('aria-label', '')
                if 'in property' in aria_label.lower():
                    bathroom = aria_label.split()[0]

                square_footage = "N/A"
                property_type = "N/A"
                latitude = "N/A"
                longitude = "N/A"

                try:
                    listing_url = "https://www.rightmove.co.uk" + link_element.get("href")
                    self.driver.execute_script("window.open(arguments[0]);", listing_url)
                    self.driver.switch_to.window(self.driver.window_handles[1])

                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )

                    try:
                        sqft_element = self.driver.find_element(By.XPATH, "//p[contains(text(), 'sq ft')]")
                        square_footage = sqft_element.text.strip()
                    except:
                        pass

                    try:
                        prop_elem = self.driver.find_element(By.CSS_SELECTOR, 'p._1hV1kqpVceE9m-QrX_hWDN')
                        property_type = prop_elem.text.strip()
                    except:
                        all_p_elements = self.driver.find_elements(By.TAG_NAME, "p")
                        known_types = [
                            'flat', 'apartment', 'house', 'bungalow', 'studio', 'maisonette',
                            'duplex', 'terraced', 'semi-detached', 'detached', 'end of terrace',
                            'cottage', 'townhouse', 'mews', 'mobile home', 'park home', 'land',
                            'farmhouse', 'barn conversion', 'retirement property', 'houseboat',
                            'block of apartments'
                        ]
                        for p_elem in all_p_elements:
                            text = p_elem.text.strip().lower()
                            for ktype in known_types:
                                if ktype in text:
                                    property_type = p_elem.text.strip()
                                    break
                            if property_type != "N/A":
                                break

                    try:
                        page_source = self.driver.page_source
                        match = re.search(r'"latitude":([0-9.]+),"longitude":(-?[0-9.]+)', page_source)
                        if match:
                            latitude = match.group(1)
                            longitude = match.group(2)
                            print(f"Coordinates found: {latitude}, {longitude}")
                        else:
                            print("Coordinates not found in page source.")
                    except Exception as e:
                        print(f"Error extracting coordinates: {e}")

                except Exception as e:
                    print(f"Could not extract additional data: {e}")
                finally:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])

                print(
                    f"Price: {price}, Address: {address}, Description: {description}, "
                    f"Bedrooms: {bedroom}, Bathrooms: {bathroom}, Sqft: {square_footage}, "
                    f"Type: {property_type}, Lat: {latitude}, Long: {longitude}"
                )

                self.results.append({
                    'price': price,
                    'address': address,
                    'description': description,
                    'bedrooms': bedroom,
                    'bathrooms': bathroom,
                    'square_footage': square_footage,
                    'property_type': property_type,
                    'latitude': latitude,
                    'longitude': longitude,
                })

            except Exception as e:
                print(f"Error extracting property: {e}")

    def to_csv(self):
        if not self.results:
            print("No results to save!")
            return

        #  Portable path: Desktop/data_scraper
        save_path = os.path.join(os.path.expanduser("~"), "Desktop", "data_scraper")
        os.makedirs(save_path, exist_ok=True)

        filename = f'rightmove_prices_{time.strftime("%Y%m%d_%H%M%S")}.csv'
        full_path = os.path.join(save_path, filename)

        with open(full_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'price', 'address', 'description', 'bedrooms', 'bathrooms',
                'square_footage', 'property_type', 'latitude', 'longitude'
            ])
            writer.writeheader()
            writer.writerows(self.results)

        print(f" Saved {len(self.results)} entries to: {full_path}")

    def run(self):
        try:
            base_url = "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E87490"
            for page in range(0, 2):  # Adjust the range for the number of pages you want to scrape
                url = f"{base_url}&index={page * 24}"
                print(f"\nProcessing page {page + 1}...")
                html = self.fetch(url)
                self.parse(html)
                time.sleep(random.uniform(2, 5))
        except Exception as e:
            print(f"Scraping failed: {e}")
        finally:
            self.driver.quit()
            self.to_csv()

if __name__ == '__main__':
    scraper = RightmoveScraper()
    scraper.run()

