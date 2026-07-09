import inspect

import factor_analyzer.factor_analyzer as factor_analyzer_module
import numpy as np
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


def calculate_eigenvalues(dataframe):
    """Tính trị riêng của ma trận tương quan theo thứ tự giảm dần."""
    correlation = dataframe.corr().to_numpy()
    if not np.isfinite(correlation).all():
        raise ValueError(
            "Unable to calculate eigenvalues because the data contains "
            "a column with no variance."
        )
    eigenvalues = np.linalg.eigvalsh(correlation)[::-1]
    return np.where(np.abs(eigenvalues) < 1e-12, 0.0, eigenvalues)


def determine_num_factors(dataframe):
    """Chọn toàn bộ nhân tố có trị riêng lớn hơn 1 (tiêu chuẩn Kaiser)."""
    eigenvalues = calculate_eigenvalues(dataframe)
    selected_count = int(sum(eigenvalue > 1 for eigenvalue in eigenvalues))
    if selected_count == 0:
        raise ValueError(
            "No eigenvalue is greater than 1, so the Kaiser criterion "
            "cannot select a factor. Please enter the number of factors manually."
        )
    return selected_count


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
    if n_factors > dataframe.shape[1]:
        raise ValueError(
            f"The number of factors ({n_factors}) cannot exceed the number "
            f"of variables ({dataframe.shape[1]})."
        )
    if not 0 <= threshold <= 1:
        raise ValueError("The loading threshold must be between 0 and 1.")

    analyzer = FactorAnalyzer(
        n_factors=n_factors,
        rotation=rotation,
        method=method,
        use_smc=False,
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
