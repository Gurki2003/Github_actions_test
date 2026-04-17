import re
import smtplib
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from email.mime.text import MIMEText
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
url = "https://neomacro.in/products/vgn-vxe-r1-series?variant=51089222598934"


# Email configuration from GitHub Actions secrets
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "workdummy12345@gmail.com"
SMTP_PASS = "sucf smwf snax houw"
ALERT_TO = "gurkirat1228@gmail.com"

# --- Functions ---

def get_stock_status():
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
    a_soup = soup.find('div', class_='product-form__buttons')
    b_soup = a_soup.find('button', class_='product-form__submit')
    soldOut_or_not = b_soup.get_text(strip=True)
    if soldOut_or_not == "Sold out":
        return 0
    else:
        return 1     


def send_email_alert():
    subject = "VXE R1 PRO in back in stock!"
    body = f"\n\nCheck it here: {url}"
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
        current_stock = get_stock_status()
        print(f"📦 Current stock status: {current_stock}")

        if current_stock <= 0:
            print("ℹ️ Product is not in stock. No need to send alert.")
        else:
            send_email_alert()

    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    main()
