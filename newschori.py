"""
newschori.py

Your original Selenium scraper, kept as-is in approach (same URL, same
scroll-and-wait pattern, same "gPFEn" class), with two additions:

1. It now also grabs each headline's link (needed for the "Get NEWS" table
   and double-click-to-open behaviour in tk.py).
2. Each headline is run through your pretrained TF-IDF + Logistic
   Regression model right after scraping, so every item in `l` already has
   a "category" key by the time tk.py reads it.

`l` is populated at import time, same as your original script — tk.py does
`import newschori` and reads `newschori.l`.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "logistic_model.joblib")
VEC_PATH = os.path.join(BASE_DIR, "tfidf_vectorizer.joblib")

URL = "https://news.google.com/topics/CAAqJQgKIh9DQkFTRVFvSUwyMHZNRE55YXpBU0JXVnVMVWRDS0FBUAE?hl=en-IN&gl=IN&ceid=IN%3Aen"

l = []


def _get_link(art):
    """
    The 'gPFEn' element is usually the <a> tag itself (that's why .text on
    it already gave you the full headline in your original script) — so
    looking *above* it for an ancestor <a> finds nothing. Try, in order:
    1. art itself, if it's already an <a>
    2. the nearest ancestor <a>
    3. an <a> among its siblings
    """
    try:
        if art.tag_name.lower() == "a":
            href = art.get_attribute("href")
            if href:
                return href
    except Exception:
        pass

    try:
        anchor = art.find_element(By.XPATH, "./ancestor::a[1]")
        href = anchor.get_attribute("href")
        if href:
            return href
    except Exception:
        pass

    try:
        anchor = art.find_element(By.XPATH, "./parent::*/a[1]")
        href = anchor.get_attribute("href")
        if href:
            return href
    except Exception:
        pass

    return "#"


def _scrape():
    driver = webdriver.Edge()
    wait = WebDriverWait(driver, 10)
    results = []

    try:
        driver.get(URL)

        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        articles = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "gPFEn")))

        seen = set()
        for art in articles:
            title = art.text.strip()
            if not title or title in seen:
                continue
            seen.add(title)

            results.append({"title": title, "link": _get_link(art)})

    finally:
        driver.quit()

    return results


def _categorize(items):
    if not items:
        return items
    try:
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VEC_PATH)
        texts = [it["title"] for it in items]
        X = vectorizer.transform(texts)
        preds = model.predict(X)
        for it, cat in zip(items, preds):
            it["category"] = cat
    except Exception as e:
        # If the model can't load for any reason, still show the news —
        # just mark it as uncategorized instead of crashing the app.
        for it in items:
            it["category"] = f"Uncategorized ({e.__class__.__name__})"
    return items


l = _categorize(_scrape())