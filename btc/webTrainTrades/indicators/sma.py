from indicators.libmath import l_sma
import helpers as h

def sma(df, source, emalen):
    long_signal = [False]
    short_signal = [False]
    smaout = []
    
    try:
        if not df.empty and emalen:
            smaout = l_sma(df, source, emalen)

            for index in range(len(df)):
                if index > 0 :
                    emaup = smaout[index] > smaout[index - 1]
                    emadown = smaout[index] < smaout[index - 1]

                    long_signal.append(emaup)
                    short_signal.append(emadown)
        
    except Exception as e:
         h.logger.warning(f'SMA {e}')

    return long_signal, short_signal, smaout