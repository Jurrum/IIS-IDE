from persona_generator import generate_personas
from conversation import run_persona_conversation
import pandas as pd
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Set the number of personas to simulate
persona_count = 3

def main():
    load_dotenv()
    print("Paste the description of the original state (e.g., current dashboard features):")
    original_state_description = input()
    print("Paste the description of the new/adaptive state (e.g., new dashboard features):")
    adaptive_state_description = input()
    
    personas = generate_personas(persona_count)
    results = []

    for persona in tqdm(personas, desc="Simulating personas"):
        row = {**persona} # Start with persona attributes

        # Run conversation for the original state
        original_results = run_persona_conversation(persona, original_state_description, "Original")
        if original_results:
            row.update(original_results)

        # Run conversation for the new/adaptive state
        adaptive_results = run_persona_conversation(persona, adaptive_state_description, "Adaptive")
        if adaptive_results:
            row.update(adaptive_results)
        
        results.append(row)

    df = pd.DataFrame(results)

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
        df[col] = pd.to_numeric(df[col], errors='coerce')
        if col in scale_rating_cols:
            df[col] = df[col].where(df[col].isin([1, 2, 3, 4, 5]))

    output_filename = "simulated_persona_metrics.csv"
    df.to_csv(output_filename, index=False)
    print(f"Simulation complete. Results saved to {output_filename}.")

    # Print summary stats for numeric columns
    if not df[numeric_cols].empty:
        print("\nSummary statistics for numeric metrics:")
        print(df[numeric_cols].describe())
    else:
        print("No numeric metric columns found or DataFrame is empty for statistics.")

    # --- Plotting section commented out --- 
    # TODO: Update visualizations for the new detailed metrics (Performance, SUS, TLX).
    # Consider plotting overall SUS scores, key TLX subscales, or total task times.
    # import matplotlib.pyplot as plt
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
