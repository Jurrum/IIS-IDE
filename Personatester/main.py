from persona_generator import generate_personas
from conversation import run_persona_conversation
import pandas as pd
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Set the number of personas to simulate
persona_count = 25

def main():
    load_dotenv()
    print("Paste the description of the original state:")
    original_state = input()
    print("Paste the description of the new state:")
    new_state = input()
    personas = generate_personas(persona_count)
    results = []

    for persona in tqdm(personas, desc="Simulating personas"):
        # First, score and answer questions for the original state
        original_scores, original_raw_answers = run_persona_conversation(persona, original_state, original_state)
        # Then, for the new state, pass previous answers (original_scores) to reference in prompt
        new_scores, new_raw_answers = run_persona_conversation(persona, original_state, new_state, prev_answers=original_scores)
        row = {**persona}
        if original_scores and original_raw_answers:
            for q in original_scores:
                row[f"{q}_original_score"] = original_scores[q]
                row[f"{q}_original_raw"] = original_raw_answers[q]
        if new_scores and new_raw_answers:
            for q in new_scores:
                row[f"{q}_new_score"] = new_scores[q]
                row[f"{q}_new_raw"] = new_raw_answers[q]
        results.append(row)

    df = pd.DataFrame(results)

    # Convert score columns to numeric, coerce errors to NaN, and keep only integers 1-5
    score_columns = [col for col in df.columns if col.endswith('_score')]
    for col in score_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].where(df[col].isin([1, 2, 3, 4, 5]))

    df.to_csv("simulated_persona_scores.csv", index=False)
    print("Simulation complete. Results saved to simulated_persona_scores.csv.")

    # Print summary stats
    if len(score_columns) == 0 or df[score_columns].empty:
        print("No score columns found or DataFrame is empty.")
    else:
        print(df[score_columns].describe())

    # --- Boxplots for original and new scenario ---
    import matplotlib.pyplot as plt
    import seaborn as sns
    # Boxplot for original scores
    original_score_cols = [col for col in df.columns if col.endswith('_original_score')]
    new_score_cols = [col for col in df.columns if col.endswith('_new_score')]
    # Define short labels for each question
    short_labels = [
        'Q1: Dashboard',
        'Q2: Comfort',
        'Q3: Workload',
        'Q4: Recommend'
    ]
    # Adjust for number of questions
    orig_labels = short_labels[:len(original_score_cols)]
    new_labels = short_labels[:len(new_score_cols)]

    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    sns.boxplot(data=df[original_score_cols], orient='h')
    plt.title('Original Situation Scores')
    plt.xlabel('Score')
    plt.yticks(range(len(orig_labels)), orig_labels)
    plt.subplot(1, 2, 2)
    sns.boxplot(data=df[new_score_cols], orient='h')
    plt.title('New Scenario Scores')
    plt.xlabel('Score')
    plt.yticks(range(len(new_labels)), new_labels)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
