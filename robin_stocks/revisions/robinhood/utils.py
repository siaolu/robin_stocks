"""Contains all the URL endpoints for interacting with Robinhood API."""
from robin_stocks.robinhood.helper import id_for_chain, id_for_stock


# Login
def login_url():
    """Returns the URL for logging into Robinhood."""
    return 'https://api.robinhood.com/oauth2/token/'


def challenge_url(challenge_id: str) -> str:
    """Returns the URL for responding to a login challenge."""
    return f'https://api.robinhood.com/challenge/{challenge_id}/respond/'


# Profiles
def account_profile_url(account_number: Optional[str] = None) -> str:
    """Returns the URL for accessing the account profile."""
    if account_number:
        return f'https://api.robinhood.com/accounts/{account_number}'
    return 'https://api.robinhood.com/accounts/?default_to_all_accounts=true'


def basic_profile_url() -> str:
    """Returns the URL for accessing basic user profile information."""
    return 'https://api.robinhood.com/user/basic_info/'


def investment_profile_url() -> str:
    """Returns the URL for accessing the investment profile."""
    return 'https://api.robinhood.com/user/investment_profile/'


def portfolio_profile_url(account_number: Optional[str] = None) -> str:
    """Returns the URL for accessing the portfolio profile."""
    if account_number:
        return f'https://api.robinhood.com/portfolios/{account_number}'
    return 'https://api.robinhood.com/portfolios/'


def security_profile_url() -> str:
    """Returns the URL for accessing the security profile."""
    return 'https://api.robinhood.com/user/additional_info/'


def user_profile_url() -> str:
    """Returns the URL for accessing the user profile."""
    return 'https://api.robinhood.com/user/'


def portfolio_historicals_url(account_number: str) -> str:
    """Returns the URL for accessing portfolio historicals."""
    return f'https://api.robinhood.com/portfolios/historicals/{account_number}/'


# Stocks
def earnings_url() -> str:
    """Returns the URL for accessing earnings data."""
    return 'https://api.robinhood.com/marketdata/earnings/'


def events_url() -> str:
    """Returns the URL for accessing stock-related events."""
    return 'https://api.robinhood.com/options/events/'


def fundamentals_url() -> str:
    """Returns the URL for accessing stock fundamentals."""
    return 'https://api.robinhood.com/fundamentals/'


def historicals_url() -> str:
    """Returns the URL for accessing stock historical data."""
    return 'https://api.robinhood.com/quotes/historicals/'


def instruments_url() -> str:
    """Returns the URL for accessing stock instruments."""
    return 'https://api.robinhood.com/instruments/'


def news_url(symbol: str) -> str:
    """Returns the URL for accessing news related to a stock."""
    return f'https://api.robinhood.com/midlands/news/{symbol}/?'


def popularity_url(symbol: str) -> str:
    """Returns the URL for accessing the popularity data of a stock."""
    stock_id = id_for_stock(symbol)
    return f'https://api.robinhood.com/instruments/{stock_id}/popularity/'


def quotes_url() -> str:
    """Returns the URL for accessing stock quotes."""
    return 'https://api.robinhood.com/quotes/'


def ratings_url(symbol: str) -> str:
    """Returns the URL for accessing stock ratings."""
    stock_id = id_for_stock(symbol)
    return f'https://api.robinhood.com/midlands/ratings/{stock_id}/'


def splits_url(symbol: str) -> str:
    """Returns the URL for accessing stock splits data."""
    stock_id = id_for_stock(symbol)
    return f'https://api.robinhood.com/instruments/{stock_id}/splits/'


# Account
def phoenix_url() -> str:
    """Returns the URL for accessing unified accounts in Phoenix."""
    return 'https://phoenix.robinhood.com/accounts/unified'


def positions_url(account_number: Optional[str] = None) -> str:
    """Returns the URL for accessing positions."""
    if account_number:
        return f'https://api.robinhood.com/positions/?account_number={account_number}'
    return 'https://api.robinhood.com/positions/'


