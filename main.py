import os
import time
from datetime import datetime, timezone

import requests

BINANCE_URL = "https://api.binance.com/api/v3/klines"
TELEGRAM_URL = "https://api.telegram.org/bot{}/sendMessage"

SYMBOL = "AVAXUSDT"
INTERVAL = "1h"
EMA_PERIOD = 13


def get_closed_candles(limit=100):
    """Return only completed 1h candles, excluding the currently forming candle."""
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "limit": limit,
    }

    response = requests.get(BINANCE_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    now_ms = int(time.time() * 1000)

    # Binance kline fields:
    # [0] open time, [1] open, [2] high, [3] low, [4] close, [6] close time
    closed = [k for k in data if int(k[6]) < now_ms]
    return closed


def ema(values, period):
    """EMA equivalent to the common adjust=False calculation."""
    if len(values) < period:
        raise ValueError("EMA hesaplamak için yeterli mum yok.")

    multiplier = 2 / (period + 1)

    # Seed with SMA of the first period values.
    current = sum(values[:period]) / period

    for price in values[period:]:
        current = (price - current) * multiplier + current

    # To detect the latest cross we need the EMA of every candle,
    # so calculate the full series separately.
    series = [None] * (period - 1)
    current = sum(values[:period]) / period
    series.append(current)

    for price in values[period:]:
        current = (price - current) * multiplier + current
        series.append(current)

    return series


def crossed_up(candles):
    """
    Signal condition:
      previous closed candle close <= previous EMA13
      latest closed candle close  > latest EMA13
    """
    closes = [float(k[4]) for k in candles]
    ema_values = ema(closes, EMA_PERIOD)

    prev_close = closes[-2]
    last_close = closes[-1]
    prev_ema = ema_values[-2]
    last_ema = ema_values[-1]

    signal = prev_close <= prev_ema and last_close > last_ema

    return signal, {
        "previous_close": prev_close,
        "previous_ema": prev_ema,
        "last_close": last_close,
        "last_ema": last_ema,
        "candle_open_ms": int(candles[-1][0]),
        "candle_close_ms": int(candles[-1][6]),
    }


def send_telegram(message):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID environment variable'ları eksik."
        )

    url = TELEGRAM_URL.format(bot_token)
    payload = {
        "chat_id": chat_id,
        "text": message,
    }

    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()


def main():
    candles = get_closed_candles()

    if len(candles) < EMA_PERIOD + 2:
        raise RuntimeError("Yeterli kapanmış 1 saatlik mum alınamadı.")

    signal, info = crossed_up(candles)

    candle_time = datetime.fromtimestamp(
        info["candle_close_ms"] / 1000, tz=timezone.utc
    ).strftime("%Y-%m-%d %H:%M UTC")

    print(
        f"{SYMBOL} | {candle_time} | "
        f"Close={info['last_close']:.4f} | EMA13={info['last_ema']:.4f} | "
        f"CrossUp={signal}"
    )

    if not signal:
        return

    message = (
        "🚨 AVAXUSDT EMA13 YUKARI KIRILIM\n\n"
        f"Parite: {SYMBOL}\n"
        "Zaman dilimi: 1H\n"
        f"Kapanış: {info['last_close']:.4f}\n"
        f"EMA13: {info['last_ema']:.4f}\n"
        f"Önceki kapanış: {info['previous_close']:.4f}\n"
        f"Önceki EMA13: {info['previous_ema']:.4f}\n"
        f"Mum kapanışı: {candle_time}\n\n"
        "Sinyal: Fiyat EMA13'ü aşağıdan yukarı kesti."
    )

    send_telegram(message)
    print("Telegram sinyali gönderildi.")


if __name__ == "__main__":
    main()
