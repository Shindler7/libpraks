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

ALL_DATA = False

# запуск морфологии
morh = pymorphy2.MorphAnalyzer()

def startmodule(text):
    if not re.match(r'.*[^0-9 +\-\*\/()].*', text): #валидируем ввод на что-то еще кроме цифр, матем.знаков и скобок
        try:     # Путь 1: пользователь ввёл калькуляторную строку
            return eval(text)
        except:
            return 'Ошибка расчёта.'

    # Проверка 2: пользователь ввёл запрос для БД.
    answer = inuserstring(text)
    if not answer: return 'Нет подходящих данных, ну или неверный запрос.'

    return answer

class compilereq():
  # Проверка базы и рекомпиляция списков: типы ссылок и существующие тэги.
  def __init__(self):
    
    at = []
    for key in db.urlbase.values():
      for item in key[URL_TAGS]: # уникальный набор тэгов.
        if item.strip() not in at: at.append(item.strip())

    self._tagurl = at

  def getTag(self):
    return self._tagurl

def inuserstring(txt):
  # Разбор запроса пользователя.
  
  ustr = txt.lower()
  ustr = re.findall(r'\S+', ustr)
  lenUstr = len(ustr)-1 # индекс от длины.

  key_dict = {'tag': [], 'lang': [], 'type': [], 'extag': [], 'exlang': [], 'extype': []} # lang, type, tag
  
  # Кроличья нора: выводится всё, поэтому тратить время на подборку не нужно.
  TakeAll = ['всё', 'все', 'all']
  if ustr[0] in TakeAll:
      res = returnLib(key_dict)
      res = printLib(res)
      return res
  
  # Подготовительные процедуры для цикла.
  clTagGl = compilereq()
  INLEFT = 0  # флаг сдвига по строке.
  
  # Цикл обработки фразы пользователя.
  while True:
    
    # СЛОВО1 СЛОВО2 СЛОВО3 - возможно СЛОВО1 и СЛОВО2 - ключевая фраза (база данных), и возможно отрицание (исключение)
    # Поэтому проверка идёт от последнего слова к первому. С накоплением фразы.
    # 'Статичное напряжение во Flask без базы данных'.
    # данных - не ключевое слово
    # базы данных - ключевая фраза (+)
    # без - отрицание - и фраза уходит в исключение.
    # Flask - ключевое слово
    # во - предлог. Flask (+)

    if lenUstr-INLEFT < 0 or not ustr: break    # выход после анализа или если строка пустая.

    # ********** внутренняя процедура проверки по базе
    def checkinBD(word):
      
      try:
        smorh = morh.parse(word)[0]      # Подключили морфологию.  
        if smorh.tag.POS == 'PREP':      # Сами по себе предлоги опускаются.
          return -1

        # тэги
        if word in clTagGl.getTag() and word not in key_dict['tag'] and word not in key_dict['extag']: return f'tag*{word}'
      
        # Языковой ключ
        for id, string in db.langtype.items():
          if smorh.normal_form in string and smorh.normal_form not in key_dict['lang'] and word not in key_dict['exlang']: return f'lang*{id}'

        # Анализ других слов
        for id, string in db.keytype.items():
          if smorh.normal_form in string and smorh.normal_form not in key_dict['type'] and word not in key_dict['extype']: return f'type*{id}'
      except:
        return -1
      else:
        return 0 # Все проверки провалены.
    # ********** внутренняя процедура проверки по базе

    # проверка очередного слова в строке.
    userword = ustr[lenUstr]
    if INLEFT > 0: userword = f'{ustr[lenUstr-INLEFT]} {userword}'  # расширенное слово

    # проверка слова по совпадению с БД и выводы.
    wordcheck = checkinBD(userword) 
    if wordcheck == -1:
      lenUstr, INLEFT = lenUstr-INLEFT-1, 0
    elif wordcheck == 0:
      if INLEFT == 0: INLEFT = 1
      else: lenUstr, INLEFT = lenUstr-INLEFT, 0
    else:
      keyname = wordcheck.split('*')
      try:  # обработка out of range
        smorh = morh.parse(ustr[lenUstr-INLEFT-1])[0]
      except:
        smorh = ''
      finally:  # проверка исключения ("не flask")
        if smorh.normal_form in ['без', 'не', 'исключить']: key_dict[f'ex{keyname[0]}'].append(keyname[1])
        else: key_dict[keyname[0]].append(keyname[1])

      # убираемся на столе, снимаем флаги
      lenUstr, INLEFT = lenUstr-INLEFT-1, 0
  
  # Не разобрали ни одного слова. Пустой словарь, пустой.
  # Как более элегантно проверить, что key_dict.values() пустые?
  if not key_dict['tag'] and not key_dict['lang'] and not key_dict['type'] and not key_dict['extag'] and not key_dict['exlang'] and not key_dict['extype']:
    return ''
  
  # Выборка статей по типу и тэгам.
  res = returnLib(key_dict)
  
  # Подготовка к выводу
  res = printLib(res)

  return res

