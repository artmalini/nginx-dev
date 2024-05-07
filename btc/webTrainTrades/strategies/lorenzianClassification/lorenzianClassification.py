from indicators.vslrt import vslrt
from indicators.hloot import hloot
from indicators.ema import ema
from indicators.sma import sma
import plotly.graph_objects as go
import pandas as pd
import helpers as h

def lC(df):
    # Inputs
    dateRange = False
    source = df['open']
    neighborsCount = 8
    maxBarsBack = 2000
    featureCount = 5
    colorCompression = 1

    # ==== VSLRT ====
    useVSLRT = False
    vslrtLen1 = 20
    vslrtLen2 = 50

    # ==== HLOOT ====
    useHLOOT = True
    hlooSource = "open"
    hlootLength = 2
    hlootPercent = 0.7
    hlootHllength = 53
    hoot = [0.0] * 2
    loot = [0.0] * 2
    hlootMav = 'VAR'
    useReverseOrderHLOOT = False

    #  ==== Moving Average ====
    useEma = False
    emaSource = "open"
    emalen = 8
    ema_coord = [0.0] * 2
    # ----
    useSma = True
    smaSource = "open"
    smalen = 200
    smaout_coord = [0.0] * 2

    # Supertrend
    useSUPERTREND = False  


    useReverseOrder = False

    if useVSLRT:
        vslrt_long_entry, vslrt_short_entry = vslrt(df, source, vslrtLen1, vslrtLen2)
    if useHLOOT:
        hloot_long_entry, hloot_short_entry, hoot, loot = hloot(df, hlooSource, hlootLength, hlootPercent, hlootHllength, hlootMav, useReverseOrderHLOOT)
    if useEma:
        ema_long_entry, ema_short_entry, emaout = ema(df, emaSource, emalen)
    if useSma:
        sma_long_entry, sma_short_entry, smaout = sma(df, smaSource, smalen)

    # h.logger.info(f"emaout {ema_long_entry} lenema {len(ema_long_entry)} short {len(ema_long_entry)} lendef {len(df)}")
    # return
    dfPlaceholrers = [] # pd.DataFrame(index=df.index, columns=['close_datetime'], data=True)
    if not df.empty:
        for index in range(len(df)):
            dfPlaceholrers.append(True)

    # result = [all(values) for values in zip(list1, list2, list3)]


    # h.logger.info(f"vslrt_long_entry {vslrt_long_entry}")
    # h.logger.info(f"dfPlaceholrers {dfPlaceholrers}")
    try:
        isVSLRTlong = dfPlaceholrers
        isVSLRTshort = dfPlaceholrers
        if useVSLRT:
            isVSLRTlong = vslrt_long_entry
            isVSLRTshort = vslrt_short_entry
        isHLOOTlong = dfPlaceholrers
        isHLOOTshort = dfPlaceholrers
        if useHLOOT:
            isHLOOTlong = hloot_long_entry
            isHLOOTshort = hloot_short_entry
        isUseEMAlong = dfPlaceholrers
        isUseEMAshort = dfPlaceholrers
        if useEma:
            isUseEMAlong = ema_long_entry
            ema_coord = emaout
            isUseEMAshort = ema_short_entry
        isUseSMAlong = dfPlaceholrers
        isUseSMAshort = dfPlaceholrers
        if useSma:
            isUseSMAlong = sma_long_entry
            smaout_coord = smaout
            isUseSMAshort = sma_short_entry
        # h.logger.info(f"isVSLRTlong LC {isVSLRTlong}")
        # reverseActive = False
        # if useReverseOrderHLOOT and reversedHOOTentry and isHLOOTlong and reverseActive == False:
        #     reverseActive = True
        #     isHLOOTlong = False
        #     isHLOOTshort = True

        # if useReverseOrderHLOOT and reversedHOOTentry and isHLOOTshort and reverseActive == False:
        #     reverseActive = True
        #     isHLOOTshort = False
        #     isHLOOTlong = True

        # print(len(isVSLRTlong))
        df['long_entry'] = [all(values) for values in zip(isVSLRTlong, isHLOOTlong, isUseEMAlong, isUseSMAlong)]
        df['short_entry'] = [all(values) for values in zip(isVSLRTshort, isHLOOTshort, isUseEMAshort, isUseSMAshort)]

        # if useHLOOT:
        return {
            "long_entry": df['long_entry'], 
            "short_entry": df['short_entry'],
            "high_HLOOT": hoot,
            "low_HLOOT": loot,
            "ema_coord": ema_coord,
            "sma_coord": smaout_coord
        }
        
        # return df['long_entry'], df['short_entry']
    except Exception as e:
        h.logger.warning(f"issue LC {e}")
    # long_entry = isVSLRTlong
    # short_entry = isVSLRTshort
