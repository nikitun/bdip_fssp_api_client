# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import requests
from urllib.parse import urlparse, parse_qs


class CrmContactGet():
    
    def __init__(self, id=None):
        self.__api_method_url = 'crm.contact.get'
        self.id = id
    
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

        # Логин и пароль
        self.auth_login = None
        self.auth_password = None
        # Параметыр приложения
        self.internet_name = None
        self.client_id = None
        self.client_secret = None
        # Токены доступа
        self.access_token = None
        self.refresh_token = None
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
        # Если первый запуск и токены еще не получены
        if not self.access_token or not self.access_token:
            if not self.getAccessAndRefreshTokens():
                return
        # Выполняется соответствующий метод API
        if isinstance(self.task, CrmContactGet):
            self.crmContactGet()

    def crmContactGet(self):

        # Цикл нужен для обновления токена
        payload = {'ID':self.task.id}
        url = 'https://'+self.internet_name+'/rest/'+self.task.api_method_url+'/?auth='+self.access_token
        while True:
            # Вызов метода API
            r = requests.post(url=url, json=payload)
            # Код "401" - токен доступа устарел и требует обновления
            if r.status_code == 401:
                self.sleep(0.5)
                self.refreshAccessToken()
                continue
            break
                
        # Если "неудачный" запрос, то проверка причины
        # Ошибки можно определять по коду или по наличию поля "error"
        # 400 - {"error":"","error_description":"Not found"}
        # 503 - {"error":"QUERY_LIMIT_EXCEEDED","error_description":"Too many requests"}
        if r.status_code != 200:
            if 'error' in r.json():
                self.on_error.emit('API Bitrix 24. Загрузка данных контакта завершилась с ошибкой. error_description: '+r.json()['error_description'])
            else:
                self.on_error.emit('API Bitrix 24. Загрузка данных контакта завершилась с неизвестной ошибкой')
            return

        self.on_response.emit('API Bitrix 24. Данные о контакте ID '+self.task.id+' успешно получены')
        self.__response = r.json()['result']

    # Получение токенов через логин и пароль
    def getAccessAndRefreshTokens(self):

        # Проверка заданности необходимых членов класса
        if not self.internet_name or\
                not self.client_id or\
                not self.auth_login or\
                not self.auth_password:
            self.on_error.emit('API Bitrix 24. Получение токена доступа завершилось с ошибкой. Не задан(ы) client_id или(и) логин, или(и) пароль')
            return False

        # Получение кода авторизации (autorization code grant)
        # Проверка по status_code здесь не подходит, т.к даже
        # при успешном редиректе возвращается 404
        # scope (разрешения) выставляются в настройках приложения,
        # передача их через адресную строку почему-то не работает
        url = 'https://'+self.internet_name+'/oauth/authorize'
        params =\
            {
                'client_id':self.client_id,
                'response_type':'code',
                'redirect_uri':'app_URL'
            }
        auth = requests.auth.HTTPBasicAuth(self.auth_login, self.auth_password)
        try:
            r = requests.get(url=url, params=params, auth=auth, timeout=3)
        except (requests.ConnectionError, requests.Timeout):
            self.on_error.emit('API Bitrix 24. Получение токена доступа завершилось с ошибкой. Истекло ожидание сервера')
            return False
        redirect_url_parsed = urlparse(r.url)
        redirect_query = parse_qs(redirect_url_parsed.query)
        if 'code' not in redirect_query:
            self.on_error.emit('API Bitrix 24. Получение токена доступа завершилось с ошибкой. Неправильный(ые) логин или(и) пароль, или(и) client_id')
            return False
        code = redirect_query['code'][0]

        # Получение пары токенов access_token и refresh_token
        url = 'https://oauth.bitrix.info/oauth/token'
        params =\
            {
                'grant_type':'authorization_code',
                'client_id':self.client_id,
                'client_secret':self.client_secret,
                'code':code
            }
        try:
            r = requests.get(url=url, params=params, timeout=3)
        except (requests.ConnectionError, requests.Timeout):
            self.on_error.emit('API Bitrix 24. Получение токена доступа завершилось с ошибкой. Истекло ожидание сервера')
            return False

        if r.status_code != 200:
            self.on_error.emit('API Bitrix 24. Получение токена доступа завершилось с ошибкой. Неправильный(ые) client_id или(и) client_secret')
            return False
        self.access_token, self.refresh_token =\
            r.json()['access_token'], r.json()['refresh_token']
        return True

    # Получение пары access_token и нового refresh_token из refresh_token
    def refreshAccessToken(self):

        # Проверка заданности необходимых членов класса
        if not self.client_id or\
                not self.client_secret or\
                not self.refresh_token:
            self.on_error.emit('API Bitrix 24. Обновление токена доступа завершилось с ошибкой. Не задан(ы) client_id или(и) client_secret, или(и) refresh_token')
            return False

        url = 'https://oauth.bitrix.info/oauth/token'
        params =\
            {
                'grant_type':'refresh_token',
                'client_id':self.client_id,
                'client_secret':self.client_secret,
                'refresh_token':self.refresh_token
            }
        try:
            r = requests.get(url=url, params=params, timeout=3)
        except (requests.ConnectionError, requests.Timeout):
            self.on_error.emit('API Bitrix 24. Обновление токена доступа завершилось с ошибкой. Истекло ожидание сервера')
            return False

        if r.status_code != 200:
            self.on_error.emit('API Bitrix 24. Обновление токена доступа завершилось с ошибкой. Неправильный(ые) client_id или(и) client_secret, или(и) refresh_token')
            return False
        self.access_token, self.refresh_token =\
            r.json()['access_token'], r.json()['refresh_token']
        return True
