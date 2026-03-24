import streamlit
import metatrader_interface
import dotenv
import os
import helper_functions
import strategy_router
import time
import datetime
from backtesting import Backtest


def get_platform_info():
    platform_connected = False
    platform = streamlit.session_state['platform']
    settings_file = streamlit.session_state['settings_file']

    if platform == "MetaTrader 5":
        if settings_file == "Yes":
            dotenv.load_dotenv()
            mt5_username = os.getenv('metatrader_username')
            mt5_password = os.getenv('metatrader_password')
            mt5_server = os.getenv('metatrader_server')
            mt5_filepath = os.getenv('metatrader_filepath')
        else:
            mt5_username = trading_platform.text_input('Username', type='default')
            mt5_password = trading_platform.text_input('Password', type='password')
            mt5_server = trading_platform.text_input('Server')
            mt5_filepath = trading_platform.text_input('Filepath')

        if mt5_username and mt5_password and mt5_server and mt5_filepath:
            try:
                if metatrader_interface.start_metatrader(mt5_username, mt5_password, mt5_server, mt5_filepath):
                    platform_connected = True
                    streamlit.session_state['platform_connected'] = True
            except Exception as e:
                streamlit.session_state['platform_connected'] = False
                streamlit.error(f"Failed to connect to MetaTrader 5: {e}")
    else:
        streamlit.warning(f"{platform} is not supported yet.")

    if not platform_connected:
        raise Exception(f"Failed to connect to {platform}")

    symbols, timeframes, strategies = helper_functions.get_platform_info('MetaTrader5', None, None)
    streamlit.session_state['symbols'] = symbols
    streamlit.session_state['timeframes'] = timeframes
    streamlit.session_state['strategies'] = strategies


if __name__ == '__main__':
    streamlit.set_page_config(page_title='Terminal', page_icon='📈', layout='wide')

    # Session state init
    for key, default in [
        ('settings_file', None), ('platform', None), ('symbol', None),
        ('timeframe', None), ('symbols', []), ('timeframes', []),
        ('strategies', []), ('running', False), ('make_trades', None),
        ('platform_connected', False),
    ]:
        if key not in streamlit.session_state:
            streamlit.session_state[key] = default

    # ── Header ──────────────────────────────────────────────────────────────
    streamlit.header('Terminal')
    header_container = streamlit.container()
    settings_choice, alert_listener, trading_platform, settings = header_container.columns(4)

    settings_choice.selectbox('Use Settings File', ['Yes', 'No'], index=None,
                               placeholder='Select an option', key='settings_file')

    alerting_option = alert_listener.selectbox('Alert Listener', ['Discord'], index=None,
                                                placeholder='Select an alerting option')
    if alerting_option == 'Discord':
        if streamlit.session_state['settings_file'] == 'Yes':
            dotenv.load_dotenv()
            discord_key = os.getenv('discord_key')
        else:
            discord_key = alert_listener.text_input('Discord Key', type='default')

    trading_platform.selectbox('Trading Platform', ['MetaTrader 5'], index=None,
                                placeholder='Select a trading platform',
                                on_change=get_platform_info, key='platform')

    settings.selectbox('Make Trades', ['Yes', 'No'], index=None,
                        placeholder='Select an option', key='make_trades')

    # ── Connection status banner ─────────────────────────────────────────────
    if streamlit.session_state.get('platform_connected'):
        streamlit.success(f"✅ Connected to {streamlit.session_state['platform']}")
    elif streamlit.session_state.get('platform'):
        streamlit.warning("⚠️ Platform selected but not connected")

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab_backtest, tab_live = streamlit.tabs(["📊 Backtesting", "⚡ Live Trading"])

    # ── Backtesting Tab ───────────────────────────────────────────────────────
    with tab_backtest:
        streamlit.subheader("Backtesting")
        col_sym, col_tf, col_strat = streamlit.columns(3)
        bt_symbol = col_sym.selectbox('Symbol', streamlit.session_state['symbols'],
                                       index=None, key='bt_symbol')
        bt_timeframe = col_tf.selectbox('Timeframe', streamlit.session_state['timeframes'],
                                         index=None, key='bt_timeframe')
        bt_strategy = col_strat.selectbox('Strategy', streamlit.session_state['strategies'],
                                           index=None, key='bt_strategy')

        today = datetime.date.today()
        col_from, col_to = streamlit.columns(2)
        date_from = col_from.date_input('From', value=today - datetime.timedelta(days=30), max_value=today)
        date_to = col_to.date_input('To', value=today, max_value=today)

        # Warn if range is large on a small timeframe
        small_timeframes = ['M1', 'M5', 'M15', 'M30']
        date_range_days = (date_to - date_from).days
        if bt_timeframe in small_timeframes and date_range_days > 180:
            streamlit.warning(f"⚠️ {bt_timeframe} timeframe over {date_range_days} days may return too much data or exceed MT5 history limits. Consider using H1 or higher for ranges over 6 months.")

        if streamlit.button('▶ Run Backtest', width='stretch'):
            if not bt_symbol or not bt_timeframe or not bt_strategy:
                streamlit.error("Please select a symbol, timeframe, and strategy.")
            elif not streamlit.session_state['platform']:
                streamlit.error("Please connect to a trading platform first.")
            else:
                with streamlit.status("Running backtest...", expanded=True) as status:
                    try:
                        status.write(f"📥 Fetching {bt_symbol} data from {date_from} to {date_to}...")
                        df = metatrader_interface.get_historic_data_range(
                            bt_symbol, bt_timeframe, date_from, date_to
                        )
                        status.write(f"🧠 Running {bt_strategy}...")
                        strategy_class = strategy_router.get_strategy_class(bt_strategy)
                        # TODO - UserWarning: Some trades remain open at the end of backtest. Use `Backtest(..., finalize_trades=True)`
                        bt = Backtest(df, strategy_class, cash=1_000_000, commission=0.002)
                        stats = bt.run()
                        status.update(label="Backtest complete ✅", state="complete")

                        # Convert entire stats series to strings to avoid Arrow mixed-type errors
                        def safe_series(s):
                            return s.astype(str).to_frame()

                        def safe_df(df):
                            return df.astype(str)

                        streamlit.subheader("Results")
                        key_stats = stats[[
                            'Return [%]', 'Buy & Hold Return [%]', 'Max. Drawdown [%]',
                            'Win Rate [%]', '# Trades', 'Sharpe Ratio', 'Profit Factor'
                        ]]
                        streamlit.dataframe(safe_series(key_stats), width='stretch')

                        with streamlit.expander("Full Stats"):
                            streamlit.dataframe(safe_series(stats.drop(['_equity_curve', '_trades'])),
                                                width='stretch')

                        with streamlit.expander("Trade Log"):
                            streamlit.dataframe(safe_df(stats['_trades']), width='stretch')

                        # Chart
                        import tempfile, pathlib
                        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
                            chart_path = f.name
                        bt.plot(filename=chart_path, open_browser=False)
                        streamlit.components.v1.html(
                            pathlib.Path(chart_path).read_text(encoding='utf-8'),
                            height=600, scrolling=True
                        )
                    except Exception as e:
                        import traceback
                        streamlit.error(f"Backtest failed: {e}")
                        streamlit.code(traceback.format_exc())

    # ── Live Trading Tab ──────────────────────────────────────────────────────
    with tab_live:
        streamlit.subheader("Live Trading")

        # Button styling
        streamlit.markdown("""
            <style>
            div[data-testid="column"]:nth-of-type(1) button { background-color: #28a745; color: white; }
            div[data-testid="column"]:nth-of-type(2) button { background-color: #dc3545; color: white; }
            div[data-testid="column"]:nth-of-type(1) button:disabled,
            div[data-testid="column"]:nth-of-type(2) button:disabled { opacity: 0.4; cursor: not-allowed; }
            </style>
        """, unsafe_allow_html=True)

        col_sym2, col_tf2, col_strat2 = streamlit.columns(3)
        col_sym2.selectbox('Symbol', streamlit.session_state['symbols'], index=None, key='symbol')
        col_tf2.selectbox('Timeframe', streamlit.session_state['timeframes'], index=None, key='timeframe')
        col_strat2.selectbox('Strategy', streamlit.session_state['strategies'], index=None,
                              placeholder='Select a strategy', key='strategy')

        col_start, col_stop, col_interval = streamlit.columns([2, 2, 1])
        col_interval.number_input('Interval (s)', min_value=1, value=60, step=1, key='interval')

        if col_start.button('▶ Start Trading', use_container_width=True,
                             disabled=streamlit.session_state.running):
            if not all([streamlit.session_state.get(k) for k in ['platform', 'symbol', 'timeframe', 'strategy']]):
                streamlit.error("Please select a platform, symbol, timeframe, and strategy.")
            else:
                streamlit.session_state.running = True
                streamlit.session_state['loop_platform'] = 'MetaTrader5' if streamlit.session_state['platform'] == 'MetaTrader 5' else streamlit.session_state['platform']
                streamlit.session_state['loop_symbol'] = streamlit.session_state['symbol']
                streamlit.session_state['loop_timeframe'] = streamlit.session_state['timeframe']
                streamlit.session_state['loop_strategy'] = streamlit.session_state['strategy']
                streamlit.session_state['loop_make_trades'] = streamlit.session_state.get('make_trades')
                streamlit.rerun()

        if col_stop.button('⏹ Stop', use_container_width=True,
                            disabled=not streamlit.session_state.running):
            streamlit.session_state.running = False

        if streamlit.session_state.running:
            live_status = streamlit.empty()
            live_result = streamlit.empty()
            platform = streamlit.session_state['loop_platform']
            symbol = streamlit.session_state['loop_symbol']
            timeframe = streamlit.session_state['loop_timeframe']
            strategy = streamlit.session_state['loop_strategy']
            iteration = 0
            while streamlit.session_state.running:
                iteration += 1
                try:
                    with live_status.status(f"🔄 Iteration {iteration}...", expanded=True) as status:
                        status.write(f"📡 Fetching {symbol} on {timeframe}...")
                        data = strategy_router.strategy_router(platform, symbol, timeframe, strategy)
                        decision = data.get('decision', 'unknown').upper()
                        status.write(f"✅ Signal: **{decision}** | Entry: {data.get('entry')} | Exit: {data.get('exit')}")
                        status.update(label=f"Iteration {iteration} — {decision}", state="complete")
                    live_result.write(data)

                    if streamlit.session_state.get('loop_make_trades') == 'Yes' and data.get('decision') != 'hold':
                        try:
                            order_result = metatrader_interface.place_order(symbol, data)
                            streamlit.success(f"✅ Order placed: {decision} {symbol} | Ticket: {order_result.order}")
                        except Exception as order_err:
                            import traceback
                            streamlit.error(f"Order failed: {order_err}")
                            streamlit.code(traceback.format_exc())
                    elif data.get('decision') == 'hold':
                        streamlit.info("⏸ HOLD — no order placed")
                    else:
                        streamlit.warning("⚠️ Make Trades is not Yes — signal only mode")

                except Exception as e:
                    import traceback
                    live_status.error(f"Error on iteration {iteration}: {e}")
                    live_result.code(traceback.format_exc())
                    streamlit.session_state.running = False
                    break
                time.sleep(streamlit.session_state.get('interval', 60))
