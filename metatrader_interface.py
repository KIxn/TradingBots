import os
import dotenv
import MetaTrader5
import pandas
import data_normalizer
import datetime
import logging_config

# Load environment variables
dotenv.load_dotenv()

# Setup logging
logger = logging_config.get_logger()


# Function to start MetaTrader 5
def start_metatrader(mt5_username=None, mt5_password=None, mt5_server=None, mt5_filepath=None):
    """
    Function to start MetaTrader 5
    """
    logger.info(f"Starting MetaTrader 5 connection")
    logger.debug(f"Inputs - username: {'***' if mt5_password else 'None'}, server: {mt5_server}, filepath: {mt5_filepath}")
    
    # If any the variables are None, try to get them from the .env file
    if not mt5_username or not mt5_password or not mt5_server or not mt5_filepath:
        uname = os.getenv(metatrader_username)
        pword = os.getenv(metatrader_password)
        server = os.getenv(metatrader_server)
        terminal64filepath = os.getenv(metatrader_filepath)
        logger.debug("Using credentials from .env file")
    # Otherwise, assign the variables
    else:
        uname = mt5_username
        pword = mt5_password
        server = mt5_server
        terminal64filepath = mt5_filepath
        logger.debug("Using provided credentials")
    
    # Check if the terminal64 file exists
    if not os.path.exists(terminal64filepath):
        error_msg = f"The terminal64 file does not exist at the specified path {terminal64filepath}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    # Convert the inputs to the right data types
    # Uname is a integer
    uname = int(uname)
    # Pword is a string
    pword = str(pword)
    # Server is a string
    server = str(server)
    # Filepath is a string
    terminal64filepath = str(terminal64filepath)
    
    logger.info(f"Attempting to initialize MetaTrader 5 with login: {uname}, server: {server}")
    
    # Try to start MetaTrader 5
    try:
        mt5_start = MetaTrader5.initialize(login=uname, password=pword, server=server, path=terminal64filepath)
        logger.debug(f"MetaTrader5.initialize() called with path: {terminal64filepath}")
    except Exception as exception:
        error_msg = f"An exception occurred when starting MetaTrader 5: {exception}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    # If successful, log in to MetaTrader 5
    if mt5_start:
        logger.info("MetaTrader 5 initialized successfully, attempting login")
        try:
            login = MetaTrader5.login(login=uname, password=pword, server=server)
            logger.debug(f"MetaTrader5.login() called")
        except Exception as exception:
            logger.error(f"Login exception: {exception}")
            raise exception
        
        # If successful, return True
        if login:
            logger.info("MetaTrader 5 login successful")
            return True
        # If not successful, raise an exception
        else:
            error_msg = "MetaTrader 5 failed to log in"
            logger.error(error_msg)
            raise Exception(error_msg)
    else:
        error_msg = "MetaTrader 5 failed to start"
        logger.error(error_msg)
        raise Exception(error_msg)


# Function to get a list of all the symbols in MetaTrader 5
def get_my_symbols():
    """
    Function to get a list of all the symbols in MetaTrader 5
    """
    logger.info("Getting symbols from MetaTrader 5")
    # Get the symbols
    try:
        symbols = MetaTrader5.symbols_get()
        logger.debug(f"Retrieved {len(symbols)} symbols from MetaTrader 5")
    except Exception as exception:
        error_msg = f"An exception occurred when getting the symbols for MetaTrader 5: {exception}"
        logger.error(error_msg)
        raise Exception(error_msg)
    all_symbols = []
    # Iterate through the symbols and get the names
    for symbol in symbols:
        all_symbols.append(symbol.name)
    logger.info(f"Retrieved {len(all_symbols)} symbols from MetaTrader 5")
    # Otherwise, return the symbols
    return all_symbols


# Function to get data from MetaTrader 5
def get_historic_data(symbol, timeframe, count=10):
    """
    Function to get data from MetaTrader 5
    """
    logger.info(f"Getting historic data for {symbol} on timeframe {timeframe}, count: {count}")
    # Convert the timeframe to something MT5 friendly
    timeframe = convert_to_mt5_timeframe(timeframe)
    logger.debug(f"Converted timeframe to MT5: {timeframe}")
    # Get the data
    try:
        data = MetaTrader5.copy_rates_from_pos(symbol, timeframe, 0, count)
    except Exception as exception:
        error_msg = f"An exception occurred when getting the data for MetaTrader 5: {exception}"
        logger.error(error_msg)
        raise Exception(error_msg)
    # Convert the data to a DataFrame
    data = pandas.DataFrame(data)
    # Pass the data to the data normalizer
    data = data_normalizer.normalize_data_format(data, "MetaTrader5")
    logger.info(f"Successfully retrieved and normalized data for {symbol}: \n {data}")
    # Return the data
    return data


