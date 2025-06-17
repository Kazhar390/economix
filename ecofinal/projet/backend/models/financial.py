import numpy as np
import numpy_financial as npf
from typing import List, Dict

def financial_analysis(project_data: dict) -> dict:
    """
    Comprehensive financial analysis including:
    - ROI, NPV, IRR, Payback Period
    - Break-even analysis
    """
    initial_investment = project_data['initial_investment']
    yearly_cashflows = project_data['yearly_cashflows']
    discount_rate = project_data.get('discount_rate', 0.1)
    years = len(yearly_cashflows)
    
    # Basic calculations
    cumulative_cashflow = np.cumsum(yearly_cashflows)
    total_return = sum(yearly_cashflows)
    
    # ROI
    roi = ((total_return - initial_investment) / initial_investment) * 100
    
    # NPV
    npv = npf.npv(discount_rate, [-initial_investment] + yearly_cashflows)
    
    # IRR
    irr = npf.irr([-initial_investment] + yearly_cashflows)
    
    # Payback Period
    payback_period = None
    for i, val in enumerate(cumulative_cashflow):
        if val >= initial_investment:
            payback_period = i + (initial_investment - cumulative_cashflow[i-1]) / yearly_cashflows[i]
            break
    
    # Break-even analysis
    fixed_costs = project_data.get('fixed_costs', initial_investment * 0.3)
    variable_costs = project_data.get('variable_costs', sum(yearly_cashflows) * 0.4)
    unit_price = project_data.get('unit_price', 1)
    units_sold = project_data.get('units_sold', sum(yearly_cashflows)/unit_price)
    
    break_even_units = fixed_costs / (unit_price - variable_costs/units_sold)
    
    return {
        'roi': round(roi, 2),
        'npv': round(npv, 2),
        'irr': round(irr * 100, 2) if irr else None,  # as percentage
        'payback_period': round(payback_period, 2) if payback_period else None,
        'break_even_units': round(break_even_units, 2),
        'total_return': round(total_return, 2),
        'cumulative_cashflows': [round(x, 2) for x in cumulative_cashflow]
    }