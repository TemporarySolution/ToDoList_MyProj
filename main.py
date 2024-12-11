import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from choise_profile import Ui_MainWindow as ChoiseProfileUI
from main_panel import Ui_MainWindow as MainPanelUI

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Инициализация текущего профиля Test
        self.current_profile = None
        self.available_profiles = ["profile_1", "profile_2", "profile_3", "profile_4"]

        # Инициализация UI выбора профиля
        self.choise_profile_ui = ChoiseProfileUI()
        self.choise_profile_ui.setupUi(self)

        # Подключение кнопок
        self.setup_choise_profile_signals()
    ##Всё в мейне или можно в каждой странице
    def setup_choise_profile_signals(self):
        """Подключение сигналов для экрана выбора профиля"""
        self.choise_profile_ui.log_in_another_profile.clicked.connect(self.log_in_another_profile)
        self.choise_profile_ui.create_profile.clicked.connect(self.create_profile)
        self.choise_profile_ui.delete_all_profiles.clicked.connect(self.delete_all_profiles)
        self.choise_profile_ui.log_in_profile.clicked.connect(self.open_main_panel)
        self.choise_profile_ui.delete_profile.clicked.connect(self.delete_profile)

        # Подключение профилей к методам
        if "profile_1" in self.available_profiles:
            self.choise_profile_ui.profile_1.clicked.connect(lambda: self.select_profile("Profile 1"))
        if "profile_2" in self.available_profiles:
            self.choise_profile_ui.profile_2.clicked.connect(lambda: self.select_profile("Profile 2"))
        if "profile_3" in self.available_profiles:
            self.choise_profile_ui.profile_3.clicked.connect(lambda: self.select_profile("Profile 3"))
        if "profile_4" in self.available_profiles:
            self.choise_profile_ui.profile_4.clicked.connect(lambda: self.select_profile("Profile 4"))

    def open_main_panel(self):
        """Переход на главное окно main_panel"""
        if not self.current_profile:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите профиль.")
            return

        self.main_panel_ui = MainPanelUI()
        self.main_panel_ui.setupUi(self)
        #Может тоже setup ui или есть лучший способ?
        # listeners для кнопок на главной панели
        self.main_panel_ui.button_change_profile.clicked.connect(self.return_to_choise_profile)

    def return_to_choise_profile(self):
        """Возврат на экран выбора профиля"""
        self.choise_profile_ui.setupUi(self)
        self.setup_choise_profile_signals()

    def log_in_another_profile(self):
        QMessageBox.information(self, "Войти в другой профиль", "Функция: Вход в другой профиль.")

    def create_profile(self):
        QMessageBox.information(self, "Создание профиля", "Функция: Создание нового профиля.")

    def delete_all_profiles(self):
        if not self.available_profiles:
            QMessageBox.warning(self, "Ошибка", "Нет профилей для удаления.")
            return

        result = QMessageBox.question(
            self,
            "Удаление всех профилей",
            "Вы уверены, что хотите удалить все профили?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if result == QMessageBox.StandardButton.Yes:
            self.available_profiles = []
            self.current_profile = None
            QMessageBox.information(self, "Удалено", "Все профили удалены.")
            self.return_to_choise_profile()

    def select_profile(self, profile_name):
        self.current_profile = profile_name
        QMessageBox.information(self, "Профиль выбран", f"Выбран {profile_name}.")

    def log_in_profile(self):
        if self.current_profile:
            QMessageBox.information(self, "Вход", f"Вход в {self.current_profile}.")
            #self.open_main_panel
        else:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите профиль.")

    def delete_profile(self):
        if not self.current_profile:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите профиль.")
            return

        result = QMessageBox.question(
            self,
            "Удаление профиля",
            f"Вы уверены, что хотите удалить {self.current_profile}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if result == QMessageBox.StandardButton.Yes:
            self.available_profiles.remove(self.current_profile)
            QMessageBox.information(self, "Удалено", f"{self.current_profile} удалён.")
            self.current_profile = None
            self.return_to_choise_profile()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
