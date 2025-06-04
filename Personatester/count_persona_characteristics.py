import pandas as pd
import os

def analyze_persona_characteristics(input_csv_path, output_csv_path):
    """
    Reads the simulated persona metrics CSV, counts unique values for specified
    categorical persona characteristics, and saves the counts to a new CSV.
    """
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: Input CSV file not found at {input_csv_path}")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Define the persona characteristic columns to analyze
    # These should match the column names in your simulated_persona_metrics.csv
    categorical_cols = [
        'role',
        'gender',
        'region',
        'education',
        'shift',
        'prior_change_experience',
        'tech_savvy', # As used in persona_generator and conversation
        'stress_tolerance',
        'outlook',
        'learning_style'
    ]

    all_counts_list = []

    for col in categorical_cols:
        if col in df.columns:
            counts = df[col].value_counts().reset_index()
            counts.columns = ['Value', 'Count']
            counts.insert(0, 'Characteristic', col)
            all_counts_list.append(counts)
        else:
            print(f"Warning: Column '{col}' not found in the input CSV. Skipping.")

    if not all_counts_list:
        print("No characteristic data found or columns missing. Output CSV will not be generated.")
        return

    final_counts_df = pd.concat(all_counts_list, ignore_index=True)

    try:
        final_counts_df.to_csv(output_csv_path, index=False)
        print(f"Successfully saved persona characteristic counts to {output_csv_path}")
    except Exception as e:
        print(f"Error writing output CSV file: {e}")

if __name__ == "__main__":
    # Define base path relative to the script or use absolute paths
    # Assuming the script is in Personatester and CSVs are one level up
    # base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
    # input_file = os.path.join(base_dir, "simulated_persona_metrics.csv")
    # output_file = os.path.join(base_dir, "persona_characteristic_counts.csv")

    # Use absolute paths as specified by the user context
    user_input_csv_path = r"C:\Users\jbdbo\Documents\Windsurf\IIS-IDE\simulated_persona_metrics.csv"
    user_output_csv_path = r"C:\Users\jbdbo\Documents\Windsurf\IIS-IDE\persona_characteristic_counts.csv"

    analyze_persona_characteristics(user_input_csv_path, user_output_csv_path)
