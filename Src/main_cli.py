import argparse
import json
import sys
from data_processor import load_and_preprocess_data
from factor_analysis import perform_factor_analysis
from llm_namer import name_all_factors

def main():
    parser = argparse.ArgumentParser(description="Factor Analysis and LLM Naming App.")
    parser.add_argument("input_file", help="Path to the CSV data file.")
    parser.add_argument("-f", "--factors", type=int, default=0, help="Number of factors to extract. Leave empty to auto-determine (Eigenvalue > 1).")
    parser.add_argument("-t", "--threshold", type=float, default=0.4, help="Factor loading threshold. Default is 0.4.")
    parser.add_argument("-r", "--rotation", type=str, default="varimax", help="Rotation method (default: varimax).")
    parser.add_argument("-m", "--method", type=str, default="minres", help="Factor extraction method (default: minres).")
    parser.add_argument("-o", "--output", type=str, default="results.json", help="Output JSON file name.")
    
    args = parser.parse_args()
    
    print(f"--- STARTING ANALYSIS ---")
    print(f"Reading data from: {args.input_file}")
    
    # 1. Read and preprocess data
    try:
        df_scaled, feature_names = load_and_preprocess_data(args.input_file)
        print(f"Successfully loaded {df_scaled.shape[0]} rows and {df_scaled.shape[1]} features.")
    except Exception as e:
        print(f"[ERROR]: {e}")
        sys.exit(1)
        
    # 2. Factor Analysis
    print(f"Performing factor analysis (rotation='{args.rotation}', method='{args.method}')...")
    try:
        n_factors_arg = args.factors if args.factors > 0 else None
        factor_groupings, n_factors_extracted = perform_factor_analysis(
            df=df_scaled, 
            feature_names=feature_names, 
            n_factors=n_factors_arg, 
            threshold=args.threshold,
            rotation=args.rotation,
            method=args.method
        )
        print(f"Successfully extracted {n_factors_extracted} factors.")
    except Exception as e:
        print(f"[ERROR]: Could not perform factor analysis. Error: {e}")
        sys.exit(1)
        
    # 3. Call LLM for naming
    print("Calling LLM to name the factors...")
    named_factors = name_all_factors(factor_groupings)
    
    # 4. Print results and save
    print("\n--- ANALYSIS RESULTS ---")
    for original_name, data in named_factors.items():
        print(f"\n[{original_name}] -> New Name: {data['llm_name']}")
        print(f"Explanation: {data['explanation']}")
        print("Component features:")
        for feature in data['features']:
            print(f"  - {feature['feature']} (Loading: {feature['loading']:.4f})")
            
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(named_factors, f, ensure_ascii=False, indent=4)
        print(f"\nSuccessfully saved all results to file: {args.output}")
    except Exception as e:
        print(f"[ERROR]: Cannot save results. Error: {e}")

if __name__ == "__main__":
    main()
