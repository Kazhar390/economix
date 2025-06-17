def calculate_function_points(inputs: dict) -> dict:
    """
    Calculate function points based on user inputs
    Inputs should contain:
    - external_inputs: Low/Average/High counts
    - external_outputs: Low/Average/High counts
    - external_inquiries: Low/Average/High counts
    - internal_files: Low/Average/High counts
    - external_interfaces: Low/Average/High counts
    - adjustment_factors: List of 14 GSCs (0-5)
    """
    # Weight factors
    weights = {
        'external_inputs': {'low': 3, 'average': 4, 'high': 6},
        'external_outputs': {'low': 4, 'average': 5, 'high': 7},
        'external_inquiries': {'low': 3, 'average': 4, 'high': 6},
        'internal_files': {'low': 7, 'average': 10, 'high': 15},
        'external_interfaces': {'low': 5, 'average': 7, 'high': 10}
    }
    
    # Calculate Unadjusted Function Points (UFP)
    ufp = 0
    for key in weights:
        for complexity in ['low', 'average', 'high']:
            count = inputs.get(key, {}).get(complexity, 0)
            ufp += count * weights[key][complexity]
    
    # Calculate Value Adjustment Factor (VAF)
    adjustment_factors = inputs.get('adjustment_factors', [0]*14)
    vaf = 0.65 + (sum(adjustment_factors) * 0.01)
    
    # Final Adjusted Function Points
    afp = ufp * vaf
    
    # Convert to LOC (optional)
    language = inputs.get('language', 'java')
    loc_per_fp = {
        'c': 110, 'java': 55, 'python': 30, 
        'c++': 55, 'javascript': 40, 'php': 40
    }
    loc = afp * loc_per_fp.get(language, 50)
    
    return {
        'ufp': round(ufp, 2),
        'afp': round(afp, 2),
        'vaf': round(vaf, 2),
        'loc_estimate': round(loc, 2),
        'language': language
    }