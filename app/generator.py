"""
Обработчик запроса пользователя.
Принимает через функцию start_module запрос пользователя (user_req).
Возвращает подготовленный для публикации текст.
"""

import re
from app.dbpanel import DBWork, get_content


def start_module(user_req) -> str:
    """
  Возвращает данные по запросу пользователя или сообщение об ошибке.

  :param user_req: Текст запроса пользователя.
  :return: Подготовленный к публикации ответ по запросу пользователя.

  """

    answer = get_key_from_request(user_req)
    if not answer:
        return 'Нет подходящих данных или неверный запрос.'

    return get_print_text(answer_bd=get_content(**answer))


def get_key_from_request(user_req: str) -> dict:
    """
  Распознаёт слова (фразы) в запросе пользователя. Формирует словарь по предустановленному шаблону.

  :param user_req: Строка запроса пользователя.
  :return: Словарь содержащий обнаруженные слова предпочтений и исключений (отрицаний),
  либо пустой словарь, если запрос неизвестный.

  """

    key_dict = {'tag': [], 'lang': [], 'type': [], 'extag': [], 'exlang': [], 'extype': []}  # lang, type, tag

    user_phrase = re.findall(r'\S+', user_req.lower())
    point_in_phrase = len(user_phrase) - 1

    # Кроличья нора: вывести всё сразу.
    if user_phrase[0] in ['всё', 'все', 'all'] or not user_phrase:
        return key_dict

    dbw = DBWork()
    shift_in_left: int = 0  # флаг сдвига по строке.

    # Проверка ведётся от последнего слова к первому. Цель - поиск словосочетаний и отрицаний (не, нет)
    while point_in_phrase - shift_in_left >= 0:

        def check_in_bd(word) -> list or None:
            """
          Проверяет слово (фразу) на присутствие в базе данных и локальном словаре уже отобранных слов.
          Применяет морфологический анализ для идентификации слов в различных склонениях.

          :param word: Слово (фраза) для проверки.
          :return: Список из двух значений: [вид фразы, фраза].
          None - если слово не найдено в словарях.

      """

            # Категории.
            if word in dbw.get_list_category.keys() and \
                    dbw.get_list_category[word] not in key_dict['tag']:
                return ['tag', dbw.get_list_category[word]]

            # Язык.
            if word in dbw.get_list_language and \
                    word not in key_dict['lang']:
                return ['lang', word]

            # Типы
            if word in dbw.get_list_types.keys() and \
                    dbw.get_list_types[word] not in key_dict['type']:
                return ['type', dbw.get_list_types[word]]

            return

        actually_word = user_phrase[point_in_phrase]
        if shift_in_left > 0:
            actually_word = f'{user_phrase[point_in_phrase - shift_in_left]} {actually_word}'

        actually_word_check = check_in_bd(actually_word)

        if actually_word_check == 0 or (actually_word_check is None and shift_in_left > 0):
            point_in_phrase, shift_in_left = point_in_phrase - shift_in_left - 1, 0
        elif actually_word_check is None:
            shift_in_left = 1
        else:
            key_dict[actually_word_check[0]].append(actually_word_check[1])
            point_in_phrase, shift_in_left = point_in_phrase - shift_in_left - 1, 0

    # Не найдено ни одного ключевого слова.
    if not all(True for values in key_dict.values() if values):
        return dict()

    return key_dict


def get_print_text(*, answer_bd: list) -> str:
    """
    Обрабатывает результаты запроса базы данных и переводит
    в html-текст.
    :param {dict} answer_bd: Список с результатами обработки в базе данных.
    :return: Форматированный текст с HTML-тегами.
    """

    types = DBWork().get_list_types_reverse
    types_id: int = -1
    text_print: str = ''
    for string in answer_bd:
        if types_id != string.types_id:
            text_print += '</p>' if text_print else ''
            text_print += f'<h3><span class="green_color">{types[string.types_id].title()}</span></h3>'
            text_print += '<p class="lead">'
            types_id = string.types_id

        text_print += f'<a id="urldb" href="{string.url}">{string.name}</a>'
        text_print += '<br>' if string.lang == 'ru' else f' ({string.lang})<br>'

    return f'{text_print}</p>'


# Документирование.
__all__ = ['start_module']
