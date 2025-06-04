from persona_generator import generate_personas
from conversation import run_persona_conversation
from analysis import analyze_simulation_data
from questions import NASA_TLX_SUBSCALES_PAPER # Import the subscales list
import pandas as pd
import os # Ensure os is imported for path operations
import sys # For sys.stdout.encoding
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Set the number of personas to simulate
persona_count = 100

def main():
    load_dotenv()
    original_state_description = input("Enter the description for the Original State: ")
    new_state_description = input("Enter the description for the New State: ")

    print("\n--- Original State Description ---")
    try:
        print(original_state_description)
    except UnicodeEncodeError:
        print(original_state_description.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding, errors='replace'))
    print("\n--- New State Description ---")
    try:
        print(new_state_description)
    except UnicodeEncodeError:
        print(new_state_description.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding, errors='replace'))
    print("---------------------------------------------------------\n")
    
    personas = generate_personas(persona_count)
    results = []

    for persona in tqdm(personas, desc="Simulating personas"):
        row = {**persona} # Start with persona attributes

        # Run conversation for the original state
        original_results = run_persona_conversation(persona, original_state_description, "Original")
        if original_results:
            row.update(original_results)

        # Run conversation for the new/adaptive state
        adaptive_results = run_persona_conversation(persona, new_state_description, "Adaptive")
        if adaptive_results:
            row.update(adaptive_results)
        
        results.append(row)

    df = pd.DataFrame(results)
    df_all_personas = df # Assign df to df_all_personas here

    # Identify different types of numeric columns
    # Performance metrics (Time, Errors) are numeric but not necessarily 1-5 scales.
    # SUS items and TLX items are 1-5 scales.
    # Raw text columns (ending with _Raw_Performance, _Raw_SUS, _Raw_TLX) should be excluded from numeric conversion.

    # Columns that should be numeric (includes performance metrics, SUS, TLX)
    numeric_cols = []
    # Columns that are specifically 1-5 scale ratings (SUS items, TLX subscales)
    scale_rating_cols = []

    for col_name in df.columns:
        if col_name.endswith("_Raw_Performance") or col_name.endswith("_Raw_SUS") or col_name.endswith("_Raw_TLX"):
            continue # Skip raw text columns
        
        # Check for persona attributes, skip them for numeric conversion here
        if col_name in personas[0]: # Assumes all personas have same keys
             continue

        if col_name.startswith("Original_Time_") or col_name.startswith("Adaptive_Time_") or \
           col_name.startswith("Original_Errors_") or col_name.startswith("Adaptive_Errors_"):
            numeric_cols.append(col_name)
        elif col_name.startswith("Original_SUS_") or col_name.startswith("Adaptive_SUS_") or \
             col_name.startswith("Original_TLX_") or col_name.startswith("Adaptive_TLX_"):
            numeric_cols.append(col_name)
            scale_rating_cols.append(col_name)

    for col in numeric_cols:
        df_all_personas[col] = pd.to_numeric(df_all_personas[col], errors='coerce')
        if col in scale_rating_cols:
            df_all_personas[col] = df_all_personas[col].where(df_all_personas[col].isin([1, 2, 3, 4, 5]))

    output_filename = "simulated_persona_metrics.csv"
    df_all_personas.to_csv(output_filename, index=False)
    print(f"Simulation complete. Results saved to {output_filename}.")

    # Call analysis function from analysis.py
    # Pass the DataFrame and the list of identified numeric columns (excluding persona attributes and raw text)
    # The analysis function will handle composite score calculations and further statistical analysis.
    # Define numeric columns for analysis (excluding persona attributes and raw text)
    # This helps in identifying which columns to process for scores, changes, and summaries.
    # It's better to define this explicitly than to infer it too dynamically.
    # We'll collect these after numeric extraction.
    # For now, we'll pass an empty list and let analysis.py derive from prefixes if needed,
    # or refine this list after extract_numeric_responses if it returns the specific columns it created.
    
    # For now, let's identify numeric columns that were extracted for Original and Adaptive scenarios
    # This is a simplified way; ideally, extract_numeric_responses would return these.
    # We'll focus on the stems that would be present in both Original_ and Adaptive_ forms.
    # This list will be used by analysis.py to identify performance metrics for summarization.

    # Let's get the numeric columns that were actually created by extract_numeric_responses
    # We need to ensure this happens before calling analyze_simulation_data
    all_numeric_columns_created = [] 
    if not df_all_personas.empty:
        # Infer numeric columns that are not persona attributes or raw text based on prefixes
        # This is a bit indirect. A more direct way would be for extract_numeric_responses to return them.
        # We are interested in the base metric names (stems) that have Original_ and Adaptive_ versions.
        # For example, if we have 'Original_Time_Subtask1_seconds', the stem is 'Time_Subtask1_seconds'.
        # The analysis function expects a list of these stems if they are to be auto-detected for summary.
        # However, the current implementation of analyze_simulation_data uses the full column names from the passed list.
        # So, we will pass the list of 'Original_...' prefixed columns that are numeric.
        
        # Collect 'Original_' prefixed columns that are likely numeric metrics (not persona attributes, not raw text, not composite scores)
        for col in df_all_personas.columns:
            if col.startswith('Original_') and \
               not col.endswith(('_SUS_Score', '_TLX_Overall')) and \
               not any(subscale in col for subscale in NASA_TLX_SUBSCALES_PAPER) and \
               not col in ['Original_Raw_Performance', 'Original_Raw_SUS', 'Original_Raw_TLX'] and \
               f"Adaptive_{col.replace('Original_', '')}" in df_all_personas.columns: # Ensure corresponding Adaptive column exists
                try:
                    pd.to_numeric(df_all_personas[col]) # Check if column is numeric
                    all_numeric_columns_created.append(col) # Add the Original_ column name
                except ValueError:
                    pass # Not purely numeric
    
    viz_output_dir = 'visualizations'
    if not os.path.exists(viz_output_dir):
        os.makedirs(viz_output_dir)

    # Analyze the collected data
    # analyze_simulation_data will now save the summary to 'simulated_persona_analyzed_data.csv'
    # and return the detailed DataFrame for us to save as 'simulated_persona_metrics.csv'.
    detailed_df_from_analysis = analyze_simulation_data(df_all_personas, viz_output_dir, all_numeric_columns_created, NASA_TLX_SUBSCALES_PAPER)

    # Save the detailed per-persona DataFrame (returned by analysis.py)
    detailed_output_filename = 'simulated_persona_metrics.csv'
    try:
        if detailed_df_from_analysis is not None:
            detailed_df_from_analysis.to_csv(detailed_output_filename, index=False, float_format='%.2f')
            print(f"\nSuccessfully saved detailed per-persona data to {detailed_output_filename}")
        else:
            print("Analysis function did not return a DataFrame. Detailed data not saved.")
    except Exception as e:
        print(f"Error saving detailed data to {detailed_output_filename}: {e}")

    # Visualizations are called within analyze_simulation_data using the detailed_df_from_analysis (internally referred to as df there)
    print("--- Main script execution complete ---")
    # import seaborn as sns
    # # Boxplot for original scores
    # original_score_cols = [col for col in df.columns if col.endswith('_original_score')]
    # new_score_cols = [col for col in df.columns if col.endswith('_new_score')]
    # # Define short labels for each question
    # short_labels = [
    #     'Q1: Dashboard',
    #     'Q2: Comfort',
    #     'Q3: Workload',
    #     'Q4: Recommend'
    # ]
    # # Adjust for number of questions
    # orig_labels = short_labels[:len(original_score_cols)]
    # new_labels = short_labels[:len(new_score_cols)]

    # plt.figure(figsize=(10, 5))
    # plt.subplot(1, 2, 1)
    # sns.boxplot(data=df[original_score_cols], orient='h')
    # plt.title('Original Situation Scores')
    # plt.xlabel('Score')
    # plt.yticks(range(len(orig_labels)), orig_labels)
    # plt.subplot(1, 2, 2)
    # sns.boxplot(data=df[new_score_cols], orient='h')
    # plt.title('New Scenario Scores')
    # plt.xlabel('Score')
    # plt.yticks(range(len(new_labels)), new_labels)
    # plt.tight_layout()
    # plt.show()

if __name__ == "__main__":
    main()