# Function to convert the timeframe to something MT5 friendly
def convert_to_mt5_timeframe(timeframe: str):
    """
    Function to convert the timeframe to something MT5 friendly
    """
    if timeframe == "M1":
        return MetaTrader5.TIMEFRAME_M1
    elif timeframe == "M2":
        return MetaTrader5.TIMEFRAME_M2
    elif timeframe == "M3":
        return MetaTrader5.TIMEFRAME_M3
    elif timeframe == "M4":
        return MetaTrader5.TIMEFRAME_M4
    elif timeframe == "M5":
        return MetaTrader5.TIMEFRAME_M5
    elif timeframe == "M6":
        return MetaTrader5.TIMEFRAME_M6
    elif timeframe == "M10":
        return MetaTrader5.TIMEFRAME_M10
    elif timeframe == "M12":
        return MetaTrader5.TIMEFRAME_M12
    elif timeframe == "M15":
        return MetaTrader5.TIMEFRAME_M15
    elif timeframe == "M20":
        return MetaTrader5.TIMEFRAME_M20
    elif timeframe == "M30":
        return MetaTrader5.TIMEFRAME_M30
    elif timeframe == "H1":
        return MetaTrader5.TIMEFRAME_H1
    elif timeframe == "H2":
        return MetaTrader5.TIMEFRAME_H2
    elif timeframe == "H3":
        return MetaTrader5.TIMEFRAME_H3
    elif timeframe == "H4":
        return MetaTrader5.TIMEFRAME_H4
    elif timeframe == "H6":
        return MetaTrader5.TIMEFRAME_H6
    elif timeframe == "H8":
        return MetaTrader5.TIMEFRAME_H8
    elif timeframe == "H12":
        return MetaTrader5.TIMEFRAME_H12
    elif timeframe == "D1":
        return MetaTrader5.TIMEFRAME_D1
    elif timeframe == "W1":
        return MetaTrader5.TIMEFRAME_W1
    elif timeframe == "MN1":
        return MetaTrader5.TIMEFRAME_MN1
    else:
        raise Exception("The timeframe is not supported")


# Function to get historical data between two dates
def get_historic_data_range(symbol, timeframe, date_from, date_to):
    """
    Returns OHLCV DataFrame with columns Open/High/Low/Close/Volume
    indexed by datetime — compatible with backtesting.py.
    """
    import pytz, calendar
    from datetime import datetime

    logger.info(f"Getting historical data for {symbol} from {date_from} to {date_to} on timeframe {timeframe}")
    
    timezone = pytz.timezone("Etc/UTC")
    utc_from = int(
        calendar.timegm(datetime(date_from.year, date_from.month, date_from.day, tzinfo=timezone).timetuple())
    )
    utc_to = int(calendar.timegm(datetime(date_to.year, date_to.month, date_to.day, 23, tzinfo=timezone).timetuple()))
    mt5_timeframe = convert_to_mt5_timeframe(timeframe)
    
    logger.debug(f"Fetching data: symbol={symbol}, timeframe={timeframe}, from={utc_from}, to={utc_to}")
    
    try:
        data = MetaTrader5.copy_rates_range(symbol, mt5_timeframe, utc_from, utc_to)
        logger.debug(f"Retrieved {len(data) if data is not None else 0} data points")
    except Exception as exception:
        error_msg = f"Failed to fetch historical data: {exception}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    if data is None or len(data) == 0:
        error = MetaTrader5.last_error()
        error_msg = f"No data returned for {symbol} between {date_from} and {date_to}. MT5 error: {error}"
        logger.error(error_msg)
        print("copy_rates_range Inputs: ", symbol, mt5_timeframe, utc_from, utc_to)
        raise Exception(error_msg)
    
    df = pandas.DataFrame(data)
    df["time"] = pandas.to_datetime(df["time"], unit="s")
    df = df.set_index("time")
    df = df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "tick_volume": "Volume"})
    output_data = df[["Open", "High", "Low", "Close", "Volume"]]
    logger.info(f"Successfully retrieved {len(df)} data points for {symbol} \n {output_data}")
    return output_data


# Function to place an order on MetaTrader 5
def place_order(symbol, signal, order_filling = "FOK"):
    """
    Places a market order based on a signal dict with decision, entry, and exit.
    Stop loss is set at 10% against the position.
    """
    logger.info(f"Placing order for {symbol} with signal: {signal}")
    
    decision = signal["decision"]
    if decision == "hold":
        logger.info("Hold signal - no order placed")
        return None

    logger.debug(f"Getting symbol info for {symbol}")
    symbol_info = MetaTrader5.symbol_info(symbol)
    if symbol_info is None:
        error_msg = f"Symbol {symbol} not found"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    if not symbol_info.visible:
        logger.debug(f"Symbol {symbol} not visible, selecting it")
        MetaTrader5.symbol_select(symbol, True)

    lot = 0.1
    price = MetaTrader5.symbol_info_tick(symbol).ask if decision == "buy" else MetaTrader5.symbol_info_tick(symbol).bid
    take_profit = signal["exit"]

    if decision == "buy":
        order_type = MetaTrader5.ORDER_TYPE_BUY
        stop_loss = price * 0.90  # 10% below entry
        logger.debug(f"Buy order - price: {price}, take_profit: {take_profit}, stop_loss: {stop_loss}")
    else:
        order_type = MetaTrader5.ORDER_TYPE_SELL
        stop_loss = price * 1.10  # 10% above entry
        logger.debug(f"Sell order - price: {price}, take_profit: {take_profit}, stop_loss: {stop_loss}")
    
    if order_filling == "FOK":
        order_type_filling = MetaTrader5.ORDER_FILLING_FOK
    elif order_filling == "IOC":
        order_type_filling = MetaTrader5.ORDER_FILLING_IOC
    else:
        order_type_filling = MetaTrader5.ORDER_FILLING_RETURN

    request = {
        "action": MetaTrader5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": round(stop_loss, symbol_info.digits),
        "tp": round(take_profit, symbol_info.digits),
        "deviation": 20,
        "magic": 234000,
        "comment": "trading-bot",
        "type_time": MetaTrader5.ORDER_TIME_GTC,
        "type_filling": order_type_filling,
    }

    logger.debug(f"Sending order request: {request}")
    
    try:
        result = MetaTrader5.order_send(request)
        logger.debug(f"Order result: retcode={result.retcode}, comment={result.comment}")
    except Exception as e:
        error_msg = f"Order send failed: {e}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    if result.retcode != MetaTrader5.TRADE_RETCODE_DONE:
        error_msg = f"Order failed: {result.retcode} — {result.comment}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    logger.info(f"Order placed successfully for {symbol}: {result.comment}")
    return result
