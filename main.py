# -*- coding: utf-8 -*-

# Задание значения переменной среды
# import os; os.environ['FOO'] = 'bar'


import os
import errno
import json
from PyQt5 import QtCore, QtGui, QtWidgets
import btxapi as BtxApi
import fsspapi as FsspApi


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.uiCreateLtAuth()
        self.uiCreateLtControls()
        self.uiCreateLtOutput()
        self.uiCreateMainWindow()

        self.loadAuthDataFromFile()

        self.btx_api_agent = BtxApi.ApiAgent()
        self.btx_api_agent.on_status.connect(self.apiAgentOnStatus, QtCore.Qt.QueuedConnection)
        self.btx_api_agent.on_error.connect(self.apiAgentOnError, QtCore.Qt.QueuedConnection)
        self.btx_api_agent.on_response.connect(self.apiAgentOnResponse, QtCore.Qt.QueuedConnection)

        self.fssp_api_agent = FsspApi.ApiAgent()
        self.fssp_api_agent.on_status.connect(self.apiAgentOnStatus, QtCore.Qt.QueuedConnection)
        self.fssp_api_agent.on_error.connect(self.apiAgentOnError, QtCore.Qt.QueuedConnection)
        self.fssp_api_agent.on_response.connect(self.apiAgentOnResponse, QtCore.Qt.QueuedConnection)

    def uiCreateLtAuth(self):
        # Верхний групбокс для авторизации в Битрикс
        # Первая (верхняя) строка: логин, пароль
        ui_lb_btx_login = QtWidgets.QLabel(text='Login: ')
        self.ui_le_btx_login = QtWidgets.QLineEdit()
        ui_lb_btx_password = QtWidgets.QLabel(text='Password: ')
        self.ui_le_btx_password = QtWidgets.QLineEdit()
        self.ui_le_btx_password.setEchoMode(QtWidgets.QLineEdit.Password)
        ui_lt_btx_auth_line1 = QtWidgets.QHBoxLayout()
        ui_lt_btx_auth_line1.addWidget(ui_lb_btx_login)
        ui_lt_btx_auth_line1.addWidget(self.ui_le_btx_login)
        ui_lt_btx_auth_line1.addWidget(ui_lb_btx_password)
        ui_lt_btx_auth_line1.addWidget(self.ui_le_btx_password)
        # Вторая строка: интернет имя приложения
        ui_lb_btx_internet_name = QtWidgets.QLabel(text='App Internet Name: ')
        self.ui_le_btx_internet_name = QtWidgets.QLineEdit()
        ui_lt_btx_auth_line2 = QtWidgets.QHBoxLayout()
        ui_lt_btx_auth_line2.addWidget(ui_lb_btx_internet_name)
        ui_lt_btx_auth_line2.addWidget(self.ui_le_btx_internet_name)
        # Четвертая строка: идентификатор клиента
        ui_lb_btx_client_id = QtWidgets.QLabel(text='Client Id: ')
        self.ui_le_btx_client_id = QtWidgets.QLineEdit()
        ui_lt_btx_auth_line3 = QtWidgets.QHBoxLayout()
        ui_lt_btx_auth_line3.addWidget(ui_lb_btx_client_id)
        ui_lt_btx_auth_line3.addWidget(self.ui_le_btx_client_id )
         # Третья строка: секретный код клиента
        ui_lb_btx_client_secret = QtWidgets.QLabel(text='Client Secret: ')
        self.ui_le_btx_client_secret = QtWidgets.QLineEdit()
        ui_lt_btx_auth_line4 = QtWidgets.QHBoxLayout()
        ui_lt_btx_auth_line4.addWidget(ui_lb_btx_client_secret)
        ui_lt_btx_auth_line4.addWidget(self.ui_le_btx_client_secret)
        ui_lt_btx_auth_line4.setStretchFactor(self.ui_le_btx_client_secret,19)
        ui_lt_btx_auth = QtWidgets.QVBoxLayout()
        ui_lt_btx_auth.addLayout(ui_lt_btx_auth_line1)
        ui_lt_btx_auth.addLayout(ui_lt_btx_auth_line2)
        ui_lt_btx_auth.addLayout(ui_lt_btx_auth_line3)
        ui_lt_btx_auth.addLayout(ui_lt_btx_auth_line4)
        ui_gb_btx_auth = QtWidgets.QGroupBox(title='Авторизация Битрикс24')
        ui_gb_btx_auth.setLayout(ui_lt_btx_auth)

        # Нижний групбокс для токена API УФССП
        ui_lb_fssp_token = QtWidgets.QLabel(text='Token: ')
        self.ui_le_fssp_token = QtWidgets.QLineEdit()
        ui_lt_fssp_token_line = QtWidgets.QHBoxLayout()
        ui_lt_fssp_token_line.addWidget(ui_lb_fssp_token)
        ui_lt_fssp_token_line.addWidget(self.ui_le_fssp_token)
        ui_lt_fssp_token = QtWidgets.QVBoxLayout()
        ui_lt_fssp_token.setAlignment(QtCore.Qt.AlignTop)
        ui_lt_fssp_token.addLayout(ui_lt_fssp_token_line)
        ui_gb_fssp_auth = QtWidgets.QGroupBox(title='Авторизация УФССП')
        ui_gb_fssp_auth.setLayout(ui_lt_fssp_token)

        # Размертка с левыи и правым групбоксами
        self.ui_lt_auth = QtWidgets.QVBoxLayout()
        self.ui_lt_auth.addWidget(ui_gb_btx_auth)
        self.ui_lt_auth.addWidget(ui_gb_fssp_auth)
        self.ui_lt_auth.setStretchFactor(ui_gb_btx_auth,2)
        self.ui_lt_auth.setStretchFactor(ui_gb_fssp_auth,1)

    def uiCreateLtControls(self):
        # Групбокс для элементов выбора режима ввода данных физ. лица
        self.ui_rb_fssp_api_call_setmode_params = QtWidgets.QRadioButton('Параметры')
        self.ui_rb_fssp_api_call_setmode_params.setChecked(True)
        self.ui_rb_fssp_api_call_setmode_id = QtWidgets.QRadioButton('Id контакта')
        ui_lt_fssp_api_call_line1 = QtWidgets.QHBoxLayout()
        ui_lt_fssp_api_call_line1.addWidget(self.ui_rb_fssp_api_call_setmode_params)
        ui_lt_fssp_api_call_line1.addWidget(self.ui_rb_fssp_api_call_setmode_id)
        ui_lt_fssp_api_call_line1.addStretch(1)
        self.ui_pb_fssp_api_call_run = QtWidgets.QPushButton('Run')
        self.ui_pb_fssp_api_call_run.clicked.connect(self.onRunBtnClicked, QtCore.Qt.QueuedConnection)
        ui_lt_fssp_api_call_line2 = QtWidgets.QHBoxLayout()
        ui_lt_fssp_api_call_line2.addWidget(self.ui_pb_fssp_api_call_run)
        ui_lt_fssp_api_call_line2.addStretch(1)
        ui_lt_fssp_call_setmode = QtWidgets.QVBoxLayout()
        ui_lt_fssp_call_setmode.setAlignment(QtCore.Qt.AlignTop)
        ui_lt_fssp_call_setmode.addLayout(ui_lt_fssp_api_call_line1)
        ui_lt_fssp_call_setmode.addLayout(ui_lt_fssp_api_call_line2)
        self.ui_gb_fssp_api_call_setmode = QtWidgets.QGroupBox(title='Выбор режима ввода данных физ. лица')
        self.ui_gb_fssp_api_call_setmode.setLayout(ui_lt_fssp_call_setmode)

        # Ввод параметров физ. лица
        self.ui_lb_individ_params_region = QtWidgets.QLabel('№ региона*:')
        self.ui_le_individ_params_region = QtWidgets.QLineEdit()
        #self.ui_le_individ_params_region.setValidator(QtGui.QIntValidator())
        self.ui_le_individ_params_region.returnPressed.connect(self.onFsspApiParamsLineEditReturnPressed, QtCore.Qt.QueuedConnection)
        self.ui_lb_individ_params_firstname = QtWidgets.QLabel('Имя*:')
        self.ui_le_individ_params_firstname = QtWidgets.QLineEdit()
        #self.ui_le_individ_params_firstname.setValidator(QtGui.QIntValidator())
        self.ui_le_individ_params_firstname.returnPressed.connect(self.onFsspApiParamsLineEditReturnPressed, QtCore.Qt.QueuedConnection)
        self.ui_lb_individ_params_lastname = QtWidgets.QLabel('Фамилия*:')
        self.ui_le_individ_params_lastname = QtWidgets.QLineEdit()
        self.ui_le_individ_params_lastname.returnPressed.connect(self.onFsspApiParamsLineEditReturnPressed, QtCore.Qt.QueuedConnection)
        self.ui_lb_individ_params_secondname = QtWidgets.QLabel('Отчество:')
        self.ui_le_individ_params_secondname = QtWidgets.QLineEdit()
        self.ui_le_individ_params_secondname.returnPressed.connect(self.onFsspApiParamsLineEditReturnPressed, QtCore.Qt.QueuedConnection)
        self.ui_lb_individ_params_birthdate = QtWidgets.QLabel('Д. р. (dd.mm.YYYY):')
        self.ui_le_individ_params_birthdate = QtWidgets.QLineEdit()
        self.ui_le_individ_params_birthdate.returnPressed.connect(self.onFsspApiParamsLineEditReturnPressed, QtCore.Qt.QueuedConnection)
        ui_lt_fssp_api_params = QtWidgets.QGridLayout()
        ui_lt_fssp_api_params.addWidget(self.ui_lb_individ_params_region,0,0)
        ui_lt_fssp_api_params.addWidget(self.ui_le_individ_params_region,0,1)
        ui_lt_fssp_api_params.addWidget(self.ui_lb_individ_params_firstname,1,0)
        ui_lt_fssp_api_params.addWidget(self.ui_le_individ_params_firstname,1,1)
        ui_lt_fssp_api_params.addWidget(self.ui_lb_individ_params_lastname,2,0)
        ui_lt_fssp_api_params.addWidget(self.ui_le_individ_params_lastname,2,1)
        ui_lt_fssp_api_params.addWidget(self.ui_lb_individ_params_secondname,3,0)
        ui_lt_fssp_api_params.addWidget(self.ui_le_individ_params_secondname,3,1)
        ui_lt_fssp_api_params.addWidget(self.ui_lb_individ_params_birthdate,4,0)
        ui_lt_fssp_api_params.addWidget(self.ui_le_individ_params_birthdate,4,1)
        self.ui_gb_fssp_api_params = QtWidgets.QGroupBox('Параметры')
        self.ui_gb_fssp_api_params.setLayout(ui_lt_fssp_api_params)

        # Ввод id контакта
        self.ui_lb_btx_contact_id = QtWidgets.QLabel('Id:')
        self.ui_le_btx_contact_id = QtWidgets.QLineEdit()
        #self.ui_le_btx_contact_id.setValidator(QtGui.QIntValidator())
        self.ui_le_btx_contact_id.returnPressed.connect(self.onBtxContactIdLineEditReturnPressed, QtCore.Qt.QueuedConnection)
        self.ui_lb_btx_contact_region = QtWidgets.QLabel('№ региона*:')
        self.ui_le_btx_contact_region = QtWidgets.QLineEdit()
        self.ui_le_btx_contact_region.returnPressed.connect(self.onBtxContactIdLineEditReturnPressed, QtCore.Qt.QueuedConnection)
        ui_lt_btx_contact_id_params = QtWidgets.QGridLayout()
        ui_lt_btx_contact_id_params.addWidget(self.ui_lb_btx_contact_id,0,0)
        ui_lt_btx_contact_id_params.addWidget(self.ui_le_btx_contact_id,0,1)
        ui_lt_btx_contact_id_params.addWidget(self.ui_lb_btx_contact_region,1,0)
        ui_lt_btx_contact_id_params.addWidget(self.ui_le_btx_contact_region,1,1)
        ui_lt_btx_contact_id = QtWidgets.QVBoxLayout()
        ui_lt_btx_contact_id.setAlignment(QtCore.Qt.AlignTop)
        ui_lt_btx_contact_id.addLayout(ui_lt_btx_contact_id_params)
        self.ui_gb_fssp_api_id = QtWidgets.QGroupBox('Id контакта')
        self.ui_gb_fssp_api_id.setLayout(ui_lt_btx_contact_id)
        self.ui_lt_fssp_api_call_parameters = QtWidgets.QHBoxLayout()
        self.ui_lt_fssp_api_call_parameters.addWidget(self.ui_gb_fssp_api_params)
        self.ui_lt_fssp_api_call_parameters.setStretchFactor(self.ui_gb_fssp_api_params,3)
        self.ui_lt_fssp_api_call_parameters.addWidget(self.ui_gb_fssp_api_id)
        self.ui_lt_fssp_api_call_parameters.setStretchFactor(self.ui_gb_fssp_api_id,2)

    def uiCreateLtOutput(self):
        # Текстовый редактор вывода
        self.ui_te_output = QtWidgets.QTextEdit()
        self.ui_te_output.setMinimumSize(300, 200)
        #self.ui_te_output.setReadOnly(True)
        # Доквиджет для текстового редактора вывода
        self.ui_dw_output = QtWidgets.QDockWidget()
        self.ui_dw_output.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.ui_dw_output.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        self.ui_dw_output.dockLocationChanged.connect(self.onDockWidgetOutputLocationChanged) #lambda : self.resize(self.minimumWidth(), self.height()))
        self.ui_dw_output.setWidget(self.ui_te_output)

    def uiCreateMainWindow(self):
        # Центральный виджет
        self.ui_lt_main = QtWidgets.QVBoxLayout()
        self.ui_lt_main.addLayout(self.ui_lt_auth)
        self.ui_lt_main.addWidget(self.ui_gb_fssp_api_call_setmode)
        self.ui_lt_main.addLayout(self.ui_lt_fssp_api_call_parameters)
        self.ui_lt_main.addStretch(1)
        ui_cw_main = QtWidgets.QWidget()
        ui_cw_main.setFixedWidth(500)
        ui_cw_main.setLayout(self.ui_lt_main)
        self.setCentralWidget(ui_cw_main)
        # Доквиджет с выводом
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.ui_dw_output)

    def onDockWidgetOutputLocationChanged(self):
        if self.ui_dw_output.isFloating():
            self.setMinimumWidth(self.centralWidget().width())
            self.resize(self.centralWidget().width(), self.height())
        else:
            self.setMinimumWidth(self.centralWidget().width() + self.ui_dw_output.width() + 6)
            self.resize(self.centralWidget().width() + self.ui_dw_output.width() + 6, self.height())

    def onFsspApiParamsLineEditReturnPressed(self):
        self.ui_rb_fssp_api_call_setmode_params.setChecked(True)
        self.run()

    def onBtxContactIdLineEditReturnPressed(self):
        self.ui_rb_fssp_api_call_setmode_id.setChecked(True)
        self.run()

    def onRunBtnClicked(self):
        self.run()

    def run(self):
        # Если поток не запущен
        if not self.fssp_api_agent.isRunning():
            
            # Проверка выбора режима ввода параметров поиска в базе УФССП
            if self.ui_rb_fssp_api_call_setmode_params.isChecked():
                # Если режим непосредственного ввода параметров физ. лица
                self.fssp_api_agent.task = FsspApi.SearchPhysical(
                    self.ui_le_fssp_token.text(),
                    self.ui_le_individ_params_region.text(),
                    self.ui_le_individ_params_firstname.text(),
                    self.ui_le_individ_params_lastname.text(),
                    self.ui_le_individ_params_secondname.text(),
                    self.ui_le_individ_params_birthdate.text()
                )
            elif self.ui_rb_fssp_api_call_setmode_id.isChecked():
                # Если режим ввода id контакта в списке Битрикс
                # Получаем данные контакта из Битрикс
                self.btx_api_agent.internet_name = self.ui_le_btx_internet_name.text()
                self.btx_api_agent.client_id = self.ui_le_btx_client_id.text()
                self.btx_api_agent.client_secret = self.ui_le_btx_client_secret.text()
                self.btx_api_agent.auth_login = self.ui_le_btx_login.text()
                self.btx_api_agent.auth_password = self.ui_le_btx_password.text()
                self.btx_api_agent.task = BtxApi.CrmContactGet(
                    self.ui_le_btx_contact_id.text()
                )
                self.btx_api_agent.start()
                self.btx_api_agent.wait()
                if not self.btx_api_agent.response:
                    return
                # Создаем объект поиска физ. лица для API УФССП
                self.fssp_api_agent.task = FsspApi.SearchPhysical(
                    self.ui_le_fssp_token.text(),
                    # self.btx_api_agent.response['UF_CRM_5D4D5B9CC501D'], #['ADDRESS_REGION'],
                    self.ui_le_btx_contact_region.text(),
                    self.btx_api_agent.response['NAME'],
                    self.btx_api_agent.response['LAST_NAME'],
                    self.btx_api_agent.response['SECOND_NAME'],
                    self.btx_api_agent.response['BIRTHDATE']
                )
            
            # Запуск запроса данных в API УФССП
            self.fssp_api_agent.start()
        else:
            self.ui_te_output.append('Ожидание завершения выполняющегося запроса')

    def saveAuthDataToFile(self):
        # Сохраняется все, кроме пароля
        # Создается директория
        try:
            os.makedirs(r'./lastsession')
        except OSError as e:
            if e.errno != errno.EEXIST:
                self.ui_te_output.append('Ошибка при сохранении параметров сессии: невозможно создать директорию')
                return
        authdata_btx =\
            {
                'login':self.ui_le_btx_login.text(),
                'internet_name':self.ui_le_btx_internet_name.text(),
                'client_id':self.ui_le_btx_client_id.text(),
                'client_secret':self.ui_le_btx_client_secret.text()
            }
        authdata_fssp =\
            {
                'app_token':self.ui_le_fssp_token.text()
            }
        # Сохранение данных в файл
        try:
            with open(r'./lastsession/bitrix24.json', 'w') as json_file:
                json.dump(authdata_btx, json_file)
        except Exception:
            self.ui_te_output.append('Ошибка при сохранении параметров Битрикс24: не удается создать bitrix24.json')
        else:
            self.ui_te_output.append('Параметры Битрикс24 сохранены в bitrix24.json')
        try:
            with open(r'./lastsession/fssp.json', 'w') as json_file:
                json.dump(authdata_fssp, json_file)
        except Exception:
            self.ui_te_output.append('Ошибка при сохранении параметров УФССП: не удается создать fssp.json')
        else:
            self.ui_te_output.append('Параметры УФССП сохранены в bitrix24.json')

    def loadAuthDataFromFile(self):
        try:
            with open(r'./lastsession/bitrix24.json', 'r') as json_file:
                data = json.load(json_file)
                self.ui_le_btx_login.setText(data['login'])
                self.ui_le_btx_internet_name.setText(data['internet_name'])
                self.ui_le_btx_client_id.setText(data['client_id'])
                self.ui_le_btx_client_secret.setText(data['client_secret'])
        except Exception:
            self.ui_te_output.append('Ошибка при загрузке параметров Битрикс24: не удается прочитать bitrix24.json')
        else:
            self.ui_te_output.append('Параметры Битрикс24 загружены из файла bitrix24.json')
        try:
            with open(r'./lastsession/fssp.json', 'r') as json_file:
                data = json.load(json_file)
                self.ui_le_fssp_token.setText(data['app_token'])
        except Exception:
            self.ui_te_output.append('Ошибка при загрузке параметров УФССП: не удается прочитать fssp.json')
        else:
            self.ui_te_output.append('Параметры УФССП загружены из файла fssp.json')

    def apiAgentOnStatus(self, text):
        self.ui_te_output.append(text)

    def apiAgentOnError(self, text):
        self.ui_te_output.append(text)

    def apiAgentOnResponse(self, text):
        self.ui_te_output.append(text)

    def closeEvent(self, event):
        self.saveAuthDataToFile()
        self.hide()
        #self.mythread.running = False
        self.mythread.wait() # .wait(9000)
        event.accept()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle('УФССП')
    window.resize(1440, 810)
    window.show()
    sys.exit(app.exec_())

