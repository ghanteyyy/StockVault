"""Fetch target quotes without holding up the Wishlist on slow requests."""

import math
from concurrent.futures import ThreadPoolExecutor, wait

from Shares import scraper


QUOTE_WAIT_SECONDS = 3
_quote_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix='target-quote')


def _market_price(symbol):
    try:
        quote = scraper.get_market_data(symbol)
        price = float(str(quote['market_price']).replace(',', '').strip())
    except Exception:
        # A failed request or unexpected quote must not hide other targets.
        return None

    return price if math.isfinite(price) and price >= 0 else None


def market_prices(symbols):
    futures = {_quote_pool.submit(_market_price, symbol): symbol for symbol in dict.fromkeys(symbols)}
    done, pending = wait(futures, timeout=QUOTE_WAIT_SECONDS)
    for future in pending:
        future.cancel()

    return {futures[future]: future.result() for future in done}
