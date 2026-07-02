import pandas as pd
from sklearn.preprocessing import StandardScaler

def load_and_preprocess_data(file_path):
    """
    Load data from a CSV file, check for missing values, and standardize it.
    
    Args:
        file_path (str): The path to the CSV file.
        
    Returns:
        tuple: (pandas.DataFrame containing standardized data, list of column names)
        
    Raises:
        ValueError: If the file contains missing values or is not numeric.
    """
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Không thể đọc file {file_path}. Lỗi: {e}")
        
    if df.isnull().values.any():
        raise ValueError("Dữ liệu chứa giá trị thiếu (Missing values/NaN). Vui lòng làm sạch dữ liệu trước khi tiếp tục.")
        
    # Check if all columns are numeric
    non_numeric_cols = df.select_dtypes(exclude=['number']).columns
    if len(non_numeric_cols) > 0:
        raise ValueError(f"Dữ liệu chứa các cột không phải số: {list(non_numeric_cols)}. Cần chuyển đổi thành số trước.")
        
    feature_names = df.columns.tolist()
    
    # Standardize data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df)
    
    # Convert back to DataFrame to keep the format
    df_scaled = pd.DataFrame(scaled_data, columns=feature_names)
    
    return df_scaled, feature_names
