import csv
import requests
from bs4 import BeautifulSoup

# --- Configuration ---
URL = "https://realpython.github.io/fake-jobs/"
OUTPUT_FILE = "job_listings.csv"
FIELDNAMES = ["Job Title", "Company Name", "Location", "Job Detail Page URL"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def fetch_webpage(url):
    """Fetches the HTML content of the page."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None


def parse_jobs(html_content):
    """Parses HTML using the explicit Real Python element structure."""
    soup = BeautifulSoup(html_content, "html.parser")
    job_listings = []

    # Real Python wraps each job posting in a div with the class 'card-content'
    job_cards = soup.find_all("div", class_="card-content")

    for card in job_cards:
        # 1. Extract Job Title
        title_element = card.find("h2", class_="title")
        job_title = title_element.text.strip() if title_element else "N/A"

        # 2. Extract Company Name
        company_element = card.find("h3", class_="company")
        company_name = company_element.text.strip() if company_element else "N/A"

        # 3. Extract Location
        location_element = card.find("p", class_="location")
        location = location_element.text.strip() if location_element else "N/A"

        # 4. Extract Job Detail Page URL
        # The site provides two footer links ('Learn' and 'Apply'). We extract the 'Apply' link.
        links = card.find_all("a", class_="card-footer-item")
        job_url = "N/A"
        if len(links) >= 2:
            job_url = links[1]["href"].strip() if links[1].has_attr("href") else "N/A"
        elif len(links) == 1:
            job_url = links[0]["href"].strip() if links[0].has_attr("href") else "N/A"

        # Combine into required field dictionary
        job_data = {
            "Job Title": job_title,
            "Company Name": company_name,
            "Location": location,
            "Job Detail Page URL": job_url
        }
        
        job_listings.append(job_data)

    return job_listings


def save_to_csv(data, filename):
    """Stores the scraped results directly into a CSV file."""
    if not data:
        print("No job data found to save.")
        return

    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(data)
            
        print(f"Successfully saved {len(data)} job listings to '{filename}'.")
    except IOError as e:
        print(f"Error writing to CSV file: {e}")


def main():
    print(f"Starting web scraper for: {URL}...")
    html = fetch_webpage(URL)
    
    if html:
        jobs = parse_jobs(html)
        save_to_csv(jobs, OUTPUT_FILE)
    else:
        print("Scraping failed because the webpage could not be retrieved.")


if __name__ == "__main__":
    main()
