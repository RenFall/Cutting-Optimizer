from generators.random_parts import generate_random_parts
from ui.pygame_app import CuttingGame

def main():
    print("Starting Cutting Optimizer...")

    # Генерируем 10 случайных деталей
    parts = generate_random_parts(count=12)
    
    game = CuttingGame(parts)
    game.run()

if __name__ == "__main__":
    main()