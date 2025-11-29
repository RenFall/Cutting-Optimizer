# algorithms/first_fit.py
from typing import List
from models.shape import Rectangle
from algorithms.base import PackingAlgorithm

class FirstFitDecreasing(PackingAlgorithm):
    def __init__(self, step: int = 20):
        # step - шаг сетки поиска. Чем меньше, тем плотнее, но медленнее.
        self.step = step

    def pack(self, shapes: List[Rectangle], sheet_width: float, sheet_height: float) -> List[Rectangle]:
        # 1. Сортируем: сначала самые высокие, потом широкие
        # Это эвристика: высокие детали сложнее всего впихнуть в оставшиеся щели
        sorted_shapes = sorted(shapes, key=lambda s: s.height, reverse=True)
        
        placed_shapes = []
        
        for shape in sorted_shapes:
            # Сбрасываем позицию
            shape.x, shape.y = 0, 0
            is_placed = False
            
            # 2. Перебираем координаты (Scanline)
            # Ищем позицию: Y (строки), потом X (столбцы)
            # Внимание: для скорости мы идем с шагом self.step
            for y in range(0, int(sheet_height - shape.height) + 1, self.step):
                for x in range(0, int(sheet_width - shape.width) + 1, self.step):
                    
                    # Пробуем поставить деталь сюда
                    shape.x = x
                    shape.y = y
                    
                    # 3. Проверяем коллизии
                    if not self._has_collision(shape, placed_shapes):
                        placed_shapes.append(shape)
                        is_placed = True
                        break # Переходим к следующей детали
                
                if is_placed:
                    break
            
            # Если не влезла - просто не добавляем в placed_shapes
            
        return placed_shapes

    def _has_collision(self, current: Rectangle, others: List[Rectangle]) -> bool:
        for other in others:
            if current.intersects(other):
                return True
        return False