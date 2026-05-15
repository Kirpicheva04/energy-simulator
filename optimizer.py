import numpy as np
from scipy.optimize import linprog
from typing import List, Dict
import warnings


class EnergyOptimizer:
    """Решает оптимизационную задачу распределения энергии"""

    def __init__(self, consumers: List, generators: List):
        self.consumers = consumers
        self.generators = generators
        self.hours = 24

    def optimize_hour(self, hour: int) -> Dict:
        total_demand = sum(c.hourly_demand[hour] for c in self.consumers)
        total_capacity = sum(g.hourly_capacity[hour] for g in self.generators)

        if total_capacity >= total_demand:
            return self._optimize_cost(hour, total_demand)
        else:
            return self._optimize_coverage(hour, total_capacity)

    def _optimize_cost(self, hour: int, total_demand: float) -> Dict:
        """
        Минимизация стоимости при полном покрытии спроса
        """
        # Сортируем генераторы по стоимости (дешёвые сначала)
        sorted_gens = sorted(
            enumerate(self.generators),
            key=lambda x: x[1].cost_per_kwh
        )

        generation = {}
        remaining_demand = total_demand
        total_cost = 0.0

        for idx, gen in sorted_gens:
            if remaining_demand <= 0:
                generation[gen.name] = 0.0
            else:
                # Берём сколько нужно, но не больше мощности генератора
                max_available = gen.hourly_capacity[hour]
                to_generate = min(max_available, remaining_demand)
                generation[gen.name] = to_generate
                total_cost += to_generate * gen.cost_per_kwh
                remaining_demand -= to_generate

        return {
            'hour': hour,
            'status': 'optimal',
            'generation': generation,
            'total_cost': total_cost, # общая стоимость часа
            'total_demand': total_demand, # спрос
            'unmet_demand': 0.0,
            'disconnected_consumers': [],
            'curtailment': sum(generation.values()) - total_demand
        }

    def _optimize_coverage(self, hour: int, total_capacity: float) -> Dict:
        """
        Максимизация покрытия при дефиците энергии
        """
        # Все генераторы на максимум
        generation = {}
        total_cost = 0.0
        for gen in self.generators:
            power = gen.hourly_capacity[hour]
            generation[gen.name] = power
            total_cost += power * gen.cost_per_kwh

        # Сортируем потребителей по приоритету
        sorted_consumers = sorted(
            self.consumers,
            key=lambda c: (c.priority, c.hourly_demand[hour])
        )

        remaining_capacity = total_capacity
        connected = []
        disconnected = []

        for consumer in sorted_consumers:
            demand = consumer.hourly_demand[hour]
            if remaining_capacity >= demand:
                connected.append(consumer.name)
                remaining_capacity -= demand
            else:
                disconnected.append(consumer.name)

        total_demand = sum(c.hourly_demand[hour] for c in self.consumers)

        return {
            'hour': hour,
            'status': 'deficit',
            'generation': generation,
            'total_cost': total_cost,
            'total_demand': total_demand,
            'unmet_demand': total_demand - total_capacity,
            'disconnected_consumers': disconnected,
            'curtailment': 0.0
        }

    def run_simulation(self) -> List[Dict]:
        """Запуск симуляции на 24 часа"""
        results = []
        for hour in range(self.hours):
            result = self.optimize_hour(hour)
            results.append(result)
        return results