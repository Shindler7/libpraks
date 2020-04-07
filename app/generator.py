# Обработка командной строки.
import app._dblib as db
import pymorphy2
import re

# Тэги для БД urlbase
URL_NAME = 0
URL_URL = 1
URL_LANG = 2
URL_TYPE = 3
URL_TAGS = 4

morh = pymorphy2.MorphAnalyzer()

def startmodule(user_req):
  """
  Возвращает данные по запросу пользователя или ошибку.
  :param user_req: Строка (str) с запросом пользователя или текстом ошибки.
  :return: Str
  """
  
  if not re.match(r'.*[^0-9 +\-\*\/()].*', user_req): #валидируем ввод на что-то еще кроме цифр, матем.знаков и скобок
    try:     # Путь 1: пользователь ввёл калькуляторную строку
      return eval(user_req)
    except:
      return 'Ошибка расчёта.'

  # Проверка 2: пользователь ввёл запрос для БД.
  answer = inuserstring(user_req)
  if not answer: return 'Нет подходящих данных или неверный запрос.'

  return answer

class compilereq():
  """
  Класс производит компиляцию списка уникальных тэгов в базе данных (urlbase).
  """

  def __init__(self):
    
    tag_lst = list()
    for key in db.urlbase.values():
      [tag_lst.append(item.strip()) for item in key[URL_TAGS] if item.strip() not in tag_lst]

    self._tag_lst = tag_lst

  def getTag(self):
    """
    Возвращается list уникальных тэгов в базе данных (urlbase)
    :return: List()
    """
    return self._tag_lst

def inuserstring(user_req):
  """
  Анализ строки запроса пользователя и выделение ключевых слов-зависимостей.
  :param user_req: Строка запроса пользователя (str).
  :return: Словарь (dict) содержащий обнаруженные слова предпочтений и исключений (отрицаний).
  """
  
  key_dict = {'tag': [], 'lang': [], 'type': [], 'extag': [], 'exlang': [], 'extype': []} # lang, type, tag

  user_phrase = re.findall(r'\S+', user_req.lower())
  point_uphrase = len(user_phrase)-1
  
  # Кроличья нора: вывести всё сразу.
  if user_phrase[0] in ['всё', 'все', 'all'] or not user_phrase:
    return returnLib(key_dict, to_print=True)
  
  cq_tag = compilereq()
  shift_inleft = 0  # флаг сдвига по строке.
  
  while point_uphrase-shift_inleft >= 0:
    
    # Проверка ведётся от последнего слова к первому. Цель - поиск словосочетаний и отрицаний (не, нет)

    # * Внутренняя функция проверки слов по базе данных.
    def checkinBD(word):
      """
      Проверяется принятая фраза (слово) на присутствие в базе данных, а также в локальном словаре уже отобранных слов.
      :param word: Слово или фраза (str) для проверки.
      :return: Str, в формате 'видфразы*фраза' - когда фраза и её принадлежность определены.
      :return: 0, слово не опознано. 
      :return: None, фраза не для обработки (предлоги) или возникло исключение (например, out of range).
      """

      try:
        word_morh = morh.parse(word)[0]      
        if word_morh.tag.POS == 'PREP':      # Предлоги опускаются.
          return 

        # тэги
        if word in cq_tag.getTag() and word not in key_dict['tag'] and word not in key_dict['extag']: 
          return f'tag*{word}'
      
        # язык
        for id, string in db.langtype.items():
          if word_morh.normal_form in string and word_morh.normal_form not in key_dict['lang'] and word not in key_dict['exlang']: 
            return f'lang*{id}'
        
        # другие слова
        for id, string in db.keytype.items():
          if word_morh.normal_form in string and word_morh.normal_form not in key_dict['type'] and word not in key_dict['extype']: 
            return f'type*{id}'
      except: 
        return
      else:
        return 0 # Все проверки провалены.
    # * Конец внутренней процедуры.

    actualy_word = user_phrase[point_uphrase]
    if shift_inleft > 0:
      actualy_word = f'{user_phrase[point_uphrase-shift_inleft]} {actualy_word}'
    
    actualy_word_check = checkinBD(actualy_word)
    if actualy_word_check is None:
      point_uphrase, shift_inleft = point_uphrase-shift_inleft-1, 0
    elif actualy_word_check == 0:
      if shift_inleft == 0:
        shift_inleft = 1
      else:
        point_uphrase, shift_inleft = point_uphrase-shift_inleft, 0
    else:
      try:  # обработка out of range
        word_negative = morh.parse(user_phrase[point_uphrase-shift_inleft-1])[0]
      except:
        word_negative = None
      finally:  # проверка исключения ("не flask")
        key_name = actualy_word_check.split('*')
        if word_negative.normal_form in ['без', 'не', 'исключить']: 
          key_dict[f'ex{key_name[0]}'].append(key_name[1])
        else: 
          key_dict[key_name[0]].append(key_name[1])

      point_uphrase, shift_inleft = point_uphrase-shift_inleft-1, 0
  
  # Не найдено ни одного ключевого слова.
  if sum(True for values in key_dict.values() if values) == 0:
    return ''
  
  return returnLib(key_dict, to_print=True)


