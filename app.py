import streamlit
import discord_interaction
import metatrader_interface
import dotenv
import os
import helper_functions
import strategy_router
import time



# Function to get the data for button push
def get_data():
    """
    Function to get the data for button push
    """
    # Get the platform from the session state
    platform = streamlit.session_state['platform']
    # If the platform state is None, write an error message to the copilot container
    if platform is None:
        copilot_container.error("Please select a platform")
        return False
    else:
        # If the platform is MetaTrader 5, make sure the platform is MetaTrader5
        if platform == 'MetaTrader 5':
            platform = 'MetaTrader5'
    # Get the symbol and timeframe from the session state
    symbol = streamlit.session_state['symbol']
    # If the symbol state is None, write an error message to the copilot container
    if symbol is None:
        copilot_container.error("Please select a symbol")
        return False
    # Get the timeframe from the session state
    timeframe = streamlit.session_state['timeframe']
    # If the timeframe state is None, write an error message to the copilot container
    if timeframe is None:
        copilot_container.error("Please select a timeframe")
        return False
    # Get the strategy from the session state
    strategy = streamlit.session_state['strategy']
    # If the strategy state is None, write an error message to the copilot container
    if strategy is None:
        copilot_container.error("Please select a strategy")
        return False
    # Run the strategy with live status feedback
    try:
        with copilot_container.status("Running strategy...", expanded=True) as status:
            status.write(f"📡 Connecting to {platform}...")
            status.write(f"📊 Fetching {symbol} data on {timeframe} timeframe...")
            status.write(f"🧠 Running strategy: {strategy}...")
            data = strategy_router.strategy_router(
                platform=platform,
                symbol=symbol,
                timeframe=timeframe,
                strategy_name=strategy
            )
            decision = data.get('decision', 'unknown').upper()
            status.write(f"✅ Signal: **{decision}** | Entry: {data.get('entry')} | Exit: {data.get('exit')}")
            status.update(label=f"Strategy complete — {decision}", state="complete")
        copilot_container.write(data)
    except Exception as exception:
        import traceback
        copilot_container.error(f"An exception occurred when getting data: {exception}")
        copilot_container.code(traceback.format_exc())
        return False
    return True


# Function to get information for a given platform
def get_platform_info():
    """
    Function to get information for a given platform
    :param platform: The platform to get information for
    :param container: The container to add the widgets to
    """
    # Set up branching variables
    platform_connected = False
    # Get the platform from the session state
    platform = streamlit.session_state['platform']
    # Get the settings file selection from the session state
    settings_file = streamlit.session_state['settings_file']
    # Get any required information based on the platform
    if platform == "MetaTrader 5":
        if settings_file == "Yes":
            # Load environment variables from the .env file
            dotenv.load_dotenv()
            # Get the MetaTrader 5 username, password, server, and filepath from the .env file
            mt5_username = os.getenv('metatrader_username')
            mt5_password = os.getenv('metatrader_password')
            mt5_server = os.getenv('metatrader_server')
            mt5_filepath = os.getenv('metatrader_filepath')
        else:
            # Add four text inputs to the third column
            mt5_username = trading_platform.text_input('Username', value='', max_chars=None, key=None, type='default')
            mt5_password = trading_platform.text_input('Password', value='', max_chars=None, key=None, type='password')
            mt5_server = trading_platform.text_input('Server', value='', max_chars=None, key=None, type='default')
            mt5_filepath = trading_platform.text_input('Filepath', value='', max_chars=None, key=None, type='default')
        # When all four text inputs are filled, try to open the terminal
        if mt5_username and mt5_password and mt5_server and mt5_filepath:
            try:
                # Start MetaTrader 5
                mt5_start = metatrader_interface.start_metatrader(
                    mt5_username=mt5_username, 
                    mt5_password=mt5_password, 
                    mt5_server=mt5_server, 
                    mt5_filepath=mt5_filepath
                )
                # If successful, log in to MetaTrader 5
                if mt5_start:
                    copilot_container.success("MetaTrader5 started successfully")
                    platform_connected = True
                else:
                    copilot_container.error(f"MetaTrader 5 failed to start. Reason: {mt5_start}")
            except Exception as exception:
                copilot_container.error(f"An exception occurred when starting MetaTrader 5: {exception}")   
    else:
        print(f"{platform} is not supported yet.")
    # Check if the platform is connected
    if platform_connected is False:
        raise Exception(f"Failed to connect to {platform}")
    # Get the platform information
    symbols, timeframes, strategies = helper_functions.get_platform_info('MetaTrader5', symbol_st, timeframe_st)
    # Update the symbol, timeframe and strategies selectboxes
    streamlit.session_state['symbols'] = symbols
    streamlit.session_state['timeframes'] = timeframes
    streamlit.session_state['strategies'] = strategies
    return True
        


