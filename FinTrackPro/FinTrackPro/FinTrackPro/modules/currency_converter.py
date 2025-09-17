import streamlit as st
import requests
import time
from datetime import datetime
from utils.api_utils import get_exchange_rates, get_supported_currencies

def show_currency_converter():
    st.header("💱 Currency Converter")
    st.markdown("Convert between different currencies with real-time exchange rates.")
    
    # Get supported currencies
    currencies = get_supported_currencies()
    
    if not currencies:
        st.error("❌ Unable to load currency data. Please check your internet connection and try again.")
        return
    
    # Currency converter interface
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("From")
        from_currency = st.selectbox(
            "Select source currency:",
            options=list(currencies.keys()),
            index=list(currencies.keys()).index('USD') if 'USD' in currencies else 0,
            format_func=lambda x: f"{x} - {currencies[x]}"
        )
        
        amount = st.number_input(
            "Amount to convert:",
            min_value=0.01,
            value=100.0,
            step=0.01,
            format="%.2f"
        )
    
    with col2:
        st.subheader("To")
        to_currency = st.selectbox(
            "Select target currency:",
            options=list(currencies.keys()),
            index=list(currencies.keys()).index('EUR') if 'EUR' in currencies else 1,
            format_func=lambda x: f"{x} - {currencies[x]}"
        )
    
    # Convert button
    if st.button("🔄 Convert", type="primary", use_container_width=True):
        if from_currency == to_currency:
            st.warning("⚠️ Source and target currencies are the same!")
        else:
            with st.spinner("Getting latest exchange rates..."):
                # Get exchange rates
                rates = get_exchange_rates(from_currency)
                
                if rates and to_currency in rates:
                    exchange_rate = rates[to_currency]
                    converted_amount = amount * exchange_rate
                    
                    # Display result
                    st.success("✅ Conversion successful!")
                    
                    # Result display
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        st.metric(
                            label=f"Amount in {from_currency}",
                            value=f"{amount:,.2f}"
                        )
                    
                    with col2:
                        st.metric(
                            label="Exchange Rate",
                            value=f"1 {from_currency} = {exchange_rate:.4f} {to_currency}"
                        )
                    
                    with col3:
                        st.metric(
                            label=f"Amount in {to_currency}",
                            value=f"{converted_amount:,.2f}"
                        )
                    
                    # Additional info
                    st.info(f"📊 **{amount:,.2f} {from_currency}** = **{converted_amount:,.2f} {to_currency}**")
                    st.caption(f"Exchange rate updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    
                else:
                    st.error("❌ Failed to get exchange rate. Please try again later.")
    
    st.divider()
    
    # Popular currency pairs
    st.subheader("📈 Popular Currency Pairs")
    
    popular_pairs = [
        ('USD', 'EUR'),
        ('USD', 'GBP'),
        ('USD', 'JPY'),
        ('EUR', 'GBP'),
        ('USD', 'CAD'),
        ('USD', 'AUD')
    ]
    
    if st.button("🔄 Refresh Rates", use_container_width=True):
        st.rerun()
    
    # Display popular pairs in a grid
    cols = st.columns(3)
    
    for i, (base, target) in enumerate(popular_pairs):
        if base in currencies and target in currencies:
            with cols[i % 3]:
                rates = get_exchange_rates(base)
                if rates and target in rates:
                    rate = rates[target]
                    st.metric(
                        label=f"{base} → {target}",
                        value=f"{rate:.4f}"
                    )
                else:
                    st.metric(
                        label=f"{base} → {target}",
                        value="N/A"
                    )
    
    # Currency information
    st.divider()
    st.subheader("ℹ️ Currency Information")
    
    selected_currency = st.selectbox(
        "Select a currency to learn more:",
        options=list(currencies.keys()),
        format_func=lambda x: f"{x} - {currencies[x]}"
    )
    
    if selected_currency:
        st.markdown(f"""
        **Currency Code:** {selected_currency}
        
        **Full Name:** {currencies[selected_currency]}
        
        **Usage:** This currency is used in various countries and territories worldwide.
        """)
    
    # Exchange rate trends (placeholder for future enhancement)
    st.divider()
    st.subheader("📊 Exchange Rate Trends")
    st.info("📈 Historical exchange rate charts and trends will be available in future updates.")
    
    # Disclaimer
    st.divider()
    st.caption("""
    **Disclaimer:** Exchange rates are provided for informational purposes only and may not reflect real-time market rates. 
    For actual financial transactions, please consult with your bank or financial institution.
    """)