def returnLib(dict_req, to_print=False):
  """
  Возвращает словарь с выборкой результатов на основе словаря расшифрованных запросов пользователя.
  :param dict_req: Словарь (dict) с фразами для выборки на основе запроса пользователя.
  :param to_print: True - возврат текста для печати, False - возврат только словаря с выборкой.
  :return: Str, dict
  """

  dic_result = {}

  for string in db.urlbase.values():
    # Флаг включения строки в выборку, false - нет
    in_tag=False      
    in_cat=False
    lang=False

    # Проверка тэгов
    if not dict_req['tag']: in_tag=True
    elif (set(string[URL_TAGS]) >= set(dict_req['tag'])) == True: in_tag=True
    # исключение
    if dict_req['extag'] and (set(string[URL_TAGS]) >= set(dict_req['extag'])) == True: in_tag=False

    # Проверка категории
    if not dict_req['type']: in_cat=True
    elif string[URL_TYPE] in dict_req['type']: in_cat=True
    # исключение
    if string[URL_TYPE] in dict_req['extype']: in_cat=False

    # Проверка языка (проверяем только если указано, иначе - берём всё). 
    if not dict_req['lang']: lang=True
    elif string[URL_LANG] in dict_req['lang']: lang = True
    # исключение
    if string[URL_LANG] in dict_req['exlang']: lang = False
    
    if in_tag and in_cat and lang:    # Строка включается
      # Если категории в словаре нет, создадим. 
      if dic_result.get(string[URL_TYPE]) is None: dic_result.update({string[URL_TYPE]:[]})
      if string[URL_LANG] != 'ru':
        dic_result[string[URL_TYPE]].append(f'({string[URL_LANG]}) {string[URL_NAME]}')
      else:
        dic_result[string[URL_TYPE]].append(string[URL_NAME])
      dic_result[string[URL_TYPE]].append(string[URL_URL])

    in_tag, in_cat, lang = False, False, False

  if to_print:
    return printLib(dic_result)
  else:
    return dic_result            

def printLib(dict_to_print):
  """
  Возвращает текст для печати, сформированный на основе переданного словаря с выборкой по запросу пользователя.
  :param: dict_to_print - словарь (dict) с выборкой по запросу пользователя.
  :return: str
  """

  text_print = ''

  for key_type in db.keytypedisp.keys():
    if dict_to_print.get(key_type): #is not None
      text_print += f'<span id="hehe">{db.keytypedisp[key_type]}</span><br>'
      text_print += '<p>'

      for to_print in range(0, len(dict_to_print[key_type]), 2):
        text_print += f'<a id="urldb" href="{dict_to_print[key_type][to_print+1]}">{dict_to_print[key_type][to_print]}</a><br>'
      
      text_print += '</p><br>'

  return text_print

