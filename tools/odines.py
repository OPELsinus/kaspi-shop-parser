from contextlib import suppress
from pathlib import Path
from threading import Thread
from time import sleep

from pyautogui import moveTo

from config import global_env_data
from tools.app import App, process_list_path
from tools.process import kill_process_list


class Odines(App):
    def __init__(self, timeout=60):
        super(Odines, self).__init__(
            Path(r"C:\Program Files\1cv8\common\1cestart.exe"), timeout=timeout
        )
        self.fuckn_tooltip = {
            "class_name": "V8ConfirmationWindow",
            "control_type": "ToolTip",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        self.root_selector = {
            "title_re": '1С:Предприятие - .*',
            "class_name": "V8TopLevelFrame",
            "control_type": "Window",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        self.root_window = None
        if self.wait_element(self.root_selector, timeout=1):
            self.root_window = self.find_element(self.root_selector, timeout=1)

    def wait_fuckn_tooltip(self):
        with suppress(Exception):
            window = self.find_element(self.root_selector)
            position = window.element.element_info.rectangle.mid_point()
            moveTo(position[0], position[1])
            self.wait_element(self.fuckn_tooltip, until=False)

    # * ----------------------------------------------------------------------------------------------------------------
    def auth(self):
        self.run()

        self.parent_switch(
            {
                "title": "Запуск 1С:Предприятия",
                "class_name": "V8NewLocalFrameBaseWnd",
                "control_type": "Window",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        )
        self.find_element(
            {
                "title": "Информационная база #1" if self.debug else "go_copy",
                "class_name": "",
                "control_type": "ListItem",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).click(double=True, set_focus=True)
        sleep(3)

        self.parent_switch(
            {
                "title": "Доступ к информационной базе",
                "class_name": "V8NewLocalFrameBaseWnd",
                "control_type": "Window",
                "found_index": 0,
            },
            timeout=30,
        )
        self.find_element(
            {
                "title": "",
                "class_name": "",
                "control_type": "ComboBox",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).type_keys(
            global_env_data["odines_username"],
            self.keys.TAB,
            clear=True,
            click=True,
            set_focus=True,
        )

        self.find_element(
            {
                "title": "",
                "class_name": "",
                "control_type": "Edit",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).type_keys(
            global_env_data["odines_password"],
            self.keys.TAB,
            clear=True,
            click=True,
            set_focus=True,
        )
        self.find_element(
            {
                "title": "OK",
                "class_name": "",
                "control_type": "Button",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).click(set_focus=True)
        sleep(10)

        # ? skip err
        message_ = {
            "title": "Конфигурация базы данных не соответствует сохраненной конфигурации.\nПродолжить?",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        button_ = {
            "title": "Да",
            "class_name": "",
            "control_type": "Button",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(message_, timeout=0.1):
            self.find_element(button_, timeout=1).click(double=True)
            self.wait_element(message_, timeout=5, until=False)

        self.parent_switch(self.root_selector, timeout=180)
        self._stack = {0: self.parent}
        self._current_index = 0
        self.root_window = self.find_element(self.root_selector, timeout=1)
        self.close_all_windows(10, 1)
        Thread(target=self.close_1c_config, daemon=True).start()

    def quit(self):
        for i in range(10):
            if self.wait_element(
                    {
                        "class_name": "#32770",
                        "control_type": "Window",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.1,
            ):
                el = self.find_elements(
                    {
                        "class_name": "#32770",
                        "control_type": "Window",
                        "visible_only": True,
                        "enabled_only": True,
                        "parent": None,
                    },
                    timeout=0.1,
                )[-1]
                el.close()
                if el.wait_element(
                        {
                            "title": "Нет",
                            "class_name": "CCPushButton",
                            "control_type": "Button",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": 0,
                            "parent": None,
                        },
                        timeout=0.1,
                ):
                    el.find_element(
                        {
                            "title": "Нет",
                            "class_name": "CCPushButton",
                            "control_type": "Button",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": 0,
                            "parent": None,
                        },
                        timeout=0.1,
                    ).click()
            else:
                break
        for i in range(10):
            if self.wait_element(
                    {
                        "class_name": "V8NewLocalFrameBaseWnd",
                        "control_type": "Window",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.1,
            ):
                self.find_elements(
                    {
                        "class_name": "V8NewLocalFrameBaseWnd",
                        "control_type": "Window",
                        "visible_only": True,
                        "enabled_only": True,
                        "parent": None,
                    },
                    timeout=0.1,
                )[-1].close()
            else:
                break
        # * подключиться к окну если есть
        if self.wait_element(self.root_selector, timeout=0.1):
            self.root = self.find_element(self.root_selector)
            self.root.set_focus()
            # * закрыть окна
            with suppress(Exception):
                self.close_all_windows(10, 1, True)
                self.open("Файл", "Выход")
                if self.wait_element(
                        {
                            "title": "Завершить работу с программой?",
                            "class_name": "",
                            "control_type": "Pane",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": 0,
                            "parent": None,
                        },
                        timeout=5,
                ):
                    self.find_element(
                        {
                            "title": "Да",
                            "class_name": "",
                            "control_type": "Button",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": 0,
                            "parent": None,
                        },
                        timeout=1,
                    ).click()
                    self.wait_element(
                        {
                            "title": "Да",
                            "class_name": "",
                            "control_type": "Button",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": 0,
                            "parent": None,
                        },
                        timeout=5,
                        until=False,
                    )

        sleep(3)
        kill_process_list(process_list_path)
        self._stack = {0: None}
        self._current_index = 0
        sleep(3)

    # * ----------------------------------------------------------------------------------------------------------------
    def open(self, *steps):
        try:
            # sleep(1)
            self.wait_fuckn_tooltip()
            for n, step in enumerate(steps):
                if n:
                    if not self.wait_element(
                            {
                                "title": step,
                                "class_name": "",
                                "control_type": "MenuItem",
                                "visible_only": True,
                                "enabled_only": True,
                                "found_index": 0,
                                "parent": self.root,
                            },
                            timeout=2,
                    ):
                        if n - 1:
                            self.find_element(
                                {
                                    "title": steps[n - 1],
                                    "class_name": "",
                                    "control_type": "MenuItem",
                                    "visible_only": True,
                                    "enabled_only": True,
                                    "found_index": 0,
                                    "parent": self.root,
                                },
                                timeout=5,
                            ).click()
                        else:
                            self.find_element(
                                {
                                    "title": steps[n - 1],
                                    "class_name": "",
                                    "control_type": "Button",
                                    "visible_only": True,
                                    "enabled_only": True,
                                    "found_index": 0,
                                    "parent": self.root,
                                },
                                timeout=5,
                            ).click()
                    self.find_element(
                        {
                            "title": step,
                            "class_name": "",
                            "control_type": "MenuItem",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": 0,
                            "parent": self.root,
                        },
                        timeout=5,
                    ).click()
                else:
                    self.find_element(
                        {
                            "title": step,
                            "class_name": "",
                            "control_type": "Button",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": 0,
                            "parent": self.root,
                        },
                        timeout=5,
                    ).click()
        except Exception as ex:
            # traceback.print_exc()
            print(f"exception while opening {ex}")

    def maximize_inner_window(self, timeout=0.1):
        if self.wait_element(
                {
                    "title": "Развернуть",
                    "class_name": "",
                    "control_type": "Button",
                    "visible_only": True,
                    "enabled_only": True,
                    "found_index": 0,
                    "parent": self.root,
                },
                timeout=timeout,
        ):
            self.find_element(
                {
                    "title": "Развернуть",
                    "class_name": "",
                    "control_type": "Button",
                    "visible_only": True,
                    "enabled_only": True,
                    "found_index": 0,
                    "parent": self.root,
                }
            ).click()

    def check_1c_error(self, count=1):
        while count > 0:
            count -= 1
            # * Конфигурация базы данных не соответствует сохраненной конфигурации -------------------------------------
            if self.wait_element(
                    {
                        "title": "Конфигурация базы данных не соответствует сохраненной конфигурации.\nПродолжить?",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = (
                    "Конфигурация базы данных не соответствует сохраненной конфигурации"
                )
                raise Exception(error_message)

            # * Ошибка при вызове метода контекста ---------------------------------------------------------------------
            if self.wait_element(
                    {
                        "title_re": "Ошибка при вызове метода контекста (.*)",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "Ошибка при вызове метода контекста"
                raise Exception(error_message)

            # * Ошибка исполнения отчета -------------------------------------------------------------------------------
            if self.wait_element(
                    {
                        "title": "Ошибка исполнения отчета",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "Ошибка исполнения отчета"
                raise Exception(error_message)

            # * Операция не выполнена ----------------------------------------------------------------------------------
            if self.wait_element(
                    {
                        "title": "Операция не выполнена",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "Операция не выполнена"
                raise Exception(error_message)

            # * Конфликт блокировок при выполнении транзакции ----------------------------------------------------------
            if self.wait_element(
                    {
                        "title_re": "Конфликт блокировок при выполнении транзакции:.*",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "Конфликт блокировок при выполнении транзакции"
                raise Exception(error_message)

            # * Введенные данные не отображены в списке, так как не соответствуют отбору -------------------------------
            if self.wait_element(
                    {
                        "title": "Введенные данные не отображены в списке, так как не соответствуют отбору.",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "Введенные данные не отображены в списке, так как не соответствуют отбору"
                raise Exception(error_message)

            # * critical В поле введены некорректные данные ------------------------------------------------------------
            if self.wait_element(
                    {
                        "title_re": "В поле введены некорректные данные.*",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "critical В поле введены некорректные данные"
                raise Exception(error_message)

            # * critical Не удалось провести ---------------------------------------------------------------------------
            if self.wait_element(
                    {
                        "title_re": "Не удалось провести.*",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "critical Не удалось провести"
                raise Exception(error_message)

            # * Сеанс работы завершен администратором ------------------------------------------------------------------
            if self.wait_element(
                    {
                        "title": "Сеанс работы завершен администратором.",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "critical Сеанс работы завершен администратором"
                raise Exception(error_message)

            # * Сеанс отсутствует или удален ---------------------------------------------------------------------------
            if self.wait_element(
                    {
                        "title_re": "Сеанс отсутствует или удален.*",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "critical Сеанс отсутствует или удален"
                raise Exception(error_message)

            # * Неизвестное окно ошибки ---------------------------------------------------------------------------
            if self.wait_element(
                    {
                        "title": "1С:Предприятие",
                        "class_name": "V8NewLocalFrameBaseWnd",
                        "control_type": "Window",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "critical Неизвестное окно ошибки"
                raise Exception(error_message)

    def close_1c_error(self):
        # * Ошибка исполнения отчета -----------------------------------------------------------------------------------
        selector_ = {
            "title": "Ошибка исполнения отчета",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "OK",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return False

        # * Ошибка при вызове метода контекста -------------------------------------------------------------------------
        selector_ = {
            "title_re": "Ошибка при вызове метода контекста (.*)",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "OK",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return False

        # * Завершить работу с программой? -----------------------------------------------------------------------------
        selector_ = {
            "title": "Завершить работу с программой?",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "Да",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return False

        # * Операция не выполнена --------------------------------------------------------------------------------------
        selector_ = {
            "title": "Операция не выполнена",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "OK",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return False

        # * Конфликт блокировок при выполнении транзакции --------------------------------------------------------------
        selector_ = {
            "title_re": "Конфликт блокировок при выполнении транзакции:.*",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "OK",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return False

        # * Введенные данные не отображены в списке, так как не соответствуют отбору -----------------------------------
        selector_ = {
            "title": "Введенные данные не отображены в списке, так как не соответствуют отбору.",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "OK",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return False

        # * Данные были изменены. Сохранить изменения? -----------------------------------------------------------------
        selector_ = {
            "title": "Данные были изменены. Сохранить изменения?",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "Нет",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return False

        # * critical В поле введены некорректные данные ----------------------------------------------------------------
        selector_ = {
            "title_re": "В поле введены некорректные данные.*",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "Да",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return True

        # * critical Не удалось провести -------------------------------------------------------------------------------
        selector_ = {
            "title_re": 'Не удалось провести ".*',
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "OK",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return True

        # * Сеанс работы завершен администратором ----------------------------------------------------------------------
        selector_ = {
            "title": "Сеанс работы завершен администратором.",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "Завершить работу",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return True

        # * Сеанс отсутствует или удален -------------------------------------------------------------------------------
        selector_ = {
            "title_re": "Сеанс отсутствует или удален.*",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "Завершить работу",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return True

    def close_1c_config(self):
        while True:
            with suppress(Exception):
                self.find_element(
                    {
                        "title_re": "В конфигурацию ИБ внесены изменения.*",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0,
                )
                self.find_element(
                    {
                        "title": "Нет",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0,
                ).click(log=False)

    def close_all_windows(self, count=10, idx=1, ext=False):
        root_window = self.root_window.element
        if ext:
            with suppress(Exception):
                # * закрыть всплывашку
                self.close_1c_error()
                self.open("Окна", "Закрыть все")
        while True:
            if (
                    len(
                        self.find_elements(
                            {
                                "title": "Закрыть",
                                "class_name": "",
                                "control_type": "Button",
                                "visible_only": True,
                                "enabled_only": True,
                                "parent": root_window,
                            },
                            timeout=1,
                        )
                    )
                    > idx
            ):
                # * закрыть всплывашку
                self.close_1c_error()
                # * закрыть
                with suppress(Exception):
                    self.find_element(
                        {
                            "title": "Закрыть",
                            "class_name": "",
                            "control_type": "Button",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": idx,
                            "parent": root_window,
                        },
                        timeout=1,
                    ).click()
                # * закрыть всплывашку
                self.close_1c_error()
            else:
                break
            # ! выход
            count -= 1
            if count <= 0:
                raise Exception("Не все окна закрыты")


if __name__ == '__main__':
    app = Odines()
    app.auth()
    print('SUCCESS')
    print('sleep 3 sec')
    sleep(3)
    app.quit()
