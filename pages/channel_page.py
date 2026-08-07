"""Twitch streamer/channel page — dismiss overlays, wait for it to load.

Note: on the unauthenticated mobile web app the live <video> element is often
not mounted (Twitch nudges users to the native app), so "loaded" is keyed off
the channel header (Follow / More actions), falling back to the player when it
does render.
"""
import logging
import time

from selenium.webdriver.common.by import By

from config.settings import settings
from framework.base_page import BasePage

log = logging.getLogger(__name__)


class ChannelPage(BasePage):
    # Any of these means the channel page has rendered.
    READY = (
        By.CSS_SELECTOR,
        'video, [data-a-target="video-player"], '
        '[aria-label^="Follow"], button[aria-label="More actions"]',
    )

    # Overlays that may (or may not) appear — each handled best-effort. This is
    # the "handle the pop-up before the video" requirement from the spec.
    OVERLAYS = [
        (By.CSS_SELECTOR, '[data-a-target="consent-banner-accept"]'),
        (By.CSS_SELECTOR, '[data-a-target="player-overlay-mature-accept"]'),
        (By.CSS_SELECTOR,
         '[data-a-target="content-classification-gate-overlay-start-watching-button"]'),
        (By.XPATH, "//button[contains(., 'Start Watching')]"),
        (By.XPATH, "//button[contains(., 'Continue') or contains(., 'Not now') "
                   "or contains(., 'No thanks') or contains(., 'Maybe later')]"),
        (By.CSS_SELECTOR, '[aria-label="Close"], [aria-label="close"]'),
    ]

    def dismiss_popups(self):
        for locator in self.OVERLAYS:
            self.try_click(locator, timeout=3)
        return self

    def wait_until_loaded(self):
        # Step 6: wait until the streamer page is loaded (handling pop-ups).
        self.dismiss_popups()
        self.find(self.READY)
        time.sleep(settings.player_settle)   # let content/player settle
        self.dismiss_popups()                # some overlays only appear late
        return self

    def take_screenshot(self, path):
        return self.screenshot(path)
