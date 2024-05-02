import pandas as pd
import numpy as np
import math
import ta_py as ta
from indicators.libmath import linreg, l_highest, l_sum, l_lowest, l_nz
import helpers as h

hlootSrc = [0.0] * 5
hlootSrclowest = [0.0] * 5
varFunc = [0.0] * 2
longStop = [0.0] * 2
shortStop = [0.0] * 2
dir = [1] * 2
longStopl = [0.0] * 2
shortStopl = [0.0] * 2
varFuncl = [0.0] * 2
dirl = [1] * 2
hoot = [0.0] * 3
loot = [0.0] * 3

def Var_Func(df, length):
    try:
        global hlootSrc
        global varFunc
        hlootSrcPrevious = hlootSrc[1]
        
        valpha = 2 / (length + 1)
        
        vud1 = np.where(hlootSrc[0] > hlootSrcPrevious, hlootSrc[0] - hlootSrcPrevious, 0)
        vdd1 = np.where(hlootSrc[0] < hlootSrcPrevious, hlootSrcPrevious - hlootSrc[0], 0)
        
        vUD = l_sum(df, 'open', vud1, 9)
        vDD = l_sum(df, 'open', vdd1, 9)
        
        vCMO = (vUD - vDD) / (vUD + vDD) if (vUD + vDD) != 0 else 0
        
        varFunc = [(valpha * abs(vCMO) * hlootSrc[0]) + (1 - valpha * abs(vCMO)) * varFunc[1]] + varFunc[:-1] 
        # Shift values in varFunc list to make space for the new VAR value       
        h.logger.info(f"Var_Func {varFunc[0]}")
        return varFunc[0]
    except Exception as e:
        h.logger.warning(f"Var_Func {e}")

def Var_Funcl(df, length):
    try:
        global hlootSrclowest
        global varFuncl
        hlootSrclowestPrevious = hlootSrclowest[1]

        valphal = 2 / (length + 1)

        vud1l = np.where(hlootSrclowest[0] > hlootSrclowestPrevious, hlootSrclowest[0] - hlootSrclowestPrevious, 0)
        vdd1l = np.where(hlootSrclowest[0] < hlootSrclowestPrevious, hlootSrclowestPrevious - hlootSrclowest[0], 0)
        vUDl = l_sum(df, 'open', vud1l, 9)
        vDDl = l_sum(df, 'open', vdd1l, 9)

        vCMOl = (vUDl - vDDl) / (vUDl + vDDl) if (vUDl + vDDl) != 0 else 0

        varFuncl = [(valphal * abs(vCMOl) * hlootSrclowest[0]) + (1 - valphal * abs(vCMOl)) * varFuncl[1]] + varFuncl[:-1]

        h.logger.info(f"Var_Funcl result {varFuncl[0]}")
        return varFuncl[0]
    except Exception as e:
        h.logger.warning(f"Var_Funcl {e}")

# def Var_Func_old(df, length, hllength, recursioncount):
#     delShift = 0
#     if recursioncount == 0:
#         return 0.0
    
#     valpha = 2 / (length + 1)
    
#     hlootSrc = l_highest(df, 'high', hllength + recursioncount)
#     hlootSrcPrevious = l_highest(df, 'high', hllength + recursioncount + 1)
    
#     vud1 = np.where(hlootSrc > hlootSrcPrevious, hlootSrc - hlootSrcPrevious, 0)
#     vdd1 = np.where(hlootSrc < hlootSrcPrevious, hlootSrcPrevious - hlootSrc, 0)
    
#     vUD = l_sum(df, 'open', vud1, 9)
#     vDD = l_sum(df, 'open', vdd1, 9)
    
#     vCMO = (vUD - vDD) / (vUD + vDD) if (vUD + vDD) != 0 else 0
    
#     previous_VAR = Var_Func(df, length, hllength, recursioncount - 1)
#     VAR = (valpha * abs(vCMO) * hlootSrc) + (1 - valpha * abs(vCMO)) * previous_VAR
#     h.logger.info(f"Recursion Var_Func {VAR}")
#     return VAR

def Wwma_Func(hlootSrc, length):
    wwalpha = 1 / length
    WWMA = np.zeros_like(hlootSrc)
    for i in range(len(hlootSrc)):
        WWMA[i] = wwalpha * hlootSrc[i] + (1 - wwalpha) * (WWMA[i-1] if i > 0 else 0)
    return WWMA

def Zlema_Func(hlootSrc, length):
    zxLag = length // 2 if length % 2 == 0 else (length - 1) // 2
    zxEMAData = hlootSrc + hlootSrc - hlootSrc.shift(zxLag)
    ZLEMA = zxEMAData.ewm(span=length, adjust=False).mean()
    return ZLEMA

def Tsf_Func(hlootSrc, length):
    lrc = hlootSrc.rolling(window=length, min_periods=0).apply(lambda x: np.polyfit(range(length), x, 1)[0], raw=True)
    lrc1 = hlootSrc.shift(length).rolling(window=length, min_periods=0).apply(lambda x: np.polyfit(range(length), x, 1)[0], raw=True)
    lrs = lrc - lrc1
    TSF = lrc + lrs
    return TSF

