# Обработка командной строки.
import app._dblib as db
import pymorphy2
import re
import logging

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
    logging.info(f'{start_module.__name__} start')

    if not re.match(r'.*[^0-9 +\-\*\/()].*', user_req):
        try:  # Путь 1: пользователь ввёл калькуляторную строку
            return eval(user_req)
        except ValueError:
            return 'Ошибка расчёта.'

    # Проверка 2: пользователь ввёл запрос для БД.
    answer = in_user_string(user_req)
    if not answer:
        answer = 'Нет подходящих данных или неверный запрос.'

    logging.info(f'{start_module.__name__} finish')
    return answer


class CompileReq:
    """
  Формирует по базе данных полный или частный набор тэгов для записей.

  :param key: Ключ категории записей в базе данных для отбора тэгов (не обязательно).

  """

    def __init__(self, *, key=None):

        self.key = key
        self.tag_lst = list()

        if self.key is None:
            for tag in db.urlbase.values():
                [self.tag_lst.append(item.strip()) for item in tag[URL_TAGS] if item.strip() not in self.tag_lst]
        else:
            for key, for_key in db.keytypedisp.items():
                if for_key.lower() == self.key.lower():
                    find_key = key
                    break
            else:
                find_key = ''

            for tag in db.urlbase.values():
                [self.tag_lst.append(item.strip()) for item in tag[URL_TAGS] if
                 item.strip() not in self.tag_lst and tag[URL_TYPE] == find_key]

    def get_tag(self) -> list:
        """
    Возвращает список тэгов.

    :return: Список выбранных тэгов.

    """

        return self.tag_lst


def in_user_string(user_req) -> dict or str:
    """
  Распознаёт слова (фразы) в запросе пользователя. Формирует словарь по предустановленному шаблону.

  :param user_req: Строка запроса пользователя.
  :return: Словарь содержащий обнаруженные слова предпочтений и исключений (отрицаний).

  """

    key_dict = {'tag': [], 'lang': [], 'type': [], 'extag': [], 'exlang': [], 'extype': []}  # lang, type, tag
    
    user_phrase = re.findall(r'\S+', user_req.lower())
    point_in_phrase = len(user_phrase) - 1
    
    # Кроличья нора: вывести всё сразу.
    if user_phrase[0] in ['всё', 'все', 'all'] or not user_phrase:
        return return_lib(key_dict, to_print=True)

    cq_tag = CompileReq()
    shift_in_left = 0  # флаг сдвига по строке.

    while point_in_phrase - shift_in_left >= 0:

        # Проверка ведётся от последнего слова к первому. Цель - поиск словосочетаний и отрицаний (не, нет)

        # * Внутренняя функция проверки слов по базе данных.

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
            if word_morph.tag.POS == 'PREP':  # Предлоги опускаются.
                return 0

                # тэги
            if word in cq_tag.get_tag() and \
                    word not in key_dict['tag'] and \
                    word not in key_dict['extag']:
                return ['tag', word]

                # язык
            for id_, string in db.langtype.items():
                if word_morph.normal_form in string and \
                        word_morph.normal_form not in key_dict['lang'] \
                        and word_morph not in key_dict['exlang']:
                    return ['lang', id_]

                # категории
            for id_, string in db.keytypedisp.items():
                if word == string.lower() and \
                        word not in key_dict['type'] and \
                        word not in key_dict['extype']:
                    return ['type', id_]

            return

        # * Конец внутренней процедуры.

        actually_word = user_phrase[point_in_phrase]
        if shift_in_left > 0:
            actually_word = f'{user_phrase[point_in_phrase - shift_in_left]} {actually_word}'

        actually_word_check = check_in_bd(actually_word)

        if actually_word_check == 0 or (actually_word_check is None and shift_in_left > 0):
            point_in_phrase, shift_in_left = point_in_phrase - shift_in_left - 1, 0
        elif actually_word_check is None:
            shift_in_left = 1
        else:
            word_negative = (morphy.parse(user_phrase[point_in_phrase - shift_in_left - 1])[
                                 0] if point_in_phrase - shift_in_left - 1 >= 0 else morphy.parse('')[0])

            if word_negative.normal_form in ['без', 'не', 'исключить']:
                key_dict[f'ex{actually_word_check[0]}'].append(actually_word_check[1])
            else:
                key_dict[actually_word_check[0]].append(actually_word_check[1])

            point_in_phrase, shift_in_left = point_in_phrase - shift_in_left - 1, 0

    # Не найдено ни одного ключевого слова.
    if not all(True for values in key_dict.values() if values):
        return ''

    return return_lib(key_dict, to_print=True)


def return_lib(dict_req, *, to_print=False) -> dict or str:
    """
  Формирует и возвращает словарь со значениями из базы данных, собранных по распознаным словам.

  :param dict_req: Словарь распознанных слов, сформированный по шаблону.
  :param to_print: True - возврат текста для печати, False - возврат только словаря с выборкой.

  """

    dic_result = {}

    for string in db.urlbase.values():
        # Флаг включения строки в выборку, false - нет
        in_tag = False
        in_cat = False
        lang = False

        # Проверка тэгов
        if not dict_req['tag']:
            in_tag = True
        elif set(string[URL_TAGS]) >= set(dict_req['tag']):
            in_tag = True
        # исключение
        if dict_req['extag'] and set(string[URL_TAGS]) >= set(dict_req['extag']):
            in_tag = False

        # Проверка категории
        if not dict_req['type']:
            in_cat = True
        elif string[URL_TYPE] in dict_req['type']:
            in_cat = True
        # исключение
        if string[URL_TYPE] in dict_req['extype']:
            in_cat = False

        # Проверка языка (проверяем только если указано, иначе - берём всё).
        if not dict_req['lang']:
            lang = True
        elif string[URL_LANG] in dict_req['lang']:
            lang = True
        # исключение
        if string[URL_LANG] in dict_req['exlang']:
            lang = False

        if in_tag and in_cat and lang:  # Строка включается
            # Если категории в словаре нет, создадим.
            if dic_result.get(string[URL_TYPE]) is None:
                dic_result.update({string[URL_TYPE]: []})
            if string[URL_LANG] != 'ru':
                dic_result[string[URL_TYPE]].append(f'({string[URL_LANG]}) {string[URL_NAME]}')
            else:
                dic_result[string[URL_TYPE]].append(string[URL_NAME])
            dic_result[string[URL_TYPE]].append(string[URL_URL]) 

        in_tag = in_cat = lang = False

    if to_print:
        return print_lib(dic_result)
    else:
        return dic_result


def print_lib(dict_to_print) -> str:
    """
  Формирует текстовый блок для вывода пользователю на основе полученного словаря с выборкой из базы данных.

  :param dict_to_print: Словарь с выборкой результатов из базы данных.

  """

    text_print = ''

    for key_type in db.keytypedisp.keys():
        if dict_to_print.get(key_type):  # is not None
            text_print += f'<h3><span class="green_color">{db.keytypedisp[key_type]}</span></h3>'
            text_print += '<p class="lead">'

            for to_print in range(0, len(dict_to_print[key_type]), 2):
                text_print += f'<a id="urldb" href="{dict_to_print[key_type][to_print + 1]}">{dict_to_print[key_type][to_print]}</a><br>'

            text_print += '</p>'

    return text_print
