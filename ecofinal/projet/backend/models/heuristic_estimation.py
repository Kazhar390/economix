import numpy as np
from typing import List, Dict

def expert_judgment_estimation(estimates: List[Dict]) -> Dict:
    """
    Calcule l'estimation basée sur le jugement d'expert
    
    Paramètres:
    - estimates: Liste des estimations d'experts, chaque estimation contient:
      - expert_name: Nom de l'expert
      - confidence: Niveau de confiance (1-10)
      - estimate: Valeur estimée (heures, coûts, etc.)
    
    Retourne:
    - Statistiques sur les estimations (moyenne, médiane, min, max, etc.)
    - Estimation pondérée par le niveau de confiance
    """
    if not estimates:
        return {"error": "Aucune estimation fournie"}
    
    # Extraire les valeurs
    values = [e["estimate"] for e in estimates]
    confidences = [e["confidence"] for e in estimates]
    
    # Calculs de base
    mean_value = np.mean(values)
    median_value = np.median(values)
    min_value = min(values)
    max_value = max(values)
    std_dev = np.std(values)
    
    # Estimation pondérée par la confiance
    weighted_estimate = sum(e["estimate"] * e["confidence"] for e in estimates) / sum(confidences)
    
    return {
        "estimates": estimates,
        "statistics": {
            "mean": round(mean_value, 2),
            "median": round(median_value, 2),
            "min": round(min_value, 2),
            "max": round(max_value, 2),
            "std_dev": round(std_dev, 2),
            "range": round(max_value - min_value, 2)
        },
        "weighted_estimate": round(weighted_estimate, 2)
    }

def delphi_method_estimation(rounds: List[List[Dict]]) -> Dict:
    """
    Implémente la méthode Delphi pour l'estimation
    
    Paramètres:
    - rounds: Liste des tours d'estimation, chaque tour contient une liste d'estimations d'experts
    
    Retourne:
    - Résultats de chaque tour
    - Convergence des estimations
    - Estimation finale
    """
    if not rounds:
        return {"error": "Aucun tour d'estimation fourni"}
    
    results = []
    convergence = []
    
    # Analyser chaque tour
    for i, round_estimates in enumerate(rounds):
        round_result = expert_judgment_estimation(round_estimates)
        results.append(round_result)
        
        # Calculer la convergence (réduction de l'écart-type)
        if i > 0:
            prev_std = results[i-1]["statistics"]["std_dev"]
            curr_std = round_result["statistics"]["std_dev"]
            std_reduction = (prev_std - curr_std) / prev_std if prev_std > 0 else 0
            convergence.append(round(std_reduction * 100, 2))  # en pourcentage
    
    # Estimation finale (dernier tour)
    final_estimate = results[-1]["weighted_estimate"]
    
    return {
        "rounds": results,
        "convergence": convergence,
        "final_estimate": final_estimate,
        "consensus_reached": len(convergence) > 0 and convergence[-1] >= 10  # Consensus si réduction > 10%
    }