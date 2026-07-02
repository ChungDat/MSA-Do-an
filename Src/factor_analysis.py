import pandas as pd
import numpy as np
from factor_analyzer import FactorAnalyzer

def determine_num_factors(df):
    """
    Determine the number of factors based on Kaiser criterion (Eigenvalue > 1).
    """
    fa = FactorAnalyzer(n_factors=df.shape[1], rotation=None)
    fa.fit(df)
    ev, _ = fa.get_eigenvalues()
    num_factors = sum(ev > 1)
    if num_factors == 0:
        return 1 # Fallback if no eigenvalue is > 1
    return num_factors

def perform_factor_analysis(df, feature_names, n_factors=None, threshold=0.4, rotation='varimax', method='minres'):
    """
    Perform Factor Analysis and return groupings of features.
    
    Args:
        df (pd.DataFrame): The standardized data.
        feature_names (list): List of feature names.
        n_factors (int): Number of factors to extract. If None, uses Eigenvalue > 1.
        threshold (float): Factor loading threshold.
        rotation (str): Rotation method (e.g., 'varimax', 'promax').
        method (str): Extraction method (e.g., 'minres', 'ml').
        
    Returns:
        tuple: (factor_groupings, n_factors)
               factor_groupings is a dict where keys are factor indices (e.g., "Factor_1") 
               and values are lists of dicts containing feature names and their loadings.
    """
    if n_factors is None or n_factors <= 0:
        n_factors = determine_num_factors(df)
        
    fa = FactorAnalyzer(n_factors=n_factors, rotation=rotation, method=method)
    fa.fit(df)
    
    loadings = fa.loadings_
    
    factor_groupings = {}
    for i in range(n_factors):
        factor_name = f"Factor_{i+1}"
        factor_groupings[factor_name] = []
        
        for j in range(len(feature_names)):
            loading = loadings[j, i]
            if abs(loading) >= threshold:
                factor_groupings[factor_name].append({
                    "feature": feature_names[j],
                    "loading": float(loading)
                })
                
        # Sort by absolute loading in descending order
        factor_groupings[factor_name].sort(key=lambda x: abs(x["loading"]), reverse=True)
        
    return factor_groupings, n_factors
