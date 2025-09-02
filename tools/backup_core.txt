import os
import traceback
from contextlib import suppress
from threading import Thread
from time import sleep

from pyautogui import moveTo
from pywinauto.timings import wait_until
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from win32gui import GetCursorInfo

from config import odines_username_rpa, odines_password_rpa, sed_username, sed_password, sprut_username, sprut_password
from config import process_list_path
from tools.app import App
from tools.clipboard import clipboard_set, clipboard_get
from tools.exceptions import ApplicationException, RobotException, BusinessException
from tools.process import kill_process_list
from tools.web import Web


class Sprut(App):
    def __init__(self, base, timeout=60, debug=False, logger=None):
        path_ = r'C:\SPRUT\Modules3.5\sprut.exe'
        super(Sprut, self).__init__(path_, timeout=timeout, debug=debug, logger=logger)
        self.base = base

    def run(self):
        self.quit()
        os.system(f'start "" "{self.path.__str__()}"')

        self.parent_switch({
            "title": "Регистрация", "class_name": "TvmsLogonForm", "control_type": "Window",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": None
        })
        self.find_element({
            "title": "", "class_name": "TcxCustomInnerTextEdit", "control_type": "Edit",
            "visible_only": True, "enabled_only": True, "found_index": 0
        }).set_text(sprut_username)
        self.find_element({
            "title": "", "class_name": "TcxCustomInnerTextEdit", "control_type": "Edit",
            "visible_only": True, "enabled_only": True, "found_index": 1
        }).type_keys(sprut_password, self.keys.TAB, protect_first=True, click=True)
        element_ = self.find_element({
            "class_name": "TvmsComboBox", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0
        })
        element_.click()
        element_.type_keys(self.base, clear=False, set_focus=False)
        sleep(0.3)
        element_.type_keys('~', clear=False)
        sleep(0.3)
        element_.type_keys('~', clear=False)

        self.parent_switch({
            "title": "\"Главное меню ПС СПРУТ\"", "class_name": "Tsprut_fm_Main", "control_type": "Window",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": None
        }, timeout=180)

    def open(self, value):
        self.search({
            "title": "", "class_name": "TvmsDBTreeList", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0
        }, value)
        self.find_element({
            "title": "", "class_name": "TvmsDBTreeList", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0
        }).type_keys('~', clear=False)
        self.parent_switch({
            "title_re": f"^.*{value}.*$", "class_name": "Treport_frm_main", "control_type": "Window",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": None
        })

    def search(self, selector, value, replace=False):
        if replace:
            value = value.replace(' ', '{%}').replace('.', '{%}').replace('«', '{%}')
            value = value.replace('»', '{%}').replace('"', '{%}').replace('\'', '{%}').replace('С', 'C')
        element = self.find_element(selector)
        element.type_keys('^F', clear=False, set_focus=True)
        self.parent_switch({
            "title": "Поиск", "class_name": "Tvms_search_fm_builder", "control_type": "Window",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": None
        })
        with suppress(Exception):
            self.find_element({
                "title": "", "class_name": "", "control_type": "Button",
                "visible_only": True, "enabled_only": True, "found_index": 1
            }, timeout=0.1).click()
        element = self.find_element({
            "title": "", "class_name": "TcxCustomInnerTextEdit", "control_type": "Edit",
            "visible_only": True, "enabled_only": True, "found_index": 0
        })
        element.type_keys(self.keys.BACKSPACE * 2, clear=False)
        element.type_keys(self.keys.DELETE * 2, clear=False)
        element.type_keys(value, protect_first=True)
        element.type_keys('~', clear=False)
        element = self.find_element({
            "title": "", "class_name": "TvmsDBToolGrid", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0
        })
        element.click()

        clipboard_set('')
        element.type_keys(f'^{element.keys.INSERT}')
        value = clipboard_get(raise_err=False, empty=True)
        if not value:
            return None
        self.find_element({
            "title": "Перейти", "class_name": "TvmsBitBtn", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0}).click()
        self.wait_element({
            "title": "Перейти", "class_name": "TvmsBitBtn", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0
        }, until=False)

        self.parent_back(1)
        return value


class Odines(App):
    def __init__(self, timeout=60, debug=False, logger=None):
        path_ = r'C:\Program Files\1cv8\common\1cestart.exe'
        super(Odines, self).__init__(path_, timeout=timeout, debug=debug, logger=logger)
        self.keys.CLEAR = self.keys.CLEAN
        self.fuckn_tooltip_selector = {
            "class_name": "V8ConfirmationWindow", "control_type": "ToolTip",
            "visible_only": True, "enabled_only": True, "found_index": 0,
            "parent": self.root
        }
        self.root_selector = {
            "title_re": "1С:Предприятие - Алматы центр / ТОО \"Magnum Cash&Carry\" / Алматы  управление / .*",
            "class_name": "V8TopLevelFrame", "control_type": "Window",
            "visible_only": True, "enabled_only": True, "found_index": 0,
            "parent": None
        }
        self.close_1c_config_flag = False
        Thread(target=self.close_1c_config, daemon=True).start()

    # * OVERWRITE ------------------------------------------------------------------------------------------------------
    # ? tested
    def run(self) -> None:
        self.quit()
        os.system(f'start "" "{self.path.__str__()}"')

        # * launcher ---------------------------------------------------------------------------------------------------
        self.root = self.find_element({
            "title": "Запуск 1С:Предприятия", "class_name": "V8NewLocalFrameBaseWnd", "control_type": "Window",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": None
        })
        self.find_element({
            "title": "go_copy", "class_name": "", "control_type": "ListItem",
            "visible_only": True, "enabled_only": True, "found_index": 0
        }).click(double=True)
        sleep(3)

        # * authentificator --------------------------------------------------------------------------------------------
        self.root = self.find_element({
            "title": "Доступ к информационной базе", "class_name": "V8NewLocalFrameBaseWnd", "control_type": "Window",
            "found_index": 0, "parent": None
        }, timeout=30)
        self.find_element({
            "title": "", "class_name": "", "control_type": "ComboBox", "visible_only": True, "enabled_only": True,
            "found_index": 0
        }).type_keys(odines_username_rpa, self.keys.TAB, click=True, clear=True, protect_first=True)
        self.find_element({
            "title": "", "class_name": "", "control_type": "Edit", "visible_only": True, "enabled_only": True,
            "found_index": 0
        }).set_text(odines_password_rpa)
        self.find_element({
            "title": "OK", "class_name": "", "control_type": "Button", "visible_only": True, "enabled_only": True,
            "found_index": 0
        }).click()

        # * set root window --------------------------------------------------------------------------------------------
        self.root = self.find_element(self.root_selector, timeout=180)

        # * close startup banners --------------------------------------------------------------------------------------
        self.close_all_inner(nav_close_all=True)

        # * close 1c config popup thread flag --------------------------------------------------------------------------
        self.close_1c_config_flag = True

    # ? tested
    def quit(self):
        # * close 1c config popup thread flag --------------------------------------------------------------------------
        self.close_1c_config_flag = False

        if self.root:
            # * закрыть окна
            # with suppress(Exception):
            self.close_all_inner(nav_close_all=True)

            # * выход
            # with suppress(Exception):
            self.navigate('Файл', 'Выход')
            if self.wait_element({
                "title": "Завершить работу с программой?", "class_name": "", "control_type": "Pane",
                "visible_only": True, "enabled_only": True, "found_index": 0, "parent": self.root
            }, timeout=5):
                self.find_element({
                    "title": "Да", "class_name": "", "control_type": "Button", "visible_only": True,
                    "enabled_only": True, "found_index": 0, "parent": self.root
                }, timeout=1).click()
                self.wait_element({
                    "title": "Да", "class_name": "", "control_type": "Button", "visible_only": True,
                    "enabled_only": True, "found_index": 0, "parent": self.root
                }, timeout=5, until=False)

        kill_process_list(process_list_path)
        sleep(3)

    # * ----------------------------------------------------------------------------------------------------------------
    # TODO TEST
    def wait_fuckn_tooltip(self):
        # with suppress(Exception):
        if self.root:
            window = self.root
            position = window.element.element_info.rectangle.mid_point()
            moveTo(position[0], position[1])
            self.wait_element(self.fuckn_tooltip_selector, until=False)
            sleep(0.5)

    # TODO TEST
    def close_1c_config(self):
        while True:
            if self.close_1c_config_flag:
                # with suppress(Exception):
                if self.wait_element({
                    "title_re": "В конфигурацию ИБ внесены изменения.*", "class_name": "", "control_type": "Pane",
                    "visible_only": True, "enabled_only": True, "found_index": 0, "parent": self.root
                }, timeout=0):
                    self.find_element({
                        "title": "Нет", "class_name": "", "control_type": "Button",
                        "visible_only": True, "enabled_only": True, "found_index": 0, "parent": self.root
                    }, timeout=0).click()
            sleep(0.5)

    # * ----------------------------------------------------------------------------------------------------------------
    # ? tested
    def navigate(self, *steps, maximize_innder=False):
        sleep(1)
        # self.wait_fuckn_tooltip()
        for n, step in enumerate(steps):
            if n:
                if not self.wait_element({
                    "title": step, "class_name": "", "control_type": "MenuItem",
                    "visible_only": True, "enabled_only": True, "found_index": 0, "parent": self.root
                }, timeout=2):
                    if n - 1:
                        self.find_element({
                            "title": steps[n - 1], "class_name": "", "control_type": "MenuItem",
                            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": self.root
                        }, timeout=5).click()
                    else:
                        self.find_element({
                            "title": steps[n - 1], "class_name": "", "control_type": "Button",
                            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": self.root
                        }, timeout=5).click()
                self.find_element({
                    "title": step, "class_name": "", "control_type": "MenuItem",
                    "visible_only": True, "enabled_only": True, "found_index": 0, "parent": self.root
                }, timeout=5).click()
            else:
                self.find_element({
                    "title": step, "class_name": "", "control_type": "Button",
                    "visible_only": True, "enabled_only": True, "found_index": 0, "parent": self.root
                }, timeout=5).click()
        if maximize_innder:
            self.maximize_inner()

    # ? tested
    def close_all_inner(self, iter_count=10, manual_close_until=1, nav_close_all=False):
        # * закрыть все внутренние окна через меню
        if nav_close_all:
            close_buttons = self.find_elements({
                "title": "Закрыть", "class_name": "", "control_type": "Button",
                "visible_only": True, "enabled_only": True, "parent": self.root
            }, timeout=1)
            if len(close_buttons) > 1:
                # with suppress(Exception):
                self.close_1c_error()
                # with suppress(Exception):
                self.navigate('Окна', 'Закрыть все')
                # with suppress(Exception):
                self.close_1c_error()

        while True:
            iter_count -= 1
            close_buttons = self.find_elements({
                "title": "Закрыть", "class_name": "", "control_type": "Button",
                "visible_only": True, "enabled_only": True, "parent": self.root
            }, timeout=1)
            if len(close_buttons) > manual_close_until:
                # with suppress(Exception):
                self.close_1c_error()
                # with suppress(Exception):
                self.find_element({
                    "title": "Закрыть", "class_name": "", "control_type": "Button", "visible_only": True,
                    "enabled_only": True, "found_index": len(close_buttons) - 1, "parent": self.root
                }, timeout=1).click()
                # with suppress(Exception):
                self.close_1c_error()
            else:
                break
            if iter_count < 0:
                raise Exception('Не все окна закрыты')

    # TODO TEST
    def maximize_inner(self, timeout=0.5):
        self.root.type_keys('%+r', set_focus=True)
        if self.wait_element({
            "title": "Развернуть", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "parent": self.root
        }, timeout=timeout):
            self.find_elements({
                "title": "Развернуть", "class_name": "", "control_type": "Button",
                "visible_only": True, "enabled_only": True, "parent": self.root
            })[-1].click()

    # * ----------------------------------------------------------------------------------------------------------------
    # TODO TEST
    def check_1c_error(self, function_name, data=None, count=1):
        root_window = self.root
        while count > 0:
            count -= 1
            # * Конфигурация базы данных не соответствует сохраненной конфигурации -------------------------------------
            if self.wait_element({
                "title": "Конфигурация базы данных не соответствует сохраненной конфигурации.\nПродолжить?",
                "class_name": "", "control_type": "Pane",
                "visible_only": True, "enabled_only": True, "found_index": 0, "parent": None
            }, timeout=0.2):
                error_message = "Конфигурация базы данных не соответствует сохраненной конфигурации"
                raise ApplicationException(error_message, function_name, data)

            # * Строка не найдена --------------------------------------------------------------------------------------
            if self.wait_element({
                "title": "Строка не найдена!", "class_name": "", "control_type": "Pane",
                "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
            }, timeout=0.2):
                error_message = "Строка не найдена"
                raise ApplicationException(error_message, function_name, data)

            # * critical Разрыв соединения -----------------------------------------------------------------------------
            if self.wait_element({
                "title_re": "^.*Удаленный хост принудительно разорвал существующее подключение.*",
                "class_name": "", "control_type": "Pane",
                "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
            }, timeout=0.2):
                error_message = "critical Ошибка разрыв соединения"
                raise ApplicationException(error_message, function_name, data)

            # * critical Ошибка исполнения отчета ----------------------------------------------------------------------
            if self.wait_element({
                "title": "Ошибка исполнения отчета", "class_name": "", "control_type": "Pane",
                "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
            }, timeout=0.2):
                error_message = "critical Ошибка исполнения отчета"
                raise ApplicationException(error_message, function_name, data)

            # * Ошибка при вызове метода контекста ---------------------------------------------------------------------
            if self.wait_element({
                "title": "Ошибка при вызове метода контекста (Выполнить)",
                "class_name": "", "control_type": "Pane",
                "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
            }, timeout=0.2):
                error_message = "Ошибка при вызове метода контекста"
                raise ApplicationException(error_message, function_name, data)

            # * Конфликт блокировок при выполнении транзакции ----------------------------------------------------------
            if self.wait_element({
                "title_re": "Конфликт блокировок при выполнении транзакции:.*",
                "class_name": "", "control_type": "Pane",
                "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
            }, timeout=0.2):
                error_message = "Конфликт блокировок при выполнении транзакции"
                raise ApplicationException(error_message, function_name, data)

            # * Операция не выполнена ----------------------------------------------------------------------------------
            if self.wait_element({
                "title": "Операция не выполнена", "class_name": "", "control_type": "Pane",
                "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
            }, timeout=0.2):
                error_message = "Операция не выполнена"
                raise RobotException(error_message, function_name, data)

            # * Введенные данные не отображены в списке, так как не соответствуют отбору -------------------------------
            if self.wait_element({
                "title": "Введенные данные не отображены в списке, так как не соответствуют отбору.",
                "class_name": "", "control_type": "Pane",
                "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
            }, timeout=0.2):
                error_message = "Введенные данные не отображены в списке, так как не соответствуют отбору"
                raise RobotException(error_message, function_name, data)

            # * critical В поле введены некорректные данные ------------------------------------------------------------
            if self.wait_element({
                "title_re": "В поле введены некорректные данные.*", "class_name": "", "control_type": "Pane",
                "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
            }, timeout=0.2):
                error_message = "critical В поле введены некорректные данные"
                raise RobotException(error_message, function_name, data)

            # * critical Не удалось провести ---------------------------------------------------------------------------
            if self.wait_element({
                "title_re": "Не удалось провести.*", "class_name": "", "control_type": "Pane",
                "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
            }, timeout=0.2):
                error_message = "critical Не удалось провести"
                raise BusinessException(error_message, function_name, data)

            # * critical Сеанс работы завершен администратором ---------------------------------------------------------
            if self.wait_element({
                "title": "Сеанс работы завершен администратором.", "class_name": "", "control_type": "Pane",
                "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
            }, timeout=0.2):
                error_message = "critical Сеанс работы завершен администратором"
                raise ApplicationException(error_message, function_name, data)

            # * Сеанс отсутствует или удален ---------------------------------------------------------------------------
            if self.wait_element({
                "title_re": "Сеанс отсутствует или удален.*", "class_name": "", "control_type": "Pane",
                "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
            }, timeout=0.2):
                error_message = "critical Сеанс отсутствует или удален"
                raise ApplicationException(error_message, function_name, data)

            # * critical Неизвестное окно ошибки -----------------------------------------------------------------------
            if self.wait_element({
                "title": "1С:Предприятие", "class_name": "V8NewLocalFrameBaseWnd", "control_type": "Window",
                "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
            }, timeout=0.2):
                error_message = "critical Неизвестное окно ошибки"
                raise RobotException(error_message, function_name, data)

    # TODO TEST
    def close_1c_error(self):
        root_window = self.root
        # * Конфигурация базы данных не соответствует сохраненной конфигурации -----------------------------------------
        message_ = {
            "title": "Конфигурация базы данных не соответствует сохраненной конфигурации.\nПродолжить?",
            "class_name": "", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": None
        }
        button_ = {
            "title": "Да", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": None
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * Строка не найдена ------------------------------------------------------------------------------------------
        message_ = {
            "title": "Строка не найдена!", "class_name": "", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        button_ = {
            "title": "OK", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * Ошибка исполнения отчета -----------------------------------------------------------------------------------
        message_ = {
            "title_re": "^.*Удаленный хост принудительно разорвал существующее подключение.*",
            "class_name": "", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        button_ = {
            "title": "OK", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * Ошибка исполнения отчета -----------------------------------------------------------------------------------
        message_ = {
            "title": "Ошибка исполнения отчета", "class_name": "", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        button_ = {
            "title": "OK", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * Ошибка при вызове метода контекста -------------------------------------------------------------------------
        message_ = {
            "title": "Ошибка при вызове метода контекста (Выполнить)", "class_name": "",
            "control_type": "Pane", "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        button_ = {
            "title": "OK", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * Завершить работу с программой? -----------------------------------------------------------------------------
        message_ = {
            "title": "Завершить работу с программой?", "class_name": "", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        button_ = {
            "title": "Да", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * Операция не выполнена --------------------------------------------------------------------------------------
        message_ = {
            "title": "Операция не выполнена", "class_name": "", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        button_ = {
            "title": "OK", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * Конфликт блокировок при выполнении транзакции --------------------------------------------------------------
        message_ = {
            "title_re": "Конфликт блокировок при выполнении транзакции:.*", "class_name": "", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        button_ = {
            "title": "OK", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * Введенные данные не отображены в списке, так как не соответствуют отбору -----------------------------------
        message_ = {
            "title": "Введенные данные не отображены в списке, так как не соответствуют отбору.",
            "class_name": "", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        button_ = {
            "title": "OK", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * Данные были изменены. Сохранить изменения? -----------------------------------------------------------------
        message_ = {
            "title": "Данные были изменены. Сохранить изменения?", "class_name": "", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        button_ = {
            "title": "Нет", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * critical В поле введены некорректные данные ----------------------------------------------------------------
        message_ = {
            "title_re": "В поле введены некорректные данные.*", "class_name": "", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        button_ = {
            "title": "Да", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * critical Не удалось провести -------------------------------------------------------------------------------
        message_ = {
            "title_re": "Не удалось провести \".*", "class_name": "", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        button_ = {
            "title": "OK", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * Сеанс работы завершен администратором ----------------------------------------------------------------------
        message_ = {
            "title": "Сеанс работы завершен администратором.", "class_name": "", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        button_ = {
            "title": "Завершить работу", "class_name": "", "control_type": "Button", "visible_only": True,
            "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * Сеанс отсутствует или удален -------------------------------------------------------------------------------
        message_ = {
            "title_re": "Сеанс отсутствует или удален.*", "class_name": "", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        button_ = {
            "title": "Завершить работу", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * Выбранное действие не было выполнено -----------------------------------------------------------------------
        message_ = {
            "title": "Выбранное действие не было выполнено! Продолжить?", "class_name": "", "control_type": "Pane",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        button_ = {
            "title": "Да", "class_name": "", "control_type": "Button",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        # * Неизвестное окно ошибки ------------------------------------------------------------------------------------
        selector_ = {
            "title": "1С:Предприятие", "class_name": "V8NewLocalFrameBaseWnd", "control_type": "Window",
            "visible_only": True, "enabled_only": True, "found_index": 0, "parent": root_window
        }
        if self.wait_element(selector_, timeout=0.1):
            self.find_element(selector_).close()

    def approve(self, doc_name: str, function_name: str, try_count: int = 30, delay: float = 0) -> str:
        while True:
            # * нажать Провести
            self.find_element({
                "title": "Провести", "class_name": "", "control_type": "Button",
                "visible_only": True, "enabled_only": True, "found_index": 0
            }, timeout=1).click()

            # * дождаться проведения
            done = self.wait_element({
                "title": "Отмена проведения", "class_name": "", "control_type": "Button",
                "visible_only": True, "enabled_only": True, "found_index": 0
            }, timeout=10)

            # ! выход
            try_count -= 1
            if try_count < 0:
                raise Exception(f'Документ {str(doc_name)} не проведен либо нет номера')

            # ! проверка и закрытие ошибок
            if not done:
                try:
                    self.check_1c_error(function_name)
                except Exception as err:
                    traceback.print_exc()
                    if 'critical' in str(err):
                        raise err
                    self.close_1c_error()
            else:
                doc_num = str(self.find_element({
                    "title": "", "class_name": "", "control_type": "Edit",
                    "visible_only": True, "enabled_only": True, "found_index": 0
                }, timeout=0.1).element.iface_value.CurrentValue.replace(' ', ''))
                if not len(doc_num):
                    continue
                break
            sleep(delay)
        self.check_1c_error(function_name)
        return doc_num

    def deprove(self, doc_name: str, function_name: str, try_count: int = 30, delay: float = 0) -> str:
        while True:
            # * нажать Отмена проведения
            self.find_element({
                "title": "Отмена проведения", "class_name": "", "control_type": "Button",
                "visible_only": True, "enabled_only": True, "found_index": 0
            }, timeout=1).click()

            # * дождаться отмены проведения
            done = self.wait_element({
                "title": "Отмена проведения", "class_name": "", "control_type": "Button",
                "visible_only": True, "enabled_only": False, "found_index": 0
            }, timeout=10)

            # ! выход
            try_count -= 1
            if try_count < 0:
                raise Exception(f'Документ {str(doc_name)}. Не отменяется проведение')

            # ! проверка и закрытие ошибок
            if not done:
                try:
                    self.check_1c_error(function_name)
                except Exception as err:
                    traceback.print_exc()
                    if 'critical' in str(err):
                        raise err
                    self.close_1c_error()
            else:
                doc_num = str(self.find_element({
                    "title": "", "class_name": "", "control_type": "Edit",
                    "visible_only": True, "enabled_only": True, "found_index": 0
                }, timeout=0.1).element.iface_value.CurrentValue.replace(' ', ''))
                if not len(doc_num):
                    continue
                break
            sleep(delay)
        self.check_1c_error(function_name)
        return doc_num


class Cursor:
    W_LIST = [0, 65539, 65541, 65549, 65551, 65553, 65555, 65557, 65567,
              21235549, 70125255, 81790569, 86903163, 92144431, 162268339, 221514109, 225446471, 313067975]

    def __init__(self, timeout=600.0, duration=3.0, until=True, white_list=None):
        self.timeout = timeout
        self.duration = duration
        self.until = until
        self.white_list = white_list or list(self.W_LIST)

        self.start = True
        self.result = list()

    def wait_delay(self):
        self.start = True
        Thread(target=self.get, daemon=True).start()
        sleep(self.duration)
        self.start = False
        result = all(self.result)
        self.result = list()
        return result

    def get(self):
        while self.start:
            cursor = GetCursorInfo()[1]
            if cursor not in self.white_list:
                self.result.append(False)
            else:
                self.result.append(True)

    def wait(self, raise_err):
        if raise_err:
            return wait_until(self.timeout, 0, self.wait_delay, self.until)
        else:
            try:
                return wait_until(self.timeout, 0, self.wait_delay, self.until)
            except (Exception,):
                return False


class Sed(Web):

    def run(self):
        self.quit()
        self.driver = webdriver.Chrome(service=Service(self.path.__str__()), options=self.options)
        self.get('http://172.16.10.86/user/login')
        self.find_element('//input[@id="login"]').type_keys(sed_username)
        self.find_element('//input[@id="password"]').type_keys(sed_password)
        self.find_element('//input[@id="submit"]').click(page_load=True)
        self.load()
        self.wait_element('//span[@class="user_shortinfo_infoname"]')

    def load(self, timeout=None):
        selector_ = '//div[@id="thinking" and contains(@style, "block")]'
        self.wait_element(selector_, timeout=2)
        selector_ = '//div[@id="thinking" and contains(@style, "none")]'
        self.wait_element(selector_, timeout=timeout if timeout is not None else self.timeout)


if __name__ == '__main__':
    app = Sprut('REPS', 5, True)
    app.run()
    # * ---------------------------------------------------------------------------------------------------------------*
    app.open('Отчеты')
    app.quit()
