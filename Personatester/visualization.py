import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from questions import NASA_TLX_SUBSCALES_PAPER # Import for TLX subscale names

def generate_standard_visualizations(df, numeric_cols_from_main, output_dir='visualizations'):
    print(f"\n--- Generating Standard Visualizations (saving to ./{output_dir}) ---")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Set a consistent style
    sns.set_theme(style="whitegrid")

    # 1. SUS Scores Comparison (Bar and Box)
    if 'Original_SUS_Score' in df.columns and 'Adaptive_SUS_Score' in df.columns:
        plt.figure(figsize=(10, 6))
        
        plt.subplot(1, 2, 1)
        sus_means = df[['Original_SUS_Score', 'Adaptive_SUS_Score']].mean()
        sus_means.plot(kind='bar', color=['skyblue', 'lightcoral'])
        plt.title('Mean SUS Scores (0-100)')
        plt.ylabel('Mean SUS Score')
        plt.xticks(rotation=0)
        plt.ylim(0, 100) # SUS scores are 0-100

        plt.subplot(1, 2, 2)
        sns.boxplot(data=df[['Original_SUS_Score', 'Adaptive_SUS_Score']].rename(columns={'Original_SUS_Score': 'Original', 'Adaptive_SUS_Score': 'Adaptive'}))
        plt.title('Distribution of SUS Scores')
        plt.ylabel('SUS Score')
        plt.ylim(0, 100)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'sus_scores_comparison.png'))
        plt.close()
        print("Generated: sus_scores_comparison.png")

    # 2. Overall TLX Scores Comparison (Bar and Box)
    if 'Original_TLX_Overall' in df.columns and 'Adaptive_TLX_Overall' in df.columns:
        plt.figure(figsize=(10, 6))
        
        plt.subplot(1, 2, 1)
        tlx_means = df[['Original_TLX_Overall', 'Adaptive_TLX_Overall']].mean()
        tlx_means.plot(kind='bar', color=['skyblue', 'lightcoral'])
        plt.title('Mean Overall NASA-TLX Scores')
        plt.ylabel('Mean TLX Score')
        plt.xticks(rotation=0)
        # Assuming TLX scores are roughly 1-20 or 0-100 after scaling, adjust if needed
        # For now, let's use a dynamic upper limit based on data, or a common TLX range.
        # If raw TLX subscales are 1-20, average is also 1-20. If weighted/scaled, it might be 0-100.
        # Our current TLX is an average of 1-5 ratings, so it's 1-5.
        plt.ylim(1, 5) 

        plt.subplot(1, 2, 2)
        sns.boxplot(data=df[['Original_TLX_Overall', 'Adaptive_TLX_Overall']].rename(columns={'Original_TLX_Overall': 'Original', 'Adaptive_TLX_Overall': 'Adaptive'}))
        plt.title('Distribution of Overall TLX Scores')
        plt.ylabel('Overall TLX Score')
        plt.ylim(1, 5)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'tlx_overall_scores_comparison.png'))
        plt.close()
        print("Generated: tlx_overall_scores_comparison.png")

    # # 3. Performance Metrics Comparison (Automated)
    # print("\n--- Generating Performance Metric Visualizations ---")
    # perf_metric_stems = set()
    # for col in numeric_cols_from_main: # Use the passed list of numeric columns
    #     if col.startswith("Original_Time_") or col.startswith("Original_Errors_"):
    #         perf_metric_stems.add(col.replace("Original_", ""))
    #     elif col.startswith("Adaptive_Time_") or col.startswith("Adaptive_Errors_"):
    #         # This case helps catch stems if only an Adaptive version exists, though less common
    #         perf_metric_stems.add(col.replace("Adaptive_", ""))

    # if not perf_metric_stems:
    #     print("No performance metric stems found to visualize.")
    # else:
    #     for stem in sorted(list(perf_metric_stems)):
    #         orig_col = f"Original_{stem}"
    #         adap_col = f"Adaptive_{stem}"
            
    #         if orig_col in df.columns and adap_col in df.columns:
    #             plt.figure(figsize=(10, 6))
    #             metric_title_name = stem.replace('_', ' ').title()

    #             # Ensure columns are numeric before plotting
    #             df[orig_col] = pd.to_numeric(df[orig_col], errors='coerce')
    #             df[adap_col] = pd.to_numeric(df[adap_col], errors='coerce')

    #             # Bar Chart of Means
    #             plt.subplot(1, 2, 1)
    #             try:
    #                 perf_means = df[[orig_col, adap_col]].mean()
    #                 perf_means.plot(kind='bar', color=['skyblue', 'lightcoral'])
    #                 plt.title(f'Mean {metric_title_name}')
    #                 plt.ylabel(f'Mean {stem.split("_")[-1].title()}') # e.g., Seconds or Count
    #                 plt.xticks(rotation=0)
    #             except Exception as e:
    #                 print(f"Could not plot bar chart for {metric_title_name}: {e}")
    #                 plt.title(f'Mean {metric_title_name} (Error)')

    #             # Box Plot of Distributions
    #             plt.subplot(1, 2, 2)
    #             try:
    #                 sns.boxplot(data=df[[orig_col, adap_col]])
    #                 plt.title(f'Distribution of {metric_title_name}')
    #                 plt.ylabel(f'{stem.split("_")[-1].title()}') # e.g., Seconds or Count
    #             except Exception as e:
    #                 print(f"Could not plot boxplot for {metric_title_name}: {e}")
    #                 plt.title(f'Distribution of {metric_title_name} (Error)')
                
    #             plt.tight_layout()
    #             plot_filename = f'perf_{stem.lower()}.png'
    #             plt.savefig(os.path.join(output_dir, plot_filename))
    #             plt.close()
    #             print(f"Generated: {plot_filename}")
    #         else:
    #             print(f"Skipping plots for performance metric '{stem}': Original or Adaptive column missing.")

    # 4. Individual NASA-TLX Subscale Comparisons
    print("\n--- Generating Individual NASA-TLX Subscale Visualizations ---")
    for subscale in NASA_TLX_SUBSCALES_PAPER:
        orig_col = f"Original_TLX_{subscale}"
        adap_col = f"Adaptive_TLX_{subscale}"
        subscale_title_name = subscale.replace('_', ' ').title()

        if orig_col in df.columns and adap_col in df.columns:
            plt.figure(figsize=(10, 6))

            # Ensure columns are numeric
            df[orig_col] = pd.to_numeric(df[orig_col], errors='coerce')
            df[adap_col] = pd.to_numeric(df[adap_col], errors='coerce')

            # Bar Chart of Means
            plt.subplot(1, 2, 1)
            try:
                subscale_means = df[[orig_col, adap_col]].mean()
                subscale_means.plot(kind='bar', color=['skyblue', 'lightcoral'])
                plt.title(f'Mean TLX {subscale_title_name}')
                plt.ylabel('Mean Rating (1-5)')
                plt.xticks(rotation=0)
                plt.ylim(1, 5) # Raw TLX subscale ratings are 1-5
            except Exception as e:
                print(f"Could not plot bar chart for TLX {subscale_title_name}: {e}")
                plt.title(f'Mean TLX {subscale_title_name} (Error)')

            # Box Plot of Distributions
            plt.subplot(1, 2, 2)
            try:
                sns.boxplot(data=df[[orig_col, adap_col]].rename(columns={orig_col: 'Original', adap_col: 'Adaptive'}))
                plt.title(f'Distribution of TLX {subscale_title_name}')
                plt.ylabel('Rating (1-5)')
                plt.ylim(1, 5)
            except Exception as e:
                print(f"Could not plot boxplot for TLX {subscale_title_name}: {e}")
                plt.title(f'Distribution of TLX {subscale_title_name} (Error)')
            
            plt.tight_layout()
            plot_filename = f'tlx_subscale_{subscale.lower()}.png'
            plt.savefig(os.path.join(output_dir, plot_filename))
            plt.close()
            print(f"Generated: {plot_filename}")
        else:
            print(f"Skipping plots for TLX subscale '{subscale_title_name}': Original or Adaptive column missing.")

    # # 5. Visualizing Distributions of Change Scores (COMMENTED OUT as per user request to reduce visual clutter)
    # print("\n--- Generating Visualizations for Change Score Distributions ---")
    # change_score_columns = [col for col in df.columns if col.endswith('_Change')]

    # if not change_score_columns:
    #     print("No '..._Change' columns found to visualize their distributions.")
    # else:
    #     for change_col in sorted(change_score_columns):
    #         if pd.api.types.is_numeric_dtype(df[change_col]):
    #             plt.figure(figsize=(12, 5))
    #             title_name = change_col.replace('_', ' ').title()

    #             # Histogram of Change Scores
    #             plt.subplot(1, 2, 1)
    #             try:
    #                 sns.histplot(df[change_col].dropna(), kde=True, bins=15)
    #                 plt.title(f'Distribution of {title_name}')
    #                 plt.xlabel(title_name)
    #                 plt.ylabel('Frequency')
    #             except Exception as e:
    #                 print(f"Could not plot histogram for {title_name}: {e}")
    #                 plt.title(f'Histogram for {title_name} (Error)')

    #             # Box Plot of Change Scores
    #             plt.subplot(1, 2, 2)
    #             try:
    #                 sns.boxplot(y=df[change_col].dropna())
    #                 plt.title(f'Box Plot of {title_name}')
    #                 plt.ylabel(title_name)
    #             except Exception as e:
    #                 print(f"Could not plot boxplot for {title_name}: {e}")
    #                 plt.title(f'Box Plot for {title_name} (Error)')
                
    #             plt.tight_layout()
    #             plot_filename = f'change_dist_{change_col.lower().replace("_change", "")}.png'
    #             plt.savefig(os.path.join(output_dir, plot_filename))
    #             plt.close()
    #             print(f"Generated: {plot_filename}")
    #         else:
    #             print(f"Skipping distribution plots for non-numeric change column: {change_col}")

    print("--- Standard Visualization Generation Complete ---")

def generate_grouped_bar_chart_for_segment(df, segment_attribute, value_columns, title_prefix, y_label, output_dir='visualizations', y_limit=None):
    if not all(col in df.columns for col in value_columns):
        print(f"Skipping grouped bar chart for {title_prefix} by {segment_attribute}: one or more value columns missing.")
        return
    if segment_attribute not in df.columns:
        print(f"Skipping grouped bar chart for {title_prefix} by {segment_attribute}: segment attribute column missing.")
        return

    plt.figure(figsize=(10, 6))
    try:
        # Group by the segment attribute and calculate the mean of the value columns
        # Ensure that value_columns are numeric before mean calculation
        for col in value_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        grouped_data = df.groupby(segment_attribute)[value_columns].mean()
        
        if grouped_data.empty:
            print(f"No data to plot for {title_prefix} by {segment_attribute} after grouping.")
            plt.close()
            return

        grouped_data.plot(kind='bar', ax=plt.gca()) # Use ax=plt.gca() to plot on the current figure's axes
        
        plt.title(f'{title_prefix} by {segment_attribute.replace("_", " ").title()}')
        plt.ylabel(y_label)
        plt.xlabel(segment_attribute.replace("_", " ").title())
        plt.xticks(rotation=45, ha='right')
        if y_limit:
            plt.ylim(y_limit)
        plt.legend(title='Scenario')
        plt.tight_layout()
        
        filename = f'{title_prefix.lower().replace(" ", "_")}_by_{segment_attribute}.png'
        plt.savefig(os.path.join(output_dir, filename))
        plt.close()
        print(f"Generated: {filename}")

    except Exception as e:
        print(f"Error generating grouped bar chart for {title_prefix} by {segment_attribute}: {e}")
        plt.close()

