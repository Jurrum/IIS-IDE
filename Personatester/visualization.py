import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from questions import NASA_TLX_SUBSCALES_PAPER # Import for TLX subscale names
from questions import NASA_TLX_SUBSCALES # Import for TLX subscale names

def plot_nasa_tlx_subscales(df, output_dir):
    # Check if we have any non-NaN TLX data before attempting to plot
    tlx_data = df[[col for col in df.columns if col.startswith('Original_TLX_') or col.startswith('Adaptive_TLX_')]].dropna(how='all')
    if not tlx_data.empty and not tlx_data.isna().all().all():
        # Create a figure with two subplots
        fig, axs = plt.subplots(1, 2, figsize=(15, 6))

        # Plot the mean TLX subscale scores for Original and Adaptive conditions
        for i, condition in enumerate(['Original', 'Adaptive']):
            # Filter columns to only include TLX subscales (not TLX_Overall)
            subscale_cols = [col for col in tlx_data.columns 
                            if col.startswith(condition + '_TLX_') and 
                            not col.endswith('_Overall')]
            
            # Get the means for these columns
            means = tlx_data[subscale_cols].mean()
            
            # Create the bar plot
            means.plot(kind='bar', ax=axs[i], color='skyblue' if condition == 'Original' else 'lightcoral')
            axs[i].set_title(f'Mean {condition} NASA-TLX Subscale Scores')
            axs[i].set_ylabel('Mean TLX Score')
            axs[i].set_ylim(0, 21)  # Set y-axis limits for the 0-21 scale
            
            # Extract just the subscale names from the column names
            subscale_names = [col.replace(f'{condition}_TLX_', '') for col in subscale_cols]
            
            # Make sure we have the right number of tick locations
            axs[i].set_xticks(range(len(subscale_names)))
            axs[i].set_xticklabels(subscale_names, rotation=45)

        # Layout so plots do not overlap
        fig.tight_layout()

        # Save the plot
        plt.savefig(os.path.join(output_dir, 'nasa_tlx_subscales.png'))
        plt.close()
        print("Generated: nasa_tlx_subscales.png")
        
        # Also create a comparison plot for TLX Overall scores
        if 'Original_TLX_Overall' in df.columns and 'Adaptive_TLX_Overall' in df.columns:
            plt.figure(figsize=(10, 6))
            
            # Calculate means
            orig_mean = df['Original_TLX_Overall'].mean()
            adap_mean = df['Adaptive_TLX_Overall'].mean()
            
            # Create bar chart
            plt.bar(['Original', 'Adaptive'], [orig_mean, adap_mean], 
                   color=['skyblue', 'lightcoral'])
            plt.title('Mean NASA-TLX Overall Workload Score')
            plt.ylabel('Mean TLX Overall Score (0-21)')
            plt.ylim(0, 21)  # Set y-axis limits for the 0-21 scale
            
            # Add value labels on top of bars
            plt.text(0, orig_mean + 0.5, f'{orig_mean:.2f}', ha='center')
            plt.text(1, adap_mean + 0.5, f'{adap_mean:.2f}', ha='center')
            
            # Save the plot
            plt.savefig(os.path.join(output_dir, 'nasa_tlx_overall_comparison.png'))
            plt.close()
            print("Generated: nasa_tlx_overall_comparison.png")

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
        # Check if we have any non-NaN TLX data before attempting to plot
        tlx_data = df[['Original_TLX_Overall', 'Adaptive_TLX_Overall']].dropna(how='all')
        if not tlx_data.empty and not tlx_data.isna().all().all():
            plt.figure(figsize=(10, 6))
            
            plt.subplot(1, 2, 1)
            tlx_means = tlx_data.mean()
            tlx_means.plot(kind='bar', color=['skyblue', 'lightcoral'])
            plt.title('Mean Overall NASA-TLX Scores')
            plt.ylabel('Mean TLX Score')
            plt.xticks(rotation=0)
            # NASA TLX uses a 0-21 scale for each dimension
            # The overall TLX score is the average of all dimensions, so it's also 0-21
            plt.ylim(0, 21) 

            plt.subplot(1, 2, 2)
            try:
                renamed_data = tlx_data.rename(columns={'Original_TLX_Overall': 'Original', 'Adaptive_TLX_Overall': 'Adaptive'})
                sns.boxplot(data=renamed_data)
                plt.title('Distribution of Overall TLX Scores')
                plt.ylabel('Overall TLX Score')
                plt.ylim(0, 21)
            except Exception as e:
                print(f"Error creating TLX boxplot: {e}")
                # Create a simple text plot instead
                plt.text(0.5, 0.5, 'Insufficient data for boxplot', 
                         horizontalalignment='center', verticalalignment='center')
                plt.title('Distribution of Overall TLX Scores (No Data)')

            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'tlx_overall_scores_comparison.png'))
            plt.close()
            print("Generated: tlx_overall_scores_comparison.png")
        else:
            print("Skipping TLX overall scores comparison: insufficient non-NaN data.")

    # 2.1. NASA TLX Overall Scores Boxplot
    if 'Original_TLX_Overall' in df.columns and 'Adaptive_TLX_Overall' in df.columns:
        # Check if we have any non-NaN TLX data before attempting to plot
        tlx_data = df[['Original_TLX_Overall', 'Adaptive_TLX_Overall']].dropna(how='all')
        if not tlx_data.empty and not tlx_data.isna().all().all():
            plt.figure(figsize=(10, 6))
            try:
                sns.boxplot(data=tlx_data)
                plt.title('NASA TLX Overall Scores: Original vs Adaptive')
                plt.ylabel('NASA TLX Overall Score (0-21)')
                plt.ylim(0, 21)  # Set y-axis limits for the 0-21 scale
                plt.grid(True)
            except Exception as e:
                print(f"Error creating NASA TLX overall boxplot: {e}")
                # Create a simple text plot instead
                plt.text(0.5, 0.5, 'Insufficient data for boxplot', 
                         horizontalalignment='center', verticalalignment='center')
                plt.title('NASA TLX Overall Scores (No Data)')
            
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'nasa_tlx_overall_boxplot.png'))
            plt.close()
            print("Generated: nasa_tlx_overall_boxplot.png")
        else:
            print("Skipping NASA TLX overall boxplot: insufficient non-NaN data.")

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

    # 4. NASA TLX Subscales Comparison
    print("\n--- Generating NASA TLX Subscale Visualizations ---")
    plot_nasa_tlx_subscales(df, output_dir)
    print("Generated: nasa_tlx_subscales.png and nasa_tlx_overall.png")
        
    # Commented out section for change score distributions
    # print("\n--- Generating Visualizations for Change Score Distributions ---")
    # change_score_columns = [col for col in df.columns if col.endswith('_Change')]
    # 
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

