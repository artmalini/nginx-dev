import pandas as pd
import helpers as h

def trackBenefits(long_entry, short_entry, df, money):
    # Track current position and starting capital
    current_position = None
    starting_capital = money  # Starting capital in dollars
    current_capital = starting_capital
    entry_time = None
    entry_price = None

    # Lists to store trade information
    trades = []

    for i in range(len(df)):
        # Check if it's a long entry point
        if long_entry[i]:
            if current_position != 'long':  # If not already in a long position
                # long_entry_point = df.index[i]
                if current_position == 'short':  # If in a short position, close it
                    exit_time = df.index[i]
                    exit_price = df.loc[exit_time, 'open']
                    percent_change = ((entry_price - exit_price) / entry_price) * 100
                    current_capital *= (1 + percent_change / 100)
                    trades.append({'Entry Type': 'Short', 'Entry Time': entry_time, 'Exit Time': exit_time, 'Entry Price': entry_price, 'Exit Price': exit_price, 'Profit/Loss (%)': percent_change})
                current_position = 'long'
                entry_time = df.index[i]
                entry_price = df.loc[entry_time, 'open']
        # Check if it's a short entry point
        elif short_entry[i]:
            if current_position != 'short':  # If not already in a short position
                # short_entry_point = df.index[i]
                if current_position == 'long':  # If in a long position, close it
                    exit_time = df.index[i]
                    exit_price = df.loc[exit_time, 'open']
                    percent_change = ((exit_price - entry_price) / entry_price) * 100
                    current_capital *= (1 + percent_change / 100)
                    trades.append({'Entry Type': 'Long', 'Entry Time': entry_time, 'Exit Time': exit_time, 'Entry Price': entry_price, 'Exit Price': exit_price, 'Profit/Loss (%)': percent_change})
                current_position = 'short'
                entry_time = df.index[i]
                entry_price = df.loc[entry_time, 'open']
            
    # print(trades)
    # return
    # print(long_entry[0])
    # print(long_entry_points)
    
    # Print trade information
    count = 1
    for trade in trades:
        # entry_type = "Long" if trade['Profit/Loss (%)'] > 0 else "Short"
        # exit_type = "Short" if entry_type == "Long" else "Long"
        
        # Calculate volatility when the price moved in the opposite direction
        if trade['Entry Type'] == "long":
            exit_price = df.loc[trade['Exit Time'], 'low']
            entry_index = df.index.get_loc(pd.Timestamp(trade['Entry Time']))
            exit_index = df.index.get_loc(pd.Timestamp(trade['Exit Time']))
            high_prices = df['high'].iloc[entry_index: exit_index]
            max_volatility = max(high_prices) - exit_price
        else:
            exit_price = df.loc[trade['Exit Time'], 'high']
            entry_index = df.index.get_loc(pd.Timestamp(trade['Entry Time']))
            exit_index = df.index.get_loc(pd.Timestamp(trade['Exit Time']))
            low_prices = df['low'].iloc[entry_index: exit_index]
            max_volatility = exit_price - min(low_prices)

        # Calculate max volatility as percentage
        entry_price = df.loc[trade['Entry Time'], 'close']
        max_volatility_percent = (max_volatility / entry_price) * 100
        h.logger.info(f"{count} | Entry Type: {trade['Entry Type']} | Entry Price: {entry_price} | Exit Price: {exit_price} | Entry Time: {trade['Entry Time']} | Exit Time: {trade['Exit Time']} | Profit/Loss (%): {round(trade['Profit/Loss (%)'], 2)} | Volatility: {round(max_volatility_percent, 2)}")
        count += 1

    # Overall profit/loss since strategy started
    overall_change = ((current_capital - starting_capital) / starting_capital) * 100
    # return trades, overall_change
    h.logger.info(f"Overall Profit/Loss ($): {round(overall_change, 2)}")

    # Calculate win rate
    winning_trades = [trade for trade in trades if trade['Profit/Loss (%)'] > 0]
    win_rate = (len(winning_trades) / len(trades)) * 100

    # Print win rate
    h.logger.info(f"Win Rate (%): {round(win_rate, 2)}")