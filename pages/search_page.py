"""Twitch search results — scroll and pick a live streamer.

On m.twitch.tv the "Top" tab renders streamer cards as non-anchor widgets, but
the "Channels" tab lists each streamer as a plain `/{channel}` link — far more
stable to target. open_first_streamer() switches to that tab and clicks the
first channel.
"""
import logging
import re

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from framework.base_page import BasePage

log = logging.getLogger(__name__)

# Single-segment paths that are navigation/system, not streamer channels.
_NON_CHANNEL = {
    "directory", "activity", "home", "following", "subscriptions", "search",
    "settings", "wallet", "drops", "prime", "friends", "downloads", "login",
    "signup", "videos", "u", "team", "products", "turbo", "jobs", "p",
}
_CHANNEL_RE = re.compile(r"^/([A-Za-z0-9_]{2,25})$")


class SearchResultsPage(BasePage):
    RESULTS = (By.CSS_SELECTOR, '[data-a-target="tw-input"], [data-a-target="search-results"], main')
    CHANNELS_TAB = (By.CSS_SELECTOR, 'a[href*="type=channels"]')

    def wait_loaded(self):
        self.find(self.RESULTS)
        return self

    def scroll(self, times):
        # Step 4: scroll down N times (default 2).
        self.scroll_page(times)
        return self

    def open_first_streamer(self):
        """Step 5: select one streamer. Returns (ChannelPage, href)."""
        from pages.channel_page import ChannelPage

        # Narrow to the Channels tab, where each streamer is a real link.
        self.try_click(self.CHANNELS_TAB, timeout=8)
        self.scroll_page(1)  # nudge lazy-loaded results in

        try:
            self.wait.until(lambda d: len(self._channel_links()) > 0)
        except TimeoutException as exc:
            raise AssertionError(
                "No streamer/channel results found for the search term."
            ) from exc

        target = self._channel_links()[0]
        href = target.get_attribute("href")
        log.info("selecting streamer: %s", href)
        self._safe_click(target)
        return ChannelPage(self.driver), href

    def _channel_links(self):
        links = []
        for a in self.driver.find_elements(By.CSS_SELECTOR, "a[href]"):
            href = a.get_attribute("href") or ""
            path = href.split("twitch.tv", 1)[-1]  # -> "/koka"
            m = _CHANNEL_RE.match(path)
            if m and m.group(1).lower() not in _NON_CHANNEL:
                links.append(a)
        return links
