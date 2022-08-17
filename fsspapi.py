# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import requests
import json


class SearchPhysical:
    
    def __init__(self, token, region, firstname, lastname, secondname=None, birthdate=None):
        # Параметры физического лица
        self.__api_method_url = '/search/physical'
        self.token = token # Токен
        self.region = region # Код региона
        self.firstname = firstname # Имя
        self.lastname = lastname # Фамилия
        self.secondname = secondname # Отчество
        self.birthdate = birthdate # Дата рождения в формате dd.mm.YYYY
    
    @property
    def api_method_url(self):
        return self.__api_method_url


class SearchLegal:
    
    def __init__(self, token, region, name, address=None):
        # Параметры юридического лица
        self.__api_method_url = '/search/legal'
        self.token = token # Токен
        self.region = region # Код региона
        self.name = name # Название
        self.address = address # Адрес
    
    @property
    def api_method_url(self):
        return self.__api_method_url


class ApiAgent(QtCore.QThread):

    # Сигналы почему-то работают, только если объвлены все конструктора
    on_status = QtCore.pyqtSignal(str)
    on_error = QtCore.pyqtSignal(str)
    on_response = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

        # Базовая часть URL API
        self.__api_access_point_url = 'https://api-ip.fssp.gov.ru/api/v1.0'
        # Объект-метод API
        self.task = None
        # Последний ответ API в формате JSON, если ошибка, то None
        self.__response = None

    @property
    def response(self):
        return self.__response

    def run(self):
        
        # Это поле работает как флаг: если None, то run() завершился с ошибкой
        self.__response = None
        # Выполняется соответствующий метод API
        if isinstance(self.task, SearchPhysical):
            self.searchPhysical()
        elif isinstance(self.task, SearchLegal):
            self.searchLegal()

    def searchPhysical(self) -> int:

        # Вывод параметров поискового запроса API УФССП
        # str нужен,т.к. иногда поля в Битрикс имеют значение None
        self.on_status.emit('\n'+('='*80+'\n')*3)
        self.on_status.emit('Сформирован поиск физического лица с параметрами')
        self.on_status.emit('Номер региона: '+str(self.task.region))
        self.on_status.emit('Имя:           '+str(self.task.firstname))
        self.on_status.emit('Фамилия:       '+str(self.task.lastname))
        self.on_status.emit('Отчество:      '+str(self.task.secondname))
        self.on_status.emit('Дата рождения: '+str(self.task.birthdate)+'\n')

        if not self.task:
            self.on_error.emit('API УФССП: метод поискового запроса не задан')
            return

        # Вызов метода - отправка поискового запроса
        params =\
            {
                'token':self.task.token,
                'region':self.task.region,
                'firstname':self.task.firstname,
                'secondname':self.task.secondname,
                'lastname':self.task.lastname,
                'birthdate':self.task.birthdate
            }
        url = self.__api_access_point_url + self.task.api_method_url
        r = requests.get(url=url, params=params, timeout=3)
        if r.status_code != 200:
            self.on_error.emit('API УФССП: отправка поискового запроса завершилась с ошибкой HTTP status code '+str(r.status_code))
            return
        if r.json()['code'] == 401:
            self.on_error.emit('API УФССП: отправка поискового запроса завершилась с ошибкой invalid token')
            return

        # Проверка статуса выполнения поискового запроса
        search_task_id = r.json()['response']['task']
        attempts = 5 # Число попыток с интервалом 1 с
        params =\
            {
                'token':self.task.token,
                'task':search_task_id
            }
        while attempts:
            r = requests.get(url=self.__api_access_point_url+'/status', params=params, timeout=3)
            if r.json()['response']['status'] in (0,3):
                self.on_status.emit('API УФССП: обработка поискового запроса сервером завершена')
                break
            else:
                self.on_status.emit('API УФССП: поисковой запрос обрабатывается сервером...')
                self.sleep(2)
                attempts = attempts - 1

        # Получение результата выполнения поискового запроса
        r = requests.get(url=self.__api_access_point_url+'/result', params=params, timeout=3)
        if r.status_code != 200:
            self.on_error.emit('API УФССП: загрузка результатов поискового запроса завершилась с ошибкой HTTP status code '+str(r.status_code))
            return

        # Отправка ответа сервера обработчику сигнала
        self.on_status.emit('API УФССП: вывод результата поискового запроса')
        self.on_response.emit('\n'+json.dumps(r.json(),ensure_ascii=False,indent=4,sort_keys=True)+'\n')
        self.__response = r.json() # Вдруг понадобится

    def searchLegal(self) -> int:

        # Заглушка

        self.sleep(1)
