"""WAP scenario: search StarCraft II on Twitch (mobile) and screenshot a stream.

Maps 1:1 to the spec steps:
    1 go to Twitch
    2 click the search icon
    3 input "StarCraft II"
    4 scroll down 2 times
    5 select one streamer
    6 wait until the streamer page is loaded, then take a screenshot
Pop-ups/overlays before the video are handled by ChannelPage.dismiss_popups().
"""
import os

from config.settings import settings
from pages.home_page import HomePage


def test_search_starcraft_and_screenshot_stream(driver, artifact):
    # 1 — go to Twitch
    home = HomePage(driver).load()
    artifact("01_home")

    # 2 + 3 — click search, input the term
    results = home.search(settings.search_term).wait_loaded()
    artifact("02_search_results")

    # 4 — scroll down 2 times
    results.scroll(settings.scroll_times)
    artifact("03_after_scroll")

    # 5 — select one streamer
    channel, href = results.open_first_streamer()

    # 6 — wait until loaded (handling pop-ups), then screenshot
    channel.wait_until_loaded()
    shot = channel.take_screenshot(
        os.path.join(settings.artifacts_dir, "04_streamer_page.png")
    )

    assert os.path.exists(shot) and os.path.getsize(shot) > 0, "screenshot not captured"
    assert href, "no streamer was selected"
