# ui.py — интерфейс, панели, текст

import pygame
from settings import *

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font_small = pygame.font.Font(None, 16)
        self.font_normal = pygame.font.Font(None, 20)
        self.font_big = pygame.font.Font(None, 24)
    
    def draw_top_panel(self, day, resources, zoom, view_mode):
        """Верхняя панель с ресурсами и информацией"""
        panel = pygame.Surface((SCREEN_WIDTH, 32))
        panel.set_alpha(210)
        panel.fill((15, 15, 15))
        self.screen.blit(panel, (0, 0))
        
        # Ресурсы
        res = resources.get_all()
        res_text = f"День {day} | "
        for name, amount in res.items():
            res_text += f"{name}: {int(amount)} | "
        
        text_surface = self.font_small.render(res_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (8, 6))
        
        # Зум и режим справа
        view_names = {VIEW_NORMAL: "Обычный", VIEW_BUILD: "Строительный", VIEW_RESOURCES: "Ресурсы"}
        zoom_text = f"Зум: {int(zoom*100)}% | {view_names.get(view_mode, '?')} (F1/F2/F3)"
        zoom_surface = self.font_small.render(zoom_text, True, (200, 200, 200))
        self.screen.blit(zoom_surface, (SCREEN_WIDTH - 280, 6))
    
    def draw_bottom_panel(self, building_mode, tile_name, tx, ty, zoom):
        """Нижняя панель с подсказками и информацией о тайле"""
        # Фон
        panel = pygame.Surface((SCREEN_WIDTH, 26))
        panel.set_alpha(180)
        panel.fill((15, 15, 15))
        self.screen.blit(panel, (0, SCREEN_HEIGHT - 26))
        
        # Подсказки
        hints = "1-Разрез  2-Лесопилка  3-Времянка  F1/F2/F3-Вид  G-Сетка  R-Новая  ПКМ-Панорама  Колёсико-Зум"
        
        # Адаптируем подсказки под зум
        if zoom < 0.5:
            hints = "Слишком далеко для строительства. Приблизьте карту (колёсико)"
        
        hint_surface = self.font_small.render(hints, True, (160, 160, 160))
        self.screen.blit(hint_surface, (8, SCREEN_HEIGHT - 22))
        
        # Тайл под мышкой
        tile_info = f"[{tx},{ty}] {tile_name}"
        tile_surface = self.font_small.render(tile_info, True, (200, 200, 200))
        self.screen.blit(tile_surface, (SCREEN_WIDTH - 220, SCREEN_HEIGHT - 22))
    
    def draw_building_preview(self, x, y, width, height):
        """Предпросмотр здания перед постройкой"""
        rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, width*TILE_SIZE, height*TILE_SIZE)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)