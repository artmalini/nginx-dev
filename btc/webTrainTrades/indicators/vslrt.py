import pandas as pd
import numpy as np
from indicators.libmath import linreg
import helpers as h

# Calculate Buy/Sell Volume
def _rate(df, cond):
    try:
        # Get the size of top/bottom/body of the candle
        tw = df['high'] - np.maximum(df['open'], df['close'])
        bw = np.minimum(df['open'], df['close']) - df['low']
        body = np.abs(df['close'] - df['open'])

        ret = 0.5 * (tw + bw + (cond * 2 * body)) / (tw + bw + body)
        ret = np.where(np.isnan(ret), 0.5, ret)
        return ret
    except Exception as e:
        h.logger.warning(f"_rate {e}")

# Calculate Regression Slope for Buy/Sell Volumes
def _get_trend(df, len):
    try:
        deltaup = df['volume'] * _rate(df, df['open'] <= df['close'])
        deltadown = df['volume'] * _rate(df, df['open'] > df['close'])

        slope_volume_up = linreg(deltaup, len, 0) - linreg(deltaup, len, 1)
        slope_volume_down = linreg(deltadown, len, 0) - linreg(deltadown, len, 1)
        return slope_volume_up, slope_volume_down
    except Exception as e:
        h.logger.warning(f"_get_trend {e}")

def vslrt(df, vslrtSrc, vslrtLen1, vslrtLen2):
    try:
        # Get short/long-term regression slope
        slope_price = linreg(vslrtSrc, vslrtLen1, 0) - linreg(vslrtSrc, vslrtLen1, 1)
        slope_price_lt = linreg(vslrtSrc, vslrtLen2, 0) - linreg(vslrtSrc, vslrtLen2, 1)

        # Get buy/sell volume regression slopes for short term period
        slope_volume_up, slope_volume_down = _get_trend(df, vslrtLen1)
        # Get buy/sell volume regression slopes for long term period
        slope_volume_up_lt, slope_volume_down_lt = _get_trend(df, vslrtLen2)

        h.logger.info(f"slope_volume_up_lt {slope_volume_up_lt}")
        long_signal = (slope_price > 0) & (slope_volume_up > 0) & (slope_volume_up > slope_volume_down) & (slope_price_lt > 0) & (slope_volume_up_lt > 0) & (slope_volume_up_lt > slope_volume_down_lt)
        short_signal = (slope_price < 0) & (slope_volume_down > 0) & (slope_volume_up < slope_volume_down) & (slope_price_lt < 0) & (slope_volume_down_lt > 0) & (slope_volume_up_lt < slope_volume_down_lt)
        
        return long_signal, short_signal
    except Exception as e:
        h.logger.warning(f"vslrt {e}")