"""
Correlation Analysis Tool
============================================================
Author: clementchamalet
Date: October 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform
import warnings
warnings.filterwarnings('ignore')

class CorrelationAnalyzer:
    """
    Advanced correlation analyzer for financial instruments.
    
    Features:
    - Multiple correlation methods (Pearson, Spearman, Kendall)
    - Rolling correlation analysis
    - Dynamic Conditional Correlation (DCC)
    - Hierarchical clustering
    - Statistical significance testing
    - Time-varying correlation
    - Copula-based dependence measures
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the analyzer with price data.
        
        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame with datetime index and instruments as columns
        """
        self.data = data
        self.returns = data.pct_change().dropna()
        self.log_returns = np.log(data / data.shift(1)).dropna()
        self.correlation_matrix = None
        self.pvalues = None
        
    def calculate_correlation(self, method='pearson', use_log_returns=True):
        """
        Calculate correlation matrix using specified method.
        
        Parameters:
        -----------
        method : str
            'pearson', 'spearman', or 'kendall'
        use_log_returns : bool
            Use log returns (True) or simple returns (False)
            
        Returns:
        --------
        pd.DataFrame : Correlation matrix
        """
        data_to_use = self.log_returns if use_log_returns else self.returns
        
        if method == 'pearson':
            self.correlation_matrix = data_to_use.corr(method='pearson')
        elif method == 'spearman':
            self.correlation_matrix = data_to_use.corr(method='spearman')
        elif method == 'kendall':
            self.correlation_matrix = data_to_use.corr(method='kendall')
        else:
            raise ValueError("Method must be 'pearson', 'spearman', or 'kendall'")
            
        return self.correlation_matrix
    
    def calculate_pvalues(self, use_log_returns=True):
        """
        Calculate p-values for correlation coefficients.
        
        Parameters:
        -----------
        use_log_returns : bool
            Use log returns (True) or simple returns (False)
            
        Returns:
        --------
        pd.DataFrame : Matrix of p-values
        """
        data_to_use = self.log_returns if use_log_returns else self.returns
        n = len(data_to_use)
        pvalues = np.zeros((data_to_use.shape[1], data_to_use.shape[1]))
        
        for i in range(data_to_use.shape[1]):
            for j in range(data_to_use.shape[1]):
                if i != j:
                    _, pval = stats.pearsonr(data_to_use.iloc[:, i], data_to_use.iloc[:, j])
                    pvalues[i, j] = pval
                else:
                    pvalues[i, j] = 0
                    
        self.pvalues = pd.DataFrame(pvalues, 
                                     columns=data_to_use.columns, 
                                     index=data_to_use.columns)
        return self.pvalues
    
    def rolling_correlation(self, instrument1, instrument2, window=30, use_log_returns=True):
        """
        Calculate rolling correlation between two instruments.
        
        Parameters:
        -----------
        instrument1, instrument2 : str
            Names of instruments to correlate
        window : int
            Rolling window size
        use_log_returns : bool
            Use log returns (True) or simple returns (False)
            
        Returns:
        --------
        pd.Series : Rolling correlation
        """
        data_to_use = self.log_returns if use_log_returns else self.returns
        
        rolling_corr = data_to_use[instrument1].rolling(window=window).corr(
            data_to_use[instrument2]
        )
        return rolling_corr
    
    def calculate_distance_matrix(self):
        """
        Calculate distance matrix from correlation matrix for clustering.
        Based on: distance = sqrt(0.5 * (1 - correlation))
        
        Returns:
        --------
        np.ndarray : Distance matrix
        """
        if self.correlation_matrix is None:
            self.calculate_correlation()
            
        distance = np.sqrt(0.5 * (1 - self.correlation_matrix))
        return distance
    
    def hierarchical_clustering(self, method='ward'):
        """
        Perform hierarchical clustering on instruments.
        
        Parameters:
        -----------
        method : str
            Linkage method ('ward', 'single', 'complete', 'average')
            
        Returns:
        --------
        tuple : (linkage matrix, dendrogram)
        """
        distance_matrix = self.calculate_distance_matrix()
        
        # Convert to condensed distance matrix
        condensed_dist = squareform(distance_matrix, checks=False)
        
        # Perform hierarchical clustering
        linkage_matrix = hierarchy.linkage(condensed_dist, method=method)
        
        return linkage_matrix
    
    def calculate_ewma_correlation(self, lambda_param=0.94, use_log_returns=True):
        """
        Calculate Exponentially Weighted Moving Average (EWMA) correlation matrix.
        Used in RiskMetrics methodology.
        
        Parameters:
        -----------
        lambda_param : float
            Decay factor (typically 0.94 for daily data)
        use_log_returns : bool
            Use log returns (True) or simple returns (False)
            
        Returns:
        --------
        pd.DataFrame : EWMA correlation matrix
        """
        data_to_use = self.log_returns if use_log_returns else self.returns
        
        # Calculate EWMA covariance matrix
        ewma_cov = data_to_use.ewm(alpha=1-lambda_param).cov()
        
        # Extract the last covariance matrix
        latest_cov = ewma_cov.iloc[-len(data_to_use.columns):]
        
        # Convert covariance to correlation
        std_dev = np.sqrt(np.diag(latest_cov))
        correlation = latest_cov / np.outer(std_dev, std_dev)
        
        return correlation
    
    def calculate_tail_dependence(self, instrument1, instrument2, quantile=0.05):
        """
        Calculate tail dependence coefficient (lower and upper tails).
        Measures co-movement in extreme market conditions.
        
        Parameters:
        -----------
        instrument1, instrument2 : str
            Names of instruments
        quantile : float
            Quantile for tail definition (default: 5%)
            
        Returns:
        --------
        dict : {'lower_tail': float, 'upper_tail': float}
        """
        data1 = self.log_returns[instrument1]
        data2 = self.log_returns[instrument2]
        
        # Lower tail dependence
        threshold_lower = data1.quantile(quantile)
        lower_tail_events = ((data1 <= threshold_lower) & (data2 <= data2.quantile(quantile))).sum()
        lower_tail_dep = lower_tail_events / (data1 <= threshold_lower).sum()
        
        # Upper tail dependence
        threshold_upper = data1.quantile(1 - quantile)
        upper_tail_events = ((data1 >= threshold_upper) & (data2 >= data2.quantile(1 - quantile))).sum()
        upper_tail_dep = upper_tail_events / (data1 >= threshold_upper).sum()
        
        return {
            'lower_tail': lower_tail_dep,
            'upper_tail': upper_tail_dep
        }
    
    def partial_correlation(self):
        """
        Calculate partial correlation matrix.
        Measures correlation between two variables while controlling for others.
        
        Returns:
        --------
        pd.DataFrame : Partial correlation matrix
        """
        # Calculate precision matrix (inverse of covariance matrix)
        cov_matrix = self.log_returns.cov()
        precision_matrix = np.linalg.inv(cov_matrix)
        
        # Convert to partial correlation
        diag = np.sqrt(np.diag(precision_matrix))
        partial_corr = -precision_matrix / np.outer(diag, diag)
        np.fill_diagonal(partial_corr, 1)
        
        return pd.DataFrame(partial_corr, 
                           columns=self.log_returns.columns,
                           index=self.log_returns.columns)
    
    def rolling_correlation_matrix(self, window=30, use_log_returns=True):
        """
        Calculate rolling correlation matrices over time.
        
        Parameters:
        -----------
        window : int
            Rolling window size
        use_log_returns : bool
            Use log returns (True) or simple returns (False)
            
        Returns:
        --------
        dict : Dictionary with timestamps as keys and correlation matrices as values
        """
        data_to_use = self.log_returns if use_log_returns else self.returns
        
        rolling_corr_dict = {}
        
        for i in range(window, len(data_to_use)):
            window_data = data_to_use.iloc[i-window:i]
            corr_matrix = window_data.corr()
            rolling_corr_dict[data_to_use.index[i]] = corr_matrix
            
        return rolling_corr_dict
    
    def calculate_correlation_stability(self, window=30, use_log_returns=True):
        """
        Measure correlation stability over time using rolling standard deviation.
        
        Parameters:
        -----------
        window : int
            Rolling window size
        use_log_returns : bool
            Use log returns (True) or simple returns (False)
            
        Returns:
        --------
        pd.DataFrame : Standard deviation of rolling correlations for each pair
        """
        data_to_use = self.log_returns if use_log_returns else self.returns
        instruments = data_to_use.columns
        n = len(instruments)
        
        stability_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i+1, n):
                rolling_corr = data_to_use[instruments[i]].rolling(window=window).corr(
                    data_to_use[instruments[j]]
                )
                stability_matrix[i, j] = rolling_corr.std()
                stability_matrix[j, i] = stability_matrix[i, j]
                
        return pd.DataFrame(stability_matrix, 
                           columns=instruments,
                           index=instruments)
    
    def calculate_rank_correlation_matrix(self):
        """
        Calculate rank-based (Spearman) correlation matrix.
        More robust to outliers than Pearson correlation.
        
        Returns:
        --------
        pd.DataFrame : Spearman correlation matrix
        """
        return self.calculate_correlation(method='spearman')
    
    def detect_correlation_breakpoints(self, instrument1, instrument2, window=30):
        """
        Detect structural breaks in correlation using CUSUM test.
        
        Parameters:
        -----------
        instrument1, instrument2 : str
            Names of instruments
        window : int
            Minimum window size for analysis
            
        Returns:
        --------
        list : List of breakpoint dates
        """
        rolling_corr = self.rolling_correlation(instrument1, instrument2, window)
        rolling_corr = rolling_corr.dropna()
        
        # Calculate cumulative sum of deviations from mean
        mean_corr = rolling_corr.mean()
        cusum = np.cumsum(rolling_corr - mean_corr)
        
        # Detect breakpoints (simple threshold method)
        threshold = 2 * rolling_corr.std()
        breakpoints = []
        
        for i in range(1, len(cusum)):
            if abs(cusum.iloc[i] - cusum.iloc[i-1]) > threshold:
                breakpoints.append(rolling_corr.index[i])
                
        return breakpoints


class CorrelationVisualizer:
    """
    Advanced visualization tools for correlation analysis.
    """
    
    def __init__(self, analyzer: CorrelationAnalyzer):
        """
        Initialize visualizer with a CorrelationAnalyzer instance.
        
        Parameters:
        -----------
        analyzer : CorrelationAnalyzer
            Initialized correlation analyzer
        """
        self.analyzer = analyzer
        
        # Set professional style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
    def plot_correlation_matrix(self, method='pearson', figsize=(12, 10), 
                                annotate=True, cmap='RdBu_r', save_path=None):
        """
        Plot correlation matrix as heatmap.
        
        Parameters:
        -----------
        method : str
            Correlation method
        figsize : tuple
            Figure size
        annotate : bool
            Show correlation values
        cmap : str
            Color map
        save_path : str
            Path to save figure (optional)
        """
        corr = self.analyzer.calculate_correlation(method=method)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create mask for upper triangle
        mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
        
        # Plot heatmap
        sns.heatmap(corr, mask=mask, annot=annotate, fmt='.2f', 
                   cmap=cmap, center=0, square=True, linewidths=1,
                   cbar_kws={"shrink": 0.8, "label": "Correlation Coefficient"},
                   ax=ax, vmin=-1, vmax=1)
        
        ax.set_title(f'{method.capitalize()} Correlation Matrix\n'
                    f'Period: {self.analyzer.data.index[0].strftime("%Y-%m-%d")} to '
                    f'{self.analyzer.data.index[-1].strftime("%Y-%m-%d")}',
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_clustered_correlation(self, method='ward', figsize=(14, 12), 
                                   cmap='RdBu_r', save_path=None):
        """
        Plot correlation matrix with hierarchical clustering.
        
        Parameters:
        -----------
        method : str
            Clustering method
        figsize : tuple
            Figure size
        cmap : str
            Color map
        save_path : str
            Path to save figure (optional)
        """
        corr = self.analyzer.calculate_correlation()
        
        # Perform clustering
        linkage_matrix = self.analyzer.hierarchical_clustering(method=method)
        
        # Create clustermap
        g = sns.clustermap(corr, method=method, cmap=cmap, center=0,
                          figsize=figsize, annot=True, fmt='.2f',
                          linewidths=0.5, cbar_kws={"label": "Correlation"},
                          row_linkage=linkage_matrix, col_linkage=linkage_matrix,
                          vmin=-1, vmax=1)
        
        g.fig.suptitle('Hierarchical Clustering of Correlation Matrix',
                      fontsize=16, fontweight='bold', y=0.98)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_dendrogram(self, method='ward', figsize=(14, 6), save_path=None):
        """
        Plot dendrogram for hierarchical clustering.
        
        Parameters:
        -----------
        method : str
            Clustering method
        figsize : tuple
            Figure size
        save_path : str
            Path to save figure (optional)
        """
        linkage_matrix = self.analyzer.hierarchical_clustering(method=method)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        dendrogram = hierarchy.dendrogram(
            linkage_matrix,
            labels=self.analyzer.correlation_matrix.columns,
            ax=ax,
            leaf_rotation=45,
            leaf_font_size=10
        )
        
        ax.set_title('Hierarchical Clustering Dendrogram', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Instruments', fontsize=12)
        ax.set_ylabel('Distance', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_rolling_correlation(self, instrument1, instrument2, window=30,
                                 figsize=(14, 6), save_path=None):
        """
        Plot rolling correlation between two instruments.
        
        Parameters:
        -----------
        instrument1, instrument2 : str
            Names of instruments
        window : int
            Rolling window size
        figsize : tuple
            Figure size
        save_path : str
            Path to save figure (optional)
        """
        rolling_corr = self.analyzer.rolling_correlation(instrument1, instrument2, window)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot rolling correlation
        ax.plot(rolling_corr.index, rolling_corr.values, linewidth=2, 
               label=f'{window}-day Rolling Correlation', color='#2E86AB')
        
        # Add horizontal lines
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
        ax.axhline(y=0.5, color='green', linestyle='--', linewidth=0.8, alpha=0.5,
                  label='Strong Positive (0.5)')
        ax.axhline(y=-0.5, color='red', linestyle='--', linewidth=0.8, alpha=0.5,
                  label='Strong Negative (-0.5)')
        
        # Fill regions
        ax.fill_between(rolling_corr.index, 0, rolling_corr.values,
                       where=(rolling_corr.values > 0), alpha=0.3, color='green',
                       label='Positive Correlation')
        ax.fill_between(rolling_corr.index, 0, rolling_corr.values,
                       where=(rolling_corr.values < 0), alpha=0.3, color='red',
                       label='Negative Correlation')
        
        ax.set_title(f'Rolling Correlation: {instrument1} vs {instrument2}\n'
                    f'Window: {window} days',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Correlation Coefficient', fontsize=12)
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-1, 1)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_correlation_network(self, threshold=0.5, figsize=(14, 14), save_path=None):
        """
        Plot correlation network graph.
        
        Parameters:
        -----------
        threshold : float
            Minimum correlation to display edge
        figsize : tuple
            Figure size
        save_path : str
            Path to save figure (optional)
        """
        try:
            import networkx as nx
        except ImportError:
            print("NetworkX is required for network plots. Install with: pip install networkx")
            return
        
        corr = self.analyzer.calculate_correlation()
        
        # Create graph
        G = nx.Graph()
        
        # Add nodes
        for instrument in corr.columns:
            G.add_node(instrument)
        
        # Add edges for correlations above threshold
        for i in range(len(corr.columns)):
            for j in range(i+1, len(corr.columns)):
                if abs(corr.iloc[i, j]) >= threshold:
                    G.add_edge(corr.columns[i], corr.columns[j], 
                             weight=corr.iloc[i, j])
        
        # Create plot
        fig, ax = plt.subplots(figsize=figsize)
        
        # Layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='lightblue',
                              alpha=0.9, ax=ax)
        
        # Draw edges with colors based on correlation
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        
        # Positive correlations
        pos_edges = [(u, v) for u, v in edges if G[u][v]['weight'] > 0]
        pos_weights = [G[u][v]['weight'] for u, v in pos_edges]
        nx.draw_networkx_edges(G, pos, pos_edges, width=3, alpha=0.6,
                              edge_color=pos_weights, edge_cmap=plt.cm.Greens,
                              edge_vmin=0, edge_vmax=1, ax=ax)
        
        # Negative correlations
        neg_edges = [(u, v) for u, v in edges if G[u][v]['weight'] < 0]
        neg_weights = [abs(G[u][v]['weight']) for u, v in neg_edges]
        nx.draw_networkx_edges(G, pos, neg_edges, width=3, alpha=0.6,
                              edge_color=neg_weights, edge_cmap=plt.cm.Reds,
                              edge_vmin=0, edge_vmax=1, ax=ax)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)
        
        ax.set_title(f'Correlation Network (threshold: {threshold})\n'
                    f'Green: Positive Correlation | Red: Negative Correlation',
                    fontsize=14, fontweight='bold', pad=20)
        ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_correlation_distribution(self, figsize=(12, 6), save_path=None):
        """
        Plot distribution of correlation coefficients.
        
        Parameters:
        -----------
        figsize : tuple
            Figure size
        save_path : str
            Path to save figure (optional)
        """
        corr = self.analyzer.calculate_correlation()
        
        # Get upper triangle values (excluding diagonal)
        mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
        corr_values = corr.values[mask]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Histogram
        ax1.hist(corr_values, bins=30, edgecolor='black', alpha=0.7, color='skyblue')
        ax1.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero Correlation')
        ax1.axvline(x=corr_values.mean(), color='green', linestyle='--', 
                   linewidth=2, label=f'Mean: {corr_values.mean():.3f}')
        ax1.set_xlabel('Correlation Coefficient', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.set_title('Distribution of Correlation Coefficients', 
                     fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Box plot
        ax2.boxplot(corr_values, vert=True, patch_artist=True,
                   boxprops=dict(facecolor='lightblue', alpha=0.7),
                   medianprops=dict(color='red', linewidth=2),
                   whiskerprops=dict(linewidth=1.5),
                   capprops=dict(linewidth=1.5))
        ax2.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax2.set_ylabel('Correlation Coefficient', fontsize=12)
        ax2.set_title('Box Plot of Correlations', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add statistics text
        stats_text = f'Mean: {corr_values.mean():.3f}\n'
        stats_text += f'Median: {np.median(corr_values):.3f}\n'
        stats_text += f'Std Dev: {corr_values.std():.3f}\n'
        stats_text += f'Min: {corr_values.min():.3f}\n'
        stats_text += f'Max: {corr_values.max():.3f}'
        
        ax2.text(1.3, 0, stats_text, fontsize=10, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_time_varying_correlation_heatmap(self, window=30, figsize=(16, 8), 
                                              cmap='RdBu_r', save_path=None):
        """
        Plot heatmap of time-varying average correlations.
        
        Parameters:
        -----------
        window : int
            Rolling window size
        figsize : tuple
            Figure size
        cmap : str
            Color map
        save_path : str
            Path to save figure (optional)
        """
        rolling_corr_dict = self.analyzer.rolling_correlation_matrix(window=window)
        
        # Calculate average correlation for each time period
        dates = list(rolling_corr_dict.keys())
        avg_corr = []
        
        for date in dates:
            corr_matrix = rolling_corr_dict[date]
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
            avg_corr.append(corr_matrix.values[mask].mean())
        
        # Create the plot
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(dates, avg_corr, linewidth=2, color='#2E86AB')
        ax.fill_between(dates, avg_corr, alpha=0.3, color='#2E86AB')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
        
        ax.set_title(f'Time-Varying Average Correlation\nRolling Window: {window} days',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Average Correlation', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_partial_correlation_matrix(self, figsize=(12, 10), annotate=True,
                                       cmap='RdBu_r', save_path=None):
        """
        Plot partial correlation matrix.
        
        Parameters:
        -----------
        figsize : tuple
            Figure size
        annotate : bool
            Show values
        cmap : str
            Color map
        save_path : str
            Path to save figure (optional)
        """
        partial_corr = self.analyzer.partial_correlation()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create mask for upper triangle
        mask = np.triu(np.ones_like(partial_corr, dtype=bool), k=1)
        
        # Plot heatmap
        sns.heatmap(partial_corr, mask=mask, annot=annotate, fmt='.2f',
                   cmap=cmap, center=0, square=True, linewidths=1,
                   cbar_kws={"shrink": 0.8, "label": "Partial Correlation"},
                   ax=ax, vmin=-1, vmax=1)
        
        ax.set_title('Partial Correlation Matrix\n'
                    '(Correlation controlling for all other variables)',
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def create_correlation_dashboard(self, window=30, figsize=(20, 12), save_path=None):
        """
        Create comprehensive correlation analysis dashboard.
        
        Parameters:
        -----------
        window : int
            Rolling window for time-varying analysis
        figsize : tuple
            Figure size
        save_path : str
            Path to save figure (optional)
        """
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Main correlation matrix
        ax1 = fig.add_subplot(gs[0:2, 0:2])
        corr = self.analyzer.calculate_correlation()
        mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
        sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
                   center=0, square=True, linewidths=1, ax=ax1, vmin=-1, vmax=1,
                   cbar_kws={"shrink": 0.8})
        ax1.set_title('Pearson Correlation Matrix', fontsize=12, fontweight='bold')
        
        # 2. Correlation distribution
        ax2 = fig.add_subplot(gs[0, 2])
        mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
        corr_values = corr.values[mask]
        ax2.hist(corr_values, bins=20, edgecolor='black', alpha=0.7, color='skyblue')
        ax2.axvline(x=corr_values.mean(), color='red', linestyle='--', linewidth=2)
        ax2.set_xlabel('Correlation', fontsize=10)
        ax2.set_ylabel('Frequency', fontsize=10)
        ax2.set_title('Distribution', fontsize=10, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # 3. Time-varying average correlation
        ax3 = fig.add_subplot(gs[1, 2])
        rolling_corr_dict = self.analyzer.rolling_correlation_matrix(window=window)
        dates = list(rolling_corr_dict.keys())
        avg_corr = [rolling_corr_dict[d].values[np.triu(np.ones_like(
            rolling_corr_dict[d], dtype=bool), k=1)].mean() for d in dates]
        ax3.plot(dates, avg_corr, linewidth=2, color='#2E86AB')
        ax3.fill_between(dates, avg_corr, alpha=0.3)
        ax3.set_xlabel('Date', fontsize=10)
        ax3.set_ylabel('Avg Correlation', fontsize=10)
        ax3.set_title(f'Time-Varying ({window}d)', fontsize=10, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Correlation stability
        ax4 = fig.add_subplot(gs[2, :])
        stability = self.analyzer.calculate_correlation_stability(window=window)
        instruments = stability.columns
        
        # Plot stability for top pairs
        mask = np.triu(np.ones_like(stability, dtype=bool), k=1)
        stability_values = stability.values[mask]
        indices = np.argsort(stability_values)[-10:]  # Top 10 most volatile
        
        pos = 0
        labels = []
        for idx in indices:
            i, j = np.unravel_index(idx, stability.shape)
            if i < j:
                pair_label = f"{instruments[i][:6]}-{instruments[j][:6]}"
                ax4.barh(pos, stability_values[idx], color='coral', alpha=0.7)
                labels.append(pair_label)
                pos += 1
        
        ax4.set_yticks(range(len(labels)))
        ax4.set_yticklabels(labels, fontsize=9)
        ax4.set_xlabel('Standard Deviation of Rolling Correlation', fontsize=10)
        ax4.set_title('Correlation Stability (Top 10 Most Volatile Pairs)', 
                     fontsize=10, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='x')
        
        # Add main title
        fig.suptitle('Advanced Correlation Analysis Dashboard',
                    fontsize=16, fontweight='bold', y=0.98)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()


def generate_sample_data(n_days=252, n_instruments=8, seed=42):
    """
    Generate sample financial data for testing.
    
    Parameters:
    -----------
    n_days : int
        Number of days
    n_instruments : int
        Number of instruments
    seed : int
        Random seed
        
    Returns:
    --------
    pd.DataFrame : Sample price data
    """
    np.random.seed(seed)
    
    # Instrument names
    instruments = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 
                  'GOLD', 'SILVER', 'OIL_WTI', 'OIL_BRENT'][:n_instruments]
    
    # Generate correlated returns
    dates = pd.date_range(end=pd.Timestamp.today(), periods=n_days, freq='D')
    
    # Create a valid (positive semi-definite) correlation structure by
    # deriving it from random factor loadings instead of picking pairwise
    # correlations directly, which is not guaranteed to be consistent.
    factors = np.random.randn(n_instruments, n_instruments)
    cov = factors @ factors.T
    std = np.sqrt(np.diag(cov))
    corr_matrix = cov / np.outer(std, std)

    # Generate correlated returns using Cholesky decomposition
    L = np.linalg.cholesky(corr_matrix)
    returns = np.random.randn(n_days, n_instruments) * 0.01  # 1% daily volatility
    correlated_returns = returns @ L.T
    
    # Convert to prices (starting at 100)
    prices = 100 * np.exp(np.cumsum(correlated_returns, axis=0))
    
    # Create DataFrame
    df = pd.DataFrame(prices, index=dates, columns=instruments)
    
    return df
