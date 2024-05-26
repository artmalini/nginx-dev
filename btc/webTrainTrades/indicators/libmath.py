import numpy as np
import helpers as h
import pandas as pd
import sys

def np_shift(array: np.ndarray, offset: int = 1, fill_value=np.nan):
    result = np.empty_like(array)
    if offset > 0:
        result[:offset] = fill_value
        result[offset:] = array[:-offset]
    elif offset < 0:
        result[offset:] = fill_value
        result[:offset] = array[-offset:]
    else:
        result[:] = array
    return result

def linreg(source: np.ndarray, length: int, offset: int = 0):
    try:
        size = len(source)
        linear = np.zeros(size)

        for i in range(length, size):

            sumX = 0.0
            sumY = 0.0
            sumXSqr = 0.0
            sumXY = 0.0

            for z in range(length):
                val = source[i-z]
                per = z + 1.0
                sumX += per
                sumY += val
                sumXSqr += per * per
                sumXY += val * per

            slope = (length * sumXY - sumX * sumY) / (length * sumXSqr - sumX * sumX)
            average = sumY / length
            intercept = average - slope * sumX / length + slope

            linear[i] = intercept

        if offset != 0:
            linear = np_shift(linear, offset)

        return linear
    except Exception as e:
        h.logger.warning(f"libmath linreg {e}")

# 
# That function returns that highest value for a certain number of bars back
# def highest(data, length=None):
#     if length is None:
#         return data.max()
#     else:
#         return data.rolling(window=length, min_periods=1).max()

# def l_highest(df, source, length):
#     max_val = -1
#     try:
#         if not df.empty and length:
#             max_length = length * -1
#             for i in range(1, length):
#                 if not pd.isnull(df[source].iloc[max_length]) and max_val < df[source].iloc[max_length]:
#                     max_val = df[source].iloc[max_length]
#                 max_length += 1
#             h.logger.warning(f'libmath l_highest max_val {max_val}')
#             return max_val
#     except Exception as e:
#         h.logger.warning(f'libmath l_highest {e}')
#         return 0
    
# def l_lowest(df, source, length):
#     min_val = 99999999
#     try:
#         if not df.empty and length:
#             max_length = length * -1
#             for i in range(1, length):
#                 if not pd.isnull(df[source].iloc[max_length]) and min_val > df[source].iloc[max_length]:
#                     min_val = df[source].iloc[max_length]
#                 max_length += 1
#             return min_val
#     except Exception as e:
#         h.logger.warning(f'libmath l_lowest {e}')
#         return 0


# def l_highest(source, length):
#     max_val = -1
#     try:
#         if not source.empty and length:
#             max_length = length * -1
#             for i in range(1, length):
#                 if not pd.isnull(source.iloc[max_length]) and max_val < source.iloc[max_length]:
#                     h.logger.warning(f'source.iloc {source.iloc}')
#                     max_val = source.iloc[max_length]
#                 max_length += 1
#             h.logger.warning(f'libmath l_highest max_val {max_val}')
#             return max_val
#     except Exception as e:
#         h.logger.warning(f'libmath l_highest {e}')
#         return 0

def l_highest(df, source, length):
    sourceMax = []
    try:
        if not df.empty and length:
            for i in range(len(df)):
                max_val = -1
                for j in range(length):
                    try:
                        index = i - length + j + 1
                        if index >= 0:
                            availabledf = df[source].iloc[index]
                        else:
                            # If index is out of range, default to the current cell value
                            availabledf = df[source].iloc[i]
                        if not pd.isnull(availabledf) and max_val < availabledf:
                            max_val = availabledf
                    except IndexError:
                        pass
                sourceMax.append(max_val)
            # h.logger.info(f'libmath l_highest sourceMax {sourceMax} sourceMax length: {len(sourceMax)} df length: {len(df)}')
            return sourceMax
    except Exception as e:
        h.logger.warning(f'libmath l_highest {e}')
        return 0
    
