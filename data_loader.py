"""
Data Loader for Advanced Correlation Analysis
============================================
Utilities to load and prepare data from various formats for correlation analysis.

Author: clementchamalet
Date: October 2025
"""

import os
import pandas as pd
import numpy as np
import glob
from datetime import datetime


def load_single_asset(file_path):
    """
    Load data from a single asset file.
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file
        
    Returns:
    --------
    tuple : (asset_name, pd.DataFrame)
        Asset name extracted from filename and DataFrame with OHLC data
    """
    # Extract asset name from filename (remove extension)
    asset_name = os.path.basename(file_path)
    asset_name = os.path.splitext(asset_name)[0]
    
    # Load data
    try:
        # Read first few lines to check format
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            header = f.readline().strip()
            first_data_line = f.readline().strip()
        
        # Determine if tab-separated
        is_tab_separated = '\t' in header
        separator = '\t' if is_tab_separated else ','
        
        # Check if header contains expected column names
        expected_columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        has_header = any(col in header for col in expected_columns)
        
        # Load data with appropriate parameters
        if has_header:
            # File has header
            df = pd.read_csv(file_path, sep=separator)
        else:
            # No header, provide column names
            df = pd.read_csv(file_path, sep=separator, 
                            names=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Unknown'])
        
        # Clean column names (remove whitespace)
        df.columns = df.columns.str.strip()
        
        # Handle time column
        time_col = None
        for col in df.columns:
            if col.lower() in ['time', 'date', 'datetime', 'timestamp']:
                time_col = col
                break
        
        if time_col is None:
            # Try to use the first column as time
            time_col = df.columns[0]
            print(f"No obvious time column found in {asset_name}. Using '{time_col}' as time column.")
        
        # Check if the date column is properly formatted
        # If all dates are the same (around 1970-01-01), create artificial dates
        if time_col in df.columns:
            # First, try to parse as datetime
            try:
                df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
            except:
                print(f"Failed to parse datetime in {asset_name}, creating artificial dates.")
                df[time_col] = pd.date_range(start='2023-01-01', periods=len(df), freq='H')
            
            # Check if we have proper dates - if not, create artificial ones
            if (df[time_col].dt.year < 1980).all() or df[time_col].isna().any():
                print(f"Invalid dates detected in {asset_name}, creating artificial dates.")
                df[time_col] = pd.date_range(start='2023-01-01', periods=len(df), freq='H')
        else:
            # Create a date index
            print(f"No time column found in {asset_name}, creating artificial dates.")
            df[time_col] = pd.date_range(start='2023-01-01', periods=len(df), freq='H')
        
        # Set index and handle possible duplicates
        df = df.set_index(time_col)
        
        # Check for duplicated indices
        if df.index.duplicated().any():
            print(f"Found {df.index.duplicated().sum()} duplicate timestamps in {asset_name}")
            # Option 1: Keep first occurrence of duplicated timestamps
            df = df[~df.index.duplicated(keep='first')]
        
        # Ensure 'Close' column exists
        if 'Close' not in df.columns:
            # Try to identify a suitable column
            price_cols = [col for col in df.columns if any(name in col.lower() 
                         for name in ['close', 'price', 'last', 'settlement'])]
            
            if price_cols:
                df['Close'] = df[price_cols[0]]
            elif len(df.columns) >= 4:
                # Typical OHLC format has Close as the 4th column
                df['Close'] = df.iloc[:, 3]
            else:
                # Use last numeric column
                numeric_cols = df.select_dtypes(include=np.number).columns
                if len(numeric_cols) > 0:
                    df['Close'] = df[numeric_cols[-1]]
                else:
                    raise ValueError(f"Could not determine Close column for {asset_name}")
        
        print(f"Successfully loaded {asset_name}: {len(df)} records from {df.index.min()} to {df.index.max()}")
        
        return asset_name, df
    
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None, None


def load_multiple_assets(directory, pattern="*.csv"):
    """
    Load all assets matching the pattern from the directory.
    
    Parameters:
    -----------
    directory : str
        Directory containing asset files
    pattern : str
        Glob pattern to match files (default: "*.csv")
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with all assets' closing prices
    """
    files = glob.glob(os.path.join(directory, pattern))
    
    if not files:
        print(f"No files matching '{pattern}' found in '{directory}'")
        return None
    
    # First pass: load all assets individually
    print(f"Found {len(files)} files in {directory}. Loading data...")
    assets_data = {}
    
    for file_path in files:
        asset_name, df = load_single_asset(file_path)
        if df is not None and 'Close' in df.columns:
            assets_data[asset_name] = df['Close']
    
    if not assets_data:
        print("No valid assets found.")
        return None
    
    print(f"Combining data from {len(assets_data)} assets...")
    
    # Create a DataFrame with all assets (without trying to align indices)
    result_df = pd.DataFrame()
    
    # Add each asset one by one, avoiding reindexing problems
    for asset_name, series in assets_data.items():
        # Create a new dataframe with just this series
        temp_df = pd.DataFrame({asset_name: series})
        
        if result_df.empty:
            result_df = temp_df
        else:
            # Outer join to combine data frames
            result_df = result_df.join(temp_df, how='outer')
    
    # Fill NA values
    result_df = result_df.ffill().bfill()

    print(f"Final dataset: {len(result_df)} time periods × {len(result_df.columns)} assets")
    print(f"Period: {result_df.index.min()} to {result_df.index.max()}")
    
    return result_df


def prepare_correlation_data(files_or_dir, is_directory=False):
    """
    Prepare data for correlation analysis from either a list of files or a directory.
    
    Parameters:
    -----------
    files_or_dir : str or list
        Either a directory path or a list of file paths
    is_directory : bool
        Whether files_or_dir is a directory path
        
    Returns:
    --------
    pd.DataFrame
        DataFrame ready for correlation analysis
    """
    if is_directory:
        return load_multiple_assets(files_or_dir)
    else:
        if isinstance(files_or_dir, str):
            files_or_dir = [files_or_dir]
        
        # Load individual assets
        assets_data = {}
        for file_path in files_or_dir:
            asset_name, df = load_single_asset(file_path)
            if df is not None and 'Close' in df.columns:
                assets_data[asset_name] = df['Close']
        
        if not assets_data:
            return None
        
        # Combine assets using the same approach as in load_multiple_assets
        result_df = pd.DataFrame()
        
        for asset_name, series in assets_data.items():
            temp_df = pd.DataFrame({asset_name: series})
            
            if result_df.empty:
                result_df = temp_df
            else:
                result_df = result_df.join(temp_df, how='outer')
        
        # Fill NA values
        result_df = result_df.ffill().bfill()

        return result_df
