import openai
import os
import re
import time
from questions import QUESTIONS

def extract_score(response):
    match = re.search(r'([1-5])', response)
    return int(match.group(1)) if match else None

def run_persona_conversation(persona, original_state, new_state, delay=0.5):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    system_msg = (
        f"You are {persona['name']}, a {persona['age']}-year-old {persona['role']} "
        f"with {persona['experience_years']} years experience in manufacturing. "
        f"Your tech-savviness is {persona['tech_savvy']}, and your stress tolerance is {persona['stress_tolerance']}. "
        f"You are currently on the {persona['shift']} shift."
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

    user_msg2 = f"Now, your work environment has changed:\n{new_state}\n\nPlease answer the following questions about this new environment."
    scores = {}
    raw_answers = {}
    for q in QUESTIONS:
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                    {"role": "assistant", "content": "I understand my current situation."},
                    {"role": "user", "content": user_msg2},
                    {"role": "user", "content": q}
                ],
                max_tokens=50,
                temperature=0.7,
            )
            answer = response.choices[0].message.content
            score = extract_score(answer)
            scores[q] = score
            raw_answers[q] = answer
            time.sleep(delay)
        except Exception as e:
            print(f"Error in question '{q}': {e}")
            scores[q] = None
            raw_answers[q] = ""
    return scores, raw_answers
