# Automated-Real-Estate-Data-Scraper-Rightmove-UK-
Developed a Selenium-based dynamic web scraper to collect property prices, metadata, and coordinates from Rightmove and export them into structured CSV datasets.

Demo of the project : https://www.linkedin.com/posts/vineetnaik1611_python-webscraping-automation-activity-7382117398444675072-_dTY?utm_source=social_share_send&utm_medium=member_desktop_web&rcm=ACoAAB1r74EB1BgDMrQtlMWDlbqL7ShILewXuH4



This project is an automated **Real Estate Data Scraper** that extracts property listings from **Rightmove UK** using **Selenium WebDriver** and **BeautifulSoup**.

The scraper collects:
- Property price  
- Address  
- Description  
- Bedrooms  
- Bathrooms  
- Square footage (where available)  
- Property type  
- Latitude & longitude (parsed from page source)

All results are saved as a timestamped CSV file inside:  
`~/Desktop/data_scraper/`

---

##  Features
- Automated multi-page scraping using Selenium  
- Cookie popup handling  
- Extracts extra details by opening each listing in a new tab  
- Parses geolocation metadata from embedded JS  
- Fast HTML parsing with BeautifulSoup  
- Randomized delays to mimic organic browsing  
- Saves data in clean CSV format

---

##  How to Run the Scraper

### 1. Clone the repository
```bash
git clone https://github.com/Vineetnaik1611/Automated-Real-Estate-Data-Scraper-Rightmove-UK-.git
cd Automated-Real-Estate-Data-Scraper-Rightmove-UK-
```
### 2. Install Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Run the file
```bash
python Real_estate_data_scraper.py
```

### 4. Output Location

After completion, your CSV file will be saved to:
```txt
~/Desktop/data_scraper/
```
## Configuration

Inside the run() method, you can change the number of pages to scrape:
``bash
for page in range(0, 2):
```
Increase the range to scrape more pages

