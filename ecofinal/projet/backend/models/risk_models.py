import numpy as np
from typing import List, Dict
import random

def decision_tree_analysis(decisions: List[Dict]) -> Dict:
    """
    Analyze decisions using decision tree method
    Each decision should have:
    - name: Decision name
    - outcomes: List of possible outcomes
      - probability: Probability of outcome
      - value: Monetary value
    """
    results = []
    
    for decision in decisions:
        expected_value = sum(
            outcome['probability'] * outcome['value'] 
            for outcome in decision['outcomes']
        )
        
        # Calculate variance
        variance = sum(
            outcome['probability'] * (outcome['value'] - expected_value)**2
            for outcome in decision['outcomes']
        )
        
        results.append({
            'name': decision['name'],
            'expected_value': round(expected_value, 2),
            'variance': round(variance, 2),
            'std_deviation': round(np.sqrt(variance), 2)
        })
    
    # Find optimal decision (max expected value)
    optimal = max(results, key=lambda x: x['expected_value'])
    
    return {
        'decisions': results,
        'optimal_decision': optimal
    }

def sensitivity_analysis(base_case: dict, variations: dict) -> List[Dict]:
    """
    Perform sensitivity analysis by varying parameters
    """
    results = []
    
    for param, values in variations.items():
        for value in values:
            modified_case = base_case.copy()
            modified_case[param] = value
            
            # Here you would call your existing calculation functions
            # For example, calculate NPV with modified parameters
            npv = npf.npv(
                modified_case.get('discount_rate', 0.1),
                [-modified_case['initial_investment']] + modified_case['cashflows']
            )
            
            results.append({
                'parameter': param,
                'value': value,
                'npv': round(npv, 2),
                'deviation': round((npv - base_case['npv']) / base_case['npv'] * 100, 2)
            })
    
    return results