# def Var_Funcl(hlootSrcl, length):
#     valphal = 2 / (length + 1)
#     vud1l = np.where(hlootSrcl > hlootSrcl.shift(1), hlootSrcl - hlootSrcl.shift(1), 0)
#     vdd1l = np.where(hlootSrcl < hlootSrcl.shift(1), hlootSrcl.shift(1) - hlootSrcl, 0)
#     vUDl = np.sum(vud1l, 9)
#     vDDl = np.sum(vdd1l, 9)
#     vCMOl = np.nan_to_num((vUDl - vDDl) / (vUDl + vDDl))
#     VARl = np.zeros_like(hlootSrcl)
#     for i in range(len(hlootSrcl)):
#         VARl[i] = valphal * abs(vCMOl[i]) * hlootSrcl[i] + (1 - valphal * abs(vCMOl[i])) * (VARl[i-1] if i > 0 else 0)
#     return VARl

def Wwma_Funcl(hlootSrcl, length):
    wwalphal = 1 / length
    WWMAl = np.zeros_like(hlootSrcl)
    for i in range(len(hlootSrcl)):
        WWMAl[i] = wwalphal * hlootSrcl[i] + (1 - wwalphal) * (WWMAl[i-1] if i > 0 else 0)
    return WWMAl

def Zlema_Funcl(hlootSrcl, length):
    zxLagl = length // 2 if length % 2 == 0 else (length - 1) // 2
    zxEMADatal = hlootSrcl + hlootSrcl - hlootSrcl.shift(zxLagl)
    ZLEMAl = zxEMADatal.ewm(span=length, adjust=False).mean()
    return ZLEMAl

def Tsf_Funcl(hlootSrcl, length):
    lrcl = hlootSrcl.rolling(window=length, min_periods=0).apply(lambda x: np.polyfit(range(length), x, 1)[0], raw=True)
    lrc1l = hlootSrcl.shift(length).rolling(window=length, min_periods=0).apply(lambda x: np.polyfit(range(length), x, 1)[0], raw=True)
    lrsl = lrcl - lrc1l
    TSFl = lrcl + lrsl
    return TSFl

def getMA(df, hlootSrc, hlootSrcPrevious, hlootSrclowest, hlootSrclowestPrevious, length, hllength, mav):
    if mav == 'SMA':
        return hlootSrc.rolling(window=length, min_periods=0).mean()
    elif mav == 'EMA':
        return hlootSrc.ewm(span=length, adjust=False).mean()
    elif mav == 'WMA':
        weights = np.arange(1, length+1)
        return hlootSrc.rolling(window=length, min_periods=0).apply(lambda x: np.dot(x, weights)/weights.sum(), raw=True)
    elif mav == 'DEMA':
        return 2 * hlootSrc.ewm(span=length, adjust=False).mean() - hlootSrc.ewm(span=length, adjust=False).mean().ewm(span=length, adjust=False).mean()
    elif mav == 'TMA':
        sma1 = hlootSrc.rolling(window=math.ceil(length / 2), min_periods=0).mean()
        return sma1.rolling(window=math.floor(length / 2) + 1, min_periods=0).mean()
    elif mav == 'VAR':
        return Var_Func(df, length)
    elif mav == 'WWMA':
        return Wwma_Func(hlootSrc, length)
    elif mav == 'ZLEMA':
        return Zlema_Func(hlootSrc, length)
    elif mav == 'TSF':
        return Tsf_Func(hlootSrc, length)
    elif mav == 'HULL':
        return 2 * hlootSrc.ewm(span=length, adjust=False).mean() - hlootSrc.ewm(span=math.isqrt(length), adjust=False).mean()

def getMAl(df, hlootSrclowest, length, hllength , mav):
    if mav == 'SMA':
        return hlootSrclowest.rolling(window=length, min_periods=0).mean()
    elif mav == 'EMA':
        return hlootSrclowest.ewm(span=length, adjust=False).mean()
    elif mav == 'WMA':
        weights = np.arange(1, length+1)
        return hlootSrclowest.rolling(window=length, min_periods=0).apply(lambda x: np.dot(x, weights)/weights.sum(), raw=True)
    elif mav == 'DEMA':
        return 2 * hlootSrclowest.ewm(span=length, adjust=False).mean() - hlootSrclowest.ewm(span=length, adjust=False).mean().ewm(span=length, adjust=False).mean()
    elif mav == 'TMA':
        sma1 = hlootSrclowest.rolling(window=math.ceil(length / 2), min_periods=0).mean()
        return sma1.rolling(window=math.floor(length / 2) + 1, min_periods=0).mean()
    elif mav == 'VAR':
        return Var_Funcl(df, length)
    elif mav == 'WWMA':
        return Wwma_Funcl(hlootSrclowest, length)
    elif mav == 'ZLEMA':
        return Zlema_Funcl(hlootSrclowest, length)
    elif mav == 'TSF':
        return Tsf_Funcl(hlootSrclowest, length)
    elif mav == 'HULL':
        return 2 * hlootSrclowest.ewm(span=length, adjust=False).mean() - hlootSrclowest.ewm(span=math.isqrt(length), adjust=False).mean()


