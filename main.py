from calendar import Day
import re
import time
import requests
from datetime import datetime
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def download_pdf(url, output_file):
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_file, 'wb') as file:
            file.write(response.content)
        print(f"PDF downloaded successfully: {output_file}")
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")
        return None

def extract_mc_numbers(pdf_file):
    mc_numbers = []
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        text = page.extract_text()
        mc_numbers.extend(re.findall(r'MC-\d+', text))
    return mc_numbers

def get_contact_info(mc_number):
    base_url = "https://ai.fmcsa.dot.gov/SMS/Carrier/"
    url = f"{base_url}{mc_number}/CarrierRegistration.aspx"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        telephone = soup.find(text=re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'))
        email = soup.find(text=re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'))
        return telephone, email
    else:
        print(f"Failed to fetch contact info for MC-{mc_number}. Status code: {response.status_code}")
        return None, None

def main(date=None):
    # Step 1: Determine the PDF URL
    if date is None:
        date = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d")   # Default to today's date
    print(f"Using date: {date}")
    pdf_url = f"https://li-public.fmcsa.dot.gov/lihtml/rptspdf/LI_REGISTER{date}.PDF"
    pdf_file = "downloaded_file.pdf"
    
    # Step 2: Download the PDF
    download_pdf(pdf_url, pdf_file)
    
    # Step 3: Extract MC numbers
    mc_numbers = extract_mc_numbers(pdf_file)
    print(f"Extracted MC numbers: {mc_numbers}")
    
    # Step 4: Fetch contact info for each MC number
    for mc in mc_numbers:
        mc_number = mc.replace("MC-", "")  # Remove the "MC-" prefix
        telephone, email = get_contact_info(mc_number)
        print(f"MC-{mc_number}: Telephone: {telephone}, Email: {email}")

if __name__ == "__main__":
    main()
