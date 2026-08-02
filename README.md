# Advanced Correlation Analysis for Financial Markets

This is a personal/learning project, not a production tool or a commercially audited library.

## Overview

This repository provides a tool for analyzing correlations between financial instruments, including forex pairs, commodities, indices, and other asset classes. It loads OHLC price data from CSV files, computes Pearson/Spearman/Kendall/partial/rolling correlation, and produces matplotlib/seaborn visualizations plus an Excel export of the results.

## Table of Contents
- [Installation](#installation)
- [Data Format Requirements](#data-format-requirements)
- [Correlation Methodologies](#correlation-methodologies)
- [Analysis Options](#analysis-options)
- [Visualization Outputs](#visualization-outputs)
- [Statistical Measures](#statistical-measures)
- [Usage Examples](#usage-examples)
- [References](#references)
- [License](#license)
- [Disclaimer](#disclaimer)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/clementchmlt/asset-correlation-tool.git
   cd asset-correlation-tool
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Data Format Requirements

The tool accepts financial time series data in CSV format with the following specifications:

- Timestamp column: named `'Time'` or in the first position.
- OHLC data: Open, High, Low, Close price data.
- Optional: Volume column.
- Asset name: extracted from the filename (e.g., `EURUSD.csv` → labeled as `EURUSD`).

Example format:
```csv
Time,Open,High,Low,Close,Volume
2025-08-13 17:00:00,147.345,147.423,147.316,147.391,3539
2025-08-13 18:00:00,147.390,147.511,147.388,147.433,2751
```

## Correlation Methodologies

1. **Pearson Correlation**
   - Mathematical basis: measures linear relationships between variables
   - Formula: ρ_X,Y = cov(X,Y) / (σ_X σ_Y)
   - Applications: standard correlation analysis, suitable for normally distributed returns
   - Limitations: sensitive to outliers and non-linear relationships

2. **Spearman Rank Correlation**
   - Mathematical basis: non-parametric measure based on ranked variables
   - Formula: r_s = 1 - (6 * Σd_i^2) / (n(n^2 - 1)) where d_i is the difference in ranks
   - Applications: more robust to outliers, captures monotonic relationships
   - Advantages: suitable for non-normally distributed financial returns

3. **Kendall's Tau Correlation**
   - Mathematical basis: non-parametric measure based on concordant/discordant pairs
   - Formula: τ = 2(n_c - n_d) / (n(n - 1)) where n_c and n_d are concordant and discordant pairs
   - Applications: more robust for small samples, sensitive to changes in rank order
   - Advantages: better statistical properties for hypothesis testing

4. **Partial Correlation**
   - Mathematical basis: correlation between two variables while controlling for others
   - Calculation: derived from the inverse of the covariance matrix (precision matrix)
   - Applications: eliminating confounding effects, isolating direct relationships
   - Advantages: reveals underlying structure in multivariate systems

5. **Time-Varying Correlation**
   - Mathematical basis: rolling window or EWMA (Exponentially Weighted Moving Average)
   - Applications: analyzing correlation dynamics, regime detection
   - Advantages: captures evolving relationships between financial instruments

## Analysis Options

The interactive program provides:

- Asset selection: individual files, directory-based bulk analysis, auto-detection.
- Correlation parameters: method (Pearson/Spearman/Kendall), window size (5-100 periods), pair analysis.
- Output configuration: file format (PNG/JPG/SVG/PDF), resolution (100-600 DPI), interactive/silent export.

## Visualization Outputs

- Correlation matrices: standard, clustered, partial.
- Time series analyses: rolling, time-varying heatmaps.
- Structural analyses: dendrogram, network graph, distribution.
- Comprehensive outputs: dashboard, Excel export.

## Statistical Measures

- Significance testing: p-values, null hypothesis testing.
- Tail dependence: lower/upper tail for risk assessment.
- Stability analysis: volatility, structural break detection.

## Usage Examples

### Basic Correlation Analysis
```python
# Launch the interactive program
python main.py
# Follow prompts to select assets, methods, visualizations, and outputs.
```

### Integration with Trading Systems
```python
from correlation_analyzer import CorrelationAnalyzer, CorrelationVisualizer

data = load_trading_data()  # Your data loading function
analyzer = CorrelationAnalyzer(data)
correlation = analyzer.calculate_correlation(method='pearson')

visualizer = CorrelationVisualizer(analyzer)
visualizer.create_correlation_dashboard(save_path='trading_dashboard.png')
```

## References

The correlation and dependence concepts implemented here draw on standard references in the field:

- Campbell, J. Y., Lo, A. W., & MacKinlay, A. C. (1997). *The Econometrics of Financial Markets*. Princeton University Press.
- McNeil, A. J., Frey, R., & Embrechts, P. (2015). *Quantitative Risk Management*. Princeton University Press.
- Engle, R. (2002). "Dynamic Conditional Correlation". *Journal of Business & Economic Statistics*, 20(3), 339-350.
- Embrechts, P., McNeil, A., & Straumann, D. (2002). "Correlation and Dependence in Risk Management". In *Risk Management: Value at Risk and Beyond*. Cambridge University Press.
- Patton, A. J. (2006). "Modelling Asymmetric Exchange Rate Dependence". *International Economic Review*, 47(2), 527-556.

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

This tool is provided for research and analytical purposes only. Financial decisions should not be made solely based on the output of this software. Past correlations do not guarantee future relationships between financial instruments. Users should conduct comprehensive due diligence and risk assessment before making investment decisions.
