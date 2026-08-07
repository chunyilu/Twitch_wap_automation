"""Central, environment-driven configuration.

Every value has a sensible default and can be overridden via an environment
variable, so the same test suite runs unchanged on a laptop, in CI, or against
a different Twitch locale/device without touching code.
"""
import os
from dataclasses import dataclass


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("TWITCH_BASE_URL", "https://www.twitch.tv/")
    search_term: str = os.getenv("SEARCH_TERM", "StarCraft II")
    # Any Chrome DevTools device name: "Pixel 7", "iPhone 12 Pro", "Galaxy S20 Ultra"...
    device_name: str = os.getenv("DEVICE_NAME", "Pixel 7")
    headless: bool = _as_bool(os.getenv("HEADLESS"), False)
    window_width: int = int(os.getenv("WINDOW_WIDTH", "412"))
    window_height: int = int(os.getenv("WINDOW_HEIGHT", "915"))
    explicit_wait: int = int(os.getenv("EXPLICIT_WAIT", "25"))
    page_load_timeout: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "60"))
    scroll_times: int = int(os.getenv("SCROLL_TIMES", "2"))
    scroll_pause: float = float(os.getenv("SCROLL_PAUSE", "2.0"))
    player_settle: float = float(os.getenv("PLAYER_SETTLE", "4.0"))
    chrome_binary: str = os.getenv("CHROME_BINARY", "")
    artifacts_dir: str = os.getenv("ARTIFACTS_DIR", "artifacts")


settings = Settings()
