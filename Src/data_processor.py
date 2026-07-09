import pandas as pd
from sklearn.preprocessing import StandardScaler


def load_numeric_data(file_path):
    """Đọc CSV và kiểm tra dữ liệu chỉ gồm các giá trị số hợp lệ."""
    try:
        dataframe = pd.read_csv(file_path)
    except Exception as exc:
        raise ValueError(f"Unable to read file {file_path}. Error: {exc}") from exc

    if dataframe.empty:
        raise ValueError("The CSV file does not contain any data.")

    if dataframe.isnull().values.any():
        raise ValueError(
            "The data contains missing values (NaN). "
            "Please clean the data before continuing."
        )

    non_numeric_columns = dataframe.select_dtypes(exclude=["number"]).columns
    if len(non_numeric_columns) > 0:
        raise ValueError(
            f"The data contains non-numeric columns: {list(non_numeric_columns)}. "
            "Please convert them to numbers before continuing."
        )

    return dataframe


def load_and_preprocess_data(file_path):
    """Đọc, kiểm tra và chuẩn hóa dữ liệu số từ CSV."""
    dataframe = load_numeric_data(file_path)
    feature_names = dataframe.columns.tolist()
    scaled_data = StandardScaler().fit_transform(dataframe)
    return pd.DataFrame(scaled_data, columns=feature_names), feature_names


def calculate_descriptive_statistics(file_path):
    """Tính các đại lượng mô tả và ma trận hiệp phương sai mẫu."""
    dataframe = load_numeric_data(file_path)
    summary = pd.DataFrame(
        {
            "Min": dataframe.min(),
            "Max": dataframe.max(),
            "Mean": dataframe.mean(),
            "Variance": dataframe.var(ddof=1),
        }
    )
    return summary, dataframe.cov(ddof=1)
