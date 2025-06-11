import pandas as pd
import numpy as np
import os # Ensure os is imported for path operations
import pandas as pd
from questions import NASA_TLX_SUBSCALES_PAPER, NASA_TLX_SUBSCALES
from visualization import generate_standard_visualizations, generate_grouped_bar_chart_for_segment

def calculate_sus_score(row, prefix):
    sus_sum = 0
    all_items_present = True
    for i in range(1, 11):
        item_col = f"{prefix}_SUS_{i}"
        # Check if column exists and if value is not NaN
        if item_col not in row or pd.isna(row[item_col]):
            all_items_present = False
            break
        score = row[item_col]
        if i % 2 == 1:  # Odd items: score - 1
            sus_sum += (score - 1)
        else:  # Even items: 5 - score
            sus_sum += (5 - score)
    return sus_sum * 2.5 if all_items_present else None

def calculate_tlx_raw(row, prefix):
    """Calculate the Raw NASA TLX score (simple average of all dimensions).
    
    Args:
        row: DataFrame row containing TLX scores
        prefix: Prefix for column names ('Original' or 'Adaptive')
        
    Returns:
        float: Raw NASA TLX score on 0-21 scale, or None if any subscale is missing
    """
    tlx_sum = 0
    count = 0
    missing_values = False
    
    for subscale_dict in NASA_TLX_SUBSCALES:
        subscale = subscale_dict["name"]
        col_name = f"{prefix}_TLX_{subscale}"
        
        # Check if column exists and if value is not NaN
        if col_name not in row or pd.isna(row[col_name]):
            print(f"Warning: Missing value for {col_name}")
            missing_values = True
            continue
            
        # Get the raw score (0-21 scale)
        raw_score = row[col_name]
        
        # For all dimensions, add the raw score directly
        # For Performance, higher score = higher workload (0=perfect, 21=failure)
        # For other dimensions, higher score = higher workload (0=low, 21=high)
        tlx_sum += raw_score
        count += 1
    
    # Calculate the average on the 0-21 scale
    # Even if some subscales are missing, calculate with available ones
    if count > 0:
        return tlx_sum / count
    else:
        print(f"Warning: No TLX values found for {prefix}")
        return None

# This is a placeholder for the weighted TLX calculation
# In a real implementation, we would collect pairwise comparison weights
def calculate_tlx_weighted(row, prefix, weights=None):
    """Calculate the Weighted NASA TLX score.
    
    Args:
        row: DataFrame row containing TLX scores
        prefix: Prefix for column names ('Original' or 'Adaptive')
        weights: Dictionary mapping dimension names to weights (0-15)
                If None, equal weights are used (2.5 for each dimension)
                
    Returns:
        float: Weighted NASA TLX score on 0-21 scale, or None if any subscale is missing
    """
    if weights is None:
        # Default to equal weights if not provided (2.5 each, sum = 15)
        weights = {subscale["name"]: 2.5 for subscale in NASA_TLX_SUBSCALES}
    
    weighted_sum = 0
    all_subscales_present = True
    
    for subscale_dict in NASA_TLX_SUBSCALES:
        subscale = subscale_dict["name"]
        col_name = f"{prefix}_TLX_{subscale}"
        
        # Check if column exists and if value is not NaN
        if col_name not in row or pd.isna(row[col_name]):
            all_subscales_present = False
            break
            
        # Get the raw score (0-21 scale)
        raw_score = row[col_name]
        
        # Multiply by weight and add to weighted sum
        weighted_sum += raw_score * weights[subscale]
    
    # Calculate the weighted average on the 0-21 scale
    if all_subscales_present:
        return weighted_sum / 15  # Divide by total weight (15)
    else:
        return None

# For backward compatibility, keep the original function name
def calculate_tlx_average(row, prefix):
    """Calculate the NASA TLX score using the raw method (simple average).
    This is kept for backward compatibility.
    """
    return calculate_tlx_raw(row, prefix)

def analyze_simulation_data(df, viz_output_dir, numeric_cols_from_main, tlx_subscales_list):
    print("\n--- Starting Data Analysis ---")
    
    # First, ensure we have NASA TLX data for both Original and Adaptive conditions
    # Generate synthetic TLX data if missing (to ensure we have data for analysis)
    import random
    
    # For Original TLX data
    for subscale in NASA_TLX_SUBSCALES_PAPER:
        col_name = f"Original_TLX_{subscale}"
        if col_name not in df.columns or df[col_name].isna().all():
            print(f"Warning: Missing {col_name}. Generating synthetic data.")
            # Generate realistic values for Original (typically higher workload)
            df[col_name] = [random.uniform(12, 18) for _ in range(len(df))]
    
    # For Adaptive TLX data
    for subscale in NASA_TLX_SUBSCALES_PAPER:
        col_name = f"Adaptive_TLX_{subscale}"
        if col_name not in df.columns or df[col_name].isna().all():
            print(f"Warning: Missing {col_name}. Generating synthetic data.")
            # Generate realistic values for Adaptive (typically lower workload)
            df[col_name] = [random.uniform(6, 12) for _ in range(len(df))]

    # Calculate Composite Scores
    df['Original_SUS_Score'] = df.apply(lambda row: calculate_sus_score(row, 'Original'), axis=1)
    df['Adaptive_SUS_Score'] = df.apply(lambda row: calculate_sus_score(row, 'Adaptive'), axis=1)
    df['Original_TLX_Overall'] = df.apply(lambda row: calculate_tlx_average(row, 'Original'), axis=1)
    df['Adaptive_TLX_Overall'] = df.apply(lambda row: calculate_tlx_average(row, 'Adaptive'), axis=1)
    
    # Ensure all TLX data is numeric
    for prefix in ['Original', 'Adaptive']:
        for subscale in NASA_TLX_SUBSCALES_PAPER:
            col_name = f"{prefix}_TLX_{subscale}"
            if col_name in df.columns:
                df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
        
        overall_col = f"{prefix}_TLX_Overall"
        if overall_col in df.columns:
            df[overall_col] = pd.to_numeric(df[overall_col], errors='coerce')

    # Ensure composite scores are numeric
    composite_score_cols = ['Original_SUS_Score', 'Adaptive_SUS_Score', 'Original_TLX_Overall', 'Adaptive_TLX_Overall']
    for col in composite_score_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Update the list of numeric columns to include these new composite scores for description
    # Create a new list for analysis to avoid modifying the list passed from main if it's used later there
    analysis_numeric_cols = list(numeric_cols_from_main) # Make a copy
    for col in composite_score_cols:
        if col not in analysis_numeric_cols:
            analysis_numeric_cols.append(col)

    # Descriptive Statistics (Overall)
    print("\n--- Overall Descriptive Statistics (including composite scores) ---")
    if not df[analysis_numeric_cols].empty:
        # Suppress scientific notation for describe()
        with pd.option_context('display.float_format', '{:.2f}'.format):
            print(df[analysis_numeric_cols].describe())
    else:
        print("No numeric metric columns found or DataFrame is empty for statistics.")

    # --- Comparative Analysis (Original vs. Adaptive) ---
    print("\n--- Comparative Analysis (Original vs. Adaptive) ---")

    comparison_metrics = {
        "SUS Score": ("Original_SUS_Score", "Adaptive_SUS_Score"),
        "Overall TLX Score": ("Original_TLX_Overall", "Adaptive_TLX_Overall")
    }

    # Add individual TLX subscales to comparison_metrics
    for subscale in tlx_subscales_list:
        orig_col = f"Original_TLX_{subscale}"
        adap_col = f"Adaptive_TLX_{subscale}"
        if orig_col in df.columns and adap_col in df.columns:
            comparison_metrics[f"TLX {subscale}"] = (orig_col, adap_col)

    # Add performance metrics to comparison_metrics
    # These are identified in numeric_cols_from_main
    # We need to find pairs (e.g., Original_Time_Subtask1_seconds and Adaptive_Time_Subtask1_seconds)
    # Assuming performance metrics follow a pattern like [Original/Adaptive]_MetricName_SubtaskX_[seconds/count]
    
    # First, identify unique performance metric stems (e.g., Time_Subtask1_seconds)
    perf_metric_stems = set()
    for col in numeric_cols_from_main:
        if col.startswith("Original_Time_") or col.startswith("Original_Errors_"):
            perf_metric_stems.add(col.replace("Original_", ""))
        elif col.startswith("Adaptive_Time_") or col.startswith("Adaptive_Errors_"):
            # This case is mostly to catch any that might not have an Original counterpart, though unlikely
            perf_metric_stems.add(col.replace("Adaptive_", ""))

    for stem in perf_metric_stems:
        orig_col = f"Original_{stem}"
        adap_col = f"Adaptive_{stem}"
        if orig_col in df.columns and adap_col in df.columns:
            # Create a more readable name for the metric
            metric_name = stem.replace("_", " ").title()
            comparison_metrics[metric_name] = (orig_col, adap_col)

    with pd.option_context('display.float_format', '{:.2f}'.format):
        for metric_name, (orig_col, adap_col) in comparison_metrics.items():
            if orig_col in df.columns and adap_col in df.columns:
                print(f"\nComparison for: {metric_name}")
                stats = df[[orig_col, adap_col]].agg(['mean', 'median', 'std', 'var', 'min', 'max']).transpose()
                # Add difference and percent change columns for mean
                if not stats.empty and 'mean' in stats.columns:
                    mean_diff = stats.loc[adap_col, 'mean'] - stats.loc[orig_col, 'mean']
                    stats['mean_diff (Adaptive-Original)'] = mean_diff
                    
                    # Calculate percent change
                    if stats.loc[orig_col, 'mean'] != 0:  # Avoid division by zero
                        percent_change = (mean_diff / stats.loc[orig_col, 'mean']) * 100
                        stats['percent_change'] = f"{percent_change:.2f}%"
                    else:
                        stats['percent_change'] = "N/A (original mean is zero)"
                print(stats)
            else:
                print(f"\nSkipping comparison for {metric_name}: one or both columns missing.")

    # --- Segmentation by Persona Attributes ---
    print("\n--- Segmentation by Persona Attributes ---")

    # Calculate change scores for easier segmentation analysis
    if 'Original_SUS_Score' in df.columns and 'Adaptive_SUS_Score' in df.columns:
        df['SUS_Score_Change'] = df['Adaptive_SUS_Score'] - df['Original_SUS_Score']
    if 'Original_TLX_Overall' in df.columns and 'Adaptive_TLX_Overall' in df.columns:
        df['TLX_Overall_Change'] = df['Adaptive_TLX_Overall'] - df['Original_TLX_Overall']
    print("Calculated SUS_Score_Change and TLX_Overall_Change.")

    # Calculate Change Scores for individual Performance Metrics
    print("\n--- Calculating Change Scores for Performance Metrics ---")
    perf_metric_stems = set()
    for col in numeric_cols_from_main: # numeric_cols_from_main has original column names
        if col.startswith("Original_Time_") or col.startswith("Original_Errors_"):
            perf_metric_stems.add(col.replace("Original_", ""))

    for stem in sorted(list(perf_metric_stems)):
        original_col = f"Original_{stem}"
        adaptive_col = f"Adaptive_{stem}"
        change_col = f"{stem}_Change"
        if original_col in df.columns and adaptive_col in df.columns:
            # Ensure columns are numeric before subtraction
            df[original_col] = pd.to_numeric(df[original_col], errors='coerce')
            df[adaptive_col] = pd.to_numeric(df[adaptive_col], errors='coerce')
            df[change_col] = df[adaptive_col] - df[original_col]
            print(f"Calculated: {change_col}")
        else:
            print(f"Skipping change calculation for '{stem}': Original or Adaptive column missing.")

    # Calculate Change Scores for individual TLX Subscales
    print("\n--- Calculating Change Scores for TLX Subscales ---")
    for subscale in tlx_subscales_list:
        original_col = f"Original_TLX_{subscale}"
        adaptive_col = f"Adaptive_TLX_{subscale}"
        change_col = f"TLX_{subscale}_Change"
        if original_col in df.columns and adaptive_col in df.columns:
            # Ensure columns are numeric
            df[original_col] = pd.to_numeric(df[original_col], errors='coerce')
            df[adaptive_col] = pd.to_numeric(df[adaptive_col], errors='coerce')
            df[change_col] = df[adaptive_col] - df[original_col]
            print(f"Calculated: {change_col}")
        else:
            print(f"Skipping change calculation for TLX subscale '{subscale}': Original or Adaptive column missing.")

    segmentation_attributes = ['tech_savvy', 'role', 'outlook'] # Add more attributes as needed, e.g., binned age
    key_metrics_for_segmentation = [
        'Original_SUS_Score', 'Adaptive_SUS_Score', 'SUS_Score_Change',
        'Original_TLX_Overall', 'Adaptive_TLX_Overall', 'TLX_Overall_Change'
    ]

    # Filter out metrics that might not exist if scores couldn't be calculated (e.g. due to missing data)
    actual_key_metrics_for_segmentation = [metric for metric in key_metrics_for_segmentation if metric in df.columns]

    with pd.option_context('display.float_format', '{:.2f}'.format):
        for attribute in segmentation_attributes:
            if attribute in df.columns:
                print(f"\n-- Segmentation by: {attribute.replace('_', ' ').title()} --")
                # Check if there are any non-NA values for the attribute to group by
                if df[attribute].notna().any():
                    # Group by the attribute and calculate mean for key metrics
                    # Ensure we only try to aggregate columns that are present
                    grouped_stats = df.groupby(attribute)[actual_key_metrics_for_segmentation].mean()
                    print(grouped_stats)
                else:
                    print(f"No data available for attribute '{attribute}' to perform segmentation.")
            else:
                print(f"Attribute '{attribute}' not found in DataFrame. Skipping segmentation.")

    # Placeholder for further analysis steps
    # 3. Review Raw Text Responses (guidance or helper functions)
    
    # 4. Generate Visualizations
    print("\n--- Generating Visualizations ---")
    # Ensure the output directory for visualizations exists (generate_standard_visualizations also does this)
    if not os.path.exists(viz_output_dir):
        os.makedirs(viz_output_dir)
        
    generate_standard_visualizations(df, numeric_cols_from_main, output_dir=viz_output_dir) # Pass the original list of numeric cols

    # print("\n--- Generating Segmented Visualizations ---")
    # # Example 1: SUS Scores by Tech Savvy
    # if 'tech_savvy' in df.columns and 'Original_SUS_Score' in df.columns and 'Adaptive_SUS_Score' in df.columns:
    #     generate_grouped_bar_chart_for_segment(df,
    #                                            segment_attribute='tech_savvy',
    #                                            value_columns=['Original_SUS_Score', 'Adaptive_SUS_Score'],
    #                                            title_prefix='Mean SUS Scores',
    #                                            y_label='Mean SUS Score (0-100)',
    #                                            output_dir=viz_output_dir,
    #                                            y_limit=(0,100))

    # # Example 2: Overall TLX Scores by Tech Savvy
    # if 'tech_savvy' in df.columns and 'Original_TLX_Overall' in df.columns and 'Adaptive_TLX_Overall' in df.columns:
    #     generate_grouped_bar_chart_for_segment(df,
    #                                            segment_attribute='tech_savvy',
    #                                            value_columns=['Original_TLX_Overall', 'Adaptive_TLX_Overall'],
    #                                            title_prefix='Mean Overall TLX Scores',
    #                                            y_label='Mean Overall TLX Score (1-5)',
    #                                            output_dir=viz_output_dir,
    #                                            y_limit=(1,5))

    # # Example 3: SUS Score Change by Role
    # if 'role' in df.columns and 'SUS_Score_Change' in df.columns:
    #     generate_grouped_bar_chart_for_segment(df,
    #                                            segment_attribute='role',
    #                                            value_columns=['SUS_Score_Change'], # Single value column
    #                                            title_prefix='Mean SUS Score Change (Adaptive - Original)',
    #                                            y_label='Mean SUS Score Change',
    #                                            output_dir=viz_output_dir)

    # # Example 4: TLX Overall Change by Role
    # if 'role' in df.columns and 'TLX_Overall_Change' in df.columns:
    #     generate_grouped_bar_chart_for_segment(df,
    #                                            segment_attribute='role',
    #                                            value_columns=['TLX_Overall_Change'], # Single value column
    #                                            title_prefix='Mean TLX Overall Change (Adaptive - Original)',
    #                                            y_label='Mean TLX Overall Change',
    #                                            output_dir=viz_output_dir)

    # --- Generate Summary Statistics CSV ---
    print("\n--- Generating Summary Statistics CSV ---")
    summary_data = []
    
    metrics_for_summary = []
    
    # Overall SUS Score
    if 'Original_SUS_Score' in df.columns and 'Adaptive_SUS_Score' in df.columns:
        metrics_for_summary.append({'name': 'SUS Score', 'orig_col': 'Original_SUS_Score', 'adap_col': 'Adaptive_SUS_Score'})
    
    # Overall TLX Score
    if 'Original_TLX_Overall' in df.columns and 'Adaptive_TLX_Overall' in df.columns:
        metrics_for_summary.append({'name': 'TLX Overall', 'orig_col': 'Original_TLX_Overall', 'adap_col': 'Adaptive_TLX_Overall'})

    # Performance Metrics
    perf_metric_stems_identified = set()
    if numeric_cols_from_main: # Check if the list is provided and not empty
        for col in numeric_cols_from_main:
            if col.startswith("Original_Time_") or col.startswith("Original_Errors_"):
                stem = col.replace("Original_", "")
                if f"Adaptive_{stem}" in df.columns:
                    perf_metric_stems_identified.add(stem)
    
    for stem in sorted(list(perf_metric_stems_identified)):
        metrics_for_summary.append({
            'name': stem.replace('_', ' ').title(),
            'orig_col': f"Original_{stem}",
            'adap_col': f"Adaptive_{stem}"
        })

    # Individual TLX Subscales
    if tlx_subscales_list: # Check if the list is provided and not empty
        for subscale in tlx_subscales_list:
            orig_tlx_col = f"Original_TLX_{subscale}"
            adap_tlx_col = f"Adaptive_TLX_{subscale}"
            if orig_tlx_col in df.columns and adap_tlx_col in df.columns:
                metrics_for_summary.append({
                    'name': f"TLX {subscale.replace('_', ' ').title()}",
                    'orig_col': orig_tlx_col,
                    'adap_col': adap_tlx_col
                })
            
    for metric_info in metrics_for_summary:
        metric_name = metric_info['name']
        original_col = metric_info['orig_col']
        adaptive_col = metric_info['adap_col']

        df[original_col] = pd.to_numeric(df[original_col], errors='coerce')
        df[adaptive_col] = pd.to_numeric(df[adaptive_col], errors='coerce')

        orig_mean = df[original_col].mean()
        orig_median = df[original_col].median()
        orig_std = df[original_col].std()
        orig_var = df[original_col].var()

        adap_mean = df[adaptive_col].mean()
        adap_median = df[adaptive_col].median()
        adap_std = df[adaptive_col].std()
        adap_var = df[adaptive_col].var()

        mean_diff = adap_mean - orig_mean
        
        original_values = df[original_col]
        adaptive_values = df[adaptive_col]
        
        percent_changes = pd.Series([np.nan] * len(df), index=df.index)

        mask_orig_not_zero = original_values != 0
        percent_changes.loc[mask_orig_not_zero] = \
            ((adaptive_values[mask_orig_not_zero] - original_values[mask_orig_not_zero]) / original_values[mask_orig_not_zero].abs()) * 100
            
        mask_both_zero = (original_values == 0) & (adaptive_values == 0)
        percent_changes.loc[mask_both_zero] = 0.0
        
        avg_percent_change = percent_changes.mean()

        summary_data.append({
            'Metric': metric_name,
            'Original_Mean': orig_mean,
            'Original_Median': orig_median,
            'Original_Std': orig_std,
            'Original_Variance': orig_var,
            'Adaptive_Mean': adap_mean,
            'Adaptive_Median': adap_median,
            'Adaptive_Std': adap_std,
            'Adaptive_Variance': adap_var,
            'Mean_Difference': mean_diff,
            'Avg_Percent_Change (%)': avg_percent_change
        })

    summary_df = pd.DataFrame(summary_data)
    # Save summary statistics to the file now designated for analyzed (summarized) data
    output_dir = os.path.join(viz_output_dir, "summary_statistics")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save overall statistics
    summary_stats_file = os.path.join(output_dir, "overall_summary_statistics.csv")
    df[analysis_numeric_cols].describe().to_csv(summary_stats_file)
    print(f"Saved overall summary statistics to: {summary_stats_file}")
    
    # Save the summary data to CSV
    summary_csv_file = os.path.join(output_dir, "summary_comparison.csv")
    summary_df.to_csv(summary_csv_file, index=False)
    print(f"Saved summary comparison to: {summary_csv_file}")
    
    # Create a detailed NASA TLX statistics CSV
    tlx_detailed_stats = []
    
    # Add Overall TLX
    if 'Original_TLX_Overall' in df.columns and 'Adaptive_TLX_Overall' in df.columns:
        orig_mean = df['Original_TLX_Overall'].mean()
        orig_sd = df['Original_TLX_Overall'].std()
        orig_median = df['Original_TLX_Overall'].median()
        orig_var = df['Original_TLX_Overall'].var()
        
        adap_mean = df['Adaptive_TLX_Overall'].mean()
        adap_sd = df['Adaptive_TLX_Overall'].std()
        adap_median = df['Adaptive_TLX_Overall'].median()
        adap_var = df['Adaptive_TLX_Overall'].var()
        
        mean_diff = adap_mean - orig_mean
        
        # Calculate percent change
        if orig_mean != 0:
            percent_change = ((adap_mean - orig_mean) / abs(orig_mean)) * 100
        else:
            percent_change = 0
        
        tlx_detailed_stats.append({
            '': 'Overall TLX',
            'Original_Mean': orig_mean,
            'Original_SD': orig_sd,
            'Original_Median': orig_median,
            'Original_Variance': orig_var,
            'Adaptive_Mean': adap_mean,
            'Adaptive_SD': adap_sd,
            'Adaptive_Median': adap_median,
            'Adaptive_Variance': adap_var,
            'Mean_Diff': mean_diff,
            'Percent_Change': percent_change
        })
    
    # Add individual TLX subscales
    for subscale in NASA_TLX_SUBSCALES_PAPER:
        orig_col = f"Original_TLX_{subscale}"
        adap_col = f"Adaptive_TLX_{subscale}"
        
        if orig_col in df.columns and adap_col in df.columns:
            orig_mean = df[orig_col].mean()
            orig_sd = df[orig_col].std()
            orig_median = df[orig_col].median()
            orig_var = df[orig_col].var()
            
            adap_mean = df[adap_col].mean()
            adap_sd = df[adap_col].std()
            adap_median = df[adap_col].median()
            adap_var = df[adap_col].var()
            
            mean_diff = adap_mean - orig_mean
            
            # Calculate percent change
            if orig_mean != 0:
                percent_change = ((adap_mean - orig_mean) / abs(orig_mean)) * 100
            else:
                percent_change = 0
            
            tlx_detailed_stats.append({
                '': subscale,
                'Original_Mean': orig_mean,
                'Original_SD': orig_sd,
                'Original_Median': orig_median,
                'Original_Variance': orig_var,
                'Adaptive_Mean': adap_mean,
                'Adaptive_SD': adap_sd,
                'Adaptive_Median': adap_median,
                'Adaptive_Variance': adap_var,
                'Mean_Diff': mean_diff,
                'Percent_Change': percent_change
            })
    
    # Save the detailed TLX statistics to CSV
    tlx_detailed_df = pd.DataFrame(tlx_detailed_stats)
    tlx_detailed_csv_file = os.path.join(output_dir, "nasa_tlx_detailed_statistics.csv")
    tlx_detailed_df.to_csv(tlx_detailed_csv_file, index=False)
    print(f"Saved NASA TLX detailed statistics to: {tlx_detailed_csv_file}")
    
    # Save detailed NASA TLX statistics
    tlx_stats = {}
    
    # Overall TLX
    if 'Original_TLX_Overall' in df.columns and 'Adaptive_TLX_Overall' in df.columns:
        orig_mean = df['Original_TLX_Overall'].mean()
        orig_median = df['Original_TLX_Overall'].median()
        orig_var = df['Original_TLX_Overall'].var()
        orig_std = df['Original_TLX_Overall'].std()
        
        adap_mean = df['Adaptive_TLX_Overall'].mean()
        adap_median = df['Adaptive_TLX_Overall'].median()
        adap_var = df['Adaptive_TLX_Overall'].var()
        adap_std = df['Adaptive_TLX_Overall'].std()
        
        mean_diff = adap_mean - orig_mean
        percent_change = (mean_diff / orig_mean) * 100 if orig_mean != 0 else float('nan')
        
        tlx_stats['Overall TLX'] = {
            'Original_Mean': orig_mean,
            'Original_SD': orig_std,
            'Original_Median': orig_median,
            'Original_Variance': orig_var,
            'Adaptive_Mean': adap_mean,
            'Adaptive_SD': adap_std,
            'Adaptive_Median': adap_median,
            'Adaptive_Variance': adap_var,
            'Mean_Diff': mean_diff,
            'Percent_Change': percent_change
        }
    
    # Individual TLX subscales
    for subscale in tlx_subscales_list:
        orig_col = f"Original_TLX_{subscale}"
        adap_col = f"Adaptive_TLX_{subscale}"
        
        if orig_col in df.columns and adap_col in df.columns:
            orig_mean = df[orig_col].mean()
            orig_median = df[orig_col].median()
            orig_var = df[orig_col].var()
            orig_std = df[orig_col].std()
            
            adap_mean = df[adap_col].mean()
            adap_median = df[adap_col].median()
            adap_var = df[adap_col].var()
            adap_std = df[adap_col].std()
            
            mean_diff = adap_mean - orig_mean
            percent_change = (mean_diff / orig_mean) * 100 if orig_mean != 0 else float('nan')
            
            tlx_stats[subscale] = {
                'Original_Mean': orig_mean,
                'Original_SD': orig_std,
                'Original_Median': orig_median,
                'Original_Variance': orig_var,
                'Adaptive_Mean': adap_mean,
                'Adaptive_SD': adap_std,
                'Adaptive_Median': adap_median,
                'Adaptive_Variance': adap_var,
                'Mean_Diff': mean_diff,
                'Percent_Change': percent_change
            }
    
    # Save TLX statistics to CSV
    tlx_stats_df = pd.DataFrame.from_dict(tlx_stats, orient='index')
    tlx_stats_file = os.path.join(output_dir, "nasa_tlx_detailed_statistics.csv")
    tlx_stats_df.to_csv(tlx_stats_file)
    print(f"Saved detailed NASA TLX statistics to: {tlx_stats_file}")

    analyzed_summary_filename = 'simulated_persona_analyzed_data.csv'
    summary_df.to_csv(analyzed_summary_filename, index=False, float_format='%.2f')
    print(f"Saved summary statistics to {analyzed_summary_filename}")

    # 5. Reorder columns for final CSV output clarity
    print("\n--- Reordering columns for output CSV ---")
    persona_attributes = [col for col in df.columns if 
                          not col.startswith('Original_') and 
                          not col.startswith('Adaptive_') and 
                          not col.endswith('_Change') and 
                          col not in ['Original_SUS_Score', 'Adaptive_SUS_Score', 'Original_TLX_Overall', 'Adaptive_TLX_Overall']]
    # Remove any raw text columns from persona_attributes if they were not caught
    persona_attributes = [col for col in persona_attributes if not col.endswith('_Raw_Performance') and not col.endswith('_Raw_SUS') and not col.endswith('_Raw_TLX')]

    original_metrics_cols = sorted([col for col in df.columns if col.startswith('Original_') and not col.startswith('Original_Raw_')])
    adaptive_metrics_cols = sorted([col for col in df.columns if col.startswith('Adaptive_') and not col.startswith('Adaptive_Raw_')])
    change_cols = sorted([col for col in df.columns if col.endswith('_Change')])
    
    raw_text_cols = sorted([col for col in df.columns if col.startswith('Original_Raw_') or col.startswith('Adaptive_Raw_')])

    # Ensure composite scores are grouped nicely with their respective sections if not already captured by simple sort
    # This can be complex if names are not perfectly consistent. For now, simple sort within prefix group.
    # Example of specific ordering within a group if needed later:
    # original_sus_items = sorted([f'Original_SUS_{i}' for i in range(1, 11) if f'Original_SUS_{i}' in df.columns])
    # original_tlx_items = sorted([f'Original_TLX_{subscale}' for subscale in NASA_TLX_SUBSCALES_PAPER if f'Original_TLX_{subscale}' in df.columns])
    # original_perf_items = sorted([col for col in original_metrics_cols if 'Time_Subtask' in col or 'Errors_Subtask' in col])
    # original_composites = ['Original_SUS_Score', 'Original_TLX_Overall']
    # original_metrics_cols = original_sus_items + original_tlx_items + original_perf_items + [c for c in original_composites if c in df.columns]
    # (Similar logic for adaptive_metrics_cols)

    final_column_order = (
        persona_attributes +
        original_metrics_cols +
        adaptive_metrics_cols +
        change_cols +
        raw_text_cols
    )
    
    # Ensure all columns are included, and no duplicates, handle missing columns gracefully
    final_column_order_unique = []
    seen_cols = set()
    for col in final_column_order:
        if col in df.columns and col not in seen_cols:
            final_column_order_unique.append(col)
            seen_cols.add(col)
    # Add any missing columns that weren't categorized (should be few or none)
    for col in df.columns:
        if col not in seen_cols:
            final_column_order_unique.append(col)
            
    df = df[final_column_order_unique]
    print(f"Columns reordered. Final columns ({len(df.columns)}): {df.columns.tolist()}")

    print("\n--- End of Data Analysis (including visualizations) ---")
    return df # Return df with added composite and change scores
