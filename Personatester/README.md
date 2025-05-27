# Persona Simulation Tool

This tool simulates 100 persona reactions to changes in a manufacturing environment using ChatGPT. It collects 1-5 scale scores for each question and saves all results to a CSV.

## Structure
- `main.py`: Entry point. Runs the simulation and saves results.
- `persona_generator.py`: Generates synthetic personas.
- `questions.py`: Contains the list of evaluation questions.
- `conversation.py`: Handles the ChatGPT conversation logic and score extraction.
- `requirements.txt`: Python dependencies.

## Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Set your OpenAI API key in a `.env` file: `OPENAI_API_KEY=your_key_here`
3. Run `main.py` and follow prompts.

## Output
- `simulated_persona_scores.csv`: Contains all persona scores and metadata.
