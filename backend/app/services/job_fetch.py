import re
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

# Browser-like headers so job sites are less likely to block the request
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def extract_domain(url: str) -> str | None:
    try:
        parsed = urlparse(url)
        return parsed.netloc or None
    except Exception:
        return None


def _extract_text(el) -> str | None:
    if el is None:
        return None
    text = el.get_text(strip=True) if hasattr(el, "get_text") else str(el).strip()
    return text[:512] if text else None


async def fetch_job_from_url(url: str) -> dict:
    """Fetch job page and extract title, company, description from meta/OG and fallbacks.
    Always returns a dict with at least source_domain; may include fetch_error if the request failed.
    """
    result = {
        "title": None,
        "company": None,
        "description": None,
        "source_domain": extract_domain(url),
        "fetch_error": None,
    }
    text = None
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
            resp = await client.get(url, headers=DEFAULT_HEADERS)
            resp.raise_for_status()
            text = resp.text
    except httpx.HTTPStatusError as e:
        result["fetch_error"] = f"Site returned {e.response.status_code}. You can still add the application and edit details manually."
        return result
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        result["fetch_error"] = "Could not reach the URL (timeout or connection error). You can still add the application and edit details manually."
        return result
    except Exception:
        result["fetch_error"] = "Could not fetch the page. You can still add the application and edit details manually."
        return result

    if not text or len(text.strip()) == 0:
        return result

    try:
        soup = BeautifulSoup(text, "html.parser")
    except Exception:
        return result

    # Open Graph / meta (most job sites set these)
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        result["title"] = og_title["content"].strip()[:512]
    og_desc = soup.find("meta", property="og:description")
    if og_desc and og_desc.get("content"):
        result["description"] = og_desc["content"].strip()[:10000]
    # Twitter card fallback
    if not result["title"]:
        tw_title = soup.find("meta", attrs={"name": "twitter:title"})
        if tw_title and tw_title.get("content"):
            result["title"] = tw_title["content"].strip()[:512]

    # Standard meta
    if not result["title"]:
        meta_title = soup.find("meta", attrs={"name": re.compile(r"title", re.I)})
        if meta_title and meta_title.get("content"):
            result["title"] = meta_title["content"].strip()[:512]
    if not result["title"] and soup.title and soup.title.string:
        result["title"] = soup.title.string.strip()[:512]
    if not result["description"]:
        meta_desc = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
        if meta_desc and meta_desc.get("content"):
            result["description"] = meta_desc["content"].strip()[:10000]

    # Fallback: first <h1> (many job pages have "Job Title" in h1)
    if not result["title"]:
        h1 = soup.find("h1")
        if h1:
            result["title"] = _extract_text(h1)

    # Heuristic: company from title (e.g. "Senior Engineer at Acme" -> Acme) or domain
    if not result["company"] and result["title"]:
        at_match = re.search(r"\s+at\s+([A-Za-z0-9&\s]+?)(?:\s*[-|]|$)", result["title"])
        if at_match:
            result["company"] = at_match.group(1).strip()[:255]
    if not result["company"] and result["source_domain"]:
        result["company"] = result["source_domain"].replace("www.", "").split(".")[0][:255]

    return result
