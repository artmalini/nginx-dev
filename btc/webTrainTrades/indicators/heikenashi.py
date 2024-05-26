from indicators.libmath import l_ema
import helpers as h

def ashi_ema(source, length):
    ema_values = []
    try:
        if source and length:
            alpha = 2 / (length + 1)

            for i in range(length):
                if i == 0:
                    ema_values.append(source[i])  # First value is same as source
                else:
                    previous_ema = ema_values[-1]
                    current_value = source[i]
                    ema = alpha * current_value + (1 - alpha) * previous_ema
                    ema_values.append(ema)

            return ema_values
    except Exception as e:
        h.logger.warning(f'ashi_ema {e} {ema_values}')
        return ema_values

def heikenashi(df, lenFSM, len2SSM):
    long_signal = []
    short_signal = []
    
    try:
        if not df.empty :
            open = [0] * lenFSM
            high = [0] * lenFSM
            close = [0] * lenFSM
            low = [0] * lenFSM

            oFSM = [0] * lenFSM
            cFSM = [0] * lenFSM
            hFSM = [0] * lenFSM
            lFSM = [0] * lenFSM

            hacloseSM = [0] * len2SSM
            haopenSM = [0] * len2SSM
            hahighSM = [0] * len2SSM
            halowSM = [0] * len2SSM

            for index in range(len(df)):
                open = [df["open"].iloc[index]] + open[:-1]
                high = [df["high"].iloc[index]] + high[:-1]
                close = [df["close"].iloc[index]] + close[:-1]
                low = [df["low"].iloc[index]] + low[:-1]

                oFSM = ashi_ema(open, lenFSM)
                cFSM = ashi_ema(high, lenFSM)
                hFSM = ashi_ema(close, lenFSM)
                lFSM = ashi_ema(low, lenFSM)
                hacloseSM = [(oFSM[-1] + hFSM[-1] + lFSM[-1] + cFSM[-1]) / 4] + hacloseSM[:-1]

                if haopenSM[1] == 0 :
                    haopenSM = [(oFSM[-1] + cFSM[-1]) / 2] + haopenSM[:-1]
                if haopenSM[1] != 0 :
                    haopenSM = [(haopenSM[1] + hacloseSM[1]) / 2] + haopenSM[:-1]

                # if index == 2:
                #     h.logger.info(f"test {oFSM}")
                #     return

                hahighSM = [max(hFSM[-1], max(haopenSM[0], hacloseSM[0]))] + hahighSM[:-1]
                halowSM = [min(lFSM[-1], min(haopenSM[0], hacloseSM[0]))] + halowSM[:-1]

                o2SSM = ashi_ema(haopenSM, len2SSM)
                c2SSM = ashi_ema(hacloseSM, len2SSM)
                h2SSM = ashi_ema(hahighSM, len2SSM)
                l2SSM = ashi_ema(halowSM, len2SSM)

                # crossover
                buy_condition = ((c2SSM[-2] < o2SSM[-2]) and (c2SSM[-1] > o2SSM[-1])) and (c2SSM[-1] > c2SSM[-2]) # and (c2SSM[-1] > h2SSM[-2]) #
                # crossunder
                sell_condition = ((c2SSM[-2] > o2SSM[-2]) and (c2SSM[-1] < o2SSM[-1])) and (c2SSM[-1] < c2SSM[-2]) # and (c2SSM[-1] < l2SSM[-2]) #  
                
                # if index == 1400:
                #     h.logger.info(f"test {o2SSM} {h2SSM}")
                #     return

                long_signal.append(buy_condition)
                short_signal.append(sell_condition)
        
    except Exception as e:
         h.logger.warning(f'heikenashi {e}')

    # h.logger.info(f"Buy {long_signal}")
    return long_signal, short_signal