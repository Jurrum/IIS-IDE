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
        }
        personas.append(persona)
    return personas
