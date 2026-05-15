import matplotlib.pyplot as plt
from models import Consumer, Generator
from optimizer import EnergyOptimizer
from visualizer import EnergyVisualizer
from test_cases import create_test_case_surplus, test_case_deficit


def run_scenario(scenario_name, consumers, generators):
    """Запуск одного сценария"""
    print(f"\n{'=' * 80}")
    print(f"  {scenario_name}")
    print(f"{'=' * 80}")

    optimizer = EnergyOptimizer(consumers, generators)
    results = optimizer.run_simulation()

    gen_names = [g.name for g in generators]

    # ==================== ТАБЛИЦА 1: РАСПИСАНИЕ ГЕНЕРАТОРОВ ====================
    print(f"\n  РАСПИСАНИЕ РАБОТЫ ГЕНЕРАТОРОВ (кВт)")

    COL_WIDTH = 22  # ширина столбца

    total_width = 6 + COL_WIDTH * len(gen_names) + 10 + 10 + 12
    print("-" * total_width)

    header = f"{'Час':<6}"
    for name in gen_names:
        short_name = name[:COL_WIDTH - 2] if len(name) > COL_WIDTH - 2 else name
        header += f"{short_name:<{COL_WIDTH}}"
    header += f"{'Сумма':<10}{'Спрос':<10}{'Статус':<12}"
    print(header)
    print("-" * total_width)

    for r in results:
        row = f"{r['hour']:<6}"
        for name in gen_names:
            power = r['generation'].get(name, 0.0)
            row += f"{power:<{COL_WIDTH}.1f}"
        total_gen = sum(r['generation'].values())
        status = 'OK' if r['status'] in ['optimal', 'OK'] else 'DEFICIT'
        row += f"{total_gen:<10.1f}{r['total_demand']:<10.1f}{status:<12}"
        print(row)

    # ==================== ТАБЛИЦА 2: ПОЧАСОВАЯ СТОИМОСТЬ ====================
    print(f"\n\n ПОЧАСОВАЯ СТОИМОСТЬ ЭНЕРГИИ")
    print("-" * 60)
    print(f"{'Час':<6} {'Стоимость (у.е.)':<20} {'Генерация (кВт)':<18} {'Цена за кВт':<15}")
    print("-" * 60)

    for r in results:
        total_gen = sum(r['generation'].values())
        if total_gen > 0:
            price_per_kwh = r['total_cost'] / total_gen
        else:
            price_per_kwh = 0
        print(f"{r['hour']:<6} {r['total_cost']:<20.2f} {total_gen:<18.1f} {price_per_kwh:<15.3f}")

    # ==================== ТАБЛИЦА 3: ОТКЛЮЧЁННЫЕ ПОТРЕБИТЕЛИ ====================
    print(f"\n\n ОТКЛЮЧЁННЫЕ ПОТРЕБИТЕЛИ")
    print("-" * 70)

    hours_with_deficit = sum(1 for r in results if r['status'] in ['deficit', 'DEFICIT'])

    if hours_with_deficit == 0:
        print("Все потребители получают энергию, отключений нет.")
    else:
        print(f"{'Час':<6} {'Дефицит (кВт)':<16} {'Отключены'}")
        print("-" * 70)
        for r in results:
            if r['status'] in ['deficit', 'DEFICIT']:
                disconnected = r.get('disconnected_consumers', r.get('disconnected', []))
                if disconnected:
                    consumers_list = ', '.join(disconnected)
                else:
                    consumers_list = '(нет данных)'
                print(f"{r['hour']:<6} {r['unmet_demand']:<16.1f} {consumers_list}")

    # ==================== ИТОГОВАЯ СТАТИСТИКА ====================
    total_daily_cost = sum(r['total_cost'] for r in results)
    total_daily_demand = sum(r['total_demand'] for r in results)
    total_daily_gen = sum(sum(r['generation'].values()) for r in results)
    hours_ok = 24 - hours_with_deficit

    solar_gen = sum(
        sum(r['generation'].get(g.name, 0) for g in generators if g.generator_type == 'solar')
        for r in results
    )
    diesel_gen = sum(
        sum(r['generation'].get(g.name, 0) for g in generators if g.generator_type == 'diesel')
        for r in results
    )

    print(f"\n{'=' * 70}")
    print(f"ИТОГОВАЯ СТАТИСТИКА ЗА СУТКИ")
    print(f"  {'=' * 70}")
    print(f"  Общая стоимость:        {total_daily_cost:>10.2f} у.е.")
    print(f"  Общий спрос:            {total_daily_demand:>10.1f} кВт·ч")
    print(f"  Общая генерация:        {total_daily_gen:>10.1f} кВт·ч")
    if total_daily_gen > 0:
        print(f"    - солнечные фермы:    {solar_gen:>10.1f} кВт·ч ({solar_gen / total_daily_gen * 100:.0f}%)")
        print(f"    - дизель-генераторы:  {diesel_gen:>10.1f} кВт·ч ({diesel_gen / total_daily_gen * 100:.0f}%)")
    if total_daily_demand > 0:
        print(f"  Покрытие спроса:        {total_daily_gen / total_daily_demand * 100:>10.1f}%")
    print(f"  Часов без дефицита:     {hours_ok:>10}")
    print(f"  Часов с дефицитом:      {hours_with_deficit:>10}")
    if total_daily_gen > 0:
        print(f"  Средняя цена за кВт·ч:  {total_daily_cost / total_daily_gen:>10.3f} у.е.")
    print(f"{'=' * 70}")

    # ==================== ВИЗУАЛИЗАЦИЯ ====================
    viz = EnergyVisualizer()
    fig = viz.plot_all_in_one(results, generators, scenario_name)
    plt.show()

    return results


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                СИМУЛЯТОР ЭНЕРГОСЕТИ - ТЕСТОВЫЕ СЦЕНАРИИ                  ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")

    # Сценарий 1: Лето (избыток)
    consumers1, generators1 = create_test_case_surplus()
    results1 = run_scenario("ЛЕТНИЙ ДЕНЬ — ИЗБЫТОК ЭНЕРГИИ", consumers1, generators1)

    # Сценарий 2: Зима (дефицит)
    consumers2, generators2 = test_case_deficit()
    results2 = run_scenario("ЗИМНИЙ ДЕНЬ — ДЕФИЦИТ ЭНЕРГИИ", consumers2, generators2)