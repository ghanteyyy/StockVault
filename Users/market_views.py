"""Read-only NEPSE snapshots for the user workspace."""

import asyncio
import logging
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.cache.backends.locmem import LocMemCache
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_safe
from nepse import AsyncNepse


logger = logging.getLogger(__name__)

CACHE_KEY = 'stockvault:market-data:v1'
LAST_GOOD_KEY = f'{CACHE_KEY}:last-good'
CACHE_TTL = 60
FAILURE_TTL = 15
STALE_TTL = 24 * 60 * 60
FETCH_TIMEOUT = 5
MAX_MOVERS = 10

_fallback_cache = LocMemCache('stockvault-market-data', {})
_summary_fields = (
    ('total turnover', 'Total turnover', 'currency'),
    ('total traded shares', 'Shares traded', 'count'),
    ('total transactions', 'Transactions', 'count'),
    ('total scrips traded', 'Scrips traded', 'count'),
    ('total market capitalization', 'Market capitalization', 'currency'),
    ('total float market capitalization', 'Float market capitalization', 'currency'),
)


def _number(value):
    try:
        number = Decimal(str(value).strip().replace(',', ''))
    except InvalidOperation:
        return None
    if number.is_finite() and number.adjusted() <= 18:
        return number
    return None


def _index(payload):
    if not isinstance(payload, list):
        return None
    for row in payload:
        if not isinstance(row, dict):
            continue
        name = str(row.get('index', '')).strip().casefold()
        if name not in ('nepse', 'nepse index') and str(row.get('id')) != '58':
            continue
        value = _number(row.get('currentValue'))
        if value is None or value <= 0:
            continue
        try:
            market_date = date.fromisoformat(str(row.get('businessDate') or row.get('generatedTime'))[:10])
        except ValueError:
            market_date = None
        return {
            'value': value, 'change': _number(row.get('change')),
            'percent': _number(row.get('perChange')), 'date': market_date,
        }
    return None


def _summary(payload):
    if not isinstance(payload, list):
        return None
    details = {
        str(row.get('detail', '')).casefold().strip(' :').removesuffix(' rs').rstrip(): row.get('value')
        for row in payload if isinstance(row, dict)
    }
    metrics = []
    for field, label, kind in _summary_fields:
        value = _number(details.get(field))
        if value is None or value < 0:
            continue
        if kind == 'count':
            if value != value.to_integral_value():
                continue
            value = int(value)
        metrics.append({'label': label, 'value': value, 'kind': kind})
    return metrics or None


def _movers(payload):
    if not isinstance(payload, list):
        return None
    rows = []
    for row in payload:
        if not isinstance(row, dict):
            continue
        symbol = row.get('symbol')
        price = _number(row.get('ltp'))
        percent = _number(row.get('percentageChange'))
        if not isinstance(symbol, str) or not symbol.strip() or percent is None or price is None or price < 0:
            continue
        rows.append({
            'symbol': symbol.strip(), 'name': row.get('securityName') or '', 'price': price,
            'change': _number(row.get('pointChange')), 'percent': percent,
        })
        if len(rows) == MAX_MOVERS:
            break
    return rows if rows or not payload else None


async def _fetch_market_data():
    # A fresh async client isolates the package's token state to this refresh.
    client = AsyncNepse()
    calls = {
        'index': client.getNepseIndex, 'summary': client.getSummary,
        'gainers': client.getTopGainers, 'losers': client.getTopLosers,
    }
    data = {}

    async def fetch(name, request):
        try:
            data[name] = await request()
        except Exception as error:
            logger.warning('NEPSE %s feed unavailable (%s)', name, type(error).__name__)

    async with client.client:
        try:
            # The module retries transport errors recursively. Limit the entire
            # refresh while keeping sections that already completed.
            async with asyncio.timeout(FETCH_TIMEOUT):
                await asyncio.gather(*(fetch(name, request) for name, request in calls.items()))
        except TimeoutError:
            logger.warning('NEPSE market refresh exceeded its deadline')
    return data


def _fetch_sections():
    return async_to_sync(_fetch_market_data)()


def _cache_get(key):
    try:
        return cache.get(key)
    except Exception:
        return _fallback_cache.get(key)


def _cache_set(key, value, timeout):
    _fallback_cache.set(key, value, timeout)
    try:
        cache.set(key, value, timeout)
    except Exception:
        pass  # The workspace still works when its shared cache is unavailable.


def _market_snapshot():
    snapshot = _cache_get(CACHE_KEY)
    if snapshot is not None:
        return snapshot

    try:
        raw = _fetch_sections()
    except Exception as error:
        logger.warning('NEPSE market feed unavailable (%s)', type(error).__name__)
        raw = {}

    now = timezone.now()
    last_good = _cache_get(LAST_GOOD_KEY) or {}
    recent = {}
    snapshot = {}
    stale = False
    failed = False
    for name, normalize in (('index', _index), ('summary', _summary), ('gainers', _movers), ('losers', _movers)):
        value = normalize(raw.get(name))
        if value is not None:
            recent[name] = (value, now)
        else:
            failed = True
            saved = last_good.get(name)
            if saved and now - saved[1] <= timedelta(seconds=STALE_TTL):
                value = saved[0]
                recent[name] = saved
                stale = True
        snapshot[name] = value

    snapshot['stale'] = stale
    snapshot['fetched_at'] = max((fetched_at for _, fetched_at in recent.values()), default=None)
    snapshot['unavailable'] = not recent
    if recent:
        _cache_set(LAST_GOOD_KEY, recent, STALE_TTL)
    _cache_set(CACHE_KEY, snapshot, FAILURE_TTL if failed else CACHE_TTL)
    return snapshot


@login_required(login_url='login')
@require_safe
def MarketDataPage(request):
    snapshot = _market_snapshot()
    return render(request, 'users/market_data.html', {
        'page_title': 'Market Data | StockVault',
        **snapshot,
        'mover_sections': (
            {'id': 'gainers', 'title': 'Top Gainers', 'rows': snapshot['gainers']},
            {'id': 'losers', 'title': 'Top Losers', 'rows': snapshot['losers']},
        ),
    })
