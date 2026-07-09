import argparse
import json

from .data_processor import load_and_preprocess_data
from .factor_analysis import perform_factor_analysis
from .llm_namer import name_all_factors


def build_parser():
    parser = argparse.ArgumentParser(
        description="Factor Analysis and LLM Naming App."
    )
    parser.add_argument("input_file", help="Path to the input CSV file.")
    parser.add_argument("-f", "--factors", type=int, default=0)
    parser.add_argument("-t", "--threshold", type=float, default=0.4)
    parser.add_argument("-r", "--rotation", default="varimax")
    parser.add_argument("-m", "--method", default="minres")
    parser.add_argument("-o", "--output", default="results.json")
    return parser


def main():
    args = build_parser().parse_args()
    dataframe, feature_names = load_and_preprocess_data(args.input_file)
    factor_groupings, extracted = perform_factor_analysis(
        dataframe,
        feature_names,
        args.factors or None,
        args.threshold,
        args.rotation,
        args.method,
    )
    print(f"Extracted {extracted} factors.")
    results = name_all_factors(factor_groupings)

    with open(args.output, "w", encoding="utf-8") as output_file:
        json.dump(results, output_file, ensure_ascii=False, indent=4)
    print(f"Saved results to: {args.output}")


if __name__ == "__main__":
    main()
