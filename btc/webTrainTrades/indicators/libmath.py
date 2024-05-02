import numpy as np
import helpers as h
import pandas as pd

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


def l_highest(source, length):
    max_val = -1
    try:
        if not source.empty and length:
            max_length = length * -1
            for i in range(1, length):
                if not pd.isnull(source.iloc[max_length]) and max_val < source.iloc[max_length]:
                    h.logger.warning(f'source.iloc {source.iloc}')
                    max_val = source.iloc[max_length]
                max_length += 1
            h.logger.warning(f'libmath l_highest max_val {max_val}')
            return max_val
    except Exception as e:
        h.logger.warning(f'libmath l_highest {e}')
        return 0
    
def l_lowest(source, length):
    min_val = 99999999
    try:
        if not source.empty and length:
            max_length = length * -1
            for i in range(1, length):
                if not pd.isnull(source.iloc[max_length]) and min_val > source.iloc[max_length]:
                    min_val = source.iloc[max_length]
                max_length += 1
            return min_val
    except Exception as e:
        h.logger.warning(f'libmath l_lowest {e}')
        return 0
    
def l_sum(df, source, value, length):
    sum = value
    try:
        if not df.empty and length:
            max_length = length * -1
            for i in range(1, length):
                if not pd.isnull(df[source].iloc[max_length]):
                    # print(sum, value)
                    sum += value
            return sum
    except Exception as e:
        h.logger.warning(f'libmath l_sum {e}')
        return value

def l_nz(source, replacement):
    if pd.isnull(source) :
        return replacement
    return source