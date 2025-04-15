from flask import Flask, render_template, request
import yfinance as yf
import datetime
import pytz

app = Flask(__name__)

def get_stock_info(symbol):
    """
    Retrieves stock information for the given symbol.
    
    Args:
        symbol (str): The stock symbol to look up
        
    Returns:
        dict: Information about the stock or None if an error occurred
    """
    try:
        # Get stock information
        stock = yf.Ticker(symbol)
        
        # Basic info
        info = stock.info
        
        # Check if we got valid data
        if not info or 'regularMarketPrice' not in info:
            return None
        
        # Get current price and previous close
        current_price = info.get('regularMarketPrice')
        previous_close = info.get('previousClose')
        
        # Calculate changes
        price_change = current_price - previous_close
        percent_change = (price_change / previous_close) * 100
        
        # Format the sign for display
        sign = '+' if price_change >= 0 else ''
        
        return {
            'name': info.get('longName', 'Unknown Company'),
            'symbol': symbol.upper(),
            'price': current_price,
            'change': f"{sign}{price_change:.2f}",
            'percent_change': f"{sign}{percent_change:.2f}%"
        }
    except Exception as e:
        print(f"Error retrieving stock information: {e}")
        return None

def get_current_time():
    """
    Gets the current date and time in PDT (Pacific Daylight Time).
    
    Returns:
        str: Formatted date and time string
    """
    # Get current UTC time
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    
    # Convert to Pacific Time (US)
    pacific_tz = pytz.timezone('US/Pacific')
    pacific_time = utc_now.astimezone(pacific_tz)
    
    # Format like the example (Mon Oct 10 17:23:48 PDT 2016)
    return pacific_time.strftime("%a %b %d %H:%M:%S %Z %Y")

@app.route('/', methods=['GET', 'POST'])
def index():
    stock_info = None
    error_message = None
    current_time = None
    symbol = ""
    
    if request.method == 'POST':
        symbol = request.form.get('symbol', '').strip()
        
        if symbol:
            stock_info = get_stock_info(symbol)
            current_time = get_current_time()
            
            if not stock_info:
                error_message = f"Could not retrieve information for symbol: {symbol}. Please check your internet connection or try a different symbol."
    
    return render_template('index.html', 
                           stock_info=stock_info, 
                           error_message=error_message, 
                           current_time=current_time,
                           symbol=symbol)

if __name__ == '__main__':
    app.run(debug=True)