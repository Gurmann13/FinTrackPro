import requests
import streamlit as st
import os
from datetime import datetime

def get_exchange_rates(base_currency='USD'):
    """
    Get exchange rates from exchangerate-api.com
    
    Args:
        base_currency (str): Base currency code (default: USD)
    
    Returns:
        dict: Dictionary of exchange rates or None if failed
    """
    try:
        # Use free exchangerate-api.com service
        api_key = os.getenv("EXCHANGE_API_KEY", "")
        
        if api_key:
            # If API key is available, use the authenticated endpoint
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
        else:
            # Use the free endpoint (limited requests)
            url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        
        # Make API request with timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different API response formats
        if 'conversion_rates' in data:
            return data['conversion_rates']
        elif 'rates' in data:
            return data['rates']
        else:
            st.error("❌ Unexpected API response format")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Network error fetching exchange rates: {str(e)}")
        return None
    except requests.exceptions.Timeout:
        st.error("❌ Request timeout. Please try again later.")
        return None
    except Exception as e:
        st.error(f"❌ Error fetching exchange rates: {str(e)}")
        return None

def get_supported_currencies():
    """
    Get list of supported currencies with their full names
    
    Returns:
        dict: Dictionary mapping currency codes to full names
    """
    try:
        # First try to get from API
        api_key = os.getenv("EXCHANGE_API_KEY", "")
        
        if api_key:
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/codes"
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if 'supported_codes' in data:
                    # Convert list of [code, name] pairs to dictionary
                    return {code: name for code, name in data['supported_codes']}
            except:
                pass  # Fall back to default list
        
        # Fallback to common currencies if API fails
        return get_default_currencies()
        
    except Exception as e:
        st.warning(f"⚠️ Using default currency list: {str(e)}")
        return get_default_currencies()

def get_default_currencies():
    """
    Get default list of common currencies
    
    Returns:
        dict: Dictionary of common currencies
    """
    return {
        'USD': 'US Dollar',
        'EUR': 'Euro',
        'GBP': 'British Pound Sterling',
        'JPY': 'Japanese Yen',
        'AUD': 'Australian Dollar',
        'CAD': 'Canadian Dollar',
        'CHF': 'Swiss Franc',
        'CNY': 'Chinese Yuan',
        'SEK': 'Swedish Krona',
        'NZD': 'New Zealand Dollar',
        'MXN': 'Mexican Peso',
        'SGD': 'Singapore Dollar',
        'HKD': 'Hong Kong Dollar',
        'NOK': 'Norwegian Krone',
        'TRY': 'Turkish Lira',
        'RUB': 'Russian Ruble',
        'INR': 'Indian Rupee',
        'BRL': 'Brazilian Real',
        'ZAR': 'South African Rand',
        'KRW': 'South Korean Won',
        'DKK': 'Danish Krone',
        'PLN': 'Polish Zloty',
        'TWD': 'Taiwan New Dollar',
        'THB': 'Thai Baht',
        'MYR': 'Malaysian Ringgit',
        'IDR': 'Indonesian Rupiah',
        'CZK': 'Czech Republic Koruna',
        'HUF': 'Hungarian Forint',
        'ILS': 'Israeli New Sheqel',
        'CLP': 'Chilean Peso',
        'PHP': 'Philippine Peso',
        'AED': 'UAE Dirham',
        'COP': 'Colombian Peso',
        'SAR': 'Saudi Riyal',
        'RON': 'Romanian Leu',
        'BGN': 'Bulgarian Lev',
        'HRK': 'Croatian Kuna',
        'ISK': 'Icelandic Krona',
        'UAH': 'Ukrainian Hryvnia'
    }

def get_historical_rates(base_currency, target_currency, date):
    """
    Get historical exchange rate for a specific date
    
    Args:
        base_currency (str): Base currency code
        target_currency (str): Target currency code
        date (str): Date in YYYY-MM-DD format
    
    Returns:
        float: Exchange rate or None if failed
    """
    try:
        api_key = os.getenv("EXCHANGE_API_KEY", "")
        
        if not api_key:
            st.warning("⚠️ Historical rates require API key")
            return None
        
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/history/{base_currency}/{date}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'conversion_rates' in data and target_currency in data['conversion_rates']:
            return data['conversion_rates'][target_currency]
        else:
            return None
            
    except Exception as e:
        st.error(f"❌ Error fetching historical rates: {str(e)}")
        return None

