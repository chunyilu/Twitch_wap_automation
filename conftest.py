"""Pytest fixtures and hooks shared by the whole suite."""
import os

import pytest

from config.settings import settings
from framework.driver_factory import build_driver


@pytest.fixture
def driver():
    drv = build_driver()
    yield drv
    drv.quit()


@pytest.fixture
def artifact(driver):
    """Save a named step screenshot into the artifacts dir.

    Sequentially-numbered names (01_, 02_, ...) also feed tools/make_gif.py,
    which stitches them into the README run gif.
    """
    os.makedirs(settings.artifacts_dir, exist_ok=True)

    def _save(name):
        path = os.path.join(settings.artifacts_dir, f"{name}.png")
        driver.save_screenshot(path)
        return path

    return _save


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """On failure, grab a screenshot so failures are always debuggable."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        drv = item.funcargs.get("driver")
        if drv is not None:
            os.makedirs(settings.artifacts_dir, exist_ok=True)
            drv.save_screenshot(
                os.path.join(settings.artifacts_dir, f"FAILURE_{item.name}.png")
            )
