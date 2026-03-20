from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from app.logger import get_logger

logger = get_logger(__name__)


def get_driver() -> webdriver.Chrome:

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    try:

        import os
        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", None)
        chrome_bin = os.environ.get("CHROME_BIN", None)

        if chrome_bin:
            options.binary_location = chrome_bin

        if chromedriver_path:
            service = Service(executable_path=chromedriver_path)
        else:
            service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=options)
        logger.info("WebDriver iniciado correctamente.")
        return driver

    except Exception as e:
        logger.error(f"Error al iniciar WebDriver: {e}")
        raise