def returnLib(dicts):
  # Если есть категория - выборка, если нет - всё;
  # если есть тэги - выборка, если нет - все;
  # если есть язык - выборка, если нет - все языки.
  dic_result = {}

  for string in db.urlbase.values():
    # Построчная сверка БД с типом, тэгами и языком. 
    intag = False      # Флаг включения строки в выборку, false - нет
    incat = False
    lang = False

    # Проверка тэгов
    if not dicts['tag']: intag=True
    elif (set(string[URL_TAGS]) >= set(dicts['tag'])) == True: intag=True
    # исключение
    if dicts['extag'] and (set(string[URL_TAGS]) >= set(dicts['extag'])) == True: intag=False

    # Проверка категории
    if not dicts['type']: incat=True
    elif string[URL_TYPE] in dicts['type']: incat=True
    # исключение
    if string[URL_TYPE] in dicts['extype']: incat=False

    # Проверка языка (проверяем только если указано, иначе - берём всё). 
    if not dicts['lang']: lang=True
    elif string[URL_LANG] in dicts['lang']: lang = True
    # исключение
    if string[URL_LANG] in dicts['exlang']: lang = False
    
    if intag and incat and lang:    # Строка включается
      # Если категории в словаре нет, создадим. 
      if dic_result.get(string[URL_TYPE]) is None: dic_result.update({string[URL_TYPE]:[]})
      if string[URL_LANG] != 'ru':
        dic_result[string[URL_TYPE]].append(f'({string[URL_LANG]}) {string[URL_NAME]}')
      else:
        dic_result[string[URL_TYPE]].append(string[URL_NAME])
      dic_result[string[URL_TYPE]].append(string[URL_URL])

    intag, incat, lang = False, False, False

  return dic_result            

def printLib(dicts):
  txt_r = ''
  for key in db.keytypedisp.keys():
    if dicts.get(key) is not None:
      
        #txt_r += '<br>'
        txt_r += f'<span id="hehe">{db.keytypedisp[key]}</span><br><br>'        # Добавление заголовка (категория)
        txt_r += '<ul id="db">'
        for pri in range(0,len(dicts[key]),2):

            # Вся фраза является гиперссылкой
            txt_r += f'<li><a id="urldb" href="{dicts[key][pri+1]}">{dicts[key][pri]}</a></li>'        
            # В конце фразы (>) сделано гиперссылкой.
            #txt_r += f'<li id="urldb">{dicts[key][pri]} (<a id="urldb" href="{dicts[key][pri+1]}">></a>)</li>'

        txt_r += '</ul><br>'

        # Проверка валидности url (ОТКЛЮЧЕНО, ВРЕМЯЗАТРАТНО)
        #url = dicts[key][pri+1]   # проверка валидности ссылки
        #try:
        #  urllib.request.urlopen(url).getcode()
        #  txt_r += f'* {dicts[key][pri]} ({url})\n'
        #except:
        #  txt_r += f'* {dicts[key][pri]} - заморожено, сайт не отвечает\n'          

  return txt_r
