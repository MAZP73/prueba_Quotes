import time
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.utils.driver import get_driver
from app.db.schemas import QuoteCreateSchema
from app.logger import get_logger

logger = get_logger(__name__)

BASE_URL = "https://quotes.toscrape.com"


class ScraperService:

    def scrape_all_quotes(self) -> List[QuoteCreateSchema]:

        driver = get_driver()
        all_quotes: List[QuoteCreateSchema] = []
        current_url = BASE_URL

        try:
            while current_url:
                logger.info(f"Scraping página: {current_url}")
                driver.get(current_url)

                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "quote"))
                )

                quote_elements = driver.find_elements(By.CLASS_NAME, "quote")
                logger.info(f"  → {len(quote_elements)} citas encontradas en esta página.")

                for elem in quote_elements:
                    try:
                        text = elem.find_element(By.CLASS_NAME, "text").text.strip()

                        text = text.strip("\u201c\u201d").strip()

                        author = elem.find_element(By.CLASS_NAME, "author").text.strip()

                        tag_elements = elem.find_elements(By.CLASS_NAME, "tag")
                        tags = [t.text.strip() for t in tag_elements if t.text.strip()]

                        all_quotes.append(
                            QuoteCreateSchema(text=text, author=author, tags=tags)
                        )
                    except Exception as e:
                        logger.warning(f"Error al parsear cita: {e}")
                        continue

                try:
                    next_btn = driver.find_element(By.CSS_SELECTOR, "li.next > a")
                    next_href = next_btn.get_attribute("href")
                    current_url = next_href if next_href.startswith("http") else BASE_URL + next_href
                    time.sleep(1)
                except Exception:
                    logger.info("No hay más páginas. Scraping finalizado.")
                    current_url = None

        except Exception as e:
            logger.error(f"Error general en scraping: {e}")
            raise
        finally:
            driver.quit()
            logger.info("WebDriver cerrado.")

        logger.info(f"Total de citas extraídas: {len(all_quotes)}")
        return all_quotes