if __name__ == '__main__':
    #### Streamlit Setup ####
    # Start the streamlit app
    streamlit.set_page_config(
        page_title='Terminal',
        page_icon='📈',
        layout='wide'
    )
    # Create the session states
    if "settings_file" not in streamlit.session_state:
        streamlit.session_state.settings_file = None
    if "platform" not in streamlit.session_state:
        streamlit.session_state.platform = None
    if "symbol" not in streamlit.session_state:
        streamlit.session_state.symbol = None
    if "timeframe" not in streamlit.session_state:
        streamlit.session_state.timeframe = None
    if "symbols" not in streamlit.session_state:
        streamlit.session_state.symbols = []
    if "timeframes" not in streamlit.session_state:
        streamlit.session_state.timeframes = []
    if "strategies" not in streamlit.session_state:
        streamlit.session_state.strategies = []
    if "running" not in streamlit.session_state:
        streamlit.session_state.running = False
    if "make_trades" not in streamlit.session_state:
        streamlit.session_state.make_trades = None
    # Create the header
    streamlit.header('Terminal')
    # Create the header container
    header_container = streamlit.container()
    # Create four columns in the header container
    settings_choice, alert_listener, trading_platform, settings = header_container.columns(4)
    # Create a start_stop container
    start_stop = streamlit.container()
    start_button = False
    # Create a start button
    if start_button == False:
        # Create a start button that stretches across the page and is green
        start = start_stop.button(
            'Start', 
            use_container_width=True
            )
        start_button = True
    # Create a copilot container
    copilot_container = streamlit.container()
    # Add a title to the copilot container
    copilot_container.header(
        'Intelligence & Data'
    )
    # Create three columns in the copilot container
    symbol_st, timeframe_st, strategy_st = copilot_container.columns(3)
    # Add an empty dropdown to symbol_st and timeframe_st
    symbol_st.selectbox(
        'Symbol',
        streamlit.session_state['symbols'],
        index=None,
        key='symbol'
    )
    timeframe_st.selectbox(
        'Timeframe',
        streamlit.session_state['timeframes'],
        index=None,
        key='timeframe'
    )
    strategy_st.selectbox(
        'Strategy',
        streamlit.session_state['strategies'],
        index=None,
        placeholder='Select a strategy',
        key='strategy'
    )
    # Add a button to the Copilot container
    copilot_container.button('Get Data', on_click=get_data, use_container_width=True)

    # Button colour styling
    streamlit.markdown("""
        <style>
        div[data-testid="column"]:nth-of-type(1) button { background-color: #28a745; color: white; }
        div[data-testid="column"]:nth-of-type(2) button { background-color: #dc3545; color: white; }
        div[data-testid="column"]:nth-of-type(1) button:disabled,
        div[data-testid="column"]:nth-of-type(2) button:disabled { opacity: 0.4; cursor: not-allowed; }
        </style>
    """, unsafe_allow_html=True)

    # Start/Stop trading loop buttons
    col_start, col_stop, col_interval = copilot_container.columns([2, 2, 1])
    interval = col_interval.number_input('Interval (seconds)', min_value=1, value=60, step=1, key='interval')
    if col_start.button('▶ Start Trading with Strategy', use_container_width=True, disabled=streamlit.session_state.running):
        if not streamlit.session_state['platform'] or not streamlit.session_state['symbol'] or not streamlit.session_state['timeframe'] or not streamlit.session_state['strategy']:
            copilot_container.error("Please select a platform, symbol, timeframe, and strategy before starting.")
        else:
            streamlit.session_state.running = True
            streamlit.session_state['loop_platform'] = 'MetaTrader5' if streamlit.session_state['platform'] == 'MetaTrader 5' else streamlit.session_state['platform']
            streamlit.session_state['loop_symbol'] = streamlit.session_state['symbol']
            streamlit.session_state['loop_timeframe'] = streamlit.session_state['timeframe']
            streamlit.session_state['loop_strategy'] = streamlit.session_state['strategy']
            streamlit.session_state['loop_make_trades'] = streamlit.session_state.get('make_trades')
            streamlit.rerun()
    if col_stop.button('⏹ Stop', use_container_width=True, disabled=not streamlit.session_state.running):
        streamlit.session_state.running = False

    # Live trading loop
    if streamlit.session_state.running:
        live_status = copilot_container.empty()
        live_result = copilot_container.empty()
        platform = streamlit.session_state['loop_platform']
        symbol = streamlit.session_state['loop_symbol']
        timeframe = streamlit.session_state['loop_timeframe']
        strategy = streamlit.session_state['loop_strategy']
        iteration = 0
        while streamlit.session_state.running:
            iteration += 1
            try:
                with live_status.status(f"🔄 Running iteration {iteration}...", expanded=True) as status:
                    status.write(f"📡 Fetching {symbol} on {timeframe}...")
                    data = strategy_router.strategy_router(platform=platform, symbol=symbol, timeframe=timeframe, strategy_name=strategy)
                    decision = data.get('decision', 'unknown').upper()
                    status.write(f"✅ Signal: **{decision}** | Entry: {data.get('entry')} | Exit: {data.get('exit')}")
                    status.update(label=f"Iteration {iteration} — {decision}", state="complete")
                live_result.write(data)
                # Place order if Make Trades is Yes and signal is not hold
                copilot_container.info(f"🔍 Debug — make_trades: `{streamlit.session_state.get('loop_make_trades')}` | decision: `{data.get('decision')}`")
                if streamlit.session_state.get('loop_make_trades') == 'Yes' and data.get('decision') != 'hold':
                    try:
                        order_result = metatrader_interface.place_order(symbol, data)
                        copilot_container.success(f"✅ Order placed: {data['decision'].upper()} {symbol} | Ticket: {order_result.order}")
                    except Exception as order_err:
                        import traceback
                        copilot_container.error(f"Order failed: {order_err}")
                        copilot_container.code(traceback.format_exc())
                elif data.get('decision') == 'hold':
                    copilot_container.info("⏸ Signal is HOLD — no order placed")
                else:
                    copilot_container.warning("⚠️ Make Trades is not set to Yes — no order placed")
            except Exception as e:
                import traceback
                live_status.error(f"Error on iteration {iteration}: {e}")
                live_result.code(traceback.format_exc())
                streamlit.session_state.running = False
                break
            time.sleep(streamlit.session_state.get('interval', 60))    # Add an option to use a settings file
    settings_file = settings_choice.selectbox(
        'Use Settings File',
        ['Yes', 'No'],
        index=None,
        placeholder='Select an option', 
        key='settings_file'
    )
    # Configure the alert listener column #
    # Add a dropdown to the alert listener column
    alerting_option = alert_listener.selectbox(
        'Alert Listener', 
        ['Discord', 'Direct'], 
        index=None,
        placeholder='Select an alerting option'
    )
    if alerting_option == 'Discord':
        copilot_container.write('Connecting to Discord...')
        if settings_file:
            # Load environment variables from the .env file
            dotenv.load_dotenv()
            # Get the Discord key from the .env file
            discord_key = os.getenv('discord_key')
        else:
            # Add a text input to the alert listener column
            discord_key = alert_listener.text_input('Discord Key', value='', max_chars=None, key=None, type='default')
    # Add a dropdown to the trading platform column
    trading_platform_selection = trading_platform.selectbox(
        'Trading Platform', 
        ['MetaTrader 5', 'Binance', 'Coinbase'],
        index=None,
        placeholder='Select a trading platform',
        on_change=get_platform_info, 
        key='platform'
    )
    # Add a selectbox to the fourth column
    make_trades = settings.selectbox(
        'Make Trades', 
        ['Yes', 'No'],
        index=None,
        placeholder='Select an option',
        key='make_trades'
    )
    
    
        
     
