import openai
import os
import re
import time
from questions import QUESTIONS

def extract_score(response):
    """
    Extracts the first valid score (1-5) from the response string.
    Handles digits, word numbers, and patterns like '4/5', 'four out of five', etc.
    """
    import re
    word_to_num = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5
    }
    # Lowercase for easier matching
    resp = response.lower()
    # 1. Look for digit or word followed by '/5' or 'out of 5'
    pattern = r'(\b[1-5]\b|one|two|three|four|five)\s*(/|out of)\s*5'
    match = re.search(pattern, resp)
    if match:
        val = match.group(1)
        return word_to_num.get(val, None)
    # 2. Look for explicit 'rate ... as a X' or 'score ... X'
    pattern2 = r'(?:rate|score|give|is|at|of|to|as)\D{0,10}(one|two|three|four|five|[1-5])\b'
    match = re.search(pattern2, resp)
    if match:
        val = match.group(1)
        return word_to_num.get(val, None)
    # 3. Look for any standalone digit or word 1-5
    pattern3 = r'\b(one|two|three|four|five|[1-5])\b'
    match = re.search(pattern3, resp)
    if match:
        val = match.group(1)
        return word_to_num.get(val, None)
    return None


import random

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

def vary_question(q, persona):
    # Vary phrasing based on learning style and random choice
    variants = [q]
    if persona.get('learning_style') == 'Visual':
        variants.append(q + " (Please visualize your answer)")
    if persona.get('learning_style') == 'Kinesthetic':
        variants.append("Imagine acting out this scenario: " + q)
    variants.append(f"{q} (Answer honestly, considering your {persona.get('outlook','')} outlook)")
    variants.append(f"{q} (Keep in mind your prior experience: {persona.get('prior_change_experience','')})")
    return random.choice(variants)

def run_persona_conversation(persona, original_state, new_state, delay=0.5, prev_answers=None, peer_stats=None, scenario_idx=None, feedback=None):
    import openai
    import os
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # System message includes richer persona context
    system_msg = (
        f"You are {persona['name']}, a {persona['age']}-year-old {persona['role']} from {persona.get('region','Unknown')}. "
        f"Education: {persona.get('education','Unknown')}, Gender: {persona.get('gender','Unknown')}. "
        f"Big Five: O={persona.get('openness',3)}, C={persona.get('conscientiousness',3)}, E={persona.get('extraversion',3)}, A={persona.get('agreeableness',3)}, N={persona.get('neuroticism',3)}. "
        f"Tech-savviness: {persona['tech_savvy']}, Stress tolerance: {persona['stress_tolerance']}, Learning style: {persona.get('learning_style','Unknown')}. "
        f"Prior tech experience: {persona.get('prior_tech_experience',0)} years. Prior change experience: {persona.get('prior_change_experience','Unknown')}. "
        f"Outlook: {persona.get('outlook','neutral')}. You are currently on the {persona['shift']} shift."
    )
    user_msg = f"Here is your current work environment:\n{original_state}\n\nPlease acknowledge you understand your situation."
    try:
        openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_msg},
                      {"role": "user", "content": user_msg}],
            max_tokens=50,
            temperature=0.7,
        )
    except Exception as e:
        print(f"Error in priming: {e}")
        return None, None

    # Feedback/peer influence
    peer_text = ""
    if peer_stats:
        peer_text = f"\nHere is what your peers have answered so far: {peer_stats}"
    feedback_text = ""
    if feedback:
        feedback_text = f"\nFeedback: {feedback}"

    # If prev_answers, reference them
    prev_text = ""
    if prev_answers:
        prev_text = "\nYour previous answers: " + ", ".join([f'{k}: {v}' for k,v in prev_answers.items()])

    user_msg2 = f"Now, your work environment has changed:\n{new_state}{prev_text}{peer_text}{feedback_text}\n\nPlease answer the following questions about this new environment."
    scores = {}
    raw_answers = {}
    for q in QUESTIONS:
        try:
            # Vary question
            varied_q = vary_question(q, persona)
            # Add randomness/noise
            noise = random.random()
            if noise < 0.07:
                varied_q += " (If unsure, it's okay to say so.)"
            if noise < 0.03:
                varied_q = "You may answer off-topic: " + varied_q
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                    {"role": "assistant", "content": "I understand my current situation."},
                    {"role": "user", "content": user_msg2},
                    {"role": "user", "content": varied_q}
                ],
                max_tokens=80,
                temperature=0.9,
            )
            answer = response.choices[0].message.content
            score = extract_score(answer)
            # Bias score according to persona
            bias = get_persona_bias(persona)
            if score is not None:
                score = min(5, max(1, score + bias))
            # Add extra randomness
            if random.random() < 0.03:
                score = random.choice([1,2,3,4,5])
            scores[q] = score
            raw_answers[q] = answer
            time.sleep(delay)
        except Exception as e:
            print(f"Error in question '{q}': {e}")
            scores[q] = None
            raw_answers[q] = ""
    return scores, raw_answers
