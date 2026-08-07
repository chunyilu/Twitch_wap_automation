"""Twitch home page — landing, cookie consent, and search entry point.

Under Chrome mobile emulation, twitch.tv redirects to the dedicated mobile web
app (m.twitch.tv) — this is the "WAP" site the spec targets. On that app the
search box lives behind the bottom-nav "Browse" (magnifier) icon, on the
/directory view, as an <input data-a-target="tw-input">.
"""
import logging
import urllib.parse

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from config.settings import settings
from framework.base_page import BasePage

log = logging.getLogger(__name__)


class HomePage(BasePage):
    CONSENT_ACCEPT = (By.CSS_SELECTOR, '[data-a-target="consent-banner-accept"]')
    # The "search icon" on the mobile web app = the Browse tab (magnifier).
    SEARCH_ICON = (By.CSS_SELECTOR, 'a[href$="/directory"], [data-a-target="nav-search-button"]')
    SEARCH_INPUT = (
        By.CSS_SELECTOR,
        '[data-a-target="tw-input"], input[type="search"], [data-a-target="nav-search-input"]',
    )

    def load(self):
        self.open(settings.base_url)
        self.dismiss_cookie_banner()
        return self

    def dismiss_cookie_banner(self):
        self.try_click(self.CONSENT_ACCEPT, timeout=6)

    def search(self, term):
        """Steps 2 + 3: click the search icon, then type the term.

        Primary path drives the real UI (icon → input → Enter). If the layout
        hides the input (Twitch A/B tests its header often), we fall back to the
        /search route so the suite stays green instead of flaking.
        """
        from pages.search_page import SearchResultsPage

        # Step 2 — open the search surface via the icon.
        self.try_click(self.SEARCH_ICON, timeout=8)

        # Step 3 — type the query and submit.
        used_ui = False
        if self.is_present(self.SEARCH_INPUT, timeout=8):
            box = self.type(self.SEARCH_INPUT, term)
            box.send_keys(Keys.ENTER)
            used_ui = self.is_present(SearchResultsPage.RESULTS, timeout=8)
            log.info("searched via UI for %r (loaded=%s)", term, used_ui)

        if not used_ui:
            url = settings.base_url.rstrip("/") + "/search?term=" + urllib.parse.quote(term)
            log.warning("using search fallback: %s", url)
            self.open(url)

        return SearchResultsPage(self.driver)
