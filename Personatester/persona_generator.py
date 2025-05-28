import random

def generate_personas(n, seed=42):
    random.seed(seed)
    personas = []
    for i in range(n):
        persona = {
            "id": i,
            "name": f"Persona_{i}",
            "age": random.randint(20, 60),
            "role": random.choice(["Operator", "Technician", "Supervisor"]),
            "experience_years": random.randint(1, 30),
            "tech_savvy": random.choice(["Low", "Medium", "High"]),
            "stress_tolerance": random.choice(["Low", "Medium", "High"]),
            "shift": random.choice(["Day", "Night"]),
            "outlook": random.choice(["optimistic", "neutral", "pessimistic"]),
            # Big Five personality traits (1-5)
            "openness": random.randint(1, 5),
            "conscientiousness": random.randint(1, 5),
            "extraversion": random.randint(1, 5),
            "agreeableness": random.randint(1, 5),
            "neuroticism": random.randint(1, 5),
            # Learning style
            "learning_style": random.choice(["Visual", "Auditory", "Kinesthetic", "Reading/Writing"]),
            # Demographics
            "region": random.choice(["North America", "Europe", "Asia", "South America", "Africa", "Oceania"]),
            "education": random.choice(["High School", "Associate Degree", "Bachelor's", "Master's", "PhD"]),
            "gender": random.choice(["Male", "Female", "Other"]),
            # Prior tech experience (years)
            "prior_tech_experience": random.randint(0, 30),
            # Background (prior experience with change)
            "prior_change_experience": random.choice(["None", "Some", "Extensive"]),
        }
        personas.append(persona)
    return personas
