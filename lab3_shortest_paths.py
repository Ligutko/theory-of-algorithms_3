"""Лабораторна робота № 3. Найкоротші шляхи: Дейкстра і Флойд.

Завдання (дослівно): 1) для свого варіанту графа знайти найкоротші шляхи до
всіх вершин від вершини a за Дейкстрою; 2) знайти найкоротші шляхи між усіма
парами вершин за Флойдом; 3) написати програмну реалізацію, спосіб
представлення графа - на свій розсуд.

Це ІНШИЙ граф, ніж у Лабі 2 (DFS/BFS) і в Лабі 1 - свій, окремий варіант
2 з додатка В, зважений і орієнтований. Представлення обрано матрицею ваг
C, бо саме так задає граф сама методичка.

Варіант 2. Виконав: студент групи СА-24б Лігутко А.А.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

INF = float('inf')

VERTICES = ['a', 'b', 'c', 'd', 'e', 'f']

# Додаток В, варіант 2 (дуга, вага)
REBRA = [('a', 'b', 3), ('a', 'c', 6), ('b', 'd', 2),
         ('c', 'f', 5), ('d', 'f', 4), ('f', 'e', 7)]


def matrytsya_vah(vertices, rebra):
    """Матриця ваг C: C[i][j] - вага дуги i->j, INF якщо дуги немає."""
    idx = {v: i for i, v in enumerate(vertices)}
    n = len(vertices)
    C = [[INF] * n for _ in range(n)]
    for i in range(n):
        C[i][i] = 0
    for a, b, w in rebra:
        C[idx[a]][idx[b]] = w
    return C


def _pokaz(vertices, C, w=5):
    def cell(x):
        return 'inf' if x == INF else str(x)
    rows = ['      ' + ''.join(f'{v:>{w}}' for v in vertices)]
    for i, v in enumerate(vertices):
        rows.append(f'  {v:>2}  ' + ''.join(f'{cell(x):>{w}}' for x in C[i]))
    return '\n'.join(rows)


def _pokaz_protokol(vertices, protokol, w=5):
    """Той самий формат, що й _pokaz (підписані стовпці, тільки цифри) -
    замість тексту 'a=0, b=3, c=6' рядок за рядком, який важко зчитувати.

    Стовпець "Множина U" доданий за прямою вимогою методички: приклад
    Дейкстри в ній наводить зведену таблицю саме з колонками
    "Кроки | w | Множина U | D[...]" - без явного U тут була б лише
    половина обов'язкового формату."""
    def cell(x):
        return 'inf' if x == INF else str(x)
    shyr_u = max(11, max(len(u) for _, _, u in protokol) + 2)
    rows = ['  крок  Множина U'.ljust(6 + shyr_u)
            + ''.join(f'{v:>{w}}' for v in vertices)]
    for v, d, u in protokol:
        rows.append(f'  +{v:<4}{u:<{shyr_u}}'
                     + ''.join(f'{cell(x):>{w}}' for x in d))
    return '\n'.join(rows)


# ══════════════ АЛГОРИТМ ДЕЙКСТРИ ══════════════

def dijkstra(vertices, C, start):
    """Псевдокод методички буквально: U - оброблені вершини, D - поточні
    найкращі відстані від start. На кожному з n-1 кроків беремо
    необроблену вершину з мінімальним D і релаксуємо через неї.

    Крім D повертає poperednyk - для кожної вершини яка вершина стоїть
    перед нею в найкоротшому шляху від start. Це і є "виписати вершини,
    які передують", яке методичка прямо вимагає для відновлення шляху -
    без цього є лише довжини шляхів, а не самі шляхи.
    """
    idx = {v: i for i, v in enumerate(vertices)}
    n = len(vertices)
    s = idx[start]
    U = {s}
    D = list(C[s])
    poperednyk = [start if C[s][v] < INF else None for v in range(n)]
    poperednyk[s] = None

    def _u_yak_tekst(mnozhyna):
        return '{' + ','.join(vertices[i] for i in sorted(mnozhyna)) + '}'

    protokol = [(start, list(D), _u_yak_tekst(U))]
    for _ in range(n - 1):
        w = min((j for j in range(n) if j not in U), key=lambda j: D[j])
        U.add(w)
        for v in range(n):
            if v not in U and D[w] + C[w][v] < D[v]:
                D[v] = D[w] + C[w][v]
                poperednyk[v] = vertices[w]
        protokol.append((vertices[w], list(D), _u_yak_tekst(U)))
    return D, protokol, poperednyk


def vidnovyty_shlyah(vertices, poperednyk, start, tsil):
    """Йде від tsil назад по poperednyk до start. None, якщо недосяжна."""
    if tsil == start:
        return [start]
    idx = {v: i for i, v in enumerate(vertices)}
    shlyah = [tsil]
    v = tsil
    while v != start:
        p = poperednyk[idx[v]]
        if p is None:
            return None
        shlyah.append(p)
        v = p
    return list(reversed(shlyah))


def print_dijkstra(vertices, C, start):
    print(f'АЛГОРИТМ ДЕЙКСТРИ, ДЖЕРЕЛО = {start}')
    print()
    print('Матриця ваг C (вхідні дані):')
    print(_pokaz(vertices, C))
    print()
    D, protokol, poperednyk = dijkstra(vertices, C, start)
    print('ПРОТОКОЛ - той самий результат детально, крок за кроком '
          '(яку вершину додано і якою стала таблиця D після цього):')
    print(_pokaz_protokol(vertices, protokol))
    print()
    print('НАЙКОРОТШІ ШЛЯХИ - КІНЦЕВИЙ РЕЗУЛЬТАТ (відновлено з '
          'попередників, не лише довжини):')
    for v in vertices:
        shlyah = vidnovyty_shlyah(vertices, poperednyk, start, v)
        d = D[vertices.index(v)]
        if shlyah is None:
            print(f'  до {v}: недосяжна')
        else:
            print(f'  до {v}: ' + ' -> '.join(shlyah) + f'   (довжина {d})')
    return D, poperednyk


# ══════════════ АЛГОРИТМ ФЛОЙДА ══════════════

def floyd(vertices, C):
    """A_0 = C. На кроці k дозволяємо шляхам проходити через вершину k:
    A_k[i][j] = min(A_{k-1}[i][j], A_{k-1}[i][k] + A_{k-1}[k][j]).
    Повертає (A_фінальна, [A_0, A_1, ..., A_n])."""
    n = len(vertices)
    A = [row[:] for row in C]
    usi = [[row[:] for row in A]]
    for k in range(n):
        novi = [row[:] for row in A]
        for i in range(n):
            for j in range(n):
                cherez_k = A[i][k] + A[k][j]
                if cherez_k < novi[i][j]:
                    novi[i][j] = cherez_k
        A = novi
        usi.append([row[:] for row in A])
    return A, usi


def print_floyd(vertices, C):
    print('АЛГОРИТМ ФЛОЙДА, УСІ ПАРИ ВЕРШИН')
    print()
    A, usi = floyd(vertices, C)
    print('A0 - вхідні дані (= матриця ваг C):')
    print(_pokaz(vertices, usi[0]))
    ostannij = len(usi) - 1
    for k in range(1, ostannij):
        zminylosia = usi[k] != usi[k - 1]
        print(f'\nA{k} - проміжний крок, дозволили проходити через '
              f'"{vertices[k-1]}"{"" if zminylosia else " (без змін)"}:')
        print(_pokaz(vertices, usi[k]))
    print()
    print(f'A{ostannij} - ПІДСУМКОВА МАТРИЦЯ, КІНЦЕВИЙ РЕЗУЛЬТАТ '
          f'(найкоротші шляхи між усіма парами):')
    print(_pokaz(vertices, A))
    return A


def _krosschek(vertices, C):
    idx_a = vertices.index('a')
    D, _, _ = dijkstra(vertices, C, 'a')
    A, _ = floyd(vertices, C)
    riadok_a = A[idx_a]
    print('ПЕРЕХРЕСНА ПЕРЕВІРКА - той самий результат від а, порахований '
          'двома різними алгоритмами: рядок "a" матриці Флойда має '
          'збігтися з результатом Дейкстри від a')
    print(f'  Флойд,    рядок a: {riadok_a}')
    print(f'  Дейкстра, D від a: {D}')
    print(f'  збігається: {riadok_a == D}')


if __name__ == '__main__':
    C = matrytsya_vah(VERTICES, REBRA)
    argv = sys.argv[1:]
    if argv == ['dijkstra']:
        print_dijkstra(VERTICES, C, 'a')
    elif argv == ['floyd']:
        print_floyd(VERTICES, C)
    else:
        print('=' * 60)
        print(f'ГРАФ ВАРІАНТА 2, ДОДАТОК В  (n = {len(VERTICES)}, дуг = {len(REBRA)})')
        print('=' * 60)
        print()
        print_dijkstra(VERTICES, C, 'a')
        print()
        print('=' * 60)
        print()
        print_floyd(VERTICES, C)
        print()
        print('=' * 60)
        _krosschek(VERTICES, C)
