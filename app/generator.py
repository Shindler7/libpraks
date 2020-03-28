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
  pa = compilereq()  # запросили класс тэгов. 
  
  ustr = txt.lower()
  ustr = re.split(r'\W+', ustr)
  
  key_dict = {'tag':[], 'lang': [], 'type': []} # lang, type, tag
  
  for key in ustr:
    ma = morh.parse(key)[0]

    if ma.tag.POS == 'PREP': continue  # предлоги не обрабатываем
    
    if key in pa.getTag() and key not in key_dict['tag']:          # тэги отдельно
      key_dict['tag'].append(key)
      continue
    
    # Языковой ключ
    for id, string in db.langtype.items():
      if ma.normal_form in string and ma.normal_form not in key_dict['lang']: key_dict['lang'].append(id)

    # Анализ других слов
    for id, string in db.keytype.items():
      if ma.normal_form in string and ma.normal_form not in key_dict['type']: key_dict['type'].append(id)
  
  # Не разобрали ни одного слова. Пустой словарь, пустой.
  if not key_dict['tag'] and not key_dict['lang'] and not key_dict['type']:
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
    if not dicts['tag']:
      intag=True
    elif (set(string[URL_TAGS]) >= set(dicts['tag'])) == True:
      intag=True
    
    # Проверка категории
    if not dicts['type']:
      incat=True
    elif string[URL_TYPE] in dicts['type']: 
      incat=True

    # Проверка языка (проверяем только если указано, иначе - берём всё). 
    if not dicts['lang']:
      lang=True
    elif string[URL_LANG] in dicts['lang']: 
      lang = True
    
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

            txt_r += f'<li><a id="urldb" href="{dicts[key][pri+1]}">{dicts[key][pri]}</a></li>'        

        txt_r += '</ul><br>'

        # Проверка валидности url (ОТКЛЮЧЕНО, ВРЕМЯЗАТРАТНО)
        #url = dicts[key][pri+1]   # проверка валидности ссылки
        #try:
        #  urllib.request.urlopen(url).getcode()
        #  txt_r += f'* {dicts[key][pri]} ({url})\n'
        #except:
        #  txt_r += f'* {dicts[key][pri]} - заморожено, сайт не отвечает\n'          

  return txt_r
