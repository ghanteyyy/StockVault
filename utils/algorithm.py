import numpy as np
import pandas as pd
from prophet import Prophet


# ---------------------------
# Helpers
# ---------------------------
def _to_frame(stock_data):
    """
    stock_data: list[tuple(date_str|datetime, float)] -> DataFrame with columns ['ds','y']
    """

    df = pd.DataFrame(stock_data, columns=["ds", "y"]).copy()
    df["ds"] = pd.to_datetime(df["ds"])
    df = df.sort_values("ds").reset_index(drop=True)

    return df


def _future_dates(last_date: pd.Timestamp, days: int) -> pd.DatetimeIndex:
    """
    Generate next `days` calendar days after last_date (inclusive only for +1)
    """

    return pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days, freq="D")  # Calendar daily frequency


def _format_output(dates: pd.DatetimeIndex, yhat: np.ndarray, sigma: float | None):
    """
    Return list of {date, yhat, yhat_lower, yhat_upper} with 95% band using sigma if provided.
    """

    if sigma is None or not np.isfinite(sigma):  # fall back to a small uncertainty if sigma is missing
        sigma = 0.0

    out = []
    z = 1.96  # ~95%

    for d, y in zip(dates, yhat):
        lower = float(y - z * sigma)
        upper = float(y + z * sigma)

        out.append({
            "date": pd.to_datetime(d).strftime("%Y-%m-%d"),
            "yhat": round(float(y), 2),
            "yhat_lower": round(lower, 2),
            "yhat_upper": round(upper, 2),
        })

    return out


# ------------
# 0) Prophet
# ------------
def _predict_prophet(stock_data, days):
    df = _to_frame(stock_data)

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)

    out = []
    tail = forecast.tail(days)[["ds", "yhat", "yhat_lower", "yhat_upper"]]

    for _, row in tail.iterrows():
        out.append({
            "date": row["ds"].strftime("%Y-%m-%d"),
            "yhat": round(float(row["yhat"]), 2),
            "yhat_lower": round(float(row["yhat_lower"]), 2),
            "yhat_upper": round(float(row["yhat_upper"]), 2),
        })

    return out


# --------------- ---------------------------
# 1) Simple Moving Average (SMA) – recursive
# --------------- ---------------------------
def predict_sma(stock_data, days, window: int = 7):
    """
    Recursive SMA forecast: next value = mean of the last `window` values,
    using both historical and already-forecast values when rolling forward.
    Uncertainty ~ recent residual std.
    """

    df = _to_frame(stock_data)
    y = df["y"].astype(float).to_list()

    if len(y) < max(2, window):
        window = max(2, min(window, len(y)))

    hist_preds = []  # Compute residual sigma from a one-step-ahead SMA on the historical window

    for i in range(window, len(y)):
        hist_preds.append(np.mean(y[i-window:i]))

    if len(hist_preds) > 1:
        hist_actuals = np.array(y[window:])
        sigma = float(np.std(hist_actuals - np.array(hist_preds), ddof=1))

    else:
        sigma = float(np.std(y, ddof=1)) if len(y) > 1 else 0.0

    # Recursive forecast
    preds = []
    rolling = y.copy()

    for _ in range(days):
        start = max(0, len(rolling) - window)
        preds.append(float(np.mean(rolling[start:])))
        rolling.append(preds[-1])

    dates = _future_dates(df["ds"].iloc[-1], days)

    return _format_output(dates, np.array(preds), sigma)


# ------------------------------------
# 2) Exponential Moving Average (EMA)
# ------------------------------------
def predict_ema(stock_data, days, alpha: float = 0.2):
    """
    EMA smoothing; forecast is the final EMA value extended flat.
    Uncertainty from residual std of y - EMA(y).
    """

    df = _to_frame(stock_data)
    y = df["y"].astype(float)

    alpha = float(np.clip(alpha, 0.01, 0.99))
    ema = y.ewm(alpha=alpha, adjust=False).mean()

    residuals = y - ema
    sigma = float(np.std(residuals.iloc[1:], ddof=1)) if len(residuals) > 2 else 0.0

    last_ema = float(ema.iloc[-1])
    preds = np.full(shape=(days,), fill_value=last_ema, dtype=float)

    dates = _future_dates(df["ds"].iloc[-1], days)

    return _format_output(dates, preds, sigma)


# ------------------------------------
# 3) Linear Trend (OLS on time index)
# ------------------------------------
def predict_linear(stock_data, days):
    """
    Fit y = a + b * t on daily index and project forward.
    Uncertainty from residual std.
    """

    df = _to_frame(stock_data)
    y = df["y"].astype(float).values

    t = np.arange(len(y), dtype=float)  # t = 0..n-1

    if len(y) < 2:  # Not enough data for slope; fall back to flat
        a = float(y[-1]) if len(y) else 0.0
        b = 0.0

        sigma = 0.0

    else:
        b, a = np.polyfit(t, y, 1)  # returns slope, intercept
        y_fit = a + b * t

        sigma = float(np.std(y - y_fit, ddof=1)) if len(y) > 2 else 0.0

    # Forecast horizon t = n .. n+days-1
    t_future = np.arange(len(y), len(y) + days, dtype=float)
    preds = a + b * t_future

    dates = _future_dates(df["ds"].iloc[-1], days)

    return _format_output(dates, preds, sigma)


# --------------------------------------
# Public API (kept backward-compatible)
# --------------------------------------
def predict(stock_data, days, method: str = "prophet", **kwargs):
    """
    Backward-compatible entry point used by your view.
      - method='prophet' (default, original behavior)
      - method='sma'     (Simple Moving Average, recursive)
      - method='ema'     (Exponential Moving Average)
      - method='linear'  (Linear trend via OLS)
    kwargs are passed to the underlying method (e.g., window=14 for SMA).
    """

    m = (method or "prophet").lower()

    if m == "prophet":
        return _predict_prophet(stock_data, days)

    elif m == "sma":
        return predict_sma(stock_data, days, **kwargs)

    elif m == "ema":
        return predict_ema(stock_data, days, **kwargs)

    elif m == "linear":
        return predict_linear(stock_data, days)

    else:
        raise ValueError(f"Unknown method '{method}'. Use 'prophet', 'sma', 'ema', or 'linear'.")
