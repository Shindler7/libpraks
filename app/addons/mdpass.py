"""
Генератор паролей.
"""

import random

DICT_SOURCE = (
    [uc for uc in range(65, 91)],  # заглавные
    [lc for lc in range(97, 123)],  # строчные
    [digit for digit in range(48, 58)],  # цифры
    [33, 35, 36, 37, 38, 64],  # спецсимволы !#@$%&^
)


def generate_pass_block(**kwargs):
    """
    Генератор паролей. Действует по маске.
    """

    def get_random_symbol(word_len: int):
        rounds = 0
        cur, prev = None, None
        one_time = []
        while rounds < word_len:

            while cur == prev or cur in one_time:
                cur = random.randint(0, len(DICT_SOURCE) - 1)

            if cur == 3:
                one_time.append(cur)
            else:
                prev = cur

            yield chr(
                random.choice(DICT_SOURCE[cur])
            )

            rounds += 1

    return ''.join(s for s in get_random_symbol(
        word_len=random.randint(kwargs['min_len'], kwargs['max_len'])
    ))


def pass_generate():
    """
    Стартовая процедура генератора паролей.
    """

    func = generate_pass_block
    param = {'min_len': 4, 'max_len': 6}
    return f'{func(**param)}-{func(**param)}-{func(**param)}'


__all__ = ['pass_generate']
