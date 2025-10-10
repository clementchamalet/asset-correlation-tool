# Advanced Correlation Analysis for Financial Markets

---

## **Overview**
This repository provides a simple tool for analyzing correlations between financial instruments, including forex pairs, commodities, indices, and other asset classes. The implementation follows **rigorous statistical methodologies**.

---

## **Table of Contents**
- [Installation](#installation)
- [Data Format Requirements](#data-format-requirements)
- [Correlation Methodologies](#correlation-methodologies)
- [Analysis Options](#analysis-options)
- [Visualization Outputs](#visualization-outputs)
- [Statistical Measures](#statistical-measures)
- [Usage Examples](#usage-examples)
- [Academic References](#academic-references)
- [License](#license)
- [Disclaimer](#disclaimer)

---

## **Installation**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/username/advanced-correlation-analysis.git
   cd advanced-correlation-analysis
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## **Data Format Requirements**
The tool accepts financial time series data in **CSV format** with the following specifications:

- **Timestamp column**: Named `'Time'` or in the first position.
- **OHLC data**: Open, High, Low, Close price data.
- **Optional**: Volume column.
- **Asset name**: Extracted from the filename (e.g., `EURUSD.csv` → labeled as `EURUSD`).

**Example format:**
```csv
Time,Open,High,Low,Close,Volume
2025-08-13 17:00:00,147.345,147.423,147.316,147.391,3539
2025-08-13 18:00:00,147.390,147.511,147.388,147.433,2751
```

---

## **Correlation Methodologies**

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

## **Analysis Options**
The interactive program provides:

- **Asset Selection**: Individual files, directory-based bulk analysis, auto-detection.
- **Correlation Parameters**: Method (Pearson/Spearman/Kendall), window size (5-100 periods), pair analysis.
- **Output Configuration**: File format (PNG/JPG/SVG/PDF), resolution (100-600 DPI), interactive/silent export.

---

## **Visualization Outputs**
- **Correlation Matrices**: Standard, clustered, partial.
- **Time Series Analyses**: Rolling, time-varying heatmaps.
- **Structural Analyses**: Dendrogram, network graph, distribution.
- **Comprehensive Outputs**: Dashboard, Excel export.

---

## **Statistical Measures**
- **Significance Testing**: P-values, null hypothesis testing.
- **Tail Dependence**: Lower/upper tail for risk management.
- **Stability Analysis**: Volatility, structural break detection.

---

## **Usage Examples**

### **Basic Correlation Analysis**
```python
# Launch the interactive program
python main.py
# Follow prompts to select assets, methods, visualizations, and outputs.
```

### **Integration with Trading Systems**
```python
from correlation_analyzer import CorrelationAnalyzer, CorrelationVisualizer

data = load_trading_data()  # Your data loading function
analyzer = CorrelationAnalyzer(data)
correlation = analyzer.calculate_correlation(method='pearson')

visualizer = CorrelationVisualizer(analyzer)
visualizer.create_correlation_dashboard(save_path='trading_dashboard.png')
```

---

## **Academic References**
- [Campbell, J. Y., Lo, A. W., & MacKinlay, A. C. (1997). *The Econometrics of Financial Markets*. Princeton University Press.](https://press.princeton.edu/books/hardcover/9780691043012/the-econometrics-of-financial-markets)
- [McNeil, A. J., Frey, R., & Embrechts, P. (2015). *Quantitative Risk Management*. Princeton University Press.](https://press.princeton.edu/books/hardcover/9780691166278/quantitative-risk-management)
- [Engle, R. (2002). "Dynamic Conditional Correlation". *Journal of Business & Economic Statistics*, 20(3), 339-350.](https://www.tandfonline.com/doi/abs/10.1198/073500102288618487)
- [Embrechts, P., McNeil, A., & Straumann, D. (2002). "Correlation and Dependence in Risk Management". *Risk Management: Value at Risk and Beyond*. Cambridge University Press.](https://www.cambridge.org/core/books/risk-management/8A1E5F3E0E5A5D1E5F3E0E5A5D1E5F3E)
- [Patton, A. J. (2006). "Modelling Asymmetric Exchange Rate Dependence". *International Economic Review*, 47(2), 527-556.](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1468-2354.2006.00387.x)

---

## **License**
This project is licensed under the **[MIT License](LICENSE)**.

---

## **Disclaimer**
This tool is provided for **research and analytical purposes only**. Financial decisions should not be made solely based on the output of this software. Past correlations do not guarantee future relationships between financial instruments. Users should conduct comprehensive due diligence and risk assessment before making investment decisions.
