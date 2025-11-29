import random
from models.shape import Rectangle

def generate_random_parts(count=10, min_size=50, max_size=150):
    parts = []
    for _ in range(count):
        w = random.randint(min_size, max_size)
        h = random.randint(min_size // 2, max_size // 2)
        parts.append(Rectangle(width=w, height=h))
    return parts