def l_lowest(df, source, length):
    
    sourceMin = []
    try:
        if not df.empty and length:
            for i in range(len(df)):
                min_val = sys.maxsize
                for j in range(length):
                    try:
                        index = i - length + j + 1
                        if index >= 0:
                            availabledf = df[source].iloc[index]
                        else:
                            # If index is out of range, default to the current cell value
                            availabledf = df[source].iloc[i]
                        if not pd.isnull(availabledf) and min_val > availabledf:
                            min_val = availabledf
                    except IndexError:
                        pass
                sourceMin.append(min_val)

            return sourceMin
    except Exception as e:
        h.logger.warning(f'libmath l_lowest {e}')
        return 0
    
def l_ema(df, source, length):
    ema_values = []
    try:
        if not df.empty and length:
            alpha = 2 / (length + 1)

            for i in range(len(df)):
                if i == 0:
                    ema_values.append(df[source].iloc[i])  # First value is same as source
                else:
                    previous_ema = ema_values[-1]
                    current_value = df[source].iloc[i]
                    ema = alpha * current_value + (1 - alpha) * previous_ema
                    ema_values.append(ema)

            return ema_values
    except Exception as e:
        h.logger.warning(f'libmath l_ema {e}')
        return ema_values
    
def l_sma(df, source, length):
    sma_values = []
    try:
        if not df.empty and length:
            for i in range(len(df)):
                sum_val = 0
                for j in range(length):
                    index = i - length + j + 1
                    if index >= 0:  # Ensure index is non-negative
                        value = df[source].iloc[index]
                        if not pd.isnull(value):  # Skip NaN values
                            sum_val += value / length
                sma_values.append(sum_val)

            return sma_values
    except Exception as e:
        h.logger.warning(f'libmath l_sma {e}')
        return sma_values
    
def l_pivothigh(df, superLeft, superRight):
    pivotHigh = []
    try:
        if not df.empty:
            dfLen = len(df)
            for index in range(dfLen):
                pleft = []
                pright = []
                for left in range(superLeft):
                    leftindex = index - left
                    if leftindex >= 0:  # Ensure index is non-negative
                        pleft.append(df["high"].iloc[leftindex])
                for right in range(superRight):
                    rightindex = index + right
                    if rightindex < dfLen:  # Ensure index is within range
                        pright.append(df["high"].iloc[rightindex])

                pivotCurrentCandle = df["high"].iloc[index]
                noLeftBiggerThanCurrent = all(left <= pivotCurrentCandle for left in pleft)
                noRightBiggerThanCurrent = all(right <= pivotCurrentCandle for right in pright)
                
                if noLeftBiggerThanCurrent and noRightBiggerThanCurrent:
                    pivotHigh.append(pivotCurrentCandle)
                else:
                    pivotHigh.append(None)
    except Exception as e:
        h.logger.warning(f'l_pivothigh {e}')
    return pivotHigh


def l_pivotlow(df, superLeft, superRight):
    pivotLow = []
    try:
        if not df.empty:
            dfLen = len(df)
            for index in range(dfLen):
                pleft = []
                pright = []
                for left in range(superLeft):
                    leftindex = index - left
                    if leftindex >= 0:  # Ensure index is non-negative
                        pleft.append(df["low"].iloc[leftindex])
                for right in range(superRight):
                    rightindex = index + right
                    if rightindex < dfLen:  # Ensure index is within range
                        pright.append(df["low"].iloc[rightindex])

                pivotCurrentCandle = df["low"].iloc[index]
                noLeftBiggerThanCurrent = all(left >= pivotCurrentCandle for left in pleft)
                noRightBiggerThanCurrent = all(right >= pivotCurrentCandle for right in pright)
                
                if noLeftBiggerThanCurrent and noRightBiggerThanCurrent:
                    pivotLow.append(pivotCurrentCandle)
                else:
                    pivotLow.append(None)
    except Exception as e:
        h.logger.warning(f'l_pivotlow {e}')
    return pivotLow
    
def l_sum(value, length):
    sum = 0
    try:
        if len(value) and length:
            for i in range(len(value)):
                if not pd.isnull(value[i]) and i < length:
                    sum += value[i]
            # h.logger.info(f'SUM l_sum {sum}')
            return sum
    except Exception as e:
        h.logger.warning(f'libmath l_sum {e}')
        return 0

# pd.isnull(source)
def l_nz(source, replacement):
    # return np.nan_to_num(source, nan=replacement)
    if source == 0 :
        return replacement
    return source