from abc import ABC, abstractmethod
from typing import List
from models.shape import Rectangle

class PackingAlgorithm(ABC):
    @abstractmethod
    def pack(self, shapes: List[Rectangle], sheet_width: float, sheet_height: float) -> List[Rectangle]:
        """
        Принимает список деталей и размеры листа.
        Возвращает список размещенных деталей с обновленными координатами (x, y).
        Те детали, что не влезли, не попадают в возвращаемый список.
        """
        pass