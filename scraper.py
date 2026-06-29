#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OTA Review Scraper for Booking.com, Agoda, and MakeMyTrip.
Uses Playwright with stealth and proxy rotation.
"""

try:
    from pyvirtualdisplay import Display
    _display = Display(visible=0, size=(1280, 800))
    _display.start()
except ImportError:
    pass

import os
import re
import random
import time
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

# ── Stealth ────────────────────────────────────────────────
try:
    from playwright_stealth import stealth_sync
except ImportError:
    def stealth_sync(page):
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )

# ── Proxy management ───────────────────────────────────────
def load_proxies(file_path="proxies.txt"):
    if not os.path.exists(file_path):
        return []
    proxies = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if not line.startswith(("http://", "https://")):
                line = "http://" + line
            try:
                parsed = urlparse(line)
                if parsed.hostname and parsed.port and isinstance(parsed.port, int):
                    proxy_dict = {"server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"}
                    if parsed.username and parsed.password:
                        proxy_dict["username"] = parsed.username
                        proxy_dict["password"] = parsed.password
                    proxies.append(proxy_dict)
            except Exception:
                continue
    return proxies

def get_random_proxy(proxy_list):
    return random.choice(proxy_list) if proxy_list else None

# ── Browser launcher ───────────────────────────────────────
def _launch_browser(headless=True, proxy=None):
    playwright = sync_playwright().start()
    args = [
        "--disable-blink-features=AutomationControlled",
        "--disable-web-security",
        "--disable-features=IsolateOrigins,site-per-process",
        "--no-sandbox",
        "--disable-http2",
    ]
    launch_kwargs = {
        "headless": headless,
        "args": args,
        "ignore_default_args": ["--enable-automation"],
    }
    if proxy:
        launch_kwargs["proxy"] = proxy
    browser = playwright.chromium.launch(**launch_kwargs)
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1280, "height": 800},
        locale="en-US",
        extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
    )
    page = context.new_page()
    stealth_sync(page)
    return playwright, browser, page

def _scroll_and_load(page, load_more_selector=None, scroll_attempts=6):
    for _ in range(scroll_attempts):
        try:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.8)")
        except Exception:
            time.sleep(1)
            continue
        time.sleep(random.uniform(1.0, 2.0))
        if load_more_selector:
            try:
                btn = page.query_selector(load_more_selector)
                if btn and btn.is_visible():
                    btn.click()
                    time.sleep(random.uniform(2.0, 3.5))
            except Exception:
                pass
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    except Exception:
        pass
    time.sleep(2)

# ── Booking.com ────────────────────────────────────────────
def scrape_booking_reviews_with_proxy(url, headless=True, max_reviews=30):
    proxies = load_proxies()
    for attempt in range(3):
        proxy = get_random_proxy(proxies)
        pw, browser, page = None, None, None
        try:
            pw, browser, page = _launch_browser(headless, proxy)
            reviews_tab_url = url.split("?")[0].split("#")[0] + "#tab-reviews"
            page.goto(reviews_tab_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("body", timeout=10000)
            time.sleep(4)

            for ck_sel in ["#onetrust-accept-btn-handler", "button:has-text('Accept')", "button:has-text('I agree')"]:
                try:
                    btn = page.query_selector(ck_sel)
                    if btn and btn.is_visible():
                        btn.click()
                        time.sleep(1)
                        break
                except Exception:
                    pass

            try:
                page.evaluate("""
                    const el = document.querySelector('[data-testid="PropertyReviewsRegionBlock"]')
                               || document.querySelector('[id="tab-reviews"]');
                    if (el) el.scrollIntoView({behavior: 'smooth', block: 'start'});
                """)
                time.sleep(3)
            except Exception:
                pass

            for sel in [
                "[data-testid='Property-Header-Nav-Tab-Trigger-reviews']",
                "a[href*='tab-reviews']",
                "li a:has-text('Reviews')",
                "button:has-text('Reviews')",
            ]:
                try:
                    el = page.query_selector(sel)
                    if el and el.is_visible():
                        el.click()
                        print(f"Clicked reviews tab: {sel}")
                        time.sleep(3)
                        break
                except Exception:
                    pass

            print(f"URL after tab click: {page.url}")

            full_card_sel = None
            for sel in ["[data-testid='review']", "[data-testid='review-card']", ".c-review-block", ".review_item"]:
                try:
                    page.wait_for_selector(sel, timeout=10000)
                    count = len(page.query_selector_all(sel))
                    if count > 0:
                        full_card_sel = sel
                        print(f"Found {count} full review cards: {sel}")
                        break
                except Exception:
                    continue

            if not full_card_sel:
                for _ in range(5):
                    page.evaluate("window.scrollBy(0, 600)")
                    time.sleep(2)
                    for sel in ["[data-testid='review']", "[data-testid='review-card']"]:
                        cards = page.query_selector_all(sel)
                        if cards:
                            full_card_sel = sel
                            break
                    if full_card_sel:
                        break

            if not full_card_sel:
                test_ids = page.evaluate("""
                    [...document.querySelectorAll('[data-testid]')]
                      .map(el => el.getAttribute('data-testid'))
                      .filter((v, i, a) => a.indexOf(v) === i)
                      .filter(v => v.toLowerCase().includes('review'))
                """)
                print(f"No review cards found. testids: {test_ids}")
                return []

            for i in range(6):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.9)")
                time.sleep(2)
                for btn_text in ["Show more", "Load more reviews", "More reviews"]:
                    try:
                        btn = page.query_selector(f"button:has-text('{btn_text}')")
                        if btn and btn.is_visible():
                            btn.click()
                            print(f"Clicked '{btn_text}' (scroll {i+1})")
                            time.sleep(3)
                    except Exception:
                        pass
                if len(page.query_selector_all(full_card_sel)) >= max_reviews:
                    break

            cards = page.query_selector_all(full_card_sel)
            reviews = []

            for idx, card in enumerate(cards[:max_reviews]):
                try:
                    name = "Guest"
                    country = ""
                    avatar_el = card.query_selector("[data-testid='review-avatar']")
                    if avatar_el:
                        for div in avatar_el.query_selector_all("div"):
                            txt = div.inner_text().strip()
                            if txt and 2 < len(txt) < 60 and "\n" not in txt:
                                if not div.query_selector("img"):
                                    name = txt
                                    break
                        for span in avatar_el.query_selector_all("span"):
                            txt = span.inner_text().strip()
                            if len(txt) > 1:
                                country = txt
                                break

                    rating = 4
                    for rating_sel in ["[data-testid='review-score']", "[class*='review-score']", "[class*='Score']"]:
                        el = card.query_selector(rating_sel)
                        if el:
                            m = re.search(r"(\d+(?:\.\d+)?)", el.inner_text())
                            if m:
                                val = float(m.group(1))
                                if val > 5:
                                    val = val / 2.0
                                rating = max(1, min(5, round(val)))
                            break

                    text = ""
                    for text_sel in [
                        "[data-testid='review-positive-text']",
                        "[data-testid='review-negative-text']",
                        "[data-testid='review-body']",
                        "[class*='review-text']",
                        "[class*='reviewText']",
                        "p",
                    ]:
                        el = card.query_selector(text_sel)
                        if el:
                            text = el.inner_text().strip()
                            if text:
                                break

                    if not text:
                        lines = [l.strip() for l in card.inner_text().split("\n") if l.strip()]
                        filtered = [l for l in lines if len(l) > 20 and not l.replace(".", "").replace(",", "").isdigit()]
                        text = max(filtered, key=len) if filtered else ""

                    if not text:
                        continue

                    date_text = ""
                    for date_sel in ["[data-testid='review-date']", "[data-testid='review-publish-date']", ".c-review-block__date", "[class*='date']"]:
                        el = card.query_selector(date_sel)
                        if el:
                            date_text = el.inner_text().strip()
                            if date_text:
                                break

                    reviews.append({
                        "guest_name": name,
                        "country": country,
                        "rating": rating,
                        "review_text": text,
                        "source": "Booking.com",
                        "date": date_text,
                    })

                except Exception as e:
                    if idx == 0:
                        print(f"First card parse error: {e}")
                    continue

            if reviews:
                print(f"Extracted {len(reviews)} reviews from Booking.com")
                return reviews
            print("Cards found but no reviews extracted.")
            return []

        except Exception as e:
            print(f"Booking attempt {attempt + 1} failed: {e}")
        finally:
            if browser:
                browser.close()
            if pw:
                pw.stop()
        time.sleep(random.uniform(3, 6))
    return []

# ── Agoda ──────────────────────────────────────────────────
def scrape_agoda_reviews(url, headless=True, max_reviews=30):
    proxies = load_proxies()
    for attempt in range(3):
        proxy = get_random_proxy(proxies)
        pw, browser, page = None, None, None
        try:
            pw, browser, page = _launch_browser(headless, proxy)
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("body", timeout=15000)
            time.sleep(5)

            for tab_sel in ["a:has-text('Reviews')", "button:has-text('Reviews')"]:
                try:
                    tab = page.query_selector(tab_sel)
                    if tab and tab.is_visible():
                        tab.click()
                        time.sleep(3)
                        break
                except Exception:
                    pass

            # Scroll to trigger review load
            for _ in range(4):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.8)")
                time.sleep(2)

            card_sel = "div.Review-comment"
            try:
                page.wait_for_selector(card_sel, timeout=15000)
            except Exception:
                print("Agoda: no review cards found.")
                return []

            cards = page.query_selector_all(card_sel)
            print(f"Agoda: found {len(cards)} cards")
            seen = set()
            reviews = []

            for idx, card in enumerate(cards[:max_reviews * 2]):
                if len(reviews) >= max_reviews:
                    break
                try:
                    text_el = card.query_selector("[data-testid='review-comment']")
                    if not text_el:
                        text_el = card.query_selector("p.Review-comment-bodyText")
                    if not text_el:
                        text_el = card.query_selector("[class*='bodyText']")
                    text = text_el.inner_text().strip() if text_el else ""
                    if not text or text in seen:
                        continue
                    seen.add(text)

                    name_el = card.query_selector("[data-info-type='reviewer-name'] strong")
                    name = name_el.inner_text().strip() if name_el else "Guest"

                    country = ""
                    reviewer_div = card.query_selector("[data-info-type='reviewer-name']")
                    if reviewer_div:
                        for span in reviewer_div.query_selector_all("span"):
                            txt = span.inner_text().strip()
                            if len(txt) > 1:
                                country = txt
                                break

                    rating = 4
                    score_el = card.query_selector("p.ifcRDN span, [class*='eyidZH']")
                    if score_el:
                        m = re.search(r"(\d+(?:\.\d+)?)", score_el.inner_text())
                        if m:
                            val = float(m.group(1))
                            if val > 5:
                                val = val / 2.0
                            rating = max(1, min(5, round(val)))

                    date_text = ""
                    date_el = card.query_selector(".Review-statusBar span")
                    if date_el:
                        date_text = date_el.inner_text().strip()

                    stay_el = card.query_selector("[data-info-type='stay-detail'] span")
                    stay = stay_el.inner_text().strip() if stay_el else ""

                    reviews.append({
                        "guest_name": name,
                        "country": country,
                        "rating": rating,
                        "review_text": text,
                        "source": "Agoda",
                        "date": date_text,
                        "stay_info": stay,
                    })

                except Exception as e:
                    if idx == 0:
                        print(f"Agoda first card error: {e}")
                    continue

            if reviews:
                print(f"Extracted {len(reviews)} reviews from Agoda")
                return reviews
            print("Agoda: cards found but no reviews extracted.")
            return []

        except Exception as e:
            print(f"Agoda attempt {attempt + 1} failed: {e}")
        finally:
            if browser:
                browser.close()
            if pw:
                pw.stop()
        time.sleep(random.uniform(3, 6))
    return []

# ── MakeMyTrip ─────────────────────────────────────────────
def scrape_mmt_reviews(url, headless=True, max_reviews=30):
    """
    MakeMyTrip blocks automated scraping with bot detection.
    Returns empty list unless real residential proxies are in proxies.txt.
    To enable: add real residential proxies to proxies.txt (one per line).
    Format: http://username:password@host:port
    """
    proxies = load_proxies()
    if not proxies:
        print("MMT: no proxies available - skipping (bot detection active)")
        return []

    for attempt in range(3):
        proxy = get_random_proxy(proxies)
        pw, browser, page = None, None, None
        try:
            pw, browser, page = _launch_browser(headless, proxy)
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("body", timeout=15000)
            time.sleep(4)

            body_text = page.inner_text("body") if page.query_selector("body") else ""
            if len(body_text) < 500 or "review" not in body_text.lower():
                print(f"MMT attempt {attempt+1}: page blocked or too short ({len(body_text)} chars)")
                continue

            try:
                page.click("button:has-text('Accept')", timeout=3000)
            except Exception:
                pass

            for _ in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.7)")
                time.sleep(2)

            for tab_sel in ["li:has-text('Reviews')", "a:has-text('Reviews')", "button:has-text('Reviews')"]:
                try:
                    el = page.query_selector(tab_sel)
                    if el and el.is_visible():
                        el.click()
                        time.sleep(3)
                        break
                except Exception:
                    pass

            for i in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.9)")
                time.sleep(2)
                for btn_text in ["Load More", "View More Reviews", "See More"]:
                    try:
                        btn = page.query_selector(f"button:has-text('{btn_text}')")
                        if btn and btn.is_visible():
                            btn.click()
                            time.sleep(3)
                    except Exception:
                        pass

            card_sel = None
            for sel in ["[class*='reviewRow']", "[class*='reviewCard']", "[class*='review_wrapper']",
                        "[class*='ReviewCard']", "[class*='guestReview']", ".reviewRow"]:
                if page.query_selector_all(sel):
                    card_sel = sel
                    break

            if not card_sel:
                print(f"MMT attempt {attempt+1}: no review cards found")
                continue

            cards = page.query_selector_all(card_sel)
            seen = set()
            reviews = []

            for idx, card in enumerate(cards[:max_reviews * 2]):
                if len(reviews) >= max_reviews:
                    break
                try:
                    text = ""
                    for ts in ["[class*='reviewText']", "[class*='review_text']", "[class*='textContent']", "p"]:
                        el = card.query_selector(ts)
                        if el:
                            text = el.inner_text().strip()
                            if text and len(text) > 10:
                                break
                    if not text:
                        lines = [l.strip() for l in card.inner_text().split("\n") if l.strip()]
                        filtered = [l for l in lines if len(l) > 20]
                        text = max(filtered, key=len) if filtered else ""
                    if not text or text in seen:
                        continue
                    seen.add(text)

                    name = "Guest"
                    for ns in ["[class*='userName']", "[class*='reviewerName']", "[class*='authorName']"]:
                        el = card.query_selector(ns)
                        if el:
                            name = el.inner_text().strip()
                            if name:
                                break

                    rating = 4
                    for rs in ["[class*='ratingBubble']", "[class*='ratingValue']", "[class*='rating']"]:
                        el = card.query_selector(rs)
                        if el:
                            m = re.search(r"(\d+(?:\.\d+)?)", el.inner_text())
                            if m:
                                val = float(m.group(1))
                                if val > 5:
                                    val = val / 2.0
                                rating = max(1, min(5, round(val)))
                            break

                    date_text = ""
                    for ds in ["[class*='date']", "[class*='Date']", "[class*='reviewDate']"]:
                        el = card.query_selector(ds)
                        if el:
                            date_text = el.inner_text().strip()
                            if date_text:
                                break

                    reviews.append({"guest_name": name, "rating": rating,
                                    "review_text": text, "source": "MakeMyTrip", "date": date_text})
                except Exception:
                    continue

            if reviews:
                print(f"Extracted {len(reviews)} reviews from MakeMyTrip")
                return reviews

        except Exception as e:
            print(f"MMT attempt {attempt+1} failed: {e}")
        finally:
            if browser:
                browser.close()
            if pw:
                pw.stop()
        time.sleep(random.uniform(4, 7))
    return []