def banktransfers_url(direction: Optional[str] = None) -> str:
    """Returns the URL for accessing bank transfers."""
    if direction == 'received':
        return 'https://api.robinhood.com/ach/received/transfers/'
    return 'https://api.robinhood.com/ach/transfers/'


def cardtransactions_url() -> str:
    """Returns the URL for accessing card transactions."""
    return 'https://minerva.robinhood.com/history/transactions/'


def daytrades_url(account: str) -> str:
    """Returns the URL for accessing recent day trades."""
    return f'https://api.robinhood.com/accounts/{account}/recent_day_trades/'


def dividends_url() -> str:
    """Returns the URL for accessing dividends."""
    return 'https://api.robinhood.com/dividends/'


def documents_url() -> str:
    """Returns the URL for accessing documents."""
    return 'https://api.robinhood.com/documents/'


def withdrawal_url(bank_id: str) -> str:
    """Returns the URL for initiating a bank withdrawal."""
    return f"https://api.robinhood.com/ach/relationships/{bank_id}/"


def linked_url(id: Optional[str] = None, unlink: bool = False) -> str:
    """Returns the URL for accessing linked accounts."""
    if unlink and id:
        return f'https://api.robinhood.com/ach/relationships/{id}/unlink/'
    if id:
        return f'https://api.robinhood.com/ach/relationships/{id}/'
    return 'https://api.robinhood.com/ach/relationships/'


def margin_url() -> str:
    """Returns the URL for accessing margin information."""
    return 'https://api.robinhood.com/margin/calls/'


def margininterest_url() -> str:
    """Returns the URL for accessing margin interest charges."""
    return 'https://api.robinhood.com/cash_journal/margin_interest_charges/'


def notifications_url(tracker: bool = False) -> str:
    """Returns the URL for accessing notifications."""
    if tracker:
        return 'https://api.robinhood.com/midlands/notifications/notification_tracker/'
    return 'https://api.robinhood.com/notifications/devices/'


def referral_url() -> str:
    """Returns the URL for accessing referral information."""
    return 'https://api.robinhood.com/midlands/referral/'


def stockloan_url() -> str:
    """Returns the URL for accessing stock loan payments."""
    return 'https://api.robinhood.com/accounts/stock_loan_payments/'


def interest_url() -> str:
    """Returns the URL for accessing account interest information."""
    return 'https://api.robinhood.com/accounts/sweeps/'


def subscription_url() -> str:
    """Returns the URL for accessing subscription fees."""
    return 'https://api.robinhood.com/subscription/subscription_fees/'


def wiretransfers_url() -> str:
    """Returns the URL for accessing wire transfers."""
    return 'https://api.robinhood.com/wire/transfers'


def watchlists_url(name: Optional[str] = None) -> str:
    """Returns the URL for accessing watchlists."""
    if name:
        return 'https://api.robinhood.com/midlands/lists/items/'
    return 'https://api.robinhood.com/midlands/lists/default/'


# Markets
def currency_url() -> str:
    """Returns the URL for accessing currency pairs."""
    return 'https://nummus.robinhood.com/currency_pairs/'


def markets_url() -> str:
    """Returns the URL for accessing market information."""
    return 'https://api.robinhood.com/markets/'


def market_hours_url(market: str, date: str) -> str:
    """Returns the URL for accessing market hours for a given market and date."""
    return f'https://api.robinhood.com/markets/{market}/hours/{date}/'


def movers_sp500_url() -> str:
    """Returns the URL for accessing S&P 500 movers."""
    return 'https://api.robinhood.com/midlands/movers/sp500/'


def get_100_most_popular_url() -> str:
    """Returns the URL for accessing the 100 most popular stocks."""
    return 'https://api.robinhood.com/midlands/tags/tag/100-most-popular/'


def movers_top_url() -> str:
    """Returns the URL for accessing top movers."""
    return 'https://api.robinhood.com/midlands/tags/tag/top-movers/'


def market_category_url(category: str) -> str:
    """Returns the URL for accessing market data by category."""
    return f'https://api.robinhood.com/midlands/tags/tag/{category}/'


