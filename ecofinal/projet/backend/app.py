# --------------------------
# 1. IMPORTS
# --------------------------
from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import numpy as np
import numpy_financial as npf
import random
from typing import List, Dict

# Importer le nouveau module
from models.heuristic_estimation import expert_judgment_estimation, delphi_method_estimation

# --------------------------
# 2. APP CONFIGURATION
# --------------------------
app = Flask(__name__)
CORS(app)

# --------------------------
# 3. CORE CALCULATION FUNCTIONS
# --------------------------
def cocomo_advanced(loc: float, mode: str = "organic") -> Dict:
    """Calculate COCOMO metrics"""
    coefficients = {
        "organic": {"a": 2.4, "b": 1.05, "c": 2.5, "d": 0.38},
        "semi-detached": {"a": 3.0, "b": 1.12, "c": 2.5, "d": 0.35},
        "embedded": {"a": 3.6, "b": 1.20, "c": 2.5, "d": 0.32}
    }
    
    coeff = coefficients.get(mode, coefficients["organic"])
    effort = coeff["a"] * math.pow(loc / 1000, coeff["b"])
    time = coeff["c"] * math.pow(effort, coeff["d"])
    staff = effort / time
    
    return {
        "effort": round(effort, 2),
        "time": round(time, 2),
        "staff": round(staff, 2),
        "unit": {"effort": "person-months", "time": "months", "staff": "persons"}
    }

def calculate_function_points(inputs: dict) -> dict:
    """Calculate function points metrics"""
    defaults = {
        'external_inputs': {'low': 0, 'average': 0, 'high': 0},
        'external_outputs': {'low': 0, 'average': 0, 'high': 0},
        'external_inquiries': {'low': 0, 'average': 0, 'high': 0},
        'internal_files': {'low': 0, 'average': 0, 'high': 0},
        'external_interfaces': {'low': 0, 'average': 0, 'high': 0},
        'adjustment_factors': [0]*14,
        'language': 'java'
    }
    params = {**defaults, **inputs}
    
    weights = {
        'external_inputs': {'low': 3, 'average': 4, 'high': 6},
        'external_outputs': {'low': 4, 'average': 5, 'high': 7},
        'external_inquiries': {'low': 3, 'average': 4, 'high': 6},
        'internal_files': {'low': 7, 'average': 10, 'high': 15},
        'external_interfaces': {'low': 5, 'average': 7, 'high': 10}
    }
    
    ufp = sum(
        count * weights[key][complexity]
        for key in weights
        for complexity, count in params[key].items()
    )
    
    vaf = 0.65 + (sum(params['adjustment_factors']) * 0.01)
    afp = ufp * vaf
    
    loc_per_fp = {'c': 110, 'java': 55, 'python': 30, 'c++': 55, 'javascript': 40}
    loc = afp * loc_per_fp.get(params['language'], 50)
    
    return {
        'ufp': round(ufp, 2),
        'afp': round(afp, 2),
        'vaf': round(vaf, 2),
        'loc_estimate': round(loc, 2),
        'language': params['language']
    }

def financial_analysis(project_data: dict) -> dict:
    """Perform complete financial analysis"""
    cashflows = project_data['cashflows']
    rate = project_data.get('rate', 0.1)
    investment = project_data['investment']
    
    npv = round(npf.npv(rate, [-investment] + cashflows), 2)
    irr = round(npf.irr([-investment] + cashflows) * 100, 2) if any(c > 0 for c in cashflows) else None
    # Supprimer cette ligne avec la parenthèse supplémentaire
    # roi = round(((sum(cashflows) - investment) / investment * 100, 2))
    
    # Garder uniquement cette ligne corrigée
    roi = round((sum(cashflows) - investment) / investment * 100, 2)
    
    cumulative = np.cumsum(cashflows).tolist()
    
    # Calcul amélioré de la période de récupération
    payback = None
    
    # Cas 1: Si un des flux cumulés dépasse l'investissement (cas standard)
    for i in range(len(cumulative)):
        if cumulative[i] >= investment:
            # Interpolation linéaire pour trouver le point exact
            if i == 0:
                payback = i + (investment / cumulative[i])
            else:
                payback = i + (investment - cumulative[i-1]) / (cumulative[i] - cumulative[i-1])
            break
    
    # Cas 2: Si aucun flux cumulé ne dépasse l'investissement, mais la tendance est positive
    if payback is None and len(cumulative) >= 2:
        # Vérifier si les flux augmentent
        last_flows = cumulative[-2:]
        if last_flows[1] > last_flows[0]:
            # Calculer le taux de croissance moyen des derniers flux
            growth_rate = (last_flows[1] - last_flows[0])
            # Estimer combien d'années supplémentaires seraient nécessaires
            remaining_to_recover = investment - last_flows[1]
            if growth_rate > 0:  # Éviter division par zéro
                additional_years = remaining_to_recover / growth_rate
                payback = len(cumulative) + additional_years
    
    return {
        'npv': npv,
        'irr': irr,
        'roi': roi,
        'payback': round(payback, 2) if payback else None,
        'cumulative': [round(x, 2) for x in cumulative]
    }

# --------------------------
# 4. API ENDPOINTS
# --------------------------
@app.route('/api/estimate/cocomo', methods=['POST'])
def handle_cocomo():
    data = request.get_json()
    try:
        result = cocomo_advanced(float(data['loc']), data.get('mode', 'organic'))
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/estimate/function-points', methods=['POST'])
def handle_function_points():
    data = request.get_json()
    try:
        result = calculate_function_points(data)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/financial/analysis', methods=['POST'])
def handle_financial():
    data = request.get_json()
    try:
        result = financial_analysis({
            'investment': float(data['investment']),
            'cashflows': [float(x) for x in data['cashflows']],
            'rate': float(data.get('rate', 0.1))
        })
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "1.0.0"})

# Ajouter les routes Expert Judgment et Delphi ici, AVANT le bloc if __name__
@app.route('/api/estimate/expert-judgment', methods=['POST', 'OPTIONS'])
def api_expert_judgment():
    if request.method == 'OPTIONS':
        # Gérer les requêtes OPTIONS pour CORS
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
        
    data = request.json
    if not data or 'estimates' not in data:
        return jsonify({'success': False, 'error': 'Données manquantes'})
    
    result = expert_judgment_estimation(data['estimates'])
    return jsonify({'success': True, 'data': result})

@app.route('/api/estimate/delphi', methods=['POST', 'OPTIONS'])
def api_delphi_method():
    if request.method == 'OPTIONS':
        # Gérer les requêtes OPTIONS pour CORS
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
        
    data = request.json
    if not data or 'rounds' not in data:
        return jsonify({'success': False, 'error': 'Données manquantes'})
    
    result = delphi_method_estimation(data['rounds'])
    return jsonify({'success': True, 'data': result})

# --------------------------
# 5. MAIN EXECUTION
# --------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# Supprimer ou commenter les anciennes définitions de routes qui sont après le bloc if __name__