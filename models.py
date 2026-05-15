from dataclasses import dataclass
from typing import List


@dataclass
class Consumer:
    """Потребитель энергии"""
    name: str
    hourly_demand: List[float]  # кВт·ч для каждого часа (0-23)
    priority: int = 1  # 1-наивысший, 3-низший

    def __post_init__(self):
        """Валидация данных после создания"""
        if len(self.hourly_demand) != 24:
            raise ValueError(f"Потребитель {self.name}: должно быть 24 значения, получено {len(self.hourly_demand)}")
        if any(d < 0 for d in self.hourly_demand):
            raise ValueError(f"Потребитель {self.name}: потребление не может быть отрицательным")


@dataclass
class Generator:
    """Генератор энергии"""
    name: str
    generator_type: str  # 'diesel', 'solar'
    hourly_capacity: List[float]  # максимальная мощность по часам (кВт)
    cost_per_kwh: float  # стоимость за кВт·ч

    def __post_init__(self):
        """Валидация данных"""
        if len(self.hourly_capacity) != 24:
            raise ValueError(f"Генератор {self.name}: должно быть 24 значения")
        if self.generator_type not in ['diesel', 'solar']:
            raise ValueError(f"Неизвестный тип генератора: {self.generator_type}")