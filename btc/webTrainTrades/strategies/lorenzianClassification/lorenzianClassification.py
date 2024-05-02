from indicators.vslrt import vslrt
from indicators.hloot import hloot

def lC(df):
    # Inputs
    dateRange = False
    source = df['open']
    neighborsCount = 8
    maxBarsBack = 2000
    featureCount = 5
    colorCompression = 1

    useVSLRT = False
    vslrtLen1 = 20
    vslrtLen2 = 50

    useHLOOT = True
    hlootLength = 2
    hlootPercent = 0.6
    hlootHllength = 10
    hlootMav = 'VAR'
    useReverseOrderHLOOT = False

    useSUPERTREND = False
    useReverseOrder = False

    if useVSLRT:
        vslrt_long_entry, vslrt_short_entry = vslrt(df, source, vslrtLen1, vslrtLen2)
    if useHLOOT:
        hloot_long_entry, hloot_short_entry, reversedHOOTentry = hloot(df, source, hlootLength, hlootPercent, hlootHllength, hlootMav, useReverseOrderHLOOT)


    isVSLRTlong = True
    isVSLRTshort = True
    if useVSLRT:
        isVSLRTlong = vslrt_long_entry
        isVSLRTshort = vslrt_short_entry
    isHLOOTlong = True
    isHLOOTshort = True
    if useHLOOT:
        isHLOOTlong = hloot_long_entry
        isHLOOTshort = hloot_short_entry

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
    df['long_entry'] = isHLOOTlong
    df['short_entry'] = isHLOOTshort
    # long_entry = isVSLRTlong
    # short_entry = isVSLRTshort
    
    return df['long_entry'], df['short_entry']