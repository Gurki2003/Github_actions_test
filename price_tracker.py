import os
import smtplib
import time
from email.mime.text import MIMEText

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
url = "https://www.amazon.in/dp/B0B5HB3F85?ref=cm_sw_r_cp_ud_dp_03WBDFYZ5RZ35EYK6RTG&ref_=cm_sw_r_cp_ud_dp_03WBDFYZ5RZ35EYK6RTG&social_share=cm_sw_r_cp_ud_dp_03WBDFYZ5RZ35EYK6RTG"
PRICE_THRESHOLD = 3998  # Target price threshold in INR

# Email configuration from GitHub Actions secrets
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "workdummy12345@gmail.com"
SMTP_PASS = "sucf smwf snax houw"
ALERT_TO = "gurkirat1228@gmail.com"

# --- Functions ---

def get_price():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    time.sleep(10)  # Allow JavaScript to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    try:
        cost_class = soup.find('div', class_="a-section a-spacing-none aok-align-center aok-relative")
        price = cost_class.find('span', class_='a-price-whole').text.strip()
        cleaned_amount = price.replace("₹", "").replace(",", "")
        amount_int = int(cleaned_amount)
        return amount_int
    except Exception as e:
        raise ValueError(f"⚠️ Failed to parse price from the page: {e}")

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
