#!/usr/bin/env python3
"""
Advanced Correlation Analysis Tool
=================================
Outil interactif d'analyse de corrélation entre actifs financiers.

Auteur: clementchmlt
Date: Octobre 2025
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from correlation_analyzer import CorrelationAnalyzer, CorrelationVisualizer
from data_loader import prepare_correlation_data, load_single_asset

# Ignorer les avertissements pour une meilleure lisibilité
warnings.filterwarnings('ignore')

def clear_screen():
    """Nettoie l'écran de la console."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Affiche l'en-tête du programme."""
    clear_screen()
    print("=" * 80)
    print("ANALYSE DE CORRÉLATION AVANCÉE")
    print("=" * 80)
    print("Développé par clementchmlt")
    print()

def select_assets():
    """Interface pour sélectionner les actifs à analyser."""
    print_header()
    print("ÉTAPE 1: Sélection des actifs à analyser")
    print("-" * 80)
    
    # Options disponibles
    print("Options disponibles:")
    print("1. Sélectionner des fichiers CSV spécifiques")
    print("2. Analyser tous les fichiers CSV d'un répertoire")
    print()
    
    while True:
        try:
            choice = int(input("Votre choix (1-2): "))
            if 1 <= choice <= 2:
                break
            print("Choix invalide. Veuillez entrer un nombre entre 1 et 2.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")
    
    if choice == 1:
        # Sélection de fichiers spécifiques
        print("\nRecherche des fichiers CSV disponibles...")
        
        # Chercher les fichiers CSV dans les répertoires courants
        csv_files = []
        search_dirs = [".", "data", "../data"]
        
        for directory in search_dirs:
            if os.path.exists(directory):
                csv_files.extend(glob.glob(os.path.join(directory, "*.csv")))
        
        if not csv_files:
            print("⚠️ Aucun fichier CSV trouvé dans les répertoires courants.")
            print("Veuillez entrer le chemin complet vers vos fichiers CSV:")
            user_path = input("Chemin du répertoire: ")
            
            if os.path.exists(user_path):
                csv_files = glob.glob(os.path.join(user_path, "*.csv"))
            else:
                print("⚠️ Chemin invalide. Impossible de continuer.")
                return None, "aucune donnée valide"
        
        if not csv_files:
            print("⚠️ Aucun fichier CSV trouvé. Impossible de continuer.")
            return None, "aucune donnée valide"
        
        # Afficher les fichiers disponibles
        print("\nFichiers disponibles:")
        for i, file_path in enumerate(csv_files, 1):
            asset_name = os.path.splitext(os.path.basename(file_path))[0]
            print(f"{i}. {asset_name} ({file_path})")
        
        # Sélection des fichiers
        print("\nSélectionnez les fichiers à analyser (ex: 1,3,5 ou 'all' pour tous):")
        selection = input("Votre sélection: ")
        
        selected_files = []
        if selection.lower() == 'all':
            selected_files = csv_files
        else:
            try:
                indices = [int(idx.strip()) for idx in selection.split(',')]
                selected_files = [csv_files[idx-1] for idx in indices if 1 <= idx <= len(csv_files)]
            except (ValueError, IndexError):
                print("⚠️ Sélection invalide. Utilisation des 3 premiers fichiers.")
                selected_files = csv_files[:min(3, len(csv_files))]
        
        # Charger les données
        print(f"\nChargement de {len(selected_files)} fichiers...")
        data = prepare_correlation_data(selected_files, is_directory=False)
        
        if data is None or data.empty or len(data.columns) < 2:
            print("⚠️ Erreur lors du chargement des données ou données insuffisantes.")
            return None, "données insuffisantes"
        
        asset_desc = ", ".join([os.path.splitext(os.path.basename(f))[0] for f in selected_files])
        return data, f"fichiers sélectionnés: {asset_desc}"
    
    else:  # choice == 2
        # Analyser un répertoire
        print("\nRecherche des répertoires disponibles...")
        
        # Chercher les répertoires contenant des CSV
        possible_dirs = [".", "data", "../data"]
        valid_dirs = [d for d in possible_dirs if os.path.exists(d) and glob.glob(os.path.join(d, "*.csv"))]
        
        selected_dir = "."
        if valid_dirs:
            print("Répertoires contenant des fichiers CSV:")
            for i, directory in enumerate(valid_dirs, 1):
                n_files = len(glob.glob(os.path.join(directory, "*.csv")))
                print(f"{i}. {directory} ({n_files} fichiers CSV)")
            
            choice_input = input("\nSélectionnez un répertoire (ou entrez un chemin personnalisé): ")
            
            # Si l'input est un nombre, c'est un choix dans la liste
            if choice_input.isdigit():
                dir_choice = int(choice_input)
                if 1 <= dir_choice <= len(valid_dirs):
                    selected_dir = valid_dirs[dir_choice-1]
                else:
                    print("Choix invalide. Utilisation du répertoire courant.")
            # Sinon, c'est un chemin personnalisé
            else:
                selected_dir = choice_input.strip()
        else:
            selected_dir = input("Aucun répertoire avec des CSV trouvé. Entrez le chemin du répertoire: ")
        
        # Vérifier si le répertoire existe et contient des CSV
        if not os.path.exists(selected_dir) or not glob.glob(os.path.join(selected_dir, "*.csv")):
            print("⚠️ Répertoire invalide ou vide. Impossible de continuer.")
            return None, "aucune donnée valide"
        
        # Charger les données
        print(f"\nChargement des fichiers CSV depuis {selected_dir}...")
        try:
            data = prepare_correlation_data(selected_dir, is_directory=True)
            
            if data is None or data.empty or len(data.columns) < 2:
                print("⚠️ Erreur lors du chargement des données ou données insuffisantes.")
                return None, "données insuffisantes"
            
            n_assets = len(data.columns)
            return data, f"{n_assets} actifs depuis {selected_dir}"
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement des données: {e}")
            print("Détails techniques pour le débogage:")
            import traceback
            traceback.print_exc()
            return None, "erreur de chargement"

def configure_analysis(data):
    """Interface pour configurer les paramètres d'analyse."""
    print_header()
    print("ÉTAPE 2: Configuration de l'analyse")
    print("-" * 80)
    
    print("Options disponibles:")
    
    # Méthode de corrélation
    print("\n1. Méthode de corrélation:")
    print("   1. Pearson - corrélation linéaire (paramétrique)")
    print("   2. Spearman - corrélation par rang (non-paramétrique)")
    print("   3. Kendall - corrélation tau (pour données ordinales)")
    
    while True:
        try:
            method_choice = int(input("\nSélectionnez une méthode (1-3, défaut: 1): ") or 1)
            if 1 <= method_choice <= 3:
                break
            print("Choix invalide. Veuillez entrer un nombre entre 1 et 3.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")
    
    methods = ['pearson', 'spearman', 'kendall']
    method = methods[method_choice-1]
    
    # Taille de fenêtre roulante
    print("\n2. Taille de la fenêtre pour l'analyse roulante:")
    
    # Suggérer une taille de fenêtre en fonction de la longueur des données
    suggested_window = min(30, max(5, len(data) // 10))
    
    while True:
        try:
            window = int(input(f"Nombre de jours (5-{len(data)//2}, défaut: {suggested_window}): ") or suggested_window)
            if 5 <= window <= len(data) // 2:
                break
            print(f"Veuillez entrer un nombre entre 5 et {len(data)//2}.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")
    
    # Paire d'actifs pour analyse détaillée (optionnel)
    pair = None
    if len(data.columns) >= 2:
        print("\n3. Paire d'actifs pour analyse détaillée (optionnel):")
        
        for i, asset in enumerate(data.columns, 1):
            print(f"   {i}. {asset}")
        
        print("\nSélectionnez deux actifs pour une analyse détaillée (ex: 1,3)")
        print("(Laisser vide pour ignorer l'analyse de paire)")
        
        selection = input("Votre sélection (optionnel): ")
        
        if selection:
            try:
                indices = [int(idx.strip()) for idx in selection.split(',')]
                if len(indices) >= 2 and all(1 <= idx <= len(data.columns) for idx in indices[:2]):
                    pair = [data.columns[idx-1] for idx in indices[:2]]
                    print(f"Paire sélectionnée: {pair[0]} vs {pair[1]}")
                else:
                    print("⚠️ Sélection invalide. Analyse de paire ignorée.")
            except (ValueError, IndexError):
                print("⚠️ Format invalide. Analyse de paire ignorée.")
    
    return {
        'method': method,
        'window': window,
        'pair': pair
    }

def select_visualizations(has_pair=False):
    """Interface pour sélectionner les visualisations à générer."""
    print_header()
    print("ÉTAPE 3: Sélection des visualisations")
    print("-" * 80)
    
    all_graphs = [
        "matrix", "clustered", "dendrogram", 
        "distribution", "partial", "network", "time_varying", "dashboard"
    ]
    
    # Ajouter "rolling" seulement si une paire a été sélectionnée
    if has_pair:
        all_graphs.insert(3, "rolling")
    
    all_graphs.append("all")
    
    descriptions = {
        "matrix": "Matrice de corrélation simple",
        "clustered": "Matrice de corrélation avec clustering hiérarchique",
        "dendrogram": "Dendrogramme des relations entre actifs",
        "rolling": "Analyse de corrélation roulante (nécessite une paire d'actifs)",
        "distribution": "Distribution des coefficients de corrélation",
        "partial": "Matrice de corrélation partielle",
        "network": "Graphique réseau des corrélations",
        "time_varying": "Évolution temporelle des corrélations moyennes",
        "dashboard": "Tableau de bord complet (résumé visuel)",
        "all": "Toutes les visualisations disponibles"
    }
    
    print("Visualisations disponibles:")
    for i, graph_type in enumerate(all_graphs, 1):
        print(f"{i}. {graph_type:12} - {descriptions[graph_type]}")
    
    print("\nSélectionnez les visualisations à générer (ex: 1,3,5 ou 'all' pour toutes):")
    selection = input("Votre sélection (défaut: 1,9): ") or "1,9"
    
    selected_graphs = []
    if selection.lower() == "all" or str(len(all_graphs)) in selection:
        selected_graphs = ["all"]
    else:
        try:
            indices = [int(idx.strip()) for idx in selection.split(',')]
            selected_graphs = [all_graphs[idx-1] for idx in indices if 1 <= idx <= len(all_graphs)]
        except (ValueError, IndexError):
            print("⚠️ Sélection invalide. Utilisation de la matrice et du tableau de bord.")
            selected_graphs = ["matrix", "dashboard"]
    
    # Si "all" est sélectionné, remplacer par la liste complète sauf "all"
    if "all" in selected_graphs:
        selected_graphs = [g for g in all_graphs if g != "all"]
        
        # Supprimer "rolling" si aucune paire n'est sélectionnée
        if not has_pair and "rolling" in selected_graphs:
            selected_graphs.remove("rolling")
    
    return selected_graphs

def configure_output():
    """Interface pour configurer les options de sortie."""
    print_header()
    print("ÉTAPE 4: Configuration de la sortie")
    print("-" * 80)
    
    # Préfixe de sortie
    print("1. Préfixe pour les fichiers de sortie:")
    prefix = input("Préfixe (défaut: correlation_output): ") or "correlation_output"
    
    # Format des graphiques
    print("\n2. Format des fichiers graphiques:")
    print("   1. PNG - format standard (défaut)")
    print("   2. JPG - taille réduite")
    print("   3. SVG - vectoriel, pour l'édition")
    print("   4. PDF - pour l'impression")
    
    while True:
        try:
            format_choice = int(input("\nSélectionnez un format (1-4, défaut: 1): ") or 1)
            if 1 <= format_choice <= 4:
                break
            print("Choix invalide. Veuillez entrer un nombre entre 1 et 4.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")
    
    formats = ['png', 'jpg', 'svg', 'pdf']
    file_format = formats[format_choice-1]
    
    # Résolution
    print("\n3. Résolution des images:")
    
    while True:
        try:
            dpi = int(input("DPI (100-600, défaut: 300): ") or 300)
            if 100 <= dpi <= 600:
                break
            print("Veuillez entrer un nombre entre 100 et 600.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")
    
    # Mode d'affichage
    print("\n4. Affichage des graphiques:")
    print("   1. Afficher et sauvegarder")
    print("   2. Sauvegarder uniquement (sans affichage)")
    
    while True:
        try:
            display_choice = int(input("\nVotre choix (1-2, défaut: 1): ") or 1)
            if 1 <= display_choice <= 2:
                break
            print("Choix invalide. Veuillez entrer un nombre entre 1 et 2.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")
    
    no_display = (display_choice == 2)
    
    return {
        'output': prefix,
        'format': file_format,
        'dpi': dpi,
        'no_display': no_display
    }

def safe_plot_function(plot_func, *args, **kwargs):
    """
    Exécute une fonction de tracé de manière sécurisée en capturant les exceptions.
    
    Parameters:
    -----------
    plot_func : function
        Fonction de tracé à exécuter
    *args, **kwargs:
        Arguments à passer à la fonction de tracé
    
    Returns:
    --------
    bool: True si le tracé a réussi, False sinon
    """
    try:
        plot_func(*args, **kwargs)
        return True
    except Exception as e:
        print(f"    ⚠️ Erreur lors du tracé: {e}")
        return False

def main():
    """
    Point d'entrée principal avec interface interactive.
    """
    print_header()
    print("Bienvenue dans l'outil d'analyse de corrélation avancée!")
    print("\nCet outil vous permet d'analyser les relations entre différents actifs financiers.")
    print("Suivez les instructions pour configurer votre analyse.")
    print("\nAppuyez sur Entrée pour commencer...")
    input()
    
    # ÉTAPE 1: Sélection des actifs
    data, data_desc = select_assets()
    
    # Vérification que les données sont valides
    if data is None:
        print("\nImpossible de continuer sans données valides. Programme terminé.")
        return
    
    # ÉTAPE 2: Configuration de l'analyse
    config = configure_analysis(data)
    
    # ÉTAPE 3: Sélection des visualisations
    graphs = select_visualizations(has_pair=config['pair'] is not None)
    
    # ÉTAPE 4: Configuration de la sortie
    output_config = configure_output()
    
    # Résumé de la configuration
    print_header()
    print("RÉSUMÉ DE LA CONFIGURATION")
    print("-" * 80)
    print(f"• Données: {data_desc}")
    print(f"• Dimensions: {len(data)} points temporels × {len(data.columns)} actifs")
    print(f"• Période: {data.index.min().date()} à {data.index.max().date()}")
    print(f"• Méthode de corrélation: {config['method']}")
    print(f"• Taille de fenêtre: {config['window']} jours")
    
    if config['pair']:
        print(f"• Paire analysée: {config['pair'][0]} vs {config['pair'][1]}")
    
    print(f"• Visualisations: {', '.join(graphs)}")
    print(f"• Préfixe de sortie: {output_config['output']}")
    print(f"• Format: {output_config['format'].upper()} ({output_config['dpi']} DPI)")
    print(f"• Mode: {'Sauvegarde uniquement' if output_config['no_display'] else 'Affichage et sauvegarde'}")
    
    print("\nAppuyez sur Entrée pour lancer l'analyse ou Ctrl+C pour annuler...")
    input()
    
    # Si no_display est activé, configurer matplotlib pour ne pas afficher
    if output_config['no_display']:
        plt.ioff()  # Désactiver le mode interactif
    
    # Exécution de l'analyse
    print_header()
    print("EXÉCUTION DE L'ANALYSE")
    print("-" * 80)
    
    # Initialisation de l'analyseur
    print("1. Initialisation de l'analyseur de corrélation")
    print("-" * 60)
    analyzer = CorrelationAnalyzer(data)
    print("✓ Analyseur initialisé")
    print(f"  - Points de données de prix: {len(data)}")
    print(f"  - Points de données de rendement: {len(analyzer.returns)}")
    print()
    
    # Calcul des corrélations
    print("2. Calcul des matrices de corrélation")
    print("-" * 60)
    
    # Corrélation avec la méthode spécifiée
    print(f"2.1 Matrice de corrélation ({config['method']}):")
    correlation = analyzer.calculate_correlation(method=config['method'])
    
    # Vérifier s'il y a des valeurs problématiques
    has_nan = np.isnan(correlation.values).any()
    has_perfect_corr = (np.abs(correlation.values) > 0.999).any()
    
    if has_nan:
        print("⚠️ Attention: La matrice de corrélation contient des valeurs manquantes (NaN).")
        print("   Certaines analyses pourraient échouer ou donner des résultats non fiables.")
    
    if has_perfect_corr:
        print("⚠️ Attention: Certaines corrélations sont presque parfaites (±1.0).")
        print("   Cela peut indiquer des problèmes dans les données ou des relations directes.")
    
    print(correlation.round(3))
    print()
    
    # P-values
    print("2.2 Signification statistique (P-values):")
    try:
        pvalues = analyzer.calculate_pvalues()
        print(pvalues.round(4))
    except Exception as e:
        print(f"⚠️ Impossible de calculer les p-values: {e}")
    print()
    
    # Analyse d'une paire spécifique si demandée
    if config['pair']:
        instrument1, instrument2 = config['pair']
        print(f"2.3 Analyse spécifique de la paire {instrument1} vs {instrument2}:")
        
        try:
            # Corrélation simple
            corr_value = correlation.loc[instrument1, instrument2]
            print(f"  - Corrélation {config['method']}: {corr_value:.4f}")
            
            # P-value si disponible
            if 'pvalues' in locals() and not np.isnan(pvalues.loc[instrument1, instrument2]):
                pval = pvalues.loc[instrument1, instrument2]
                print(f"  - P-value: {pval:.4f} {'(significatif)' if pval < 0.05 else '(non significatif)'}")
            
            # Tail dependence
            tail_dep = analyzer.calculate_tail_dependence(instrument1, instrument2, quantile=0.05)
            print(f"  - Dépendance de queue inférieure (5%): {tail_dep['lower_tail']:.4f}")
            print(f"  - Dépendance de queue supérieure (95%): {tail_dep['upper_tail']:.4f}")
            
            # Détection de ruptures structurelles
            try:
                breakpoints = analyzer.detect_correlation_breakpoints(instrument1, instrument2, window=config['window'])
                if breakpoints:
                    print(f"  - Ruptures structurelles détectées: {len(breakpoints)}")
                    print(f"    Premières dates: {[bp.date() for bp in breakpoints[:3]]}")
                else:
                    print("  - Aucune rupture structurelle détectée")
            except Exception as e:
                print(f"  - Impossible de détecter les ruptures structurelles: {e}")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'analyse de paire: {e}")
        print()
    
    # Initialisation du visualiseur
    print("3. Création des visualisations")
    print("-" * 60)
    visualizer = CorrelationVisualizer(analyzer)
    
    # Définir les paramètres communs pour toutes les visualisations
    viz_params = {
        'save_path': None,  # Sera défini pour chaque graphique
        'figsize': (12, 10) if 'dashboard' not in graphs else (20, 12)
    }
    
    # Création des visualisations demandées
    print("Génération des graphiques:")
    
    for graph_type in graphs:
        viz_params['save_path'] = f"{output_config['output']}_{graph_type}.{output_config['format']}"
        
        if graph_type == "matrix":
            print("  • Heatmap de la matrice de corrélation...")
            safe_plot_function(
                visualizer.plot_correlation_matrix,
                method=config['method'],
                save_path=viz_params['save_path']
            )
        
        elif graph_type == "clustered":
            print("  • Matrice de corrélation avec clustering...")
            # Vérifier s'il y a des valeurs manquantes ou infinies
            if has_nan:
                print("    ⚠️ Impossible de générer le clustering car la matrice contient des valeurs NaN.")
                continue
                
            safe_plot_function(
                visualizer.plot_clustered_correlation,
                save_path=viz_params['save_path']
            )
        
        elif graph_type == "dendrogram":
            print("  • Dendrogramme de clustering hiérarchique...")
            # Vérifier s'il y a des valeurs manquantes ou infinies
            if has_nan:
                print("    ⚠️ Impossible de générer le dendrogramme car la matrice contient des valeurs NaN.")
                continue
                
            safe_plot_function(
                visualizer.plot_dendrogram,
                save_path=viz_params['save_path']
            )
        
        elif graph_type == "rolling" and config['pair']:
            instrument1, instrument2 = config['pair']
            print(f"  • Corrélation roulante ({instrument1} vs {instrument2})...")
            safe_plot_function(
                visualizer.plot_rolling_correlation,
                instrument1, instrument2,
                window=config['window'],
                save_path=viz_params['save_path']
            )
        
        elif graph_type == "distribution":
            print("  • Distribution des corrélations...")
            safe_plot_function(
                visualizer.plot_correlation_distribution,
                save_path=viz_params['save_path']
            )
        
        elif graph_type == "partial":
            print("  • Matrice de corrélation partielle...")
            # Vérifier s'il y a des valeurs manquantes
            if has_nan:
                print("    ⚠️ Impossible de générer la corrélation partielle car la matrice contient des valeurs NaN.")
                continue
                
            safe_plot_function(
                visualizer.plot_partial_correlation_matrix,
                save_path=viz_params['save_path']
            )
        
        elif graph_type == "network":
            print("  • Réseau de corrélation...")
            try:
                import networkx
                # Vérifier s'il y a des valeurs manquantes
                if has_nan:
                    print("    ⚠️ Impossible de générer le réseau car la matrice contient des valeurs NaN.")
                    continue
                    
                safe_plot_function(
                    visualizer.plot_correlation_network,
                    threshold=0.5,
                    save_path=viz_params['save_path']
                )
            except ImportError:
                print("    ⚠️ Bibliothèque networkx non installée. Graphique réseau ignoré.")
                print("       Installez avec: pip install networkx")
        
        elif graph_type == "time_varying":
            print("  • Heatmap de corrélation variable dans le temps...")
            # Vérifier s'il y a assez de données pour l'analyse temporelle
            if len(data) < config['window'] * 2:
                print(f"    ⚠️ Pas assez de données pour l'analyse temporelle avec fenêtre de {config['window']}.")
                continue
                
            safe_plot_function(
                visualizer.plot_time_varying_correlation_heatmap,
                window=config['window'],
                save_path=viz_params['save_path']
            )
        
        elif graph_type == "dashboard":
            print("  • Tableau de bord complet...")
            safe_plot_function(
                visualizer.create_correlation_dashboard,
                window=config['window'],
                save_path=viz_params['save_path']
            )
    
    # Export des résultats en Excel
    print("\n4. Exportation des résultats")
    print("-" * 60)
    
    excel_path = f"{output_config['output']}_results.xlsx"
    print(f"Exportation vers Excel: {excel_path}")
    
    try:
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Exportation des données de base
            correlation.round(4).to_excel(writer, sheet_name=f'{config["method"].capitalize()}_Correlation')
            
            # Tentative d'exportation des p-values si disponibles
            if 'pvalues' in locals():
                pvalues.round(4).to_excel(writer, sheet_name='P_Values')
            
            # Tentative d'exportation de la corrélation partielle
            try:
                partial_corr = analyzer.partial_correlation()
                partial_corr.round(4).to_excel(writer, sheet_name='Partial_Correlation')
            except Exception as e:
                print(f"⚠️ Impossible d'exporter les corrélations partielles: {e}")
            
            # Tentative d'exportation de la stabilité
            try:
                stability = analyzer.calculate_correlation_stability(window=config['window'])
                stability.round(4).to_excel(writer, sheet_name='Correlation_Stability')
            except Exception as e:
                print(f"⚠️ Impossible d'exporter la stabilité des corrélations: {e}")
            
            # Exportation des données d'origine
            data.to_excel(writer, sheet_name='Raw_Data')
        
        print("✓ Exportation terminée avec succès!")
    except Exception as e:
        print(f"⚠️ Erreur lors de l'exportation vers Excel: {e}")
    
    print("\n" + "=" * 80)
    print("ANALYSE TERMINÉE!")
    print("=" * 80)
    print(f"\nFichiers générés dans le répertoire courant avec le préfixe: {output_config['output']}_")
    print("\nMerci d'avoir utilisé l'outil d'analyse de corrélation avancée.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalyse annulée par l'utilisateur.")
    except Exception as e:
        print(f"\n\nUne erreur inattendue est survenue: {e}")
        print("Détails de l'erreur:")
        import traceback
        traceback.print_exc()