def validate_currency_code(currency_code):
    """
    Validate if a currency code is supported
    
    Args:
        currency_code (str): Currency code to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        supported_currencies = get_supported_currencies()
        return currency_code.upper() in supported_currencies
    except:
        return False

def format_currency_amount(amount, currency_code):
    """
    Format amount with appropriate currency symbol
    
    Args:
        amount (float): Amount to format
        currency_code (str): Currency code
    
    Returns:
        str: Formatted currency string
    """
    try:
        # Common currency symbols
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'INR': '₹',
            'CNY': '¥',
            'KRW': '₩',
            'RUB': '₽',
            'BRL': 'R$',
            'CAD': 'C$',
            'AUD': 'A$',
            'CHF': 'CHF',
            'SEK': 'kr',
            'NOK': 'kr',
            'DKK': 'kr'
        }
        
        symbol = currency_symbols.get(currency_code, currency_code)
        
        # Format with appropriate decimal places
        if currency_code == 'JPY':
            # Japanese Yen typically has no decimal places
            return f"{symbol}{amount:,.0f}"
        else:
            return f"{symbol}{amount:,.2f}"
            
    except Exception as e:
        return f"{currency_code} {amount:,.2f}"

def get_currency_info(currency_code):
    """
    Get detailed information about a currency
    
    Args:
        currency_code (str): Currency code
    
    Returns:
        dict: Currency information or None if not found
    """
    try:
        currencies = get_supported_currencies()
        
        if currency_code in currencies:
            return {
                'code': currency_code,
                'name': currencies[currency_code],
                'symbol': get_currency_symbol(currency_code)
            }
        else:
            return None
            
    except Exception as e:
        return None

def get_currency_symbol(currency_code):
    """
    Get currency symbol for a given currency code
    
    Args:
        currency_code (str): Currency code
    
    Returns:
        str: Currency symbol
    """
    symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'INR': '₹',
        'CNY': '¥', 'KRW': '₩', 'RUB': '₽', 'BRL': 'R$', 'CAD': 'C$',
        'AUD': 'A$', 'CHF': 'CHF', 'SEK': 'kr', 'NOK': 'kr', 'DKK': 'kr',
        'PLN': 'zł', 'CZK': 'Kč', 'HUF': 'Ft', 'TRY': '₺', 'ILS': '₪',
        'THB': '฿', 'MYR': 'RM', 'SGD': 'S$', 'HKD': 'HK$', 'NZD': 'NZ$',
        'ZAR': 'R', 'MXN': '$', 'AED': 'د.إ', 'SAR': '﷼'
    }
    
    return symbols.get(currency_code, currency_code)

def check_api_status():
    """
    Check if the exchange rate API is accessible
    
    Returns:
        bool: True if API is accessible, False otherwise
    """
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_exchange_rates(base_currency='USD'):
    """
    Get exchange rates with caching to reduce API calls
    
    Args:
        base_currency (str): Base currency code
    
    Returns:
        dict: Exchange rates dictionary
    """
    return get_exchange_rates(base_currency)

def convert_amount(amount, from_currency, to_currency):
    """
    Convert amount from one currency to another
    
    Args:
        amount (float): Amount to convert
        from_currency (str): Source currency code
        to_currency (str): Target currency code
    
    Returns:
        tuple: (converted_amount, exchange_rate) or (None, None) if failed
    """
    try:
        if from_currency == to_currency:
            return amount, 1.0
        
        rates = get_cached_exchange_rates(from_currency)
        
        if rates and to_currency in rates:
            exchange_rate = rates[to_currency]
            converted_amount = amount * exchange_rate
            return round(converted_amount, 2), exchange_rate
        else:
            return None, None
            
    except Exception as e:
        st.error(f"❌ Error converting currency: {str(e)}")
        return None, None
