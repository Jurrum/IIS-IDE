import openai
import os
import re
import time
import random
from questions import (
    PERFORMANCE_TASK_DESCRIPTION, PERFORMANCE_METRICS_PROMPT_INSTRUCTIONS,
    SUS_STATEMENTS, SUS_PROMPT_INSTRUCTIONS,
    NASA_TLX_SUBSCALES_PAPER, get_nasa_tlx_prompt_text
)

def get_persona_bias(persona):
    # Bias based on outlook and Big Five
    bias = 0
    if persona.get('outlook') == 'optimistic':
        bias += 1
    elif persona.get('outlook') == 'pessimistic':
        bias -= 1
    # Big Five: high neuroticism -> more negative, high extraversion/openness -> more positive
    bias += (persona.get('extraversion', 3) - 3) * 0.5
    bias += (persona.get('openness', 3) - 3) * 0.3
    bias -= (persona.get('neuroticism', 3) - 3) * 0.5
    return int(round(bias))

def extract_performance_metrics_from_text(text):
    metrics = {}
    # Ensure keys match exactly what's asked in PERFORMANCE_METRICS_PROMPT_INSTRUCTIONS
    # Example: Time_Subtask1_seconds, Errors_Subtask1_count
    patterns = {
        "Time_Subtask1_seconds": r"Time_Subtask1_seconds:\s*(\d+)",
        "Errors_Subtask1_count": r"Errors_Subtask1_count:\s*(\d)",
        "Time_Subtask2_seconds": r"Time_Subtask2_seconds:\s*(\d+)",
        "Errors_Subtask2_count": r"Errors_Subtask2_count:\s*(\d)",
        "Time_Subtask3_seconds": r"Time_Subtask3_seconds:\s*(\d+)",
        "Errors_Subtask3_count": r"Errors_Subtask3_count:\s*(\d)"
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                metrics[key] = int(match.group(1))
            except ValueError:
                 metrics[key] = None # Handle if value is not an int
        else:
            metrics[key] = None
    return metrics

def extract_sus_scores_from_text(text):
    scores = {}
    for i in range(1, 11):
        pattern = rf"SUS_{i}:\s*([1-5])"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                scores[f"SUS_{i}"] = int(match.group(1))
            except ValueError:
                scores[f"SUS_{i}"] = None
        else:
            scores[f"SUS_{i}"] = None
    return scores

def extract_tlx_scores_from_text(text):
    scores = {}
    for subscale in NASA_TLX_SUBSCALES_PAPER: # Uses the list from questions.py
        key_name = f"TLX_{subscale}" # Match the key format, e.g., TLX_Mental_Demand
        pattern = rf"{key_name}:\s*([1-5])"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                scores[key_name] = int(match.group(1))
            except ValueError:
                scores[key_name] = None
        else:
            scores[key_name] = None
    return scores

def run_persona_conversation(persona, scenario_description, scenario_type_label, delay=1.0):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        # Return empty/error structure
        error_results = {}
        for i in range(1,4): error_results[f"{scenario_type_label}_Time_Subtask{i}_seconds"] = None; error_results[f"{scenario_type_label}_Errors_Subtask{i}_count"] = None
        for i in range(1,11): error_results[f"{scenario_type_label}_SUS_{i}"] = None
        for subscale in NASA_TLX_SUBSCALES_PAPER: error_results[f"{scenario_type_label}_TLX_{subscale}"] = None
        error_results[f"{scenario_type_label}_Raw_Performance"] = "ERROR: API Key missing"
        error_results[f"{scenario_type_label}_Raw_SUS"] = "ERROR: API Key missing"
        error_results[f"{scenario_type_label}_Raw_TLX"] = "ERROR: API Key missing"
        return error_results

    system_msg = (
        f"You are {persona['name']}, a {persona['age']}-year-old {persona['role']} from {persona.get('region','Unknown')}. "
        f"Education: {persona.get('education','Unknown')}, Gender: {persona.get('gender','Unknown')}. "
        f"Big Five: O={persona.get('openness',3)}, C={persona.get('conscientiousness',3)}, E={persona.get('extraversion',3)}, A={persona.get('agreeableness',3)}, N={persona.get('neuroticism',3)}. "
        f"Tech-savviness: {persona['tech_savvy']}, Stress tolerance: {persona['stress_tolerance']}, Learning style: {persona.get('learning_style','Unknown')}. "
        f"Prior tech experience: {persona.get('prior_tech_experience',0)} years. Prior change experience: {persona.get('prior_change_experience','Unknown')}. "
        f"Outlook: {persona.get('outlook','neutral')}. You are currently on the {persona['shift']} shift. "
        f"You will be presented with a description of a dashboard and asked to simulate tasks and provide ratings. Please adhere strictly to the requested output formats, providing each requested data point on a new line as specified."
    )

    all_results_for_scenario = {}
    parsed_metrics_accumulator = {}

    # --- 1. Performance Metrics ---
    perf_prompt_user = (
        f"You are evaluating the '{scenario_type_label}' dashboard.\n"
        f"Dashboard Description:\n{scenario_description}\n\n"
        f"{PERFORMANCE_TASK_DESCRIPTION}\n"
        f"{PERFORMANCE_METRICS_PROMPT_INSTRUCTIONS}"
    )
    try:
        response_perf = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": perf_prompt_user}
            ],
            max_tokens=350, 
            temperature=0.2 # Lowered temperature
        )
        perf_text = response_perf.choices[0].message.content
        all_results_for_scenario[f"{scenario_type_label}_Raw_Performance"] = perf_text
        parsed_metrics_accumulator.update(extract_performance_metrics_from_text(perf_text))
        time.sleep(delay)
    except Exception as e:
        print(f"Error getting performance metrics for {persona['name']} ({scenario_type_label}): {e}")
        all_results_for_scenario[f"{scenario_type_label}_Raw_Performance"] = f"ERROR: {e}"
        for i in range(1,4): parsed_metrics_accumulator[f"Time_Subtask{i}_seconds"] = None; parsed_metrics_accumulator[f"Errors_Subtask{i}_count"] = None

    # --- 2. SUS Ratings ---
    sus_full_prompt = SUS_PROMPT_INSTRUCTIONS + "\n" + "\n".join(SUS_STATEMENTS)
    sus_prompt_user = (
        f"Continuing with the '{scenario_type_label}' dashboard described previously.\n"
        f"{sus_full_prompt}"
    )
    try:
        response_sus = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"Dashboard Description (reminder for context):\n{scenario_description}"},
                {"role": "user", "content": sus_prompt_user}
            ],
            max_tokens=500, 
            temperature=0.2 # Lowered temperature
        )
        sus_text = response_sus.choices[0].message.content
        all_results_for_scenario[f"{scenario_type_label}_Raw_SUS"] = sus_text
        sus_scores = extract_sus_scores_from_text(sus_text)
        bias = get_persona_bias(persona)
        for i in range(1, 11):
            key = f"SUS_{i}"
            if sus_scores.get(key) is not None:
                sus_scores[key] = min(5, max(1, sus_scores[key] + bias))
        parsed_metrics_accumulator.update(sus_scores)
        time.sleep(delay)
    except Exception as e:
        print(f"Error getting SUS scores for {persona['name']} ({scenario_type_label}): {e}")
        all_results_for_scenario[f"{scenario_type_label}_Raw_SUS"] = f"ERROR: {e}"
        for i in range(1,11): parsed_metrics_accumulator[f"SUS_{i}"] = None

    # --- 3. NASA-TLX Ratings ---
    tlx_full_prompt = get_nasa_tlx_prompt_text()
    tlx_prompt_user = (
        f"Continuing with the '{scenario_type_label}' dashboard described previously.\n"
        f"{tlx_full_prompt}"
    )
    try:
        response_tlx = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"Dashboard Description (reminder for context):\n{scenario_description}"},
                {"role": "user", "content": tlx_prompt_user}
            ],
            max_tokens=350,
            temperature=0.2 # Lowered temperature
        )
        tlx_text = response_tlx.choices[0].message.content
        all_results_for_scenario[f"{scenario_type_label}_Raw_TLX"] = tlx_text
        tlx_scores = extract_tlx_scores_from_text(tlx_text)
        bias = get_persona_bias(persona)
        for subscale_key in NASA_TLX_SUBSCALES_PAPER:
            key = f"TLX_{subscale_key}"
            if tlx_scores.get(key) is not None:
                tlx_scores[key] = min(5, max(1, tlx_scores[key] + bias))
        parsed_metrics_accumulator.update(tlx_scores)
        time.sleep(delay)
    except Exception as e:
        print(f"Error getting TLX scores for {persona['name']} ({scenario_type_label}): {e}")
        all_results_for_scenario[f"{scenario_type_label}_Raw_TLX"] = f"ERROR: {e}"
        for subscale_key in NASA_TLX_SUBSCALES_PAPER: parsed_metrics_accumulator[f"TLX_{subscale_key}"] = None

    # Add scenario_type_label prefix to all parsed_metrics_accumulator keys before adding to all_results_for_scenario
    for k, v in parsed_metrics_accumulator.items():
        all_results_for_scenario[f"{scenario_type_label}_{k}"] = v
    
    return all_results_for_scenario
