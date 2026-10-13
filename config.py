from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"

# Use data/ directory if it exists (Docker), otherwise use root (local dev)
DATA_DIR = BASE_DIR / "data"
if DATA_DIR.exists():
    COOKIES_FILE = DATA_DIR / "cookies.json"
else:
    COOKIES_FILE = BASE_DIR / "cookies.json"

BASE_URL = "https://learning.oreilly.com"
API_V1 = f"{BASE_URL}/api/v1"
API_V2 = f"{BASE_URL}/api/v2"

REQUEST_DELAY = 0.5
REQUEST_TIMEOUT = 30

# Retry transient network failures (timeouts, connection resets, Akamai
# throttling stalls) so a single bad response doesn't abort a whole download.
MAX_RETRIES = 4
RETRY_BACKOFF = 1.5

# Book stylesheets are written for e-readers, where the reading app adds its
# own margins, so some set tiny page margins of their own (O'Reilly's uses
# "@page{margin:5px !important}"). In a PDF nothing else adds margins, so that
# rule leaves text running to the edge of the page. By default the PDF ignores
# @page rules from the book and uses the page size and margins from
# plugins/pdf_styles/print.css. Set to True to keep the book's own rules.
PDF_USE_BOOK_PAGE_RULES = False

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": BASE_URL,
    # User-Agent is intentionally omitted — curl_cffi sets it to match the
    # browser impersonation (safari17_0), and overriding it would cause a
    # TLS-fingerprint/UA mismatch that Akamai detects as a bot.
}
