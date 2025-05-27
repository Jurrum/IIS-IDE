from persona_generator import generate_personas
from conversation import run_persona_conversation
import pandas as pd
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Set the number of personas to simulate
persona_count = 5

def main():
    load_dotenv()
    print("Paste the description of the original state:")
    original_state = input()
    print("Paste the description of the new state:")
    new_state = input()
    personas = generate_personas(persona_count)
    results = []

    for persona in tqdm(personas, desc="Simulating personas"):
        scores, raw_answers = run_persona_conversation(persona, original_state, new_state)
        row = {**persona}
        if scores and raw_answers:
            for q in scores:
                row[f"{q}_score"] = scores[q]
                row[f"{q}_raw"] = raw_answers[q]
        results.append(row)

    df = pd.DataFrame(results)
    df.to_csv("simulated_persona_scores.csv", index=False)
    print("Simulation complete. Results saved to simulated_persona_scores.csv.")

    # Print summary stats
    score_columns = [col for col in df.columns if col.endswith('_score')]
    if len(score_columns) == 0 or df[score_columns].empty:
        print("No score columns found or DataFrame is empty.")
    else:
        print(df[score_columns].describe())

if __name__ == "__main__":
    main()