# Options
def aggregate_url(account_number: Optional[str] = None) -> str:
    """Returns the URL for accessing aggregate positions."""
    if account_number:
        return f'https://api.robinhood.com/options/aggregate_positions/?account_numbers={account_number}'
    return 'https://api.robinhood.com/options/aggregate_positions/'


def chains_url(symbol: str) -> str:
    """Returns the URL for accessing options chains."""
    chain_id = id_for_chain(symbol)
    return f'https://api.robinhood.com/options/chains/{chain_id}/'


def option_historicals_url(option_id: str) -> str:
    """Returns the URL for accessing options historical data."""
    return f'https://api.robinhood.com/marketdata/options/historicals/{option_id}/'


def option_instruments_url(option_id: Optional[str] = None) -> str:
    """Returns the URL for accessing options instruments."""
    if option_id:
        return f'https://api.robinhood.com/options/instruments/{option_id}/'
    return 'https://api.robinhood.com/options/instruments/'


def option_orders_url(order_id: Optional[str] = None, account_number: Optional[str] = None) -> str:
    """Returns the URL for accessing options orders."""
    url = 'https://api.robinhood.com/options/orders/'
    if order_id:
        url += f'{order_id}/'
    if account_number:
        url += f'?account_numbers={account_number}'
    return url


def option_positions_url(account_number: str) -> str:
    """Returns the URL for accessing options positions."""
    return f'https://api.robinhood.com/options/positions/?account_numbers={account_number}'


def marketdata_options_url() -> str:
    """Returns the URL for accessing options market data."""
    return 'https://api.robinhood.com/marketdata/options/'


# Pricebook
def marketdata_quotes_url(stock_id: str) -> str:
    """Returns the URL for accessing stock quotes by stock ID."""
    return f'https://api.robinhood.com/marketdata/quotes/{stock_id}/'


def marketdata_pricebook_url(stock_id: str) -> str:
    """Returns the URL for accessing stock price book data by stock ID."""
    return f'https://api.robinhood.com/marketdata/pricebook/snapshots/{stock_id}/'


# Crypto
def order_crypto_url() -> str:
    """Returns the URL for placing crypto orders."""
    return 'https://nummus.robinhood.com/orders/'


def crypto_account_url() -> str:
    """Returns the URL for accessing crypto accounts."""
    return 'https://nummus.robinhood.com/accounts/'


def crypto_currency_pairs_url() -> str:
    """Returns the URL for accessing crypto currency pairs."""
    return 'https://nummus.robinhood.com/currency_pairs/'


def crypto_quote_url(crypto_id: str) -> str:
    """Returns the URL for accessing crypto quotes by crypto ID."""
    return f'https://api.robinhood.com/marketdata/forex/quotes/{crypto_id}/'


def crypto_holdings_url() -> str:
    """Returns the URL for accessing crypto holdings."""
    return 'https://nummus.robinhood.com/holdings/'


def crypto_historical_url(crypto_id: str) -> str:
    """Returns the URL for accessing crypto historical data by crypto ID."""
    return f'https://api.robinhood.com/marketdata/forex/historicals/{crypto_id}/'


def crypto_orders_url(order_id: Optional[str] = None) -> str:
    """Returns the URL for accessing crypto orders."""
    if order_id:
        return f'https://nummus.robinhood.com/orders/{order_id}/'
    return 'https://nummus.robinhood.com/orders/'


def crypto_cancel_url(crypto_id: str) -> str:
    """Returns the URL for canceling a crypto order."""
    return f'https://nummus.robinhood.com/orders/{crypto_id}/cancel/'


# Orders
def cancel_url(order_id: str) -> str:
    """Returns the URL for canceling an order."""
    return f'https://api.robinhood.com/orders/{order_id}/cancel/'


def option_cancel_url(option_id: str) -> str:
    """Returns the URL for canceling an options order."""
    return f'https://api.robinhood.com/options/orders/{option_id}/cancel/'


def orders_url(order_id: Optional[str] = None, account_number: Optional[str] = None) -> str:
    """Returns the URL for accessing orders."""
    url = 'https://api.robinhood.com/orders/'
    if order_id:
        url += f'{order_id}/'
    if account_number:
        url += f'?account_numbers={account_number}'
    return url
