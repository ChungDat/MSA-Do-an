import inspect

import factor_analyzer.factor_analyzer as factor_analyzer_module
from factor_analyzer import FactorAnalyzer
from sklearn.utils import validation as sklearn_validation


# factor-analyzer 0.5.1 still passes the old keyword removed by newer sklearn.
if "force_all_finite" not in inspect.signature(sklearn_validation.check_array).parameters:
    _check_array = sklearn_validation.check_array

    def _check_array_compat(
        *args, force_all_finite=True, ensure_all_finite=None, **kwargs
    ):
        if ensure_all_finite is None:
            ensure_all_finite = force_all_finite
        return _check_array(
            *args, ensure_all_finite=ensure_all_finite, **kwargs
        )

    sklearn_validation.check_array = _check_array_compat
    factor_analyzer_module.check_array = _check_array_compat


def determine_num_factors(dataframe):
    """Xác định số nhân tố theo tiêu chuẩn Kaiser (eigenvalue > 1)."""
    analyzer = FactorAnalyzer(n_factors=dataframe.shape[1], rotation=None)
    analyzer.fit(dataframe)
    eigenvalues, _ = analyzer.get_eigenvalues()
    return max(1, int(sum(eigenvalues > 1)))


def perform_factor_analysis(
    dataframe,
    feature_names,
    n_factors=None,
    threshold=0.4,
    rotation="varimax",
    method="minres",
):
    """Phân tích nhân tố và nhóm các biến vượt ngưỡng hệ số tải."""
    if n_factors is None or n_factors <= 0:
        n_factors = determine_num_factors(dataframe)

    analyzer = FactorAnalyzer(
        n_factors=n_factors, rotation=rotation, method=method
    )
    analyzer.fit(dataframe)

    factor_groupings = {}
    for factor_index in range(n_factors):
        factor_name = f"Factor_{factor_index + 1}"
        features = [
            {"feature": feature, "loading": float(analyzer.loadings_[index, factor_index])}
            for index, feature in enumerate(feature_names)
            if abs(analyzer.loadings_[index, factor_index]) >= threshold
        ]
        factor_groupings[factor_name] = sorted(
            features, key=lambda item: abs(item["loading"]), reverse=True
        )

    return factor_groupings, n_factors