def hloot(df, source, length, percent, hllength, hlootMav, useReverseOrderHLOOT):
    # try:
    global hlootSrc
    global hlootSrclowest
    global longStop
    global shortStop
    global dir
    global longStopl
    global shortStopl
    global dirl
    global hoot
    global loot

    # hlootSrc[0] = l_highest(df['high'], hllength)
    # hlootSrclowest[0] = l_lowest(df['low'], hllength)
    # for col in df:

    hlootSrc = [l_highest(df['high'], hllength)] + hlootSrc[:-1]
    hlootSrcPrevious = hlootSrc[1]
    hlootSrclowest = [l_lowest(df['low'], hllength)] + hlootSrclowest[:-1]
    hlootSrclowestPrevious = hlootSrclowest[1]
    # hlootSrc = ta.recent_high(df['high'], hllength)
    # h.logger.info(f"hlootSrc  {hlootSrc}")

    # hlootSrcPrevious = l_highest(df, 'high', hllength + 1)
    # h.logger.info(f"hlootSrcPrevious {hlootSrcPrevious}")

    # hlootSrclowest = l_lowest(df, 'low', hllength)
    # hlootSrclowestPrevious = l_lowest(df, 'low', hllength + 1)
    # h.logger.info(f"hlootSrclowest {hlootSrclowest}")

    
    MAvg = getMA(df, hlootSrc, hlootSrcPrevious, hlootSrclowest, hlootSrclowestPrevious, length, hllength, hlootMav)
    # return 0, 0, 0

    fark = MAvg * percent * 0.01
    longStop = [MAvg - fark] + longStop[:-1]
    longStopPrev = l_nz(longStop[1], longStop[0])
    longStopExec = np.where(MAvg > longStopPrev, np.maximum(longStop[0], longStopPrev), longStop[0])
    shortStop = [MAvg + fark] + shortStop[:-1]
    shortStopPrev = l_nz(shortStop[1], shortStop[0])
    shortStopExec = np.where(MAvg < shortStopPrev, np.minimum(shortStop[0], shortStopPrev), shortStop[0])

    h.logger.info(f"hlootSrc  longStop {longStop} shortStop {shortStop}")
    
    dir[0] = 1
    dir[0] = l_nz(dir[1], dir[0])

    dir[0] = dir[0] if dir[0] != None else 1
    if dir[0] == -1 and MAvg > shortStopPrev:
        dir[0] = 1
    elif dir[0] == 1 and MAvg < longStopPrev:
        dir[0] = -1
    dir = [dir[0]] + dir[:-1]    
    MT = longStopExec if dir[0] == 1 else shortStopExec
    # hoot = [np.where(MAvg > MT, MT * (200 + percent) / 200, MT * (200 - percent) / 200)] + hoot[:-1]
    hoot.insert(0,np.where(MAvg > MT, MT * (200 + percent) / 200, MT * (200 - percent) / 200))
    HOTTC = 'blue'
    h.logger.info(f"HOOT {hoot}")
    # return 0, 0, 0
    
    MAvgl = getMAl(df,hlootSrclowest, length, hllength, hlootMav)
    farkl = MAvgl * percent * 0.01
    longStopl = [MAvgl - farkl] + longStopl[:-1]
    longStopPrevl = l_nz(longStopl[1], longStopl[0])
    longStoplExec = np.where(MAvgl > longStopPrevl, np.maximum(longStopl[0], longStopPrevl), longStopl[0])
    shortStopl = [MAvgl + farkl] + shortStop[:-1]
    shortStopPrevl = l_nz(shortStopl[1], longStopl[0])
    shortStoplExec = np.where(MAvgl < shortStopPrevl, np.minimum(shortStopl[0], shortStopPrevl), shortStopl[0])
    dirl[0] = 1
    dirl[0] = l_nz(dirl[1], dirl[0])

    dirl[0] = dirl[0] if dirl[0] != None else 1
    if dirl[0] == -1 and MAvgl > shortStopPrevl:
        dirl[0] = 1
    elif dirl[0] == 1 and MAvgl < longStopPrevl:
        dirl[0] = -1
    dirl = [dirl[0]] + dirl[:-1] 
    MTl = longStoplExec if dirl[0] == 1 else shortStoplExec
    # loot = [np.where(MAvgl > MTl, MTl * (200 + percent) / 200, MTl * (200 - percent) / 200)] + loot[:-1]
    loot.insert(0,np.where(MAvgl > MTl, MTl * (200 + percent) / 200, MTl * (200 - percent) / 200))
    LOTTC = 'red'
    h.logger.info(f"LOOT {loot}")
    h.logger.info(f"long exmpl {hoot} ")

    long_signal = (source > hoot[2])
    short_signal = (source < loot[2])
    reversedHOOTentry = (source < hoot[2]) & (source > loot[2])

    return long_signal, short_signal, reversedHOOTentry
    # except Exception as e:
    #     h.logger.warning(f"hloot ISSUE {e}")