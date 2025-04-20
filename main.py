"""
Точка входа в приложение диагностики дисков.

Запускает приложение для анализа и мониторинга дисковых накопителей.
"""

import sys
import os
import traceback
import warnings
import io
import logging
import time

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import qInstallMessageHandler, QtInfoMsg, QtWarningMsg, QtCriticalMsg, QtFatalMsg, QtDebugMsg

from gui import DriveAnalyzerApp


# Отключение вывода Qt
def message_handler(mode, context, message):
    # Выводим только критические ошибки
    if mode in (QtCriticalMsg, QtFatalMsg):
        print(f"Qt Error ({mode}): {message}")


# Пустой поток вывода
class NullWriter(io.IOBase):
    def write(self, *args, **kwargs):
        return 0

    def writable(self):
        return True
        
    def flush(self):
        pass


def main() -> None:
    """
    Главная функция приложения.
    
    Инициализирует приложение PyQt и запускает основное окно.
    Отлавливает критические ошибки и отображает информацию о них.
    """
    # Включаем вывод для диагностики проблем
    debug_mode = False  # Устанавливаем True для отладки, False для релиза
    
    if not debug_mode:
        # 1. Перенаправляем стандартные потоки вывода
        sys.stdout = NullWriter()
        sys.stderr = NullWriter()
        
        # 2. Отключаем предупреждения Python
        warnings.filterwarnings("ignore")
        
        # 3. Устанавливаем пустой обработчик сообщений Qt
        qInstallMessageHandler(message_handler)
        
        # 4. Отключаем логирование Python
        logging.getLogger().setLevel(logging.CRITICAL + 1)
        
        # 5. Устанавливаем дополнительные переменные окружения для Qt
        os.environ["QT_LOGGING_RULES"] = "*.debug=false;*.warning=false;*.critical=false;qt.qpa.*=false"
        os.environ["QT_FATAL_WARNINGS"] = "0"
        os.environ["QT_ASSUME_STDERR_HAS_CONSOLE"] = "0"
    else:
        print("Запуск в режиме отладки...")
        print(f"Python версия: {sys.version}")
        print(f"Рабочая директория: {os.getcwd()}")
        
    try:
        # Инициализация приложения
        app = QApplication(sys.argv)
        
        # Установка стиля и шрифта
        app.setStyle('Fusion')
        font = QFont("Arial", 10)
        app.setFont(font)
        
        # Создание и отображение основного окна
        window = DriveAnalyzerApp()
        window.show()
        
        if debug_mode:
            print("Окно приложения создано и отображено.")
            print("Запуск основного цикла событий...")
            
        # В режиме отладки - добавляем таймер для проверки активности
        if debug_mode:
            start_time = time.time()
            def check_app_alive():
                elapsed = time.time() - start_time
                print(f"Приложение активно {elapsed:.1f} секунд")
                if elapsed < 30:  # Проверяем только первые 30 секунд
                    app.processEvents()  # Обработка событий
                    QApplication.instance().postEvent(window, QApplication.instance().allEvents()[0])
                    # Повторная проверка через 5 секунд
                    QApplication.instance().processEvents()
                    window.update()
                
            # Запускаем первую проверку вручную
            app.processEvents()
            window.update()
            print("Первоначальная обработка событий выполнена.")
            
        # Запуск основного цикла событий
        sys.exit(app.exec_())
        
    except Exception as e:
        # Вывод сообщения о критической ошибке
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setWindowTitle("Критическая ошибка")
        error_msg.setText("Не удалось запустить приложение")
        error_msg.setInformativeText(str(e))
        error_msg.setDetailedText(traceback.format_exc())
        error_msg.exec_()
        
        if debug_mode:
            print(f"Критическая ошибка: {str(e)}")
            print(traceback.format_exc())


if __name__ == "__main__":
    main() 