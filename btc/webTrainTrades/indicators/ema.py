from indicators.libmath import l_ema
import helpers as h

def ema(df, source, emalen):
    long_signal = [False]
    short_signal = [False]
    emaout = []
    
    try:
        if not df.empty and emalen:
            emaout = l_ema(df, source, emalen)

            for index in range(len(df)):
                if index > 0 :
                    emaup = emaout[index] > emaout[index - 1]
                    emadown = emaout[index] < emaout[index - 1]

                    long_signal.append(emaup)
                    short_signal.append(emadown)
        
    except Exception as e:
         h.logger.warning(f'EMA {e}')

    return long_signal, short_signal, emaout