# Crypto Trading Bot
Trading Bot programmed to execute trades for all your favorite crypto coins using the Coinbase Pro API ! This trading bot utilizes the financial investment strategy of mean reversion, a methodology of calculating the average closing prices of an asset over a historical period of time, and then comparing that average to the current asset price levels. The theory suggests that asset price volatility will always return to its long-run average, thus allowing us to identify buying and selling opportunities!
As an added layer of performance enchancement, this bot applies the mean reversion theory to asset trading volumes as well, a common trading strategy in crypto markets! 

Recommended run-time of this bot is daily, Please use at your own risk. Below are instructions for setup, and running this bot. 

## Setup and Installation
The following bot utilizes the Coinbase Pro trading platform API, which requires a valid set of API credentials in order to makes data calls, execute buy orders, and place sell orders. A free API key can be obtained at the company`s website after creating a valid login: https://pro.coinbase.com/  

Additionally, users will need the latest version of python (version 3.10) to run the program, along with the following python packages: cbpro (library used to handle API requests to coinbase pro API), and pandas (used for data analysis). Both can be downloaded using the windows terminal with the following commands:

`python -m pip install cbpro`

`python -m pip install pandas`

After these few installation steps go ahead and open the CryptoTradingBot - V1 - Coinbase API.py (located within this github repo) within your IDE. The program is now ready for execution!

## Running the Bot!
Some important notes before hitting the run button are as follows:

You will need to pass your unique Coinbase Pro API credentials into the following variable titled auth_client (line 6). For security reasons it is recommended that you create a separate .py, or .txt file storing the key, secret, and passphrase in order to pass the information into the variable.

![image](https://user-images.githubusercontent.com/91297951/190295527-80e6454d-9dbf-49bf-bc80-e450ae048bd4.png)

Additionally, calling just one function (coinbase_order_execution) will run the bot for one execution cycle! All the way at the bottom of the program you will find the following variables that can be adjusted to your trading strategy and limits/tolerance. 

![image](https://user-images.githubusercontent.com/91297951/190297447-4e410528-ea73-485c-b28e-3288b423784e.png)

Once you reach this point, you are now ready to hit run! Best of Luck!

 



