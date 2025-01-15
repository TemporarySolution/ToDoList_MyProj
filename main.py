import sys
import sqlite3

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog, QListWidgetItem, QPushButton, QFileDialog
from PyQt6.QtGui import  QPixmap

from choise_profile import Ui_MainWindow as ChoiseProfileUI
from main_panel import Ui_MainWindow as MainPanelUI
from editing_tasks_panel import Ui_MainWindow as EditingPanelUI


###
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Инициализация текущего профиля
        self.current_profile = None
        self.prof_database = "db\\profiles.db"
        self.task_database = "db\\tasks.db"
        self.init_database()
        self.init_tasks_table()
        # Инициализация UI выбора профиля
        self.choise_profile_ui = ChoiseProfileUI()
        self.choise_profile_ui.setupUi(self)

        # Обновление интерфейса профилей
        self.update_profile_buttons()

        # Подключение кнопок
        self.setup_choise_profile_signals()

    def init_database(self):
        """Создание базы данных и таблиц, если их нет"""
        connection = sqlite3.connect(self.prof_database)
        cursor = connection.cursor()

        # Таблица профилей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')

        # Пример таблицы задач (динамически создаются для каждого профиля)
        # cursor.execute('''
        #     CREATE TABLE IF NOT EXISTS tasks_profile_<profile_id> (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         name TEXT NOT NULL,
        #         deadline TEXT,
        #         description TEXT,
        #         tag TEXT
        #     )
        # ''')

        connection.commit()
        connection.close()

    def setup_choise_profile_signals(self):
        """Подключение сигналов для экрана выбора профиля"""
        self.choise_profile_ui.log_in_another_profile.clicked.connect(self.log_in_another_profile)
        self.choise_profile_ui.create_profile.clicked.connect(self.create_profile)
        self.choise_profile_ui.delete_all_profiles.clicked.connect(self.delete_all_profiles)
        self.choise_profile_ui.log_in_profile.clicked.connect(self.open_main_panel)
        self.choise_profile_ui.delete_profile.clicked.connect(self.delete_profile)

        # Подключение профилей к методам
        self.choise_profile_ui.profile_1.clicked.connect(lambda: self.select_profile(1))
        self.choise_profile_ui.profile_2.clicked.connect(lambda: self.select_profile(2))
        self.choise_profile_ui.profile_3.clicked.connect(lambda: self.select_profile(3))
        self.choise_profile_ui.profile_4.clicked.connect(lambda: self.select_profile(4))

    def update_profile_buttons(self):
        """Обновление имен профилей на кнопках"""
        connection = sqlite3.connect(self.prof_database)
        cursor = connection.cursor()

        cursor.execute("SELECT name FROM profiles ORDER BY id")
        profiles = cursor.fetchall()

        buttons = [
            self.choise_profile_ui.profile_1,
            self.choise_profile_ui.profile_2,
            self.choise_profile_ui.profile_3,
            self.choise_profile_ui.profile_4
        ]

        for i, button in enumerate(buttons):
            if i < len(profiles):
                button.setText(profiles[i][0])
                button.setEnabled(True)
            else:
                button.setText(f"Profile {i + 1}")
                button.setEnabled(False)

        connection.close()

    def create_profile(self):
        """Создание нового профиля"""
        connection = sqlite3.connect(self.prof_database)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM profiles")
        profile_count = cursor.fetchone()[0]

        if profile_count >= 4:
            QMessageBox.warning(self, "Ошибка", "Невозможно создать больше 4 профилей.")
            connection.close()
            return

        profile_name, ok = QInputDialog.getText(self, "Создать профиль", "Введите имя профиля:")
        if not ok or not profile_name.strip():
            return

        try:
            cursor.execute("INSERT INTO profiles (name) VALUES (?)", (profile_name.strip(),))
            connection.commit()
            QMessageBox.information(self, "Успех", f"Профиль {profile_name} создан.")
            self.update_profile_buttons()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", f"Профиль c именем {profile_name} уже существует.")
        finally:
            connection.close()

    def delete_profile(self):
        """Удаление выбранного профиля"""
        if not self.current_profile:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите профиль.")
            return

        result = QMessageBox.question(
            self,
            "Удаление профиля",
            f"Вы уверены, что хотите удалить профиль '{self.current_profile}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if result == QMessageBox.StandardButton.Yes:
            connection = sqlite3.connect(self.prof_database)
            cursor = connection.cursor()

            try:
                cursor.execute("DELETE FROM profiles WHERE name = ?", (self.current_profile,))
                connection.commit()
                QMessageBox.information(self, "Успех", f"Профиль {self.current_profile} удалён.")
                self.current_profile = None
                self.update_profile_buttons()
            finally:
                connection.close()

    def select_profile(self, profile_index):
        """Выбор профиля по индексу"""
        connection = sqlite3.connect(self.prof_database)
        cursor = connection.cursor()

        cursor.execute("SELECT name FROM profiles ORDER BY id")
        profiles = cursor.fetchall()

        if 0 <= profile_index - 1 < len(profiles):
            self.current_profile = profiles[profile_index - 1][0]
            QMessageBox.information(self, "Профиль выбран", f"Выбран {self.current_profile}.")

        connection.close()


    def open_main_panel(self):
        """Переход на главное окно main_panel"""
        if not self.current_profile:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите профиль.")
            return

        # Переключение на главное окно
        self.main_panel_ui = MainPanelUI()
        self.main_panel_ui.setupUi(self)

        # Подключение кнопок на главной панели
        self.main_panel_ui.button_change_profile.clicked.connect(self.return_to_choise_profile)
        self.main_panel_ui.button_create_new_folder.clicked.connect(self.open_editing_panel)
        self.main_panel_ui.searchButton.clicked.connect(self.search_tasks)

    def return_to_choise_profile(self):
        """Возврат на экран выбора профиля"""
        self.choise_profile_ui.setupUi(self)
        self.update_profile_buttons()
        self.setup_choise_profile_signals()

    def open_editing_panel(self):
        """Переход на панель редактирования задачи"""
        self.editing_panel_ui = EditingPanelUI()
        self.editing_panel_ui.setupUi(self)

        # Подключение кнопок на панели редактирования

        self.editing_panel_ui.delete_task.clicked.connect(self.delete_task)

        self.editing_panel_ui.add_task.clicked.connect(self.add_task)
        self.editing_panel_ui.save_task_change.clicked.connect(self.edit_task)
        ###self.editing_panel_ui.edit_task.clicked.connect(self.edit_task)
        ###self.editing_panel_ui.back_to_group_tasks.clicked.connect(self.return_to_group_tasks)
        self.editing_panel_ui.back_to_main_panel.clicked.connect(self.return_to_main_panel)
        self.editing_panel_ui.delete_task.clicked.connect(self.delete_task)
        self.editing_panel_ui.add_complete.clicked.connect(self.delete_task)
        self.editing_panel_ui.pushButton.clicked.connect(self.select_task_picture)

    def return_to_group_tasks(self):
        """Возврат к экрану групп задач"""
        result = QMessageBox.question(
            self,
            "Возврат к группам задач",
            "Вы уверены, что хотите вернуться без сохранения изменений?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if result == QMessageBox.StandardButton.Yes:
            self.open_main_panel()

    def return_to_main_panel(self):
        """Возврат на главную панель приложения"""
        self.open_main_panel()

    """def delete_task(self):
        ###Удаление задачи###
        task_name = self.editing_panel_ui.name_of_task.toPlainText()
        if not task_name.strip():
            QMessageBox.warning(self, "Ошибка", "Невозможно удалить задачу: название задачи пустое.")
            return

        result = QMessageBox.question(
            self,
            "Удаление задачи",
            f"Вы уверены, что хотите удалить задачу '{task_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if result == QMessageBox.StandardButton.Yes:
            self.clear_task_data()
            QMessageBox.information(self, "Успех", f"Задача '{task_name}' успешно удалена.")
"""
    def clear_task_data(self):
        """Очистка данных текущей задачи"""
        self.editing_panel_ui.name_of_task.clear()
        self.editing_panel_ui.deadline_of_task.clear()
        self.editing_panel_ui.text_of_task.clear()
        #self.editing_panel_ui.name_of_folder_with_task.clear()


    ################################
    ####### Добавление задач #######
    ################################

    def search_tasks(self):
        connection = sqlite3.connect(self.task_database)
        cursor = connection.cursor()

        try:
            # Поиск задач, связанных с текущим профилем
            query = """
                SELECT id, name, deadline, description 
                FROM tasks 
                WHERE profile_name = ? AND (name LIKE ? OR description LIKE ?)
            """
            cursor.execute(query, (self.current_profile, f"%{self.main_panel_ui.Title.text()}%", f"%{self.main_panel_ui.Title.text()}%"))
            results = cursor.fetchall()

            # Очистка listWidget перед выводом новых результатов
            self.main_panel_ui.listWidget.clear()

            if results:
                # Добавление результатов поиска в виде кнопок в listWidget
                for task_id, task_name, deadline, description in results:
                    task_button = QPushButton(task_name, self)
                    task_button.clicked.connect(lambda _, t_id=task_id: self.open_editing_panel_with_task(t_id))

                    # Добавление кнопки в listWidget
                    item = QListWidgetItem()
                    self.main_panel_ui.listWidget.addItem(item)
                    self.main_panel_ui.listWidget.setItemWidget(item, task_button)
            else:
                QMessageBox.information(self, "Результаты поиска", "Задачи не найдены.")
        finally:
            connection.close()

    def open_editing_panel_with_task(self, task_id):
        """Открытие панели редактирования задачи с предзаполненными данными."""
        self.editing_panel_ui = EditingPanelUI()
        self.editing_panel_ui.setupUi(self)

        # Подключение кнопок на панели редактирования
        self.editing_panel_ui.add_complete.clicked.connect(self.delete_task)
        #self.editing_panel_ui.back_to_group_tasks.clicked.connect(self.return_to_group_tasks)
        self.editing_panel_ui.back_to_main_panel.clicked.connect(self.return_to_main_panel)
        self.editing_panel_ui.save_task_change.clicked.connect(self.edit_task)
        self.editing_panel_ui.delete_task.clicked.connect(self.delete_task)
        self.editing_panel_ui.pushButton.clicked.connect(self.select_task_picture)


        # Загрузка данных задачи в поля редактирования
        connection = sqlite3.connect(self.task_database)
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT name, deadline, description FROM tasks WHERE id = ?", (task_id,))
            task = cursor.fetchone()
            if task:
                self.editing_panel_ui.name_of_task.setPlainText(task[0])
                self.editing_panel_ui.deadline_of_task.setPlainText(task[1])
                self.editing_panel_ui.text_of_task.setPlainText(task[2])
        finally:
            connection.close()

    def init_tasks_table(self):
        """Создание таблицы задач, если её нет"""
        connection = sqlite3.connect(self.task_database)
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_name TEXT NOT NULL,
                name TEXT NOT NULL,
                deadline TEXT,
                description TEXT,
                FOREIGN KEY(profile_name) REFERENCES profiles(name)
            )
        ''')

        connection.commit()
        connection.close()

    def add_task(self):
        """Добавление новой задачи для текущего профиля"""
        if not self.current_profile:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите профиль.")
            return

        #task_name = self.editing_panel_ui.name_of_task.toPlainText().strip()
        task_name = self.editing_panel_ui.name_of_task.toPlainText().strip()
        deadline = self.editing_panel_ui.deadline_of_task.toPlainText().strip()
        description = self.editing_panel_ui.text_of_task.toPlainText().strip()
        #description = self.editing_panel_ui.text_of_task.text().strip()

        if not task_name:
            QMessageBox.warning(self, "Ошибка", "Название задачи не может быть пустым.")
            return

        connection = sqlite3.connect(self.task_database)
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO tasks (profile_name, name, deadline, description) VALUES (?, ?, ?, ?)",
                (self.current_profile, task_name, deadline, description)
            )
            connection.commit()
            QMessageBox.information(self, "Успех", f"Задача '{task_name}' добавлена.")
            self.clear_task_data()
            self.return_to_main_panel()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Произошла ошибка при добавлении задачи.")
        finally:
            connection.close()

    def edit_task(self):
        """Редактирование существующей задачи"""
        if not self.current_profile:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите профиль.")
            return

        task_name = self.editing_panel_ui.name_of_task.toPlainText().strip()
        deadline = self.editing_panel_ui.deadline_of_task.text().strip()
        description = self.editing_panel_ui.text_of_task.toPlainText().strip()

        if not task_name:
            QMessageBox.warning(self, "Ошибка", "Название задачи не может быть пустым.")
            return

        connection = sqlite3.connect(self.task_database)
        cursor = connection.cursor()

        try:
            cursor.execute(
                "UPDATE tasks SET deadline = ?, description = ? WHERE profile_name = ? AND name = ?",
                (deadline, description, self.current_profile, task_name)
            )
            connection.commit()
            QMessageBox.information(self, "Успех", f"Задача '{task_name}' обновлена.")
        finally:
            connection.close()

    def delete_task(self):
        task_name = self.editing_panel_ui.name_of_task.toPlainText().strip()

        if not task_name:
            QMessageBox.warning(self, "Ошибка", "Название задачи не может быть пустым.")
            return

        result = QMessageBox.question(
            self,
            "Удаление задачи",
            f"Вы уверены, что хотите удалить задачу '{task_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if result == QMessageBox.StandardButton.No:
            return

        connection = sqlite3.connect(self.task_database)
        cursor = connection.cursor()

        try:
            cursor.execute(
                "DELETE FROM tasks WHERE profile_name = ? AND name = ?",
                (self.current_profile, task_name)
            )
            connection.commit()
            QMessageBox.information(self, "Успех", f"Задача '{task_name}' удалена.")
            self.clear_task_data()
            self.return_to_main_panel()
        finally:
            connection.close()

    ##  Интерфейс для отображения задач нужно переделать ##

    def load_tasks(self):
        """Загрузка задач для текущего профиля"""
        if not self.current_profile:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите профиль.")
            return

        connection = sqlite3.connect(self.task_database)
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT name, deadline, description FROM tasks WHERE profile_name = ?",
                           (self.current_profile,))
            tasks = cursor.fetchall()

            # Пример: отобразить задачи в UI
            for task in tasks:
                print(f"Название: {task[0]}, Дедлайн: {task[1]}, Описание: {task[2]}")
        finally:
            connection.close()

    def log_in_another_profile(self):
        QMessageBox.information(self, "Войти в другой профиль", "Функция: Вход в другой профиль.")


    def delete_all_profiles(self):
        """Удаление всех профилей"""
        connection = sqlite3.connect(self.prof_database)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM profiles")
        profile_count = cursor.fetchone()[0]

        if profile_count == 0:
            QMessageBox.warning(self, "Ошибка", "Нет профилей для удаления.")
            connection.close()
            return

        result = QMessageBox.question(
            self,
            "Удаление всех профилей",
            "Вы уверены, что хотите удалить все профили?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if result == QMessageBox.StandardButton.Yes:
            cursor.execute("DELETE FROM profiles")
            connection.commit()
            QMessageBox.information(self, "Успех", "Все профили удалены.")
            self.current_profile = None
            self.update_profile_buttons()

        connection.close()


    def log_in_profile(self):
        """Вход в текущий профиль"""
        if self.current_profile:
            QMessageBox.information(self, "Вход", f"Вы вошли в профиль {self.current_profile}.")
        else:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите профиль.")

    def select_task_picture(self):
        """Позволяет пользователю выбрать изображение и отображает его в task_picture."""
        # Открытие диалога выбора файла
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        # Если пользователь выбрал файл
        if file_path:
            pixmap = QPixmap(file_path)

            # Проверка: изображение должно соответствовать размеру task_picture
            if self.editing_panel_ui.task_picture.size().isValid():
                pixmap = pixmap.scaled(
                    self.editing_panel_ui.task_picture.size()
                )

            # Установка изображения в QLabel
            self.editing_panel_ui.task_picture.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
