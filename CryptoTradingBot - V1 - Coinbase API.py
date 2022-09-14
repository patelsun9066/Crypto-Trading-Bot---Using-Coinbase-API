import cbpro
import pandas as pd
from time import sleep
from api_auth_credentials import api_key, api_secret, api_passphrase

auth_client = cbpro.AuthenticatedClient(api_key, api_secret, api_passphrase)  # User inputs unique API Key here
c = cbpro.PublicClient()


def past_week_historical_data(coin_ticker):
    """The following function uses the Coinbase API to retrieve historical price and volume data for the past seven
    days. The function requires one input parameter, a string which represents the abbreviated ticker of the coin we
    are looking to trade, separated by a dash and finally the abbreviated symbol of the currency exchange we would like
     the price to be denoted in. An example of the input would be: BTC-USD"""

    # Coinbase API call to get historical data. Change granularity to change date filter.
    historical_data = pd.DataFrame(c.get_product_historic_rates(product_id=coin_ticker, granularity=86400))
    historical_data.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
    historical_data['Date'] = pd.to_datetime(historical_data['Date'], unit='s')
    historical_data.set_index('Date', inplace=False)

    # filter the historical data down to seven data points (one week/seven days)
    past_week_data = historical_data.iloc[0:7]

    # Extracts the date, volume, and closing prices for each date and stores them in a list.
    dates = []
    for date in past_week_data["Date"]:
        dates.append(date)

    volume_list = []
    for volume in past_week_data["Volume"]:
        volume_list.append(volume)

    close_prices = []
    for prices in past_week_data["Close"]:
        close_prices.append(prices)

    return dates, volume_list, close_prices


def technical_indicator(analysis_data, coin_ticker):
    """The following function uses the data returned by the past_historical_week_data function (historical prices and
    volumes for the past week), and the abbreviated coin ticker being traded as a string as input parameters.This
    function then calculates the average price and average volume of the asset for the last week. Finally, using the
    financial theory of mean reversion the function will recommend a buy, sell, or hold position depending on
    relationship between the average price/volume vs. the current price/volume.
    """
    # assigns list data to variables
    volume_list = analysis_data[1]
    close_price_list = analysis_data[2]

    # calculates the average/mean of data points in each list
    average_of_volume_list = sum(volume_list) / len(volume_list)
    average_of_close_price_list = sum(close_price_list) / len(close_price_list)

    # Coinbase API call to retrieve current price/volume data
    current_product_ticker = c.get_product_ticker(product_id=coin_ticker)
    current_coin_price = float(current_product_ticker['price'])
    current_volume_level = float(current_product_ticker['volume'])

    # calculates the percentage difference between average prices/volume and current prices/volumes.
    percentage_diff_prices = ((average_of_close_price_list - current_coin_price) / average_of_close_price_list) * 100
    percentage_diff_volume = ((current_volume_level - average_of_volume_list) / current_volume_level) * 100

    # Conditionals to determine a buy, sell, or hold decision. Dependent on average vs. current from above.
    price_signal = None
    volume_signal = None

    if percentage_diff_prices > .15 and average_of_close_price_list > current_coin_price:
        price_signal = "BUY"
    elif 0 < percentage_diff_prices <= .15 and average_of_close_price_list > current_coin_price:
        price_signal = "HOLD"
    elif percentage_diff_prices <= 0 and average_of_close_price_list <= current_coin_price:
        price_signal = "SELL"

    if percentage_diff_volume > .25 and current_volume_level > average_of_volume_list:
        volume_signal = "BUY"
    elif 0 < percentage_diff_volume <= .25 and current_volume_level > average_of_volume_list:
        volume_signal = "HOLD"
    elif percentage_diff_volume <= 0 and current_volume_level <= average_of_volume_list:
        volume_signal = "SELL"

    return price_signal, volume_signal


def coinbase_order_execution(coin_ticker, wallet_balance, available_funds, purchasing_power_per_trans):
    """The following function requires the following input parameters: the ticker of the coin being traded as a
    string, your current coinbase wallet balance (amount of asset you currently own as float), available deposited
    cash dollars for purchases in coinbase account (float), and amount of asset you want to purchase for every buy
    algorithmic buy recommendation. (float). IMPORTANT: This is the only function that needs to be called in this
    program for the trading bot to execute market buy or sell orders. Please see project README on GitHub for further
    instructions."""

    # Uses input parameters to make call to other functions in this program to obtain historical data + buy/sell rec.
    data = past_week_historical_data(coin_ticker)
    tech = technical_indicator(data, coin_ticker)

    # Tracks +/- to general ledger of coinbase wallet balance and deposited funds
    coinbase_wallet_balance = wallet_balance
    purchasing_power_amount = available_funds

    # formalizes action recommendation from technical_indicator function (either buy, sell, or hold)
    action_signal = None
    if tech[0] == "BUY" and tech[1] == "BUY":
        action_signal = "BUY"
    elif tech[0] == "SELL" and tech[1] == "SELL":
        action_signal = "SELL"
    elif tech[0] == "HOLD" and tech[1] == "HOLD":
        action_signal = "HOLD"

    # Coinbase API call to retrieve current product ticker info.
    current_price = c.get_product_ticker(product_id=coin_ticker)

    # Executes buy order if recommended, returns feedback on order status, plus updates GL tracker above.
    current_buy_order = None
    current_buy_order_check = "no order yet"

    if action_signal == "BUY":
        try:
            current_buy_order = auth_client.place_limit_order(product_id=coin_ticker, side='buy',
                                                              price=current_price['price'],
                                                              size=str(purchasing_power_per_trans),
                                                              overdraft_enabled=False)
        except Exception as coin:
            print(f'Error placing buy order: {coin}')

        sleep(15)

        try:
            check = current_buy_order['id']
            current_buy_order_check = auth_client.get_order(order_id=check)
        except Exception as coin:
            print(f'Unable to check buy order. It might be rejected. {coin}')

        if current_buy_order_check['status'] == 'done':
            print(current_buy_order_check)
            coinbase_wallet_balance += float(purchasing_power_per_trans)
            dollar_spent_calc = float(current_price['price']) * float(purchasing_power_per_trans)
            purchasing_power_amount -= dollar_spent_calc
            return "Buy Order Execution Successful"
        else:
            return "Buy Order Execution Unsuccessful"

    # Executes sell order if recommended, returns feedback on order status, plus updates GL tracker above.
    current_sell_order = None
    current_sell_order_check = "no order yet"

    if action_signal == "SELL":
        try:
            current_sell_order = auth_client.sell(price=current_price['price'], size=str(coinbase_wallet_balance),
                                                  order_type='limit', product_id=coin_ticker)
        except Exception as coin:
            print(f'Error placing sell order: {coin}')

        sleep(15)

        try:
            sell_check = current_sell_order['id']
            current_sell_order_check = auth_client.get_order(order_id=sell_check)
        except Exception as coin:
            print(f'Unable to check sell order. It might be rejected. {coin}')

        if current_sell_order_check['status'] == 'done':
            print(current_sell_order_check)
            dollar_sell_calc = float(current_price['price']) * float(coinbase_wallet_balance)
            purchasing_power_amount += dollar_sell_calc
            coinbase_wallet_balance -= float(coinbase_wallet_balance)
            return "Sell Order Execution Successful"
        else:
            return "Sell Order Execution Unsuccessful"

    # If not a buy or sell recommendation, then asset should be held, or is waiting for first buy rec.
    else:
        return f'The action signal is either HOLD or has not reached a first-time BUY'


def main():
    coin_to_trade = "BTC-USD"
    current_wallet_balance = 0.00
    available_funds_to_trade_dollars = 0.00
    purchase_amount_per_buy_transaction = 0.00005
    bot_run = coinbase_order_execution(coin_to_trade, current_wallet_balance, available_funds_to_trade_dollars,
                                       purchase_amount_per_buy_transaction)
    print(bot_run)


if __name__ == '__main__':
    main()
