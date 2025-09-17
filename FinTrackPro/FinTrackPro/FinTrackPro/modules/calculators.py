import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.calculations import calculate_emi, calculate_compound_interest, calculate_tax

def show_calculators():
    st.header("🔢 Finance Calculators")
    st.markdown("Use these calculators to plan your financial future.")
    
    # Calculator selection
    calculator_type = st.selectbox(
        "Choose a calculator:",
        ["💳 Loan EMI Calculator", "💰 Investment Growth Calculator", "🧾 Tax Calculator"]
    )
    
    st.divider()
    
    if calculator_type == "💳 Loan EMI Calculator":
        show_emi_calculator()
    elif calculator_type == "💰 Investment Growth Calculator":
        show_investment_calculator()
    elif calculator_type == "🧾 Tax Calculator":
        show_tax_calculator()

def show_emi_calculator():
    st.subheader("💳 Loan EMI Calculator")
    st.markdown("Calculate your Equated Monthly Installment (EMI) for loans.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        loan_amount = st.number_input(
            "Loan Amount ($):",
            min_value=1000,
            max_value=10000000,
            value=100000,
            step=1000,
            format="%d"
        )
        
        annual_rate = st.number_input(
            "Annual Interest Rate (%):",
            min_value=0.1,
            max_value=50.0,
            value=7.5,
            step=0.1,
            format="%.1f"
        )
        
        loan_tenure_years = st.number_input(
            "Loan Tenure (Years):",
            min_value=1,
            max_value=50,
            value=15,
            step=1
        )
    
    with col2:
        if st.button("📊 Calculate EMI", type="primary", use_container_width=True):
            try:
                emi, total_payment, total_interest = calculate_emi(loan_amount, annual_rate, loan_tenure_years)
                
                st.success("✅ EMI Calculation Complete!")
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Monthly EMI",
                        value=f"${emi:,.2f}"
                    )
                
                with col2:
                    st.metric(
                        label="Total Payment",
                        value=f"${total_payment:,.2f}"
                    )
                
                with col3:
                    st.metric(
                        label="Total Interest",
                        value=f"${total_interest:,.2f}"
                    )
                
                # EMI Breakdown Chart
                st.subheader("📈 Payment Breakdown")
                
                # Create amortization schedule
                months = loan_tenure_years * 12
                monthly_rate = annual_rate / 1200
                balance = loan_amount
                
                schedule_data = []
                for month in range(1, months + 1):
                    interest_payment = balance * monthly_rate
                    principal_payment = emi - interest_payment
                    balance -= principal_payment
                    
                    schedule_data.append({
                        'Month': month,
                        'Principal': principal_payment,
                        'Interest': interest_payment,
                        'Balance': max(0, balance)
                    })
                
                df = pd.DataFrame(schedule_data)
                
                # Cumulative interest vs principal chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df['Month'],
                    y=df['Principal'].cumsum(),
                    mode='lines',
                    name='Cumulative Principal',
                    line=dict(color='green')
                ))
                
                fig.add_trace(go.Scatter(
                    x=df['Month'],
                    y=df['Interest'].cumsum(),
                    mode='lines',
                    name='Cumulative Interest',
                    line=dict(color='red')
                ))
                
                fig.update_layout(
                    title="Cumulative Principal vs Interest Payments",
                    xaxis_title="Month",
                    yaxis_title="Amount ($)",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error calculating EMI: {str(e)}")

def show_investment_calculator():
    st.subheader("💰 Investment Growth Calculator")
    st.markdown("Calculate how your investments will grow over time with compound interest.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        principal = st.number_input(
            "Initial Investment ($):",
            min_value=100,
            max_value=10000000,
            value=10000,
            step=100,
            format="%d"
        )
        
        monthly_contribution = st.number_input(
            "Monthly Contribution ($):",
            min_value=0,
            max_value=100000,
            value=500,
            step=50,
            format="%d"
        )
        
        annual_return = st.number_input(
            "Expected Annual Return (%):",
            min_value=0.1,
            max_value=50.0,
            value=8.0,
            step=0.1,
            format="%.1f"
        )
        
        investment_years = st.number_input(
            "Investment Period (Years):",
            min_value=1,
            max_value=50,
            value=20,
            step=1
        )
    
    with col2:
        if st.button("📈 Calculate Growth", type="primary", use_container_width=True):
            try:
                final_amount, total_invested, total_returns = calculate_compound_interest(
                    principal, monthly_contribution, annual_return, investment_years
                )
                
                st.success("✅ Investment Growth Calculated!")
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Final Amount",
                        value=f"${final_amount:,.2f}"
                    )
                
                with col2:
                    st.metric(
                        label="Total Invested",
                        value=f"${total_invested:,.2f}"
                    )
                
                with col3:
                    st.metric(
                        label="Total Returns",
                        value=f"${total_returns:,.2f}",
                        delta=f"{(total_returns/total_invested)*100:.1f}% gain"
                    )
                
                # Investment growth chart
                st.subheader("📊 Investment Growth Over Time")
                
                months = investment_years * 12
                monthly_rate = annual_return / 1200
                
                growth_data = []
                current_amount = principal
                total_contributions = principal
                
                for month in range(1, months + 1):
                    current_amount = current_amount * (1 + monthly_rate) + monthly_contribution
                    total_contributions += monthly_contribution
                    
                    growth_data.append({
                        'Year': month / 12,
                        'Investment Value': current_amount,
                        'Total Contributions': total_contributions,
                        'Returns': current_amount - total_contributions
                    })
                
                df = pd.DataFrame(growth_data)
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df['Year'],
                    y=df['Total Contributions'],
                    mode='lines',
                    name='Total Contributions',
                    line=dict(color='blue')
                ))
                
                fig.add_trace(go.Scatter(
                    x=df['Year'],
                    y=df['Investment Value'],
                    mode='lines',
                    name='Investment Value',
                    line=dict(color='green')
                ))
                
                fig.update_layout(
                    title="Investment Growth Projection",
                    xaxis_title="Years",
                    yaxis_title="Amount ($)",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error calculating investment growth: {str(e)}")

def show_tax_calculator():
    st.subheader("🧾 Tax Calculator")
    st.markdown("Calculate your estimated income tax based on your annual income and deductions.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        annual_income = st.number_input(
            "Annual Gross Income ($):",
            min_value=0,
            max_value=10000000,
            value=75000,
            step=1000,
            format="%d"
        )
        
        filing_status = st.selectbox(
            "Filing Status:",
            ["Single", "Married Filing Jointly", "Married Filing Separately", "Head of Household"]
        )
        
        standard_deduction = st.number_input(
            "Standard Deduction ($):",
            min_value=0,
            max_value=50000,
            value=12950,  # 2023 standard deduction for single filers
            step=50,
            format="%d"
        )
        
        other_deductions = st.number_input(
            "Other Deductions ($):",
            min_value=0,
            max_value=100000,
            value=0,
            step=100,
            format="%d"
        )
    
    with col2:
        if st.button("🧮 Calculate Tax", type="primary", use_container_width=True):
            try:
                tax_info = calculate_tax(annual_income, filing_status, standard_deduction, other_deductions)
                
                st.success("✅ Tax Calculation Complete!")
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Taxable Income",
                        value=f"${tax_info['taxable_income']:,.2f}"
                    )
                
                with col2:
                    st.metric(
                        label="Federal Tax",
                        value=f"${tax_info['federal_tax']:,.2f}"
                    )
                
                with col3:
                    st.metric(
                        label="After-Tax Income",
                        value=f"${tax_info['after_tax_income']:,.2f}"
                    )
                
                # Tax breakdown
                st.subheader("📊 Tax Breakdown")
                
                breakdown_data = {
                    'Category': ['After-Tax Income', 'Federal Tax', 'Total Deductions'],
                    'Amount': [
                        tax_info['after_tax_income'],
                        tax_info['federal_tax'],
                        tax_info['total_deductions']
                    ]
                }
                
                fig = px.pie(
                    values=breakdown_data['Amount'],
                    names=breakdown_data['Category'],
                    title="Income Distribution"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Effective tax rate
                effective_rate = (tax_info['federal_tax'] / annual_income) * 100
                st.info(f"📈 Your effective tax rate is **{effective_rate:.2f}%**")
                
            except Exception as e:
                st.error(f"❌ Error calculating tax: {str(e)}")
    
    # Tax tips
    st.divider()
    st.subheader("💡 Tax Planning Tips")
    
    tips = [
        "🏠 Consider maximizing deductions like mortgage interest and charitable contributions",
        "💼 Contribute to retirement accounts (401k, IRA) to reduce taxable income",
        "📋 Keep detailed records of all tax-deductible expenses",
        "🎓 Take advantage of education tax credits if applicable",
        "💰 Consider tax-loss harvesting for investment accounts"
    ]
    
    for tip in tips:
        st.markdown(f"- {tip}")
    
    st.caption("**Disclaimer:** This calculator provides estimates only. Consult a tax professional for accurate tax planning.")
