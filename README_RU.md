# Ссылка на диск с программой 
https://disk.yandex.ru/d/rz6UbOeM-8V8LQ
# Диагностика дисков

Приложение для анализа и мониторинга накопителей информации.

## Структура проекта

Проект организован по принципам объектно-ориентированного программирования:

- **main.py** - точка входа в приложение
- **gui.py** - классы графического интерфейса пользователя
- **func_disk.py** - модуль для работы с дисками
- **da.py** - совместимость с предыдущей версией
- **requirements.txt** - список зависимостей

## Функции приложения

- Анализ накопителей и отображение их характеристик
- Построение графиков использования дискового пространства
- Советы по обслуживанию различных типов накопителей
- Отображение системной информации

## Требования

- Python 3.11.x (рекомендуется именно 3.11.9)
- psutil==5.9.0
- matplotlib==3.5.1
- PyQt5==5.15.6

## Важно о совместимости Python!

**Приложение разработано для Python 3.11.x и может некорректно работать на более новых версиях (например, Python 3.13).**

### Решение проблем с запуском:

1. **Установите Python 3.11.9**:
   - Скачайте Python 3.11.9 с [официального сайта](https://www.python.org/downloads/release/python-3119/)
   - При установке отметьте пункт "Add Python to PATH"

2. **Проверьте используемую версию Python**:
   ```bash
   python --version
   ```

3. **Если у вас несколько версий Python**:
   - Windows: используйте команду `py -3.11 -m pip install -r requirements.txt`
   - Linux/MacOS: укажите конкретный путь к Python 3.11

4. **Создайте виртуальное окружение с Python 3.11**:
   ```bash
   # Windows
   py -3.11 -m venv venv311
   venv311\Scripts\activate

   # Linux/MacOS
   python3.11 -m venv venv311
   source venv311/bin/activate
   ```

## Установка и запуск

1. **Установка зависимостей**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Запуск приложения**:
   ```bash
   python main.py
   ```
   
   или
   
   ```bash
   python da.py
   ```

## Создание исполняемого файла

Есть несколько способов создать .exe файл для этого приложения:

### Метод 1: Использование build_exe.py

Этот метод автоматически устанавливает PyInstaller (если не установлен), проверяет зависимости и создает .exe файл.

```bash
python build_exe.py
```

### Метод 2: Использование build_simple.py

Упрощенный вариант сборки с минимальными настройками.

```bash
python build_simple.py
```

### Метод 3: Ручная сборка с использованием spec файла

Если вы хотите более гибкую настройку процесса сборки:

```bash
pyinstaller main.spec
```

## Примечания по сборке

- Для иконки приложения используется файл `Ico.ico`, который должен находиться в директории проекта
- Файл `disk_icon.png` будет автоматически добавлен в ресурсы приложения, если он существует
- Исполняемый файл будет создан в папке `dist`

## Решение распространенных проблем

### EXE-файл не запускается
- Убедитесь, что сборка производилась в Python 3.11.x
- Попробуйте запустить EXE через командную строку для просмотра ошибок
- Измените параметр `console=False` на `console=True` в spec-файле для отображения консоли с ошибками

### Приложение запускается, но не отображает некоторые элементы
- Проверьте, что все зависимости установлены в правильных версиях
- Установите точные версии библиотек: `pip install psutil==5.9.0 matplotlib==3.5.1 PyQt5==5.15.6`

### Проблемы с графиками или интерфейсом
- Некоторые темы рабочего стола могут конфликтовать с PyQt5
- Убедитесь, что у вас установлен полный пакет PyQt5: `pip install PyQt5-tools`

## Известные проблемы

- На некоторых системах могут быть проблемы с отображением графиков. В этом случае рекомендуется запускать приложение из исходного кода.
- Анализ дисков с повышенными правами может потребовать запуска программы от имени администратора. 
