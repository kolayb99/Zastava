# logger.py — система логирования и отладки

import logging
import os
import sys
from datetime import datetime

def setup_logger():
    """Настраивает логирование в файл"""
    log_filename = 'zastava.log'
    
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        encoding='utf-8'
    )
    
    # Выводим стартовое сообщение
    logging.info("=" * 50)
    logging.info(f"ЗАСТАВА запущена: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Python: {sys.version}")
    
    return logging.getLogger('zastava')


def check_required_files():
    """Проверяет, все ли файлы на месте"""
    required = [
        'main.py',
        'settings.py', 
        'game.py', 
        'map.py', 
        'resources.py', 
        'logger.py',
        'map_generator.py',
        'buildings/__init__.py',
        'buildings/coal_mine.py',
        'buildings/sawmill.py', 
        'buildings/barracks.py',
        'ui/__init__.py',
        'ui/game_ui.py',
        'ui/world_select.py',
        'world/__init__.py',
        'world/region.py',
        'world/world_map.py',
    ]
    # ... остальное без изменений
    
    missing = []
    for file in required:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print("❌ НЕ НАЙДЕНЫ ФАЙЛЫ:")
        for f in missing:
            print(f"   • {f}")
        print("\nУбедитесь что все файлы находятся в папке Zastava.")
        print("Игра не может быть запущена.")
        logging.error(f"Отсутствуют файлы: {missing}")
        return False
    
    logging.info("Все файлы на месте ✓")
    return True


def safe_call(func, *args, **kwargs):
    """Безопасный вызов функции с обработкой ошибок"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logging.error(f"Ошибка в {func.__name__}: {e}", exc_info=True)
        return None


def log_event(message):
    """Записывает событие в лог"""
    logging.info(message)