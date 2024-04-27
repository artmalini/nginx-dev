import numpy as np

def dmi(data, adxlen_adi, dilen_adi, keyLevel_adi):
    up = data['high'].diff()
    down = -data['low'].diff()
    truerange = up.where(up > down, down).rolling(dilen_adi).mean()
    plus = 100 * (up.where((up > down) & (up > 0), 0).rolling(dilen_adi).mean() / truerange)
    minus = 100 * (down.where((down > up) & (down > 0), 0).rolling(dilen_adi).mean() / truerange)
    sum_dm = plus + minus
    adx = 100 * (np.abs(plus - minus) / np.where(sum_dm == 0, 1, sum_dm)).rolling(adxlen_adi).mean()
    
    # Determine long and short signals
    long_signal = ((adx.shift(1) < keyLevel_adi) & (adx > keyLevel_adi) & (plus > minus))
    short_signal = ((adx.shift(1) < keyLevel_adi) & (adx > keyLevel_adi) & (plus < minus))
    
    # Refine signals to avoid consecutive signals in the same direction
    long_entry = (long_signal & ~(long_signal.shift(1).fillna(False)))
    short_entry = (short_signal & ~(short_signal.shift(1).fillna(False)))
    
    return long_entry, short_entry

def directionalMovement(df):    
    # Parameters for DMI
    adxlen_adi = 14
    dilen_adi = 14
    keyLevel_adi = 25

    # Calculate long and short entry points
    long_entry, short_entry = dmi(df, adxlen_adi, dilen_adi, keyLevel_adi)
    return long_entry, short_entry