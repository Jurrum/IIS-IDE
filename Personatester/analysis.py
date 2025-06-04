import pandas as pd
import numpy as np
import os # Ensure os is imported for path operations
import pandas as pd
from questions import NASA_TLX_SUBSCALES_PAPER
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

def calculate_tlx_average(row, prefix):
    tlx_sum = 0
    count = 0
    all_subscales_present = True
    for subscale in NASA_TLX_SUBSCALES_PAPER:
        col_name = f"{prefix}_TLX_{subscale}"
        # Check if column exists and if value is not NaN
        if col_name not in row or pd.isna(row[col_name]):
            all_subscales_present = False
            break
        tlx_sum += row[col_name]
        count += 1
    return (tlx_sum / count) if all_subscales_present and count > 0 else None

def analyze_simulation_data(df, viz_output_dir, numeric_cols_from_main, tlx_subscales_list):
    print("\n--- Starting Data Analysis ---")

    # Calculate Composite Scores
    df['Original_SUS_Score'] = df.apply(lambda row: calculate_sus_score(row, 'Original'), axis=1)
    df['Adaptive_SUS_Score'] = df.apply(lambda row: calculate_sus_score(row, 'Adaptive'), axis=1)
    df['Original_TLX_Overall'] = df.apply(lambda row: calculate_tlx_average(row, 'Original'), axis=1)
    df['Adaptive_TLX_Overall'] = df.apply(lambda row: calculate_tlx_average(row, 'Adaptive'), axis=1)

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
                stats = df[[orig_col, adap_col]].agg(['mean', 'median', 'std', 'min', 'max']).transpose()
                # Add a difference column for mean
                if not stats.empty and 'mean' in stats.columns:
                    stats['mean_diff (Adaptive-Original)'] = stats.loc[adap_col, 'mean'] - stats.loc[orig_col, 'mean']
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
