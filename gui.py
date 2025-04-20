"""
Модуль с GUI компонентами приложения для анализа дисков.

Содержит классы для:
- Главного окна приложения
- Окна отчетов об ошибках
- Вспомогательных окон для отображения информации
"""

import traceback
import psutil
import os
import time
import platform
from typing import Dict, Any, Tuple, List, Optional, Callable
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QLinearGradient, QGradient, QPainter, QBrush, QRadialGradient, QCursor, QPainterPath, QRegion
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QTextEdit, QScrollArea, QMessageBox, QComboBox,
    QHBoxLayout, QSizePolicy, QFrame, QProgressBar, QFileDialog,
    QGraphicsDropShadowEffect, QStyleFactory, QApplication, QGridLayout, QDialog, QTextBrowser,
    QSplitter, QStatusBar
)

from func_disk import DiskAnalyzer, SystemInfoProvider

# Настройки приложения
APP_STYLE = {
    "primary": "#4F46E5",       # Фиолетово-синий
    "secondary": "#3B82F6",     # Синий
    "success": "#10B981",       # Зеленый
    "warning": "#F59E0B",       # Оранжевый
    "danger": "#EF4444",        # Красный
    "background": "#0F172A",    # Темно-синий фон
    "card": "#1E293B",          # Карточки 
    "surface": "#334155",       # Дополнительная поверхность
    "text": "#F8FAFC",          # Основной текст
    "text_secondary": "#94A3B8", # Вторичный текст
    "primary_hover": "#5F56E5",  # Фиолетово-синий при наведении
    "primary_active": "#4A41E5", # Фиолетово-синий при нажатии
    "border": "#404040",         # Граница
    "card_alt": "#293447",      # Альтернативная карточка
    "background_secondary": "#1E293B"  # Вторичный фон
}


