import numpy as np
import pandas as pd

def calculate_emi(principal, annual_rate, tenure_years):
    """
    Calculate EMI (Equated Monthly Installment) for a loan
    
    Args:
        principal (float): Loan amount
        annual_rate (float): Annual interest rate as percentage
        tenure_years (int): Loan tenure in years
    
    Returns:
        tuple: (emi, total_payment, total_interest)
    """
    try:
        # Convert annual rate to monthly rate
        monthly_rate = annual_rate / (12 * 100)
        
        # Total number of months
        total_months = tenure_years * 12
        
        if monthly_rate == 0:
            # If no interest rate
            emi = principal / total_months
        else:
            # EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
            emi = principal * monthly_rate * (1 + monthly_rate) ** total_months / \
                  ((1 + monthly_rate) ** total_months - 1)
        
        total_payment = emi * total_months
        total_interest = total_payment - principal
        
        return round(emi, 2), round(total_payment, 2), round(total_interest, 2)
        
    except Exception as e:
        raise ValueError(f"Error calculating EMI: {str(e)}")

def calculate_compound_interest(principal, monthly_contribution, annual_return, years):
    """
    Calculate compound interest with monthly contributions
    
    Args:
        principal (float): Initial investment amount
        monthly_contribution (float): Monthly contribution amount
        annual_return (float): Expected annual return as percentage
        years (int): Investment period in years
    
    Returns:
        tuple: (final_amount, total_invested, total_returns)
    """
    try:
        # Convert annual return to monthly rate
        monthly_rate = annual_return / (12 * 100)
        
        # Total number of months
        total_months = years * 12
        
        # Calculate future value with monthly contributions
        current_amount = principal
        total_invested = principal
        
        for month in range(total_months):
            # Apply monthly interest
            current_amount = current_amount * (1 + monthly_rate)
            
            # Add monthly contribution
            current_amount += monthly_contribution
            total_invested += monthly_contribution
        
        total_returns = current_amount - total_invested
        
        return round(current_amount, 2), round(total_invested, 2), round(total_returns, 2)
        
    except Exception as e:
        raise ValueError(f"Error calculating compound interest: {str(e)}")

def calculate_simple_interest(principal, rate, time):
    """
    Calculate simple interest
    
    Args:
        principal (float): Principal amount
        rate (float): Annual interest rate as percentage
        time (float): Time period in years
    
    Returns:
        tuple: (simple_interest, total_amount)
    """
    try:
        simple_interest = (principal * rate * time) / 100
        total_amount = principal + simple_interest
        
        return round(simple_interest, 2), round(total_amount, 2)
        
    except Exception as e:
        raise ValueError(f"Error calculating simple interest: {str(e)}")

def calculate_tax(annual_income, filing_status, standard_deduction, other_deductions):
    """
    Calculate federal income tax (simplified US tax calculation)
    
    Args:
        annual_income (float): Annual gross income
        filing_status (str): Filing status
        standard_deduction (float): Standard deduction amount
        other_deductions (float): Other deductions
    
    Returns:
        dict: Tax calculation details
    """
    try:
        # Calculate total deductions
        total_deductions = standard_deduction + other_deductions
        
        # Calculate taxable income
        taxable_income = max(0, annual_income - total_deductions)
        
        # 2023 Tax brackets (simplified for single filers)
        tax_brackets = [
            (10275, 0.10),      # 10% up to $10,275
            (41775, 0.12),      # 12% from $10,276 to $41,775
            (89450, 0.22),      # 22% from $41,776 to $89,450
            (190750, 0.24),     # 24% from $89,451 to $190,750
            (364200, 0.32),     # 32% from $190,751 to $364,200
            (462550, 0.35),     # 35% from $364,201 to $462,550
            (float('inf'), 0.37) # 37% above $462,550
        ]
        
        # Adjust brackets based on filing status
        if filing_status == "Married Filing Jointly":
            # Double the brackets for married filing jointly
            tax_brackets = [(limit * 2 if limit != float('inf') else limit, rate) 
                          for limit, rate in tax_brackets]
        
        # Calculate federal tax
        federal_tax = 0
        remaining_income = taxable_income
        previous_limit = 0
        
        for limit, rate in tax_brackets:
            if remaining_income <= 0:
                break
            
            taxable_at_bracket = min(remaining_income, limit - previous_limit)
            federal_tax += taxable_at_bracket * rate
            remaining_income -= taxable_at_bracket
            previous_limit = limit
            
            if remaining_income <= 0:
                break
        
        # Calculate after-tax income
        after_tax_income = annual_income - federal_tax
        
        # Calculate effective tax rate
        effective_rate = (federal_tax / annual_income * 100) if annual_income > 0 else 0
        
        return {
            'annual_income': round(annual_income, 2),
            'total_deductions': round(total_deductions, 2),
            'taxable_income': round(taxable_income, 2),
            'federal_tax': round(federal_tax, 2),
            'after_tax_income': round(after_tax_income, 2),
            'effective_rate': round(effective_rate, 2)
        }
        
    except Exception as e:
        raise ValueError(f"Error calculating tax: {str(e)}")

def calculate_retirement_savings(current_age, retirement_age, current_savings, monthly_contribution, annual_return):
    """
    Calculate retirement savings projection
    
    Args:
        current_age (int): Current age
        retirement_age (int): Target retirement age
        current_savings (float): Current retirement savings
        monthly_contribution (float): Monthly contribution
        annual_return (float): Expected annual return as percentage
    
    Returns:
        dict: Retirement calculation details
    """
    try:
        years_to_retirement = retirement_age - current_age
        
        if years_to_retirement <= 0:
            raise ValueError("Retirement age must be greater than current age")
        
        # Calculate future value
        final_amount, total_invested, total_returns = calculate_compound_interest(
            current_savings, monthly_contribution, annual_return, years_to_retirement
        )
        
        # Calculate required monthly withdrawal for 25 years (assuming 4% withdrawal rate)
        monthly_withdrawal = (final_amount * 0.04) / 12
        
        return {
            'years_to_retirement': years_to_retirement,
            'final_amount': final_amount,
            'total_invested': total_invested,
            'total_returns': total_returns,
            'monthly_withdrawal': round(monthly_withdrawal, 2)
        }
        
    except Exception as e:
        raise ValueError(f"Error calculating retirement savings: {str(e)}")

def calculate_mortgage_payment(home_price, down_payment, annual_rate, loan_term_years):
    """
    Calculate mortgage payment details
    
    Args:
        home_price (float): Total home price
        down_payment (float): Down payment amount
        annual_rate (float): Annual interest rate as percentage
        loan_term_years (int): Loan term in years
    
    Returns:
        dict: Mortgage calculation details
    """
    try:
        loan_amount = home_price - down_payment
        
        if loan_amount <= 0:
            raise ValueError("Down payment cannot be greater than or equal to home price")
        
        # Calculate monthly payment using EMI formula
        monthly_payment, total_payment, total_interest = calculate_emi(
            loan_amount, annual_rate, loan_term_years
        )
        
        # Calculate additional details
        down_payment_percentage = (down_payment / home_price) * 100
        
        return {
            'home_price': round(home_price, 2),
            'down_payment': round(down_payment, 2),
            'down_payment_percentage': round(down_payment_percentage, 1),
            'loan_amount': round(loan_amount, 2),
            'monthly_payment': monthly_payment,
            'total_payment': total_payment,
            'total_interest': total_interest,
            'loan_term_years': loan_term_years
        }
        
    except Exception as e:
        raise ValueError(f"Error calculating mortgage payment: {str(e)}")

def calculate_savings_goal(target_amount, current_savings, annual_return, time_period_years):
    """
    Calculate monthly savings required to reach a goal
    
    Args:
        target_amount (float): Target savings amount
        current_savings (float): Current savings amount
        annual_return (float): Expected annual return as percentage
        time_period_years (int): Time period to reach goal in years
    
    Returns:
        dict: Savings goal calculation details
    """
    try:
        remaining_amount = target_amount - current_savings
        
        if remaining_amount <= 0:
            return {
                'target_amount': round(target_amount, 2),
                'current_savings': round(current_savings, 2),
                'remaining_amount': 0,
                'monthly_savings_required': 0,
                'goal_achieved': True
            }
        
        # Convert annual return to monthly rate
        monthly_rate = annual_return / (12 * 100)
        total_months = time_period_years * 12
        
        # Future value of current savings
        future_value_current = current_savings * (1 + monthly_rate) ** total_months
        
        # Amount still needed after growth of current savings
        amount_needed = target_amount - future_value_current
        
        if amount_needed <= 0:
            monthly_savings_required = 0
        else:
            # Calculate monthly payment needed using annuity formula
            if monthly_rate == 0:
                monthly_savings_required = amount_needed / total_months
            else:
                monthly_savings_required = amount_needed * monthly_rate / \
                                         ((1 + monthly_rate) ** total_months - 1)
        
        return {
            'target_amount': round(target_amount, 2),
            'current_savings': round(current_savings, 2),
            'remaining_amount': round(remaining_amount, 2),
            'monthly_savings_required': round(monthly_savings_required, 2),
            'time_period_years': time_period_years,
            'goal_achieved': False
        }
        
    except Exception as e:
        raise ValueError(f"Error calculating savings goal: {str(e)}")
