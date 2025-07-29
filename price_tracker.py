import os
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup

PRODUCT_URL = "https://www.lenovo.com/in/en/p/accessories-and-software/monitors/gaming/67b4gac1in"
PRICE_THRESHOLD = 80000

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
ALERT_TO = os.getenv("ALERT_TO")

def get_price():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(PRODUCT_URL, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    price_element = soup.select_one(".pricingSummary-details .sale-price")

    if not price_element:
        raise Exception("Price not found.")
    
    price_text = price_element.text.strip().replace(",", "").replace("₹", "")
    return float(price_text)

def send_email_alert(current_price):
    msg = MIMEText(f"The Lenovo price dropped to {current_price}!\n\n{PRODUCT_URL}")
    msg["Subject"] = "💰 Lenovo Price Drop Alert"
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print("✅ Email sent successfully.")

def main():
    try:
        current_price = get_price()
        print(f"📦 Current Price: {current_price}")

        if current_price <= PRICE_THRESHOLD:
            send_email_alert(current_price)
        else:
            print("ℹ️ No alert: price is above threshold.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
