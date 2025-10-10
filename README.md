# Asset Correlation Tool for Financial Markets

## Overview
This repository provides a simple tool for analyzing correlations between various financial instruments including forex pairs, commodities, indices, and other asset classes. The implementation follows rigorous statistical methodologies.

---

## Table of Contents
- Correlation Analysis Dashboard
- Installation
- Data Format Requirements
- Correlation Methodologies
- Analysis Options
- Visualization Outputs
- Statistical Measures
- Usage Examples
- Academic References
- License
- Disclaimer

---

## Installation
# Clone the repository
git clone https://github.com/username/advanced-correlation-analysis.git
cd advanced-correlation-analysis

# Install dependencies
pip install -r requirements.txt

---

## Data Format Requirements
The tool accepts financial time series data in CSV format with the following specifications:
- Timestamp column (named 'Time' or in the first position)
- OHLC (Open, High, Low, Close) price data
- Optional volume column
- Asset name is extracted from the filename (e.g., 'EURUSD.csv' will be labeled as 'EURUSD')

Example format:
Time,Open,High,Low,Close,Volume
2025-08-13 17:00:00,147.345,147.423,147.316,147.391,3539
2025-08-13 18:00:00,147.390,147.511,147.388,147.433,2751

---

## Correlation Methodologies
1. Pearson Correlation
   Mathematical basis: Measures linear relationships between variables
   Formula: ρ_X,Y = cov(X,Y) / (σ_X σ_Y)
   Applications: Standard correlation analysis, suitable for normally distributed returns
   Limitations: Sensitive to outliers and non-linear relationships

2. Spearman Rank Correlation
   Mathematical basis: Non-parametric measure based on ranked variables
   Formula: r_s = 1 - (6 * Σd_i^2) / (n(n^2 - 1)) where d_i is the difference in ranks
   Applications: More robust to outliers, captures monotonic relationships
   Advantages: Suitable for non-normally distributed financial returns

3. Kendall's Tau Correlation
   Mathematical basis: Non-parametric measure based on concordant/discordant pairs
   Formula: τ = 2(n_c - n_d) / (n(n - 1)) where n_c and n_d are concordant and discordant pairs
   Applications: More robust for small samples, sensitive to changes in rank order
   Advantages: Better statistical properties for hypothesis testing

4. Partial Correlation
   Mathematical basis: Correlation between two variables while controlling for others
   Calculation: Derived from inverse of covariance matrix (precision matrix)
   Applications: Eliminating confounding effects, isolating direct relationships
   Advantages: Reveals underlying structure in complex multivariate systems

5. Time-Varying Correlation
   Mathematical basis: Rolling window or EWMA (Exponentially Weighted Moving Average)
   Applications: Analyzing correlation dynamics, regime detection
   Advantages: Captures evolving relationships between financial instruments

---

## Analysis Options
The interactive program provides several analytical options:
- Asset Selection: Individual file selection, directory-based bulk analysis, automatic detection of available instruments
- Correlation Parameters: Method (Pearson, Spearman, or Kendall), window size (5-100 periods), pair analysis
- Output Configuration: File format (PNG, JPG, SVG, PDF), resolution settings (100-600 DPI), display options (interactive visualization or silent export), output naming conventions

---

## Visualization Outputs
- Correlation Matrices: Matrix, clustered, partial
- Time Series Analyses: Rolling, time-varying
- Structural Analyses: Dendrogram, network, distribution
- Comprehensive Outputs: Dashboard, Excel export

---

## Statistical Measures
- Significance Testing: P-value calculation, null hypothesis testing (H₀: ρ = 0), critical value determination
- Tail Dependence: Lower/upper tail dependence for risk management
- Stability Analysis: Volatility of correlation coefficients, identification of stable/unstable relationships, structural break detection

---

## Usage Examples
### Basic Correlation Analysis
# Launch the interactive program
python main.py
# Follow the on-screen prompts to:
# 1. Select asset files or directory
# 2. Choose correlation method and parameters
# 3. Select visualization types
# 4. Configure output options

### Integration with Trading Systems
from correlation_analyzer import CorrelationAnalyzer, CorrelationVisualizer
# Load your market data
data = load_trading_data()  # Your data loading function
# Initialize analyzer
analyzer = CorrelationAnalyzer(data)
# Get correlation matrix
correlation = analyzer.calculate_correlation(method='pearson')
# Generate dashboard
visualizer = CorrelationVisualizer(analyzer)
visualizer.create_correlation_dashboard(save_path='trading_dashboard.png')

---

## Academic References
- Campbell, J. Y., Lo, A. W., & MacKinlay, A. C. (1997). The Econometrics of Financial Markets. Princeton University Press.
- McNeil, A. J., Frey, R., & Embrechts, P. (2015). Quantitative Risk Management: Concepts, Techniques and Tools. Princeton University Press.
- Engle, R. (2002). "Dynamic Conditional Correlation: A Simple Class of Multivariate Generalized Autoregressive Conditional Heteroskedasticity Models". Journal of Business & Economic Statistics, 20(3), 339-350.
- Embrechts, P., McNeil, A., & Straumann, D. (2002). "Correlation and Dependence in Risk Management: Properties and Pitfalls". In Risk Management: Value at Risk and Beyond (pp. 176-223). Cambridge University Press.
- Patton, A. J. (2006). "Modelling Asymmetric Exchange Rate Dependence". International Economic Review, 47(2), 527-556.

---

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---

## Disclaimer
This tool is provided for research and analytical purposes only. Financial decisions should not be made solely based on the output of this software. Past correlations do not guarantee future relationships between financial instruments. Users should conduct comprehensive due diligence and risk assessment before making investment decisions.
