import pandas as pd
import numpy as np

def clean_cafe_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw cafe sales data by standardizing column names, fixing data types,
    handling missing values mathematically, and removing duplicates.
    
    Args:
        df (pd.DataFrame): The raw transaction dataframe.
        
    Returns:
        pd.DataFrame: A fully cleaned dataframe ready for downstream analysis.
    """
    # 1. Standardize invalid placeholder text to true nulls for easier handling
    df = df.replace(
        to_replace=r"(?i)^\s*(unknown|error)\s*$",
        value=np.nan,
        regex=True
    )

    # 2. Clean and standardize column names
    df.columns = (df.columns
                  .str.strip()
                  .str.lower()
                  .str.replace(" ", "_")
                  .str.replace(r"[^\w]", "", regex=True))

    # 3. Clean string columns (lowercase and strip whitespace)
    str_cols = ['item', 'payment_method', 'location']
    df[str_cols] = df[str_cols].apply(lambda x: x.str.strip().str.lower())

    # 4. Clean numeric columns (remove currency symbols/commas and convert)
    num_cols = ['quantity', 'price_per_unit', 'total_spent']
    df[num_cols] = (df[num_cols]
                    .replace({r'\$': '', ',': ''}, regex=True)
                    .apply(pd.to_numeric, errors='coerce'))

    # 5. Standardize dates
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')

    # 6. Fill categorical missing values with a designated placeholder
    df[str_cols] = df[str_cols].fillna("not_specified")

    # 7. Reconstruct missing financial data using mathematical relationships
    df["total_spent"] = df["total_spent"].fillna(df["price_per_unit"] * df["quantity"])
    df["price_per_unit"] = df["price_per_unit"].fillna(df["total_spent"] / df["quantity"])
    df["quantity"] = df["quantity"].fillna(df["total_spent"] / df["price_per_unit"])

    # 8. Drop rows with negligible missing data in core numeric/date columns
    df = df.dropna(subset=['quantity', 'price_per_unit', 'total_spent', 'transaction_date'])

    # 9. Remove identical transactions caused by system recording glitches
    df = df.drop_duplicates(subset=['item', 'quantity', 'total_spent', 'transaction_date', 'location'])
    
    # 10. Optimize memory usage for low-cardinality text columns
    df['location'] = df['location'].astype('category')
    df['payment_method'] = df['payment_method'].astype('category')

    return df

# The block below only runs if this script is executed directly 
# (it will not run if you just import the function into another file)
if __name__ == "__main__":
    
    # Define relative paths based on standard project structure
    # Moving up from src/, into data/01_raw/
    INPUT_PATH = "data/01_raw/cafe_sales.csv"
    
    # Moving up from src/, into data/03_processed/
    OUTPUT_PATH = "data/03_processed/clean_cafe_sales.csv"
    
    print("Loading raw data...")
    raw_data = pd.read_csv(INPUT_PATH)
    
    print("Cleaning data...")
    processed_data = clean_cafe_data(raw_data)
    
    print(f"Exporting cleaned data to {OUTPUT_PATH}...")
    processed_data.to_csv(OUTPUT_PATH, index=False)
    
    print("Pipeline execution complete.")