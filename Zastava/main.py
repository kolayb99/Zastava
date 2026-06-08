# main.py — точка входа с картой мира

import sys
import pygame
from settings import *
from logger import setup_logger, check_required_files

logger = setup_logger()

if not check_required_files():
    input("\nНажмите Enter для выхода...")
    sys.exit(1)

try:
    from ui.world_select import WorldSelectScreen
    from game import Game
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    logger.error(f"Ошибка импорта: {e}")
    input("\nНажмите Enter для выхода...")
    sys.exit(1)

if __name__ == "__main__":
    logger.info("Запуск игры...")
    
    try:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ЗАСТАВА")
        
        # Экран карты мира
        world_screen = WorldSelectScreen(screen)
        selected_region = world_screen.run()
        
        if selected_region:
            logger.info(f"Выбран регион: {selected_region}")
            game = Game(world=world_screen.world, region_coords=selected_region)
            game.run()
        else:
            logger.info("Выход без выбора региона")
        
    except KeyboardInterrupt:
        print("\nИгра прервана.")
        logger.info("Прервано пользователем")
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        logger.info("Игра завершена")
        pygame.quit()
        import logging
        logging.shutdown()