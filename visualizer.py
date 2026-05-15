import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict


class EnergyVisualizer:
    """Визуализация результатов симуляции"""

    @staticmethod
    def plot_all_in_one(results, generators, scenario_name):

        hours = range(24)
        gen_names = [g.name for g in generators]
        has_deficit = any(r['status'] in ['deficit', 'DEFICIT'] for r in results)

        if has_deficit:
            fig = plt.figure(figsize=(14, 10))
        else:
            fig = plt.figure(figsize=(14, 5))

        fig.suptitle(scenario_name, fontsize=14, fontweight='bold')

        # ГРАФИК 1: Генерация энергии
        if has_deficit:
            ax1 = plt.subplot(2, 2, 1)
        else:
            ax1 = plt.subplot(1, 2, 1)

        bottom = np.zeros(24)
        colors = plt.cm.Set3(np.linspace(0, 1, len(generators)))

        for i, name in enumerate(gen_names):
            values = [r['generation'][name] for r in results]
            ax1.bar(hours, values, bottom=bottom, label=name, color=colors[i], alpha=0.8)
            bottom += np.array(values)

        demand = [r['total_demand'] for r in results]
        ax1.plot(hours, demand, 'r--', linewidth=1.5, label='Спрос')
        ax1.set_xlabel('Час')
        ax1.set_ylabel('кВт')
        ax1.set_title('Генерация энергии по источникам')
        ax1.legend(fontsize=7, loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(range(0, 24))

        # ГРАФИК 2: Стоимость
        if has_deficit:
            ax2 = plt.subplot(2, 2, 2)
        else:
            ax2 = plt.subplot(1, 2, 2)

        costs = [r['total_cost'] for r in results]
        ax2.bar(hours, costs, color='orange', alpha=0.7)
        ax2.set_xlabel('Час')
        ax2.set_ylabel('у.е.')
        ax2.set_title('Почасовая стоимость энергии')
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(range(0, 24))
        avg_cost = np.mean(costs)
        ax2.axhline(y=avg_cost, color='r', linestyle='--', label=f'Средняя: {avg_cost:.2f}')
        ax2.legend(fontsize=8)

        if has_deficit:
            # ГРАФИК 3: Дефицит
            ax3 = plt.subplot(2, 2, 3)
            unmet = [r['unmet_demand'] for r in results]
            ax3.bar(hours, unmet, color='red', alpha=0.7, edgecolor='black', linewidth=0.3)
            ax3.set_xlabel('Час')
            ax3.set_ylabel('кВт')
            ax3.set_title('Дефицит')
            ax3.grid(True, alpha=0.3)
            ax3.set_xticks(range(0, 24))

            # ГРАФИК 4: Отключения
            ax4 = plt.subplot(2, 2, 4)
            disc_counts = [len(r.get('disconnected_consumers', r.get('disconnected', []))) for r in results]
            ax4.bar(hours, disc_counts, color='darkred', alpha=0.7)
            ax4.set_xlabel('Час')
            ax4.set_ylabel('Кол-во')
            ax4.set_title('Отключеные потребители')
            ax4.grid(True, alpha=0.3)
            ax4.set_xticks(range(0, 24))

        plt.tight_layout(pad=2.0, h_pad=3.0, w_pad=2.0)
        return fig