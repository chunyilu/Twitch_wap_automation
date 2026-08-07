"""Base page object: the small vocabulary every page shares.

Keeping waits, clicks and pop-up handling here (instead of in each page) is the
scalability point of the framework — new pages inherit resilient behaviour for
free and locators stay declarative.
"""
import logging
import time

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings

log = logging.getLogger(__name__)


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, settings.explicit_wait)

    # --- navigation ---
    def open(self, url):
        log.info("GET %s", url)
        self.driver.get(url)
        return self

    # --- required-element interactions (raise if missing) ---
    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        self._safe_click(el)
        return el

    def type(self, locator, text):
        el = self.find_visible(locator)
        el.clear()
        el.send_keys(text)
        return el

    # --- optional interactions (never raise; used for pop-ups) ---
    def is_present(self, locator, timeout=4) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def try_click(self, locator, timeout=4) -> bool:
        """Best-effort click. Returns True if it clicked something, else False.

        This is the primitive used to dismiss consent banners / mature-content
        overlays that may or may not appear.
        """
        try:
            el = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            self._safe_click(el)
            log.info("dismissed optional element: %s", locator)
            return True
        except TimeoutException:
            return False

    # --- helpers ---
    def scroll_page(self, times=1, pause=None):
        pause = settings.scroll_pause if pause is None else pause
        for i in range(times):
            self.driver.execute_script("window.scrollBy(0, window.innerHeight);")
            log.info("scroll %d/%d", i + 1, times)
            time.sleep(pause)

    def screenshot(self, path):
        self.driver.save_screenshot(path)
        log.info("screenshot -> %s", path)
        return path

    def _safe_click(self, el):
        try:
            el.click()
        except WebDriverException:
            # elements that are covered/animated fall back to a JS click
            self.driver.execute_script("arguments[0].click();", el)
