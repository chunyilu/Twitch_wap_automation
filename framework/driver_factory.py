"""Builds a Chrome WebDriver configured as a mobile device emulator.

Uses Chrome's built-in mobile emulation (the "Mobile emulator from Google
Chrome" required by the spec) and relies on Selenium Manager (bundled with
Selenium 4.6+) to download a matching chromedriver automatically.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from config.settings import settings


def build_driver() -> webdriver.Chrome:
    options = Options()

    # --- Mobile emulation: this is what makes it a WAP / mobile-web test ---
    options.add_experimental_option(
        "mobileEmulation", {"deviceName": settings.device_name}
    )

    if settings.headless:
        options.add_argument("--headless=new")
    options.add_argument(f"--window-size={settings.window_width},{settings.window_height}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=en-US")

    # Reduce the most obvious "I am automation" signals.
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if settings.chrome_binary:
        options.binary_location = settings.chrome_binary

    driver = webdriver.Chrome(service=Service(), options=options)
    driver.set_page_load_timeout(settings.page_load_timeout)
    return driver
