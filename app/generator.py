"""
Обработчик запроса пользователя.
Принимает через функцию start_module запрос пользователя (user_req).
Возвращает подготовленный для публикации текст.

"""

import pymorphy2
import re
from app.dbpanel import DBWork, get_content

# Тэги для БД urlbase
URL_NAME = 0
URL_URL = 1
URL_LANG = 2
URL_TYPE = 3
URL_TAGS = 4

morphy = pymorphy2.MorphAnalyzer()


def start_module(user_req) -> str:
    """
  Возвращает данные по запросу пользователя или сообщение об ошибке.

  :param user_req: Текст запроса пользователя.
  :return: Подготовленный к публикации ответ по запросу пользователя.

  """

    if not re.match(r'.*[^0-9 +\-\*\/()].*', user_req):
        try:  # Путь 1: пользователь ввёл калькуляторную строку
            return eval(user_req)
        except ValueError:
            return 'Ошибка расчёта.'

    # Проверка 2: пользователь ввёл запрос для БД.
    answer = in_user_string(user_req, to_print=False)
    if not answer:
        answer = 'Нет подходящих данных или неверный запрос.'

    return answer


def in_user_string(user_req, *, to_print=True) -> dict or str:
    """
  Распознаёт слова (фразы) в запросе пользователя. Формирует словарь по предустановленному шаблону.

  :param user_req: Строка запроса пользователя.
  :param to_print: Технический параметр. Если False - возвращает словарь.
  True - возвращает текст подготовленный для публикации.
  :return: Словарь содержащий обнаруженные слова предпочтений и исключений (отрицаний).

  """

    key_dict = {'tag': [], 'lang': [], 'type': [], 'extag': [], 'exlang': [], 'extype': []}  # lang, type, tag

    user_phrase = re.findall(r'\S+', user_req.lower())
    point_in_phrase = len(user_phrase) - 1

    # Кроличья нора: вывести всё сразу.
    if user_phrase[0] in ['всё', 'все', 'all'] or not user_phrase:
        return new_print_lib(key_dict)

    cq_new_tag = DBWork()
    shift_in_left = 0  # флаг сдвига по строке.

    # Проверка ведётся от последнего слова к первому. Цель - поиск словосочетаний и отрицаний (не, нет)
    while point_in_phrase - shift_in_left >= 0:

        def check_in_bd(word) -> list or 0 or None:
            """
          Проверяет слово (фразу) на присутствие в базе данных и локальном словаре уже отобранных слов.
          Применяет морфологический анализ для идентификации слов в различных склонениях.

          :param word: Слово (фраза) для проверки.
          :return: Список из двух значений: [вид фразы, фраза].
          0 - если предлог (неисследуемое слово).
          None - если слово не найдено в словарях.

      """

            word_morph = morphy.parse(word)[0]
            # Предлоги опускаются.
            if word_morph.tag.POS == 'PREP':
                return 0

            # Категории.
            if word in cq_new_tag.category_list.keys() and \
                    cq_new_tag.category_list[word] not in key_dict['tag']:
                return ['tag', cq_new_tag.category_list[word]]

            # Язык.
            if word in cq_new_tag.lang_list and \
                    word not in key_dict['lang']:
                return ['lang', word]

            # Типы
            if word in cq_new_tag.types_list.keys() and \
                    cq_new_tag.types_list[word] not in key_dict['type']:
                return ['type', cq_new_tag.types_list[word]]

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
        return ''

    return new_print_lib(key_dict)


def new_print_lib(query: dict) -> str:

    in_print = get_content(**query)
    types = {val: key for key, val in DBWork().get_types_name().items()}
    types_id = None
    text_print = ''
    for string in in_print:
        if types_id != string.types_id:
            text_print += '</p>' if text_print else ''
            text_print += f'<h3><span class="green_color">{types[string.types_id].title()}</span></h3>'
            text_print += '<p class="lead">'
            types_id = string.types_id

        text_print += f'<a id="urldb" href="{string.url}">{string.name}</a><br>'
    text_print += '</p>'

    return text_print


# Документирование.
__all__ = ['start_module', 'CompileReq']
