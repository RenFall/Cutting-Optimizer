from dataclasses import dataclass
import random
import uuid

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Rectangle:
    width: float
    height: float
    x: float = 0
    y: float = 0
    color: tuple = (100, 149, 237) # дефолтный синий
    id: str = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())[:6]
        
        # Flat UI colors)
        colors = [
            (231, 76, 60),   # Alizarin (Red)
            (230, 126, 34),  # Carrot (Orange)
            (241, 196, 15),  # Sun Flower (Yellow)
            (26, 188, 156),  # Turquoise (Teal)
            (52, 152, 219),  # Peter River (Blue)
            (155, 89, 182),  # Amethyst (Purple)
        ]
        self.color = random.choice(colors)
        
    @property
    def area(self):
        return self.width * self.height

    @property
    def right(self): return self.x + self.width
    @property
    def bottom(self): return self.y + self.height

    def move_to(self, x, y):
        self.x = x
        self.y = y

    def rotate(self):
        self.width, self.height = self.height, self.width

    def intersects(self, other: 'Rectangle') -> bool:
        """Проверка столкновения AABB (Axis-Aligned Bounding Box)"""
        return not (self.right <= other.x or 
                   self.x >= other.right or 
                   self.bottom <= other.y or 
                   self.y >= other.bottom)

    def is_inside(self, sheet_width, sheet_height):
        """Проверка, что деталь полностью внутри листа"""
        return (self.x >= 0 and self.y >= 0 and 
                self.right <= sheet_width and 
                self.bottom <= sheet_height)