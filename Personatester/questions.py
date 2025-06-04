# questions.py

# Description of the core tasks the persona needs to simulate
PERFORMANCE_TASK_DESCRIPTION = """
You are to simulate performing the following three subtasks:
1. Identify the next three urgent print jobs.
2. Initiate removal for each of these three jobs.
3. Check filament status for these jobs.
"""

# Instructions for how to report performance metrics
PERFORMANCE_METRICS_PROMPT_INSTRUCTIONS = """
For each of the three subtasks described above, please provide:
- Estimated time taken in seconds (e.g., 'Time_Subtask1_seconds: 30').
- Number of errors committed out of three attempts (e.g., 'Errors_Subtask1_count: 1').

Please format your response clearly for these six data points, like so:
Time_Subtask1_seconds: [value]
Errors_Subtask1_count: [value]
Time_Subtask2_seconds: [value]
Errors_Subtask2_count: [value]
Time_Subtask3_seconds: [value]
Errors_Subtask3_count: [value]
"""

# SUS Statements (ensure these are the standard 10)
SUS_STATEMENTS = [
    "1. I think that I would like to use this system frequently.",
    "2. I found the system unnecessarily complex.",
    "3. I thought the system was easy to use.",
    "4. I think that I would need the support of a technical person to be able to use this system.",
    "5. I found the various functions in this system were well integrated.",
    "6. I thought there was too much inconsistency in this system.",
    "7. I would imagine that most people would learn to use this system very quickly.",
    "8. I found the system very cumbersome to use.",
    "9. I felt very confident using the system.",
    "10. I needed to learn a lot of things before I could get going with this system."
]

# Instructions for SUS ratings
SUS_PROMPT_INSTRUCTIONS = """
Now, please rate your experience with the described dashboard using the System Usability Scale (SUS). For each statement below, provide a score from 1 (Strongly Disagree) to 5 (Strongly Agree).
Please list your scores clearly, one per line, like 'SUS_1: [score]', 'SUS_2: [score]', etc., up to 'SUS_10: [score]'.
"""

# NASA-TLX Subscales for the paper
NASA_TLX_SUBSCALES_PAPER = [
    "Mental_Demand",
    "Effort",
    "Frustration",
    "Perceived_Performance"
]

# Instructions for NASA-TLX ratings
NASA_TLX_PROMPT_INSTRUCTIONS = f"""
Finally, please rate the following aspects of your experience with the described dashboard on a 1 to 5 scale (1 being very low, 5 being very high).
Please list your scores clearly, one per line, like 'TLX_Mental_Demand: [score]', 'TLX_Effort: [score]', etc. for all subscales provided.
"""

# This can be used to dynamically build the prompt for TLX
def get_nasa_tlx_prompt_text():
    items = "\n".join([f"- {subscale}" for subscale in NASA_TLX_SUBSCALES_PAPER])
    return f"{NASA_TLX_PROMPT_INSTRUCTIONS}\nSubscales to rate:\n{items}"
