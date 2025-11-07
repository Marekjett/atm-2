import random


def to_tablica(x):
    return [int(c) for c in str(x)]

def gen_key():
    max_tries = 1_000_000_000
    for epoch in range(max_tries):
        x = random.randint(100_000_000, 999_999_999)
        tab = to_tablica(x)

        # warunek 1 — odrzuć liczby, gdzie tab[6] == 0 i tab[8] != 0
        if not tab[6] and tab[8]:
            continue

        # warunek 2 — druga i trzecia cyfra muszą sumować się do 3
        if tab[1] + tab[2] != 3:
            continue

        # warunek 3 — cyfra środkowa (4.) musi być parzysta
        if tab[4] % 2 != 0:
            continue

        # warunek 4 — ostatnia cyfra musi być mniejsza niż 5
        if tab[8] >= 5:
            continue

        # warunek 5 — suma wszystkich cyfr musi być w określonym zakresie
        s = sum(tab)
        if s < 25 or s > 35:
            continue

        return x

    return False
def validate_key(x):
    """
    Sprawdza poprawność 9-cyfrowego kodu zgodnie z zasadami gen_key().
    Zwraca True jeśli kod jest poprawny, False w przeciwnym wypadku.
    """
    # typ i długość
    if not isinstance(x, int):
        return False
    if x < 100_000_000 or x > 999_999_999:
        return False

    tab = to_tablica(x)

    # warunek 1
    if not tab[6] and tab[8]:
        return False

    # warunek 2
    if tab[1] + tab[2] != 3:
        return False

    # warunek 3
    if tab[4] % 2 != 0:
        return False

    # warunek 4
    if tab[8] >= 5:
        return False

    # warunek 5
    s = sum(tab)
    if s < 25 or s > 35:
        return False

    return True