class ErrorReportWindow(QMainWindow):
    """Окно для отображения подробного отчета об ошибке."""
    
    def __init__(self, error_details: Dict[str, Any], parent=None):
        """
        Инициализирует окно отчета об ошибке.
        
        Args:
            error_details: Словарь с деталями ошибки
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.setWindowTitle("Отчет об ошибке")
        self.setMinimumSize(QSize(800, 600))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Заголовок с градиентом
        title_frame = QFrame()
        title_frame.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 {APP_STYLE['danger']}, stop:1 #C0392B);
            border-radius: 10px;
        """)
        title_frame.setMinimumHeight(80)
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("Произошла ошибка")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        
        # Добавляем тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        title_frame.setGraphicsEffect(shadow)
        
        layout.addWidget(title_frame)
        
        # Основная информация об ошибке
        error_info = QTextEdit()
        error_info.setReadOnly(True)
        error_info.setFont(QFont("Consolas", 10))
        error_info.setStyleSheet(f"""
            QTextEdit {{
                background-color: {APP_STYLE['card']};
                color: {APP_STYLE['text']};
                border: none;
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        # Добавляем тень
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(20)
        shadow2.setColor(QColor(0, 0, 0, 60))
        shadow2.setOffset(0, 4)
        error_info.setGraphicsEffect(shadow2)
        
        error_text = f"""
        <div style="font-family: 'Segoe UI', Arial; font-size: 13px; line-height: 1.6;">
            <h2 style="color: {APP_STYLE['danger']};">{error_details.get('title', 'Неизвестная ошибка')}</h2>
            <p><b>Время:</b> {error_details.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</p>
            <p><b>Тип ошибки:</b> {error_details.get('type', 'Неизвестно')}</p>
            <p><b>Описание:</b> {error_details.get('message', 'Нет описания')}</p>
            
            <h3 style="color: {APP_STYLE['warning']};">Детали:</h3>
            <pre style="background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px;">{error_details.get('details', 'Нет дополнительных деталей')}</pre>
            
            <h3 style="color: {APP_STYLE['secondary']};">Контекст:</h3>
            <pre style="background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px;">{error_details.get('context', 'Нет информации о контексте')}</pre>
        </div>
        """
        
        error_info.setHtml(error_text)
        layout.addWidget(error_info)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        close_btn = QPushButton("Закрыть")
        close_btn.setFont(QFont("Segoe UI", 11))
        close_btn.setMinimumHeight(45)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {APP_STYLE['danger']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: #C0392B;
            }}
            QPushButton:pressed {{
                background-color: #A93226;
            }}
        """)
        close_btn.clicked.connect(self.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        # Применяем стиль к окну
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {APP_STYLE['background']};
            }}
        """)


class DriveAnalyzerApp(QMainWindow):
    """Главное окно приложения для анализа дисков."""
    
    def __init__(self):
        """Инициализирует главное окно приложения."""
        super().__init__()
        self.setWindowTitle("Диагностика и анализ дисков v1.0")
        self.setMinimumSize(1000, 700)
        self.setWindowIcon(QIcon("Ico.ico"))
        
        # Настройка цветовой палитры
        self.setup_palette()
        
        # Инициализация анализатора дисков
        self.disk_analyzer = DiskAnalyzer()
        self.system_info_provider = SystemInfoProvider()
        
        # Получаем информацию о системе
        self.system_info = self._get_system_info()
        
        # Инициализация UI
        self._init_ui()
        
    def setup_palette(self) -> None:
        """Настраивает цветовую палитру приложения."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(APP_STYLE['background']))
        palette.setColor(QPalette.WindowText, QColor(APP_STYLE['text']))
        palette.setColor(QPalette.Base, QColor(APP_STYLE['card']))
        palette.setColor(QPalette.AlternateBase, QColor(APP_STYLE['card']))
        palette.setColor(QPalette.ToolTipBase, QColor(APP_STYLE['card']))
        palette.setColor(QPalette.ToolTipText, QColor(APP_STYLE['text']))
        palette.setColor(QPalette.Text, QColor(APP_STYLE['text']))
        palette.setColor(QPalette.Button, QColor(APP_STYLE['card']))
        palette.setColor(QPalette.ButtonText, QColor(APP_STYLE['text']))
        palette.setColor(QPalette.BrightText, QColor(APP_STYLE['warning']))
        palette.setColor(QPalette.Highlight, QColor(APP_STYLE['primary']))
        palette.setColor(QPalette.HighlightedText, QColor(APP_STYLE['text']))
        
        self.setPalette(palette)
        
        # Устанавливаем глобальные настройки шрифта для приложения
        font = QFont("Segoe UI", 10)
        QApplication.setFont(font)
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Получает информацию о системе и форматирует её для отображения."""
        sys_info = self.system_info_provider.get_system_info()
        return {
            "os_name": platform.system(),
            "os_version": platform.release(),
            "processor": sys_info.get("processor", "Неизвестно"),
            "memory": round(sys_info.get("memory_total_gb", 0), 1),
            "uptime": int(time.time() - psutil.boot_time())
        }

    def _create_drives_panel(self, parent_layout: QVBoxLayout) -> None:
        """
        Создает панель с информацией о дисках.
        
        Args:
            parent_layout: Родительский layout, в который будет добавлена панель
        """
        # Создание контейнера для панели дисков
        drives_container = QFrame()
        drives_container.setStyleSheet(f"""
            QFrame {{
                background-color: {APP_STYLE['card']};
                border-radius: 10px;
                padding: 0px;
                border: 1px solid {self._with_opacity(APP_STYLE['border'], 0.5)};
            }}
        """)
        
        # Добавляем тень для контейнера
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        drives_container.setGraphicsEffect(shadow)
        
        # Создаем layout для контейнера
        drives_layout = QVBoxLayout(drives_container)
        drives_layout.setContentsMargins(15, 15, 15, 15)
        drives_layout.setSpacing(10)
        
        # Заголовок панели с кнопками
        header_layout = QVBoxLayout()
        
        # Верхний ряд с заголовком и главной кнопкой
        title_row = QHBoxLayout()
                
        header_layout.addLayout(title_row)
        
        # Второй ряд кнопок
        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        
        # Кнопка для отображения графика использования
        graph_btn = QPushButton("График использования")
        graph_btn.setStyleSheet(self._get_secondary_button_style())
        graph_btn.setCursor(QCursor(Qt.PointingHandCursor))
        graph_btn.clicked.connect(self.show_disk_usage_graph)
        button_row.addWidget(graph_btn)
        
        # Кнопка для отображения советов по обслуживанию
        tips_btn = QPushButton("Советы по обслуживанию")
        tips_btn.setStyleSheet(self._get_secondary_button_style())
        tips_btn.setCursor(QCursor(Qt.PointingHandCursor))
        tips_btn.clicked.connect(self.show_maintenance_tips)
        button_row.addWidget(tips_btn)
        
        # Добавляем место для растягивания справа
        button_row.addStretch(1)
        
        header_layout.addLayout(button_row)
        
        drives_layout.addLayout(header_layout)
        
        # Добавляем тонкую линию-разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {APP_STYLE['border']}; max-height: 1px; margin: 10px 0;")
        drives_layout.addWidget(separator)
        
        # Область прокрутки для информации о дисках
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Виджет для отображения текста
        self.drives_text = QTextEdit()
        self.drives_text.setReadOnly(True)
        self.drives_text.setFrameShape(QTextEdit.NoFrame)
        self.drives_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: transparent;
                color: {APP_STYLE['text']};
                border: none;
            }}
        """)
        
        scroll_area.setWidget(self.drives_text)
        drives_layout.addWidget(scroll_area)
        
        # Добавляем контейнер в родительский layout
        parent_layout.addWidget(drives_container)

    def _init_ui(self) -> None:
        """Инициализирует элементы пользовательского интерфейса."""
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем основной layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Секция с заголовком и информацией о системе
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)  # Уменьшаем расстояние между элементами
        
        # Создаем виджет с краткой информацией о системе
        system_info_container = QWidget()
        system_info_container.setMinimumWidth(580)
        system_info_container.setFixedHeight(80)
        system_info_container.setStyleSheet(f"""
            background-color: {self._with_opacity(APP_STYLE['background_secondary'], 0.7)}; 
            border: 1px solid {self._with_opacity(APP_STYLE['primary'], 0.2)};
            border-radius: 8px;
            padding: 10px;
            margin: 0px;
        """)
        
        # Компоновка системной информации
        system_info_layout = QGridLayout(system_info_container)
        system_info_layout.setContentsMargins(10, 3, 10, 3)
        system_info_layout.setSpacing(8)
        
        # Настраиваем ширину колонок (колонка 3 для процессора получает больше места)
        system_info_layout.setColumnStretch(0, 1)  # Колонка с метками ОС и ОЗУ
        system_info_layout.setColumnStretch(1, 2)  # Колонка со значениями ОС и ОЗУ
        system_info_layout.setColumnStretch(2, 1)  # Колонка с меткой ЦП и Время работы
        system_info_layout.setColumnStretch(3, 4)  # Колонка со значением ЦП (больше места)

        # Стили для меток и значений
        label_style = """
            color: #a0a0a0; 
            font-size: 12px;
            font-weight: 500;
            margin-right: 4px;
        """
        
        value_style = """
            color: #ffffff; 
            font-size: 12px;
            font-weight: 600;
        """

        # ОС
        os_label = QLabel("ОС:")
        os_label.setStyleSheet(label_style)
        os_value = QLabel(f"{self.system_info['os_name']} {self.system_info['os_version']}")
        os_value.setStyleSheet(value_style)
        
        system_info_layout.addWidget(os_label, 0, 0, 1, 1, Qt.AlignLeft)
        system_info_layout.addWidget(os_value, 0, 1, 1, 1, Qt.AlignLeft)
        
        # ЦП
        cpu_label = QLabel("ЦП:")
        cpu_label.setStyleSheet(label_style)
        
        # Получаем название процессора и сокращаем при необходимости
        processor_name = self.system_info['processor']
        if len(processor_name) > 45:  # Увеличиваем допустимую длину с 35 до 45
            # Сокращаем название процессора, сохраняя важные части
            parts = processor_name.split()
            # Удаляем некоторые общие слова, которые менее важны
            for word in ['Processor', 'CPU', 'with', 'Intel', 'AMD']:
                if word in parts:
                    parts.remove(word)
            # Если всё еще слишком длинное, обрезаем
            if len(' '.join(parts)) > 45:
                processor_name = ' '.join(parts[:4]) + "..."  # Берем больше частей (4 вместо 3)
        
        cpu_value = QLabel(processor_name)
        cpu_value.setStyleSheet(value_style)
        cpu_value.setToolTip(self.system_info['processor'])  # Показываем полное название в подсказке
        cpu_value.setMinimumWidth(250)  # Увеличиваем минимальную ширину с 150 до 250
        cpu_value.setWordWrap(True)  # Разрешаем перенос слов
        
        system_info_layout.addWidget(cpu_label, 0, 2, 1, 1, Qt.AlignLeft)
        system_info_layout.addWidget(cpu_value, 0, 3, 1, 1, Qt.AlignLeft)
        
        # ОЗУ
        ram_label = QLabel("ОЗУ:")
        ram_label.setStyleSheet(label_style)
        ram_value = QLabel(f"{self.system_info['memory']} ГБ")
        ram_value.setStyleSheet(value_style)
        
        system_info_layout.addWidget(ram_label, 1, 0, 1, 1, Qt.AlignLeft)
        system_info_layout.addWidget(ram_value, 1, 1, 1, 1, Qt.AlignLeft)
        
        # Время работы
        uptime_label = QLabel("Время работы:")
        uptime_label.setStyleSheet(label_style)
        uptime_value = QLabel(self._format_uptime(self.system_info['uptime']))
        uptime_value.setStyleSheet(value_style)
        
        system_info_layout.addWidget(uptime_label, 1, 2, 1, 1, Qt.AlignLeft)
        system_info_layout.addWidget(uptime_value, 1, 3, 1, 1, Qt.AlignLeft)
        
        # Создаем фрейм для логотипа
        logo_frame = QFrame()
        logo_frame.setFixedSize(32, 32)
        logo_frame.setStyleSheet("""
            background-image: url(disk_icon.png);
            background-position: center;
            background-repeat: no-repeat;
            background-size: contain;
            margin-right: 8px;
        """)
        
        # Создаем заголовок приложения
        title_label = QLabel("Диагностика дисков")
        title_label.setStyleSheet(f"""
            color: {APP_STYLE['text']};
            font-size: 16px;
            font-weight: bold;
        """)
        
        # Добавляем кнопку с информацией
        info_button = QPushButton("ℹ️")
        info_button.setToolTip("Подробная информация о системе")
        info_button.setCursor(QCursor(Qt.PointingHandCursor))
        info_button.setFixedSize(28, 28)
        info_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
                padding: 0;
            }
            QPushButton:hover {
                color: #4A6CF7;
            }
        """)
        info_button.clicked.connect(self.show_system_info)
        
        # Добавляем компоненты в шапку
        header_layout.addWidget(logo_frame, 0, Qt.AlignLeft)
        header_layout.addWidget(title_label, 0, Qt.AlignLeft)
        header_layout.addStretch(1)  # Добавляем растяжение для позиционирования
        header_layout.addWidget(system_info_container, 1, Qt.AlignLeft | Qt.AlignVCenter)  # Меняем выравнивание с Right на Left
        header_layout.addStretch(1)  # Добавляем растяжение после контейнера
        header_layout.addWidget(info_button, 0, Qt.AlignRight)
        
        main_layout.addLayout(header_layout)
        
        # Панель с информацией о дисках
        self._create_drives_panel(main_layout)
        
        # Восстанавливаем добавление статус-бара
        self._add_status_bar()
        
        # Обновляем список дисков
        self._update_drives_info()
        
        # Устанавливаем таймер для обновления информации о дисках и системной информации
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_all_info)
        # Обновляем каждые 5 секунд
        self.update_timer.start(5000)
        
    def _update_all_info(self) -> None:
        """Обновляет всю информацию в приложении."""
        try:
            # Обновляем информацию о дисках
            self._update_drives_info()
            # Восстанавливаем обновление статус-бара
            self.update_status_bar()
            
            # Обновляем информацию о системе
            self.system_info = self._get_system_info()
            
            # Обновляем отображаемые значения
            for child in self.findChildren(QLabel):
                try:
                    if child.text().startswith("ОС:"):
                        label_value = self.findChild(QLabel, text=f"{self.system_info['os_name']} {self.system_info['os_version']}")
                        if label_value:
                            label_value.setText(f"{self.system_info['os_name']} {self.system_info['os_version']}")
                    elif child.text().startswith("ЦП:"):
                        # Находим метку значения ЦП рядом с меткой "ЦП:"
                        idx = self.findChildren(QLabel).index(child)
                        if idx + 1 < len(self.findChildren(QLabel)):
                            cpu_value = self.findChildren(QLabel)[idx + 1]
                            
                            # Форматируем название процессора
                            processor_name = self.system_info['processor']
                            if len(processor_name) > 45:
                                parts = processor_name.split()
                                for word in ['Processor', 'CPU', 'with', 'Intel', 'AMD']:
                                    if word in parts:
                                        parts.remove(word)
                                if len(' '.join(parts)) > 45:
                                    processor_name = ' '.join(parts[:4]) + "..."
                            
                            # Обновляем значение и подсказку
                            cpu_value.setText(processor_name)
                            cpu_value.setToolTip(self.system_info['processor'])
                    elif child.text().startswith("ОЗУ:"):
                        label_value = self.findChild(QLabel, text=f"{self.system_info['memory']} ГБ")
                        if label_value:
                            label_value.setText(f"{self.system_info['memory']} ГБ")
                    elif child.text().startswith("Время работы:"):
                        label_value = self.findChild(QLabel, text=self._format_uptime(self.system_info['uptime']))
                        if label_value:
                            label_value.setText(self._format_uptime(self.system_info['uptime']))
                except Exception:
                    # Пропускаем ошибки обновления отдельных элементов
                    continue
        except Exception as e:
            # Логируем ошибку, но не прерываем работу приложения
            print(f"Ошибка при обновлении информации: {str(e)}")
    
    def _get_button_style(self) -> str:
        """Возвращает стиль для кнопок."""
        return f"""
            QPushButton {{
                background-color: {APP_STYLE['primary']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {APP_STYLE['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {APP_STYLE['primary_active']};
            }}
        """
    
    def _get_secondary_button_style(self) -> str:
        """Возвращает стиль для вторичных кнопок."""
        return f"""
            QPushButton {{
                background-color: {self._with_opacity(APP_STYLE['primary'], 0.1)};
                color: white;
                border: 1px solid {self._with_opacity(APP_STYLE['primary'], 0.3)};
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: 600;
                font-family: 'Segoe UI';
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {self._with_opacity(APP_STYLE['primary'], 0.15)};
                border: 1px solid {self._with_opacity(APP_STYLE['primary'], 0.4)};
            }}
            QPushButton:pressed {{
                background-color: {self._with_opacity(APP_STYLE['primary'], 0.2)};
            }}
        """
    
    def _create_info_window(self, title: str, html_content: str) -> QDialog:
        """
        Создает информационное окно с заданным заголовком и HTML-содержимым.
        
        Args:
            title: Заголовок окна
            html_content: HTML-содержимое для отображения в окне
            
        Returns:
            Диалоговое окно с информацией
        """
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(html_content)
        
        # Устанавливаем шрифт для корректного отображения кириллицы
        font = QFont("Segoe UI", 10)
        text_browser.setFont(font)
        
        # Стилизуем текстовый браузер
        text_browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {APP_STYLE['card']};
                color: {APP_STYLE['text']};
                border: 1px solid {APP_STYLE['border']};
                border-radius: 5px;
                padding: 10px;
            }}
        """)
        
        layout.addWidget(text_browser)
        
        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.setStyleSheet(self._get_button_style())
        close_button.clicked.connect(dialog.accept)
        close_button.setFixedWidth(120)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        return dialog
        
    def _add_status_bar(self) -> None:
        """Добавляет улучшенный статус бар с дополнительной информацией."""
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background-color: {APP_STYLE['card']};
                color: {APP_STYLE['text']};
                border-top: 1px solid {APP_STYLE['border']};
                padding: 2px;
                min-height: 28px;
                max-height: 28px;
                font-family: 'Segoe UI';
                font-size: 12px;
            }}
        """)
        
        # Виджет для отображения статуса дисков
        self.disk_status_widget = QFrame()
        self.disk_status_widget.setStyleSheet("background-color: transparent;")
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(5, 0, 5, 0)
        status_layout.setSpacing(10)
        self.disk_status_widget.setLayout(status_layout)
        
        # Создаем объекты, но не добавляем их в интерфейс
        self.status_icon = QLabel()
        self.status_label = QLabel()
        
        # Создаем рамку для прогресс-бара с тенью
        progress_frame = QFrame()
        progress_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {APP_STYLE['background']};
                border-radius: 4px;
                padding: 0px;
            }}
        """)
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(0)
        
        # Прогресс-бар с текстом
        self.disk_space_bar = QProgressBar()
        self.disk_space_bar.setRange(0, 100)
        self.disk_space_bar.setFormat("Общее заполнение: %v%")
        self.disk_space_bar.setAlignment(Qt.AlignCenter)
        self.disk_space_bar.setTextVisible(True)
        self.disk_space_bar.setMinimumHeight(22)
        self.disk_space_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                text-align: center;
                color: white;
                background: {APP_STYLE['card']};
                height: 22px;
                font-size: 13px;
                font-weight: 900;
                margin: 0px;
                padding: 0px;
            }}
            QProgressBar::chunk {{
                background: {APP_STYLE['success']};
                border-radius: 4px;
            }}
        """)
        
        # Добавляем тень для текста с использованием QGraphicsDropShadowEffect
        text_shadow = QGraphicsDropShadowEffect()
        text_shadow.setBlurRadius(4)
        text_shadow.setColor(QColor(0, 0, 0, 200))
        text_shadow.setOffset(0, 1)
        self.disk_space_bar.setGraphicsEffect(text_shadow)
        
        progress_layout.addWidget(self.disk_space_bar)
        status_layout.addWidget(progress_frame, stretch=1)
        
        # Добавляем тень для прогресс-бара
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(6)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 1)
        progress_frame.setGraphicsEffect(shadow)
        
        # Индикатор количества дисков с улучшенным стилем
        disk_count_frame = QFrame()
        disk_count_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {APP_STYLE['card_alt']};
                border-radius: 4px;
                padding: 0px;
            }}
        """)
        disk_count_layout = QHBoxLayout(disk_count_frame)
        disk_count_layout.setContentsMargins(6, 0, 6, 0)
        disk_count_layout.setSpacing(0)
        
        self.disk_count_label = QLabel()
        self.disk_count_label.setStyleSheet(f"""
            QLabel {{
                color: {APP_STYLE['text']};
                font-size: 11px;
                font-weight: 600;
                min-width: 100px;
                max-width: 150px;
                font-family: 'Segoe UI';
                padding: 0px;
            }}
        """)
        disk_count_layout.addWidget(self.disk_count_label)
        status_layout.addWidget(disk_count_frame)
        
        # Индикатор последнего обновления
        self.last_update_label = QLabel()
        self.last_update_label.setStyleSheet(f"""
            QLabel {{
                color: {APP_STYLE['text_secondary']};
                font-size: 11px;
                min-width: 110px;
                max-width: 110px;
                font-family: 'Segoe UI';
                font-style: italic;
                padding-right: 5px;
            }}
        """)
        status_layout.addWidget(self.last_update_label)
        
        # Добавляем виджет в статус бар
        self.statusBar().addPermanentWidget(self.disk_status_widget, 1)  # Растягиваем виджет на всю ширину
        
        # Скрываем стандартную строку сообщений в статус-баре
        self.statusBar().messageChanged.connect(lambda msg: self.statusBar().clearMessage())
        
        # Обновление статус бара каждые 5 секунд
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_bar)
        self.status_timer.start(5000)
        self.update_status_bar()
    
    def update_status_bar(self) -> None:
        """Обновляет информацию в статус баре."""
        try:
            # Получаем статистику использования дисков
            avg_usage, total_partitions, partitions = DiskAnalyzer.get_disk_usage_stats()
            
            # Обновляем информацию о количестве дисков
            disk_count_text = f"Дисков: {len(partitions)}"
            if total_partitions > 0:
                disk_count_text += f" | Разделов: {total_partitions}"
            self.disk_count_label.setText(disk_count_text)
            
            # Обновляем время последнего обновления
            now = datetime.now().strftime("%H:%M:%S")
            self.last_update_label.setText(f"Обновлено: {now}")
            
            # Устанавливаем процент заполнения
            if total_partitions > 0:
                self.disk_space_bar.setValue(int(avg_usage))
                
                # Изменяем цвет индикатора в зависимости от заполненности
                if avg_usage > 90:
                    self.disk_space_bar.setStyleSheet(f"""
                        QProgressBar {{
                            border: none;
                            background-color: {self._with_opacity(APP_STYLE['background'], 0.8)};
                            border-radius: 4px;
                            text-align: center;
                            color: white;
                            font-size: 13px;
                            font-weight: 900;
                        }}
                        QProgressBar::chunk {{
                            background-color: {APP_STYLE['danger']};
                            border-radius: 4px;
                        }}
                    """)
                else:
                    # Для всех других уровней заполнения показываем нормальный статус
                    self.disk_space_bar.setStyleSheet(f"""
                        QProgressBar {{
                            border: none;
                            background-color: {self._with_opacity(APP_STYLE['background'], 0.8)};
                            border-radius: 4px;
                            text-align: center;
                            color: white;
                            font-size: 13px;
                            font-weight: 900;
                        }}
                        QProgressBar::chunk {{
                            background-color: {APP_STYLE['success']};
                            border-radius: 4px;
                        }}
                    """)
        except Exception as e:
            # Логируем ошибку, но не прерываем работу приложения
            print(f"Ошибка при обновлении статус-бара: {str(e)}")
    
    def _format_uptime(self, uptime_seconds: int) -> str:
        """
        Форматирует время работы системы в человекочитаемом формате.
        
        Args:
            uptime_seconds: Время работы в секундах
            
        Returns:
            Строка с форматированным временем работы
        """
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days} д. {hours} ч. {minutes} мин."
        elif hours > 0:
            return f"{hours} ч. {minutes} мин."
        else:
            return f"{minutes} мин. {seconds} сек."
    
    def _with_opacity(self, hex_color: str, opacity: float) -> str:
        """
        Добавляет прозрачность к цвету.
        
        Args:
            hex_color: Цвет в формате HEX
            opacity: Значение прозрачности (0.0 - 1.0)
            
        Returns:
            Цвет с прозрачностью в формате rgba
        """
        color = QColor(hex_color)
        return f"rgba({color.red()}, {color.green()}, {color.blue()}, {opacity})"
    
    def _lighten_color(self, hex_color: str, amount=30) -> str:
        """
        Осветляет цвет.
        
        Args:
            hex_color: Цвет в формате HEX
            amount: Степень осветления
            
        Returns:
            Осветленный цвет в формате HEX
        """
        color = QColor(hex_color)
        return color.lighter(100 + amount).name()
    
    def _darken_color(self, hex_color: str, amount=20) -> str:
        """
        Затемняет цвет.
        
        Args:
            hex_color: Цвет в формате HEX
            amount: Степень затемнения
            
        Returns:
            Затемненный цвет в формате HEX
        """
        color = QColor(hex_color)
        return color.darker(100 + amount).name()
    
    def _format_size(self, bytes: float) -> str:
        """
        Форматирует размер в человекочитаемом формате.
        
        Args:
            bytes: Размер в байтах
            
        Returns:
            Форматированная строка с размером
        """
        if bytes < 1024:
            return f"{bytes:.2f} Б"
        elif bytes < 1024**2:
            return f"{bytes / 1024:.2f} КБ"
        elif bytes < 1024**3:
            return f"{bytes / (1024**2):.2f} МБ"
        else:
            return f"{bytes / (1024**3):.2f} ГБ"

    def _get_health_status_html(self, health_status: dict, disk_type: str) -> str:
        """
        Форматирует HTML-содержимое для отображения состояния диска.
        
        Args:
            health_status: Статус диска
            disk_type: Тип диска
            
        Returns:
            HTML-содержимое для отображения состояния диска
        """
        if not health_status:
            return "Неизвестно"
        
        status_text = health_status.get('status', 'Неизвестно')
        if status_text == 'OK':
            return f"<span style='color: {APP_STYLE['success']};'>{status_text}</span>"
        else:
            return f"<span style='color: {APP_STYLE['danger']};'>{status_text}</span>"

    def _show_error(self, message: str) -> None:
        """
        Показывает сообщение об ошибке.
        
        Args:
            message: Текст сообщения об ошибке
        """
        QMessageBox.warning(self, "Ошибка", message)

    def _update_drives_info(self) -> None:
        """Обновляет информацию о дисках в столбик."""
        try:
            drives_info = []
            for partition in DiskAnalyzer.get_partitions(False):
                try:
                    info = DiskAnalyzer.get_drive_info(partition)
                    
                    if "error" in info:
                        drives_info.append(f"""
                            <div style="margin-bottom: 15px; border: 1px solid {APP_STYLE['danger']}; 
                                 border-radius: 8px; padding: 10px; background-color: rgba(231, 76, 60, 0.1);">
                                <span style="color: {APP_STYLE['danger']}; font-weight: bold; font-size: 14px;">❌ Ошибка:</span> 
                                <span style="font-size: 14px;">{info['error']}</span>
                            </div>
                        """)
                        continue
                        
                    # Форматируем размеры дисков в удобочитаемом формате
                    total_formatted = self._format_size(info['total'])
                    used_formatted = self._format_size(info['used'])
                    free_formatted = self._format_size(info['free'])
                    
                    # Определяем иконку и стиль в зависимости от типа диска
                    if "SSD" in info['type']:
                        icon = "💾"  # Иконка для SSD
                        type_label = "SSD"
                        type_color = APP_STYLE['primary']
                    elif "HDD" in info['type']:
                        icon = "🖴"  # Иконка для HDD
                        type_label = "HDD"
                        type_color = APP_STYLE['secondary']
                    else:
                        icon = "📁"  # Иконка для других типов
                        type_label = info['type'] if info['type'] != "Неизвестный тип" else "Диск"
                        type_color = APP_STYLE['text_secondary']
                        
                    # Цвет для процента заполнения
                    percent_color = APP_STYLE['success']  # Зеленый
                    if info['percent'] > 90:
                        percent_color = APP_STYLE['danger']  # Красный
                        percent_style = "font-weight: bold; animation: pulse 1.5s infinite;"
                    elif info['percent'] > 70:
                        percent_color = APP_STYLE['warning']  # Оранжевый
                        percent_style = "font-weight: bold;"
                    else:
                        percent_style = ""
                    
                    # Определяем статус диска на основе заполненности
                    if info['percent'] > 90:
                        status_message = "Критически мало места"
                        status_color = APP_STYLE['danger']
                    elif info['percent'] > 70:
                        status_message = "Умеренно свободно"
                        status_color = APP_STYLE['warning']
                    elif info['percent'] < 20:
                        status_message = "Много свободного места"
                        status_color = APP_STYLE['success']
                    else:
                        status_message = "Достаточно места"
                        status_color = APP_STYLE['success']
                    
                    # Улучшенный современный дизайн карточки диска
                    drives_info.append(f"""
                        <div style="margin-bottom: 15px; border-radius: 12px; 
                             background-color: {self._with_opacity(APP_STYLE['card'], 0.9)};
                             overflow: hidden;">
                            
                            <!-- Шапка карточки -->
                            <div style="display: flex; justify-content: space-between; align-items: center; 
                                 background: {self._with_opacity(type_color, 0.15)};
                                 padding: 12px 15px; border-bottom: 1px solid {self._with_opacity(type_color, 0.2)};">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <span style="font-size: 22px;">{icon}</span>
                                    <span style="font-size: 16px; font-weight: bold; color: {APP_STYLE['text']};">
                                        {info['mountpoint']}
                                    </span>
                                </div>
                                <div>
                                    <span style="font-size: 12px; color: {type_color}; font-weight: 600; 
                                          padding: 3px 8px; background-color: {self._with_opacity(type_color, 0.15)}; 
                                          border-radius: 12px;">
                                        {type_label} | {info['fstype']}
                                    </span>
                                </div>
                            </div>
                            
                            <!-- Тело карточки -->
                            <div style="padding: 12px 15px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <div style="display: flex; flex-direction: column; gap: 2px;">
                                        <div style="display: flex; align-items: center; gap: 6px;">
                                            <span style="color: {APP_STYLE['text']}; font-weight: 600; font-size: 14px;">{total_formatted}</span>
                                            <span style="color: {APP_STYLE['text_secondary']}; font-size: 12px;">всего</span>
                                        </div>
                                        <div style="display: flex; align-items: center; gap: 6px;">
                                            <span style="color: {APP_STYLE['text']}; font-weight: 600; font-size: 14px;">{free_formatted}</span>
                                            <span style="color: {APP_STYLE['text_secondary']}; font-size: 12px;">свободно</span>
                                        </div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="color: {percent_color}; font-weight: 700; font-size: 24px; {percent_style}">{info['percent']}%</div>
                                        <div style="color: {status_color}; font-size: 12px;">{status_message}</div>
                                    </div>
                                </div>
                                
                                <!-- Прогресс бар с процентом -->
                                <div style="width: 100%; background-color: {self._with_opacity(APP_STYLE['border'], 0.3)}; border-radius: 6px; 
                                          height: 8px; overflow: hidden; margin: 10px 0;">
                                    <div style="width: {info['percent']}%; height: 100%; 
                                         background: linear-gradient(to right, {percent_color}, {self._lighten_color(percent_color, 15)}); 
                                         border-radius: 6px; transition: width 0.5s ease-in-out;">
                                    </div>
                                </div>
                            </div>
                        </div>
                    """)
                except Exception as partition_error:
                    # Пропускаем проблемные разделы и логируем ошибку
                    print(f"Ошибка обработки раздела: {str(partition_error)}")
                    continue

            # Добавляем анимацию для мигающих элементов и эффектов наведения
            animation_css = """
            <style>
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.6; }
                    100% { opacity: 1; }
                }
            </style>
            """
            
            # Обертка с минимальной высотой, чтобы избежать пустого пространства
            if not drives_info:
                # Если нет информации о дисках, показываем сообщение
                drives_info.append(f"""
                    <div style="margin: 20px; text-align: center; color: {APP_STYLE['text_secondary']};">
                        <p>Нет доступных дисков для отображения</p>
                    </div>
                """)
                
            self.drives_text.setHtml(animation_css + '<div style="font-family: Segoe UI, Arial; min-height: 200px; padding: 5px;">' + ''.join(drives_info) + '</div>')
        except Exception as e:
            # Обработка критических ошибок, чтобы приложение не закрылось
            error_message = f"Ошибка при обновлении информации о дисках: {str(e)}"
            self.drives_text.setHtml(f"""
                <div style="font-family: Segoe UI, Arial; padding: 20px; color: {APP_STYLE['danger']};">
                    <h3>Произошла ошибка</h3>
                    <p>{error_message}</p>
                    <p>Попробуйте перезапустить приложение или обратитесь к разработчику.</p>
                </div>
            """)
    
    def show_disk_usage_graph(self) -> None:
        """Отображает график использования дисков."""
        try:
            partitions = DiskAnalyzer.get_partitions(False)
            if not partitions:
                raise ValueError("Не найдено доступных разделов диска")
                
            labels = []
            sizes = []
            colors = []

            for partition in partitions:
                usage = psutil.disk_usage(partition.mountpoint)
                labels.append(f"{partition.device}\n({partition.mountpoint})")
                sizes.append(usage.percent)
                
                # Разные цвета для разных уровней заполнения
                if usage.percent > 90:
                    colors.append(APP_STYLE['danger'])  # Красный
                elif usage.percent > 70:
                    colors.append(APP_STYLE['warning'])  # Оранжевый
                else:
                    colors.append(APP_STYLE['success'])  # Зеленый

            # Создаем фигуру с темной темой
            plt.style.use('dark_background')
            fig = Figure(figsize=(12, 8), facecolor=APP_STYLE['background'])
            ax = fig.add_subplot(111, facecolor=APP_STYLE['background'])
            
            # Гистограмма с градиентной заливкой
            bars = ax.bar(labels, sizes, color=colors, edgecolor='white', linewidth=1, alpha=0.9)
            
            # Добавляем значения на столбцы
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width()/2., 
                    height,
                    f'{height:.1f}%', 
                    ha='center', 
                    va='bottom',
                    color='white',
                    fontsize=11,
                    fontweight='bold'
                )

            # Настройка осей и заголовка
            ax.set_title('Использование дискового пространства', 
                        fontsize=18, color='white', pad=20, fontweight='bold')
            ax.set_xlabel('Диски', fontsize=14, color='white', fontweight='bold')
            ax.set_ylabel('Процент использования (%)', fontsize=14, color='white', fontweight='bold')
            ax.set_ylim(0, 110)  # Немного больше 100 для отображения текста
            
            # Настройка сетки
            ax.grid(True, linestyle='--', alpha=0.2, color='white')
            
            # Настройка цветов меток
            ax.tick_params(axis='x', colors='white', labelsize=10)
            ax.tick_params(axis='y', colors='white', labelsize=10)
            
            # Убираем рамку
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            fig.tight_layout()
            
            self._show_graph_window(fig, "График использования дисков")
            
        except Exception as e:
            self.show_error_report(e, "Построение графика использования дисков")
    
    def _show_graph_window(self, figure: Figure, title: str) -> None:
        """
        Создает окно для отображения графика.
        
        Args:
            figure: Объект графика
            title: Заголовок окна
        """
        window = QMainWindow(self)
        window.setWindowTitle(title)
        window.setMinimumSize(QSize(1000, 800))
        
        # Центральный виджет с темным фоном
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {APP_STYLE['background']};")
        window.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet(f"""
            color: {APP_STYLE['text']};
            padding: 10px;
            background-color: {APP_STYLE['card']};
            border-radius: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Добавляем тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        title_label.setGraphicsEffect(shadow)
        
        layout.addWidget(title_label)
        
        # Контейнер для графика
        graph_frame = QFrame()
        graph_frame.setStyleSheet(f"""
            background-color: {APP_STYLE['card']};
            border-radius: 15px;
            padding: 15px;
        """)
        graph_layout = QVBoxLayout(graph_frame)
        
        # Добавляем тень
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(20)
        shadow2.setColor(QColor(0, 0, 0, 70))
        shadow2.setOffset(0, 5)
        graph_frame.setGraphicsEffect(shadow2)
        
        # Холст для графика
        canvas = FigureCanvas(figure)
        graph_layout.addWidget(canvas)
        
        layout.addWidget(graph_frame, 1)
        
        # Кнопка сохранения
        save_btn = QPushButton("Сохранить график")
        save_btn.setFont(QFont("Segoe UI", 12))
        save_btn.setMinimumHeight(50)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {APP_STYLE['success']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(APP_STYLE['success'], 15)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(APP_STYLE['success'], 15)};
            }}
        """)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(lambda: self._save_figure(figure))
        
        # Добавляем тень
        shadow3 = QGraphicsDropShadowEffect()
        shadow3.setBlurRadius(15)
        shadow3.setColor(QColor(0, 0, 0, 70))
        shadow3.setOffset(0, 3)
        save_btn.setGraphicsEffect(shadow3)
        
        layout.addWidget(save_btn)
        
        window.show()
    
    def _save_figure(self, figure: Figure) -> None:
        """
        Сохраняет график в файл.
        
        Args:
            figure: Объект графика для сохранения
        """
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить график",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        
        if file_name:
            try:
                figure.savefig(file_name, dpi=300, facecolor=figure.get_facecolor())
                QMessageBox.information(self, "Успех", "График успешно сохранен!")
            except Exception as e:
                self.show_error_report(e, "Сохранение графика")
    
    def show_maintenance_tips(self) -> None:
        """Отображает советы по обслуживанию дисков."""
        # Импортируем необходимые классы для создания маски
        from PyQt5.QtGui import QPainterPath
        from PyQt5.QtCore import QRectF
        # QRegion уже импортирован в начале файла из PyQt5.QtGui
        
        # Создаем кастомное окно вместо стандартного диалога
        tips_window = QMainWindow(self)
        tips_window.setWindowTitle("Советы по обслуживанию")
        tips_window.setMinimumSize(700, 500)
        tips_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        tips_window.setAttribute(Qt.WA_TranslucentBackground)  # Делаем фон прозрачным
        
        # Настраиваем центральный виджет с темным фоном
        central_widget = QWidget()
        central_widget.setStyleSheet(f"""
            background-color: {self._darken_color(APP_STYLE['background'], 10)};
            border: 1px solid {self._darken_color(APP_STYLE['background'], 20)};
            border-radius: 15px;  /* Увеличиваем радиус скругления */
        """)
        tips_window.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        
        # Устанавливаем шрифт для корректного отображения кириллицы
        font = QFont("Segoe UI", 11)
        text_browser.setFont(font)
        
        # Стилизуем текстовый браузер
        text_browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {self._darken_color(APP_STYLE['card'], 5)};
                color: {APP_STYLE['text']};
                border: none;
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        # Добавляем тень для улучшения читаемости
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        text_browser.setGraphicsEffect(shadow)
        
        # Содержимое советов
        tips_text = f"""
        <div style="font-family: 'Segoe UI', Arial; font-size: 14px; line-height: 1.7; color: {APP_STYLE['text']};">
            
            <div style="background: linear-gradient(to right, {APP_STYLE['primary']}, {self._lighten_color(APP_STYLE['primary'], 15)}); 
                    border-radius: 10px; padding: 15px; margin-bottom: 20px;">
                <h2 style="margin-top: 0; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">🔹 Для SSD накопителей:</h2>
                <ul style="color: rgba(255, 255, 255, 0.95); margin-bottom: 0; text-shadow: 0px 1px 2px rgba(0,0,0,0.3);">
                    <li>Не заполняйте полностью (оставляйте 10-15% свободного места)</li>
                    <li>Включите TRIM (для Windows: <code style="background-color: rgba(0,0,0,0.3); padding: 3px 6px; border-radius: 4px;">fsutil behavior set DisableDeleteNotify 0</code>)</li>
                    <li>Регулярно обновляйте прошивку накопителя</li>
                    <li>Избегайте частой дефрагментации (это сокращает срок службы)</li>
                    <li>Используйте систему в режиме AHCI в BIOS/UEFI для полной поддержки TRIM</li>
                </ul>
            </div>
            
            <div style="background: linear-gradient(to right, {APP_STYLE['danger']}, {self._lighten_color(APP_STYLE['danger'], 15)}); 
                    border-radius: 10px; padding: 15px; margin-bottom: 20px;">
                <h2 style="margin-top: 0; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">🔹 Для HDD накопителей:</h2>
                <ul style="color: rgba(255, 255, 255, 0.95); margin-bottom: 0; text-shadow: 0px 1px 2px rgba(0,0,0,0.3);">
                    <li>Периодически проверяйте диск на ошибки и выполняйте дефрагментацию</li>
                    <li>Избегайте ударов и вибраций во время работы жесткого диска</li>
                    <li>Контролируйте температуру накопителя (не выше 45°C)</li>
                    <li>Проверяйте жесткий диск на наличие битых секторов</li>
                    <li>Устанавливайте жесткие диски горизонтально для равномерной нагрузки</li>
                </ul>
            </div>
            
            <div style="background: linear-gradient(to right, {APP_STYLE['secondary']}, {self._lighten_color(APP_STYLE['secondary'], 15)}); 
                    border-radius: 10px; padding: 15px; margin-bottom: 20px;">
                <h2 style="margin-top: 0; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">🔹 Для всех накопителей:</h2>
                <ul style="color: rgba(255, 255, 255, 0.95); margin-bottom: 0; text-shadow: 0px 1px 2px rgba(0,0,0,0.3);">
                    <li>Регулярно создавайте резервные копии важных данных</li>
                    <li>Используйте стабилизированное питание или ИБП</li>
                    <li>Проверяйте S.M.A.R.T. статус диска с помощью специализированных утилит</li>
                    <li>Следите за свободным местом (рекомендуется минимум 10-15%)</li>
                    <li>Избегайте резкого отключения питания компьютера</li>
                    <li>Периодически удаляйте временные файлы и очищайте корзину</li>
                </ul>
            </div>
            
            <div style="background: linear-gradient(to right, {APP_STYLE['success']}, {self._lighten_color(APP_STYLE['success'], 15)}); 
                    border-radius: 10px; padding: 15px;">
                <h2 style="margin-top: 0; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">🔹 Программы для обслуживания:</h2>
                <ul style="color: rgba(255, 255, 255, 0.95); margin-bottom: 0; text-shadow: 0px 1px 2px rgba(0,0,0,0.3);">
                    <li><strong>CrystalDiskInfo</strong> - мониторинг S.M.A.R.T. и состояния дисков</li>
                    <li><strong>Victoria</strong> - диагностика и восстановление секторов HDD</li>
                    <li><strong>HDDScan</strong> - тестирование поверхности дисков</li>
                    <li><strong>SSD-Z</strong> - информация о SSD и оценка его состояния</li>
                    <li><strong>Auslogics Disk Defrag</strong> - дефрагментация HDD</li>
                </ul>
            </div>
            <div style="text-align: center; margin-top: 20px; color: {APP_STYLE['text_secondary']}; font-size: 12px;">
            </div>
        </div>
        """
        
        text_browser.setHtml(tips_text)
        layout.addWidget(text_browser)
        
        # Добавляем контейнер для заголовка
        header_container = QWidget()
        header_container.setFixedHeight(40)
        header_container.setStyleSheet(f"""
            background-color: {self._darken_color(APP_STYLE['card'], 10)};
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
        """)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        # Заголовок с иконкой
        title = QLabel("📝 Советы по обслуживанию")
        title.setStyleSheet(f"color: {APP_STYLE['text']}; font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Добавляем кнопку закрытия в верхний правый угол
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {APP_STYLE['text']};
                font-size: 20px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                color: {APP_STYLE['danger']};
            }}
        """)
        close_btn.clicked.connect(tips_window.close)
        header_layout.addWidget(close_btn)
        
        # Добавляем заголовок в основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(header_container)
        
        # Добавляем разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {self._darken_color(APP_STYLE['border'], 20)}; max-height: 1px;")
        main_layout.addWidget(separator)
        
        # Добавляем основной контент
        content_widget = QWidget()
        content_widget.setLayout(layout)
        main_layout.addWidget(content_widget)
        
        # Применяем финальный layout к центральному виджету
        central_widget.setLayout(main_layout)
        
        # Добавляем возможность перетаскивания окна за заголовок
        def mousePressEvent(event):
            if event.button() == Qt.LeftButton:
                tips_window._drag_pos = event.globalPos() - tips_window.frameGeometry().topLeft()
                event.accept()
        
        def mouseMoveEvent(event):
            if event.buttons() == Qt.LeftButton and hasattr(tips_window, '_drag_pos'):
                tips_window.move(event.globalPos() - tips_window._drag_pos)
                event.accept()
        
        # Добавляем возможность закрыть окно двойным щелчком
        def mouseDoubleClickEvent(event):
            if event.button() == Qt.LeftButton:
                tips_window.close()
        
        # Назначаем обработчики событий
        header_container.mousePressEvent = mousePressEvent
        header_container.mouseMoveEvent = mouseMoveEvent
        central_widget.mouseDoubleClickEvent = mouseDoubleClickEvent
        
        # Добавляем эффект тени для всего окна
        window_shadow = QGraphicsDropShadowEffect()
        window_shadow.setBlurRadius(30)
        window_shadow.setColor(QColor(0, 0, 0, 100))
        window_shadow.setOffset(0, 5)
        central_widget.setGraphicsEffect(window_shadow)
        
        # Создаем маску для полного скругления окна
        def applyMask():
            path = QPainterPath()
            path.addRoundedRect(QRectF(central_widget.rect()), 15, 15)
            mask = QRegion(path.toFillPolygon().toPolygon())
            central_widget.setMask(mask)
        
        # Применяем маску и обновляем ее при изменении размера окна
        central_widget.resizeEvent = lambda event: applyMask()
        applyMask()
        
        # Отображаем окно
        tips_window.show()
    
    def show_system_info(self) -> None:
        """Отображает подробную информацию о системе."""
        try:
            # Получаем системную информацию
            sys_info = self.system_info_provider.get_system_info()
            
            # Форматируем информацию в HTML
            uptime_formatted = self._format_uptime(int(time.time() - psutil.boot_time()))
            memory_total = round(sys_info.get("memory_total_gb", 0), 2)
            memory_used = round(psutil.virtual_memory().used / (1024**3), 2)
            memory_percent = psutil.virtual_memory().percent
            
            # Определяем цвет для индикатора памяти
            if memory_percent > 90:
                memory_color = APP_STYLE['danger']
            elif memory_percent > 70:
                memory_color = APP_STYLE['warning']
            else:
                memory_color = APP_STYLE['success']
            
            html_content = f"""
            <div style="font-family: 'Segoe UI', Arial; font-size: 13px; line-height: 1.6; color: {APP_STYLE['text']};">
                <div style="background: linear-gradient(to right, {APP_STYLE['primary']}, {self._lighten_color(APP_STYLE['primary'], 15)}); 
                        border-radius: 10px; padding: 15px; margin-bottom: 20px;">
                    <h2 style="margin-top: 0; color: white; text-align: center;">Информация о системе</h2>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                    <div style="flex: 1; background-color: {APP_STYLE['card']}; border-radius: 10px; padding: 15px; margin-right: 10px;">
                        <h3 style="color: {APP_STYLE['text']}; border-bottom: 1px solid {APP_STYLE['border']}; padding-bottom: 10px;">Операционная система</h3>
                        <p><b>Имя:</b> {sys_info.get('os', 'Неизвестно')}</p>
                        <p><b>Версия:</b> {sys_info.get('version', 'Неизвестно')}</p>
                        <p><b>Архитектура:</b> {sys_info.get('architecture', 'Неизвестно')}</p>
                        <p><b>Время работы:</b> {uptime_formatted}</p>
                    </div>
                    
                    <div style="flex: 1; background-color: {APP_STYLE['card']}; border-radius: 10px; padding: 15px;">
                        <h3 style="color: {APP_STYLE['text']}; border-bottom: 1px solid {APP_STYLE['border']}; padding-bottom: 10px;">Процессор и память</h3>
                        <p><b>Процессор:</b> {sys_info.get('processor', 'Неизвестно')}</p>
                        <p><b>Память (всего):</b> {memory_total} ГБ</p>
                        <p><b>Память (использовано):</b> {memory_used} ГБ ({memory_percent}%)</p>
                        
                        <div style="width: 100%; background-color: rgba(0, 0, 0, 0.2); border-radius: 6px; 
                                  margin: 10px 0; overflow: hidden; height: 16px;">
                            <div style="width: {memory_percent}%; height: 16px; 
                                 background: linear-gradient(to right, {memory_color}, {self._lighten_color(memory_color, 15)}); 
                                 border-radius: 6px;">
                            </div>
                        </div>
                    </div>
                </div>
                
                <div style="background-color: {APP_STYLE['card']}; border-radius: 10px; padding: 15px; margin-bottom: 20px;">
                    <h3 style="color: {APP_STYLE['text']}; border-bottom: 1px solid {APP_STYLE['border']}; padding-bottom: 10px;">Информация о дисках</h3>
                    <p><b>Количество разделов:</b> {sys_info.get('disk_count', 0)}</p>
                    
                    <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                        <thead>
                            <tr>
                                <th style="padding: 8px; border-bottom: 1px solid {APP_STYLE['border']}; text-align: left; color: {APP_STYLE['text_secondary']};">Диск</th>
                                <th style="padding: 8px; border-bottom: 1px solid {APP_STYLE['border']}; text-align: left; color: {APP_STYLE['text_secondary']};">Тип</th>
                                <th style="padding: 8px; border-bottom: 1px solid {APP_STYLE['border']}; text-align: left; color: {APP_STYLE['text_secondary']};">Файловая система</th>
                                <th style="padding: 8px; border-bottom: 1px solid {APP_STYLE['border']}; text-align: right; color: {APP_STYLE['text_secondary']};">Ёмкость</th>
                                <th style="padding: 8px; border-bottom: 1px solid {APP_STYLE['border']}; text-align: right; color: {APP_STYLE['text_secondary']};">Использовано</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            # Добавляем строки с информацией о дисках
            for partition in DiskAnalyzer.get_partitions(False):
                try:
                    info = DiskAnalyzer.get_drive_info(partition)
                    if "error" not in info:
                        drive_type = info['type'] if info['type'] != "Неизвестный тип" else "Не определен"
                        total_formatted = self._format_size(info['total'])
                        used_percent = f"{info['percent']}%"
                        
                        # Цвет для процента заполнения
                        if info['percent'] > 90:
                            percent_color = APP_STYLE['danger']
                        elif info['percent'] > 70:
                            percent_color = APP_STYLE['warning']
                        else:
                            percent_color = APP_STYLE['success']
                        
                        html_content += f"""
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid {self._with_opacity(APP_STYLE['border'], 0.5)}; color: {APP_STYLE['text']};">{info['device']} ({info['mountpoint']})</td>
                                <td style="padding: 8px; border-bottom: 1px solid {self._with_opacity(APP_STYLE['border'], 0.5)}; color: {APP_STYLE['text']};">{drive_type}</td>
                                <td style="padding: 8px; border-bottom: 1px solid {self._with_opacity(APP_STYLE['border'], 0.5)}; color: {APP_STYLE['text']};">{info['fstype']}</td>
                                <td style="padding: 8px; border-bottom: 1px solid {self._with_opacity(APP_STYLE['border'], 0.5)}; color: {APP_STYLE['text']}; text-align: right;">{total_formatted}</td>
                                <td style="padding: 8px; border-bottom: 1px solid {self._with_opacity(APP_STYLE['border'], 0.5)}; color: {percent_color}; text-align: right; font-weight: bold;">{used_percent}</td>
                            </tr>
                        """
                except Exception:
                    continue
            
            html_content += """
                        </tbody>
                    </table>
                </div>
                
                <div style="background-color: {APP_STYLE['card']}; border-radius: 10px; padding: 15px;">
                    <h3 style="color: {APP_STYLE['text']}; border-bottom: 1px solid {APP_STYLE['border']}; padding-bottom: 10px;">Дополнительная информация</h3>
                    <p style="color: {APP_STYLE['text_secondary']}; font-style: italic;">Для получения еще более подробной информации о системе рекомендуем использовать специализированные утилиты.</p>
                </div>
            </div>
            """
            
            # Создаем и показываем окно с информацией
            dialog = self._create_info_window("Информация о системе", html_content)
            dialog.exec_()
            
        except Exception as e:
            self.show_error_report(e, "Отображение информации о системе")

    def show_error_report(self, error: Exception, context: str = "") -> None:
        """
        Показывает подробный отчет об ошибке.
        
        Args:
            error: Объект исключения
            context: Контекст ошибки
        """
        error_details = {
            "title": "Ошибка при выполнении операции",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": error.__class__.__name__,
            "message": str(error),
            "details": traceback.format_exc(),
            "context": context
        }
        
        # Показываем окно с отчетом
        error_window = ErrorReportWindow(error_details, self)
        error_window.show() 