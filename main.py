#!/usr/bin/env python3
"""
Advanced Correlation Analysis Tool
=================================
Interactive tool for analyzing correlation between financial assets.

Author: clementchmlt
Date: October 2025
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from correlation_analyzer import CorrelationAnalyzer, CorrelationVisualizer
from data_loader import prepare_correlation_data, load_single_asset

# Ignore warnings for better readability
warnings.filterwarnings('ignore')

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Displays the program header."""
    clear_screen()
    print("=" * 80)
    print("ADVANCED CORRELATION ANALYSIS")
    print("=" * 80)
    print("Developed by clementchmlt")
    print()

def select_assets():
    """Interface for selecting the assets to analyze."""
    print_header()
    print("STEP 1: Selecting assets to analyze")
    print("-" * 80)

    # Available options
    print("Available options:")
    print("1. Select specific CSV files")
    print("2. Analyze all CSV files in a directory")
    print()

    while True:
        try:
            choice = int(input("Your choice (1-2): "))
            if 1 <= choice <= 2:
                break
            print("Invalid choice. Please enter a number between 1 and 2.")
        except ValueError:
            print("Please enter a valid number.")

    if choice == 1:
        # Select specific files
        print("\nSearching for available CSV files...")

        # Look for CSV files in the current directories
        csv_files = []
        search_dirs = [".", "data", "../data"]

        for directory in search_dirs:
            if os.path.exists(directory):
                csv_files.extend(glob.glob(os.path.join(directory, "*.csv")))

        if not csv_files:
            print("Warning: No CSV files found in the current directories.")
            print("Please enter the full path to your CSV files:")
            user_path = input("Directory path: ")

            if os.path.exists(user_path):
                csv_files = glob.glob(os.path.join(user_path, "*.csv"))
            else:
                print("Warning: Invalid path. Cannot continue.")
                return None, "no valid data"

        if not csv_files:
            print("Warning: No CSV files found. Cannot continue.")
            return None, "no valid data"

        # Display available files
        print("\nAvailable files:")
        for i, file_path in enumerate(csv_files, 1):
            asset_name = os.path.splitext(os.path.basename(file_path))[0]
            print(f"{i}. {asset_name} ({file_path})")

        # File selection
        print("\nSelect the files to analyze (e.g. 1,3,5 or 'all' for all of them):")
        selection = input("Your selection: ")

        selected_files = []
        if selection.lower() == 'all':
            selected_files = csv_files
        else:
            try:
                indices = [int(idx.strip()) for idx in selection.split(',')]
                selected_files = [csv_files[idx-1] for idx in indices if 1 <= idx <= len(csv_files)]
            except (ValueError, IndexError):
                print("Warning: Invalid selection. Using the first 3 files.")
                selected_files = csv_files[:min(3, len(csv_files))]

        # Load the data
        print(f"\nLoading {len(selected_files)} files...")
        data = prepare_correlation_data(selected_files, is_directory=False)

        if data is None or data.empty or len(data.columns) < 2:
            print("Warning: Error loading data or insufficient data.")
            return None, "insufficient data"

        asset_desc = ", ".join([os.path.splitext(os.path.basename(f))[0] for f in selected_files])
        return data, f"selected files: {asset_desc}"

    else:  # choice == 2
        # Analyze a directory
        print("\nSearching for available directories...")

        # Look for directories containing CSV files
        possible_dirs = [".", "data", "../data"]
        valid_dirs = [d for d in possible_dirs if os.path.exists(d) and glob.glob(os.path.join(d, "*.csv"))]

        selected_dir = "."
        if valid_dirs:
            print("Directories containing CSV files:")
            for i, directory in enumerate(valid_dirs, 1):
                n_files = len(glob.glob(os.path.join(directory, "*.csv")))
                print(f"{i}. {directory} ({n_files} CSV files)")

            choice_input = input("\nSelect a directory (or enter a custom path): ")

            # If the input is a number, it's a choice from the list
            if choice_input.isdigit():
                dir_choice = int(choice_input)
                if 1 <= dir_choice <= len(valid_dirs):
                    selected_dir = valid_dirs[dir_choice-1]
                else:
                    print("Invalid choice. Using the current directory.")
            # Otherwise, it's a custom path
            else:
                selected_dir = choice_input.strip()
        else:
            selected_dir = input("No directory with CSV files found. Enter the directory path: ")

        # Check that the directory exists and contains CSV files
        if not os.path.exists(selected_dir) or not glob.glob(os.path.join(selected_dir, "*.csv")):
            print("Warning: Invalid or empty directory. Cannot continue.")
            return None, "no valid data"

        # Load the data
        print(f"\nLoading CSV files from {selected_dir}...")
        try:
            data = prepare_correlation_data(selected_dir, is_directory=True)

            if data is None or data.empty or len(data.columns) < 2:
                print("Warning: Error loading data or insufficient data.")
                return None, "insufficient data"

            n_assets = len(data.columns)
            return data, f"{n_assets} assets from {selected_dir}"
        except Exception as e:
            print(f"Warning: Error loading data: {e}")
            print("Technical details for debugging:")
            import traceback
            traceback.print_exc()
            return None, "loading error"

def configure_analysis(data):
    """Interface for configuring the analysis parameters."""
    print_header()
    print("STEP 2: Configuring the analysis")
    print("-" * 80)

    print("Available options:")

    # Correlation method
    print("\n1. Correlation method:")
    print("   1. Pearson - linear correlation (parametric)")
    print("   2. Spearman - rank correlation (non-parametric)")
    print("   3. Kendall - tau correlation (for ordinal data)")

    while True:
        try:
            method_choice = int(input("\nSelect a method (1-3, default: 1): ") or 1)
            if 1 <= method_choice <= 3:
                break
            print("Invalid choice. Please enter a number between 1 and 3.")
        except ValueError:
            print("Please enter a valid number.")

    methods = ['pearson', 'spearman', 'kendall']
    method = methods[method_choice-1]

    # Rolling window size
    print("\n2. Window size for rolling analysis:")

    # Suggest a window size based on the length of the data
    suggested_window = min(30, max(5, len(data) // 10))

    while True:
        try:
            window = int(input(f"Number of days (5-{len(data)//2}, default: {suggested_window}): ") or suggested_window)
            if 5 <= window <= len(data) // 2:
                break
            print(f"Please enter a number between 5 and {len(data)//2}.")
        except ValueError:
            print("Please enter a valid number.")

    # Asset pair for detailed analysis (optional)
    pair = None
    if len(data.columns) >= 2:
        print("\n3. Asset pair for detailed analysis (optional):")

        for i, asset in enumerate(data.columns, 1):
            print(f"   {i}. {asset}")

        print("\nSelect two assets for a detailed analysis (e.g. 1,3)")
        print("(Leave blank to skip pair analysis)")

        selection = input("Your selection (optional): ")

        if selection:
            try:
                indices = [int(idx.strip()) for idx in selection.split(',')]
                if len(indices) >= 2 and all(1 <= idx <= len(data.columns) for idx in indices[:2]):
                    pair = [data.columns[idx-1] for idx in indices[:2]]
                    print(f"Selected pair: {pair[0]} vs {pair[1]}")
                else:
                    print("Warning: Invalid selection. Pair analysis skipped.")
            except (ValueError, IndexError):
                print("Warning: Invalid format. Pair analysis skipped.")

    return {
        'method': method,
        'window': window,
        'pair': pair
    }

def select_visualizations(has_pair=False):
    """Interface for selecting the visualizations to generate."""
    print_header()
    print("STEP 3: Selecting visualizations")
    print("-" * 80)

    all_graphs = [
        "matrix", "clustered", "dendrogram",
        "distribution", "partial", "network", "time_varying", "dashboard"
    ]

    # Add "rolling" only if a pair has been selected
    if has_pair:
        all_graphs.insert(3, "rolling")

    all_graphs.append("all")

    descriptions = {
        "matrix": "Simple correlation matrix",
        "clustered": "Correlation matrix with hierarchical clustering",
        "dendrogram": "Dendrogram of relationships between assets",
        "rolling": "Rolling correlation analysis (requires an asset pair)",
        "distribution": "Distribution of correlation coefficients",
        "partial": "Partial correlation matrix",
        "network": "Correlation network graph",
        "time_varying": "Time evolution of average correlations",
        "dashboard": "Full dashboard (visual summary)",
        "all": "All available visualizations"
    }

    print("Available visualizations:")
    for i, graph_type in enumerate(all_graphs, 1):
        print(f"{i}. {graph_type:12} - {descriptions[graph_type]}")

    print("\nSelect the visualizations to generate (e.g. 1,3,5 or 'all' for all of them):")
    selection = input("Your selection (default: 1,9): ") or "1,9"

    selected_graphs = []
    if selection.lower() == "all" or str(len(all_graphs)) in selection:
        selected_graphs = ["all"]
    else:
        try:
            indices = [int(idx.strip()) for idx in selection.split(',')]
            selected_graphs = [all_graphs[idx-1] for idx in indices if 1 <= idx <= len(all_graphs)]
        except (ValueError, IndexError):
            print("Warning: Invalid selection. Using the matrix and the dashboard.")
            selected_graphs = ["matrix", "dashboard"]

    # If "all" is selected, replace it with the full list except "all"
    if "all" in selected_graphs:
        selected_graphs = [g for g in all_graphs if g != "all"]

        # Remove "rolling" if no pair is selected
        if not has_pair and "rolling" in selected_graphs:
            selected_graphs.remove("rolling")

    return selected_graphs

def configure_output():
    """Interface for configuring the output options."""
    print_header()
    print("STEP 4: Configuring the output")
    print("-" * 80)

    # Output prefix
    print("1. Prefix for output files:")
    prefix = input("Prefix (default: correlation_output): ") or "correlation_output"

    # Graph file format
    print("\n2. Graph file format:")
    print("   1. PNG - standard format (default)")
    print("   2. JPG - reduced size")
    print("   3. SVG - vector, for editing")
    print("   4. PDF - for printing")

    while True:
        try:
            format_choice = int(input("\nSelect a format (1-4, default: 1): ") or 1)
            if 1 <= format_choice <= 4:
                break
            print("Invalid choice. Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a valid number.")

    formats = ['png', 'jpg', 'svg', 'pdf']
    file_format = formats[format_choice-1]

    # Resolution
    print("\n3. Image resolution:")

    while True:
        try:
            dpi = int(input("DPI (100-600, default: 300): ") or 300)
            if 100 <= dpi <= 600:
                break
            print("Please enter a number between 100 and 600.")
        except ValueError:
            print("Please enter a valid number.")

    # Display mode
    print("\n4. Graph display:")
    print("   1. Display and save")
    print("   2. Save only (no display)")

    while True:
        try:
            display_choice = int(input("\nYour choice (1-2, default: 1): ") or 1)
            if 1 <= display_choice <= 2:
                break
            print("Invalid choice. Please enter a number between 1 and 2.")
        except ValueError:
            print("Please enter a valid number.")

    no_display = (display_choice == 2)

    return {
        'output': prefix,
        'format': file_format,
        'dpi': dpi,
        'no_display': no_display
    }

def safe_plot_function(plot_func, *args, **kwargs):
    """
    Safely executes a plotting function by catching exceptions.

    Parameters:
    -----------
    plot_func : function
        Plotting function to execute
    *args, **kwargs:
        Arguments to pass to the plotting function

    Returns:
    --------
    bool: True if the plot succeeded, False otherwise
    """
    try:
        plot_func(*args, **kwargs)
        return True
    except Exception as e:
        print(f"    Warning: Error while plotting: {e}")
        return False

def main():
    """
    Main entry point with interactive interface.
    """
    print_header()
    print("Welcome to the advanced correlation analysis tool!")
    print("\nThis tool lets you analyze the relationships between different financial assets.")
    print("Follow the prompts to configure your analysis.")
    print("\nPress Enter to start...")
    input()

    # STEP 1: Asset selection
    data, data_desc = select_assets()

    # Check that the data is valid
    if data is None:
        print("\nCannot continue without valid data. Program ended.")
        return

    # STEP 2: Analysis configuration
    config = configure_analysis(data)

    # STEP 3: Visualization selection
    graphs = select_visualizations(has_pair=config['pair'] is not None)

    # STEP 4: Output configuration
    output_config = configure_output()

    # Configuration summary
    print_header()
    print("CONFIGURATION SUMMARY")
    print("-" * 80)
    print(f"- Data: {data_desc}")
    print(f"- Dimensions: {len(data)} time points x {len(data.columns)} assets")
    print(f"- Period: {data.index.min().date()} to {data.index.max().date()}")
    print(f"- Correlation method: {config['method']}")
    print(f"- Window size: {config['window']} days")

    if config['pair']:
        print(f"- Analyzed pair: {config['pair'][0]} vs {config['pair'][1]}")

    print(f"- Visualizations: {', '.join(graphs)}")
    print(f"- Output prefix: {output_config['output']}")
    print(f"- Format: {output_config['format'].upper()} ({output_config['dpi']} DPI)")
    print(f"- Mode: {'Save only' if output_config['no_display'] else 'Display and save'}")

    print("\nPress Enter to run the analysis or Ctrl+C to cancel...")
    input()

    # If no_display is enabled, configure matplotlib not to display plots
    if output_config['no_display']:
        plt.ioff()  # Disable interactive mode

    # Run the analysis
    print_header()
    print("RUNNING THE ANALYSIS")
    print("-" * 80)

    # Initialize the analyzer
    print("1. Initializing the correlation analyzer")
    print("-" * 60)
    analyzer = CorrelationAnalyzer(data)
    print("Analyzer initialized")
    print(f"  - Price data points: {len(data)}")
    print(f"  - Return data points: {len(analyzer.returns)}")
    print()

    # Compute correlations
    print("2. Computing correlation matrices")
    print("-" * 60)

    # Correlation using the specified method
    print(f"2.1 Correlation matrix ({config['method']}):")
    correlation = analyzer.calculate_correlation(method=config['method'])

    # Check for problematic values
    has_nan = np.isnan(correlation.values).any()
    has_perfect_corr = (np.abs(correlation.values) > 0.999).any()

    if has_nan:
        print("Warning: The correlation matrix contains missing values (NaN).")
        print("   Some analyses may fail or produce unreliable results.")

    if has_perfect_corr:
        print("Warning: Some correlations are nearly perfect (+-1.0).")
        print("   This may indicate issues in the data or direct relationships.")

    print(correlation.round(3))
    print()

    # P-values
    print("2.2 Statistical significance (P-values):")
    try:
        pvalues = analyzer.calculate_pvalues()
        print(pvalues.round(4))
    except Exception as e:
        print(f"Warning: Unable to compute p-values: {e}")
    print()

    # Detailed analysis of a specific pair if requested
    if config['pair']:
        instrument1, instrument2 = config['pair']
        print(f"2.3 Detailed analysis of the pair {instrument1} vs {instrument2}:")

        try:
            # Simple correlation
            corr_value = correlation.loc[instrument1, instrument2]
            print(f"  - Correlation {config['method']}: {corr_value:.4f}")

            # P-value if available
            if 'pvalues' in locals() and not np.isnan(pvalues.loc[instrument1, instrument2]):
                pval = pvalues.loc[instrument1, instrument2]
                print(f"  - P-value: {pval:.4f} {'(significant)' if pval < 0.05 else '(not significant)'}")

            # Tail dependence
            tail_dep = analyzer.calculate_tail_dependence(instrument1, instrument2, quantile=0.05)
            print(f"  - Lower tail dependence (5%): {tail_dep['lower_tail']:.4f}")
            print(f"  - Upper tail dependence (95%): {tail_dep['upper_tail']:.4f}")

            # Structural breakpoint detection
            try:
                breakpoints = analyzer.detect_correlation_breakpoints(instrument1, instrument2, window=config['window'])
                if breakpoints:
                    print(f"  - Structural breakpoints detected: {len(breakpoints)}")
                    print(f"    First dates: {[bp.date() for bp in breakpoints[:3]]}")
                else:
                    print("  - No structural breakpoints detected")
            except Exception as e:
                print(f"  - Unable to detect structural breakpoints: {e}")
        except Exception as e:
            print(f"Warning: Error during pair analysis: {e}")
        print()

    # Initialize the visualizer
    print("3. Creating visualizations")
    print("-" * 60)
    visualizer = CorrelationVisualizer(analyzer)

    # Set the common parameters for all visualizations
    viz_params = {
        'save_path': None,  # Will be set for each graph
        'figsize': (12, 10) if 'dashboard' not in graphs else (20, 12)
    }

    # Generate the requested visualizations
    print("Generating graphs:")

    for graph_type in graphs:
        viz_params['save_path'] = f"{output_config['output']}_{graph_type}.{output_config['format']}"

        if graph_type == "matrix":
            print("  - Correlation matrix heatmap...")
            safe_plot_function(
                visualizer.plot_correlation_matrix,
                method=config['method'],
                save_path=viz_params['save_path']
            )

        elif graph_type == "clustered":
            print("  - Correlation matrix with clustering...")
            # Check for missing or infinite values
            if has_nan:
                print("    Warning: Cannot generate the clustering because the matrix contains NaN values.")
                continue

            safe_plot_function(
                visualizer.plot_clustered_correlation,
                save_path=viz_params['save_path']
            )

        elif graph_type == "dendrogram":
            print("  - Hierarchical clustering dendrogram...")
            # Check for missing or infinite values
            if has_nan:
                print("    Warning: Cannot generate the dendrogram because the matrix contains NaN values.")
                continue

            safe_plot_function(
                visualizer.plot_dendrogram,
                save_path=viz_params['save_path']
            )

        elif graph_type == "rolling" and config['pair']:
            instrument1, instrument2 = config['pair']
            print(f"  - Rolling correlation ({instrument1} vs {instrument2})...")
            safe_plot_function(
                visualizer.plot_rolling_correlation,
                instrument1, instrument2,
                window=config['window'],
                save_path=viz_params['save_path']
            )

        elif graph_type == "distribution":
            print("  - Correlation distribution...")
            safe_plot_function(
                visualizer.plot_correlation_distribution,
                save_path=viz_params['save_path']
            )

        elif graph_type == "partial":
            print("  - Partial correlation matrix...")
            # Check for missing values
            if has_nan:
                print("    Warning: Cannot generate the partial correlation because the matrix contains NaN values.")
                continue

            safe_plot_function(
                visualizer.plot_partial_correlation_matrix,
                save_path=viz_params['save_path']
            )

        elif graph_type == "network":
            print("  - Correlation network...")
            try:
                import networkx
                # Check for missing values
                if has_nan:
                    print("    Warning: Cannot generate the network because the matrix contains NaN values.")
                    continue

                safe_plot_function(
                    visualizer.plot_correlation_network,
                    threshold=0.5,
                    save_path=viz_params['save_path']
                )
            except ImportError:
                print("    Warning: networkx library not installed. Network graph skipped.")
                print("       Install it with: pip install networkx")

        elif graph_type == "time_varying":
            print("  - Time-varying correlation heatmap...")
            # Check there is enough data for the time-based analysis
            if len(data) < config['window'] * 2:
                print(f"    Warning: Not enough data for the time-varying analysis with a window of {config['window']}.")
                continue

            safe_plot_function(
                visualizer.plot_time_varying_correlation_heatmap,
                window=config['window'],
                save_path=viz_params['save_path']
            )

        elif graph_type == "dashboard":
            print("  - Full dashboard...")
            safe_plot_function(
                visualizer.create_correlation_dashboard,
                window=config['window'],
                save_path=viz_params['save_path']
            )

    # Export the results to Excel
    print("\n4. Exporting the results")
    print("-" * 60)

    excel_path = f"{output_config['output']}_results.xlsx"
    print(f"Exporting to Excel: {excel_path}")

    try:
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Export the base data
            correlation.round(4).to_excel(writer, sheet_name=f'{config["method"].capitalize()}_Correlation')

            # Attempt to export p-values if available
            if 'pvalues' in locals():
                pvalues.round(4).to_excel(writer, sheet_name='P_Values')

            # Attempt to export the partial correlation
            try:
                partial_corr = analyzer.partial_correlation()
                partial_corr.round(4).to_excel(writer, sheet_name='Partial_Correlation')
            except Exception as e:
                print(f"Warning: Unable to export partial correlations: {e}")

            # Attempt to export the stability
            try:
                stability = analyzer.calculate_correlation_stability(window=config['window'])
                stability.round(4).to_excel(writer, sheet_name='Correlation_Stability')
            except Exception as e:
                print(f"Warning: Unable to export correlation stability: {e}")

            # Export the raw data
            data.to_excel(writer, sheet_name='Raw_Data')

        print("Export completed successfully!")
    except Exception as e:
        print(f"Warning: Error exporting to Excel: {e}")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    print(f"\nFiles generated in the current directory with the prefix: {output_config['output']}_")
    print("\nThank you for using the advanced correlation analysis tool.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by the user.")
    except Exception as e:
        print(f"\n\nAn unexpected error occurred: {e}")
        print("Error details:")
        import traceback
        traceback.print_exc()
