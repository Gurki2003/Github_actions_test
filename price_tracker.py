import os
import smtplib
import time
from email.mime.text import MIMEText
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
url = "https://www.myntra.com/watches/casio/casio-edifice-efr-s108de-2avudf-blue-analog-dial-stainless-steel-band-ed677/37617410/buy"
PRICE_THRESHOLD = 100000  # Target price threshold in INR

# Email configuration from GitHub Actions secrets
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "workdummy12345@gmail.com"
SMTP_PASS = "sucf smwf snax houw"
ALERT_TO = "gurkirat1228@gmail.com"

# --- Functions ---

def get_price():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1200")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(url)
    time.sleep(8)  # Allow Myntra JS to load fully

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    try:
        import re
        price_span = soup.find("span", class_="pdp-discounted-price")
        if not price_span:
            price_span = soup.find("span", class_="pdp-price")
        if not price_span:
            raise ValueError("Price element not found")
        price_text = price_span.get_text(strip=True)
        numbers = re.findall(r"\d+", price_text)
        if not numbers:
            raise ValueError(f"No numeric price found in text: {price_text}")
        amount_int = int("".join(numbers))
        return amount_int
    except Exception as e:
        raise ValueError(f"⚠️ Failed to parse price from Myntra page: {e}")


def send_email_alert(current_price):
    subject = "💰 Price Drop Alert!"
    body = f"The price dropped to ₹{current_price}!\n\nCheck it here: {url}"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print("✅ Email alert sent.")

# --- Main Script ---

def main():
    if not all([SMTP_USER, SMTP_PASS, ALERT_TO]):
        raise ValueError("❌ Missing SMTP credentials or recipient email. Set them as GitHub Secrets.")

    try:
        current_price = get_price()
        print(f"📦 Current price: ₹{current_price}")

        if current_price <= PRICE_THRESHOLD:
            print("💡 Price is below threshold! Sending email...")
            send_email_alert(current_price)
        else:
            print("ℹ️ Price is above threshold. No alert sent.")

    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    main()
