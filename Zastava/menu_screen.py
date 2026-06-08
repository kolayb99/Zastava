# menu_screen.py — экран генератора карт

import pygame
import random
from settings import *
from map_generator import MapGenerator

class MenuScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ЗАСТАВА — Генератор карт")
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.Font(None, 18)
        self.font_normal = pygame.font.Font(None, 22)
        self.font_big = pygame.font.Font(None, 28)
        
        self.params = {
            'seed': random.randint(0, 1000000),
            'width': MAP_WIDTH,
            'height': MAP_HEIGHT,
            'mountains': 'medium',
            'forests': 'medium',
            'rivers': 'medium',
            'lakes': 'medium',
            'sea': None,
            'sea_size': 0.3,
            'resources': 'medium',
        }
        
        self.preview_surface = None
        self.generate_preview()
    
    def generate_preview(self):
        try:
            gen = MapGenerator(self.params.copy())
            tiles, _ = gen.generate()
            pw, ph = 280, 180
            self.preview_surface = pygame.Surface((pw, ph))
            tile_w = max(1, pw // self.params['width'])
            tile_h = max(1, ph // self.params['height'])
            for y in range(self.params['height']):
                for x in range(self.params['width']):
                    if y < len(tiles) and x < len(tiles[0]):
                        color = TILE_COLORS.get(tiles[y][x], COLOR_GRASS)
                        pygame.draw.rect(self.preview_surface, color,
                                       (x*tile_w, y*tile_h, tile_w+1, tile_h+1))
        except Exception as e:
            print(f"Ошибка предпросмотра: {e}")
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key == pygame.K_RETURN:
                        return 'start'
                    if event.key == pygame.K_SPACE:
                        return 'start'
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        result = self._check_click(event.pos)
                        if result == 'start':
                            return 'start'
            
            self._draw()
            self.clock.tick(FPS)
        return None
    
    def _check_click(self, pos):
        x, y = pos
        
        # Кнопка случайной генерации (y=95)
        if 50 <= x <= 250 and 95 <= y <= 130:
            self._randomize()
            self.generate_preview()
            return None
        
        # Горы (y=160)
        for i in range(4):
            if 180 + i*80 <= x <= 250 + i*80 and 160 <= y <= 182:
                self.params['mountains'] = ['none','low','medium','high'][i]
                self.generate_preview()
                return None
        
        # Леса (y=195)
        for i in range(4):
            if 180 + i*80 <= x <= 250 + i*80 and 195 <= y <= 217:
                self.params['forests'] = ['none','low','medium','high'][i]
                self.generate_preview()
                return None
        
        # Реки (y=230)
        for i in range(4):
            if 180 + i*80 <= x <= 250 + i*80 and 230 <= y <= 252:
                self.params['rivers'] = ['none','low','medium','high'][i]
                self.generate_preview()
                return None
        
        # Озёра (y=265)
        for i in range(4):
            if 180 + i*80 <= x <= 250 + i*80 and 265 <= y <= 287:
                self.params['lakes'] = ['none','low','medium','high'][i]
                self.generate_preview()
                return None
        
        # Ресурсы (y=310)
        for i in range(3):
            if 180 + i*90 <= x <= 260 + i*90 and 310 <= y <= 332:
                self.params['resources'] = ['poor','medium','rich'][i]
                self.generate_preview()
                return None
        
        # Море (y=365)
        sea_opts = [(None,'Нет'), ('north','Север'), ('south','Юг'), ('east','Восток'), ('west','Запад')]
        for i, (val, _) in enumerate(sea_opts):
            if 180 + i*85 <= x <= 255 + i*85 and 365 <= y <= 387:
                self.params['sea'] = val
                self.generate_preview()
                return None
        
        # КНОПКА "НАЧАТЬ ИГРУ" (внизу)
        btn_x = SCREEN_WIDTH // 2 - 130
        btn_y = SCREEN_HEIGHT - 70
        if btn_x <= x <= btn_x + 260 and btn_y <= y <= btn_y + 45:
            return 'start'
        
        return None
    
    def _randomize(self):
        self.params['seed'] = random.randint(0, 1000000)
        self.params['mountains'] = random.choice(['none','low','medium','high'])
        self.params['forests'] = random.choice(['none','low','medium','high'])
        self.params['rivers'] = random.choice(['none','low','medium','high'])
        self.params['lakes'] = random.choice(['none','low','medium','high'])
        self.params['resources'] = random.choice(['poor','medium','rich'])
        self.params['sea'] = random.choice([None, 'north', 'south', 'east', 'west'])
        self.params['sea_size'] = random.uniform(0.2, 0.4)
    
    def _draw_button(self, text, x, y, w, h, active=False):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered = (x <= mouse_x <= x + w and y <= mouse_y <= y + h)
        
        rect = pygame.Rect(x, y, w, h)
        if hovered:
            bg_color = (120, 160, 100)
            border_color = (255, 255, 200)
        elif active:
            bg_color = (100, 140, 80)
            border_color = (200, 200, 200)
        else:
            bg_color = (70, 70, 70)
            border_color = (150, 150, 150)
        
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=5)
        pygame.draw.rect(self.screen, border_color, rect, 1, border_radius=5)
        
        text_surf = self.font_small.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def _draw(self):
        self.screen.fill((25, 25, 30))
        
        # Заголовок
        title = self.font_big.render("ЗАСТАВА — Генератор карт", True, (255, 200, 60))
        self.screen.blit(title, (SCREEN_WIDTH//2 - 150, 15))
        
        # Информация
        y = 55
        info = [
            f"Seed: {self.params['seed']}  |  Размер: {self.params['width']}×{self.params['height']}",
            f"Море: {self.params['sea'] or 'Нет'} ({int(self.params['sea_size']*100)}%)  |  Ресурсы: {self.params['resources']}",
        ]
        for line in info:
            text = self.font_small.render(line, True, (180, 180, 180))
            self.screen.blit(text, (30, y))
            y += 20
        
        # Кнопка случайной генерации
        rand_btn = pygame.Rect(50, 95, 200, 35)
        pygame.draw.rect(self.screen, (80, 60, 40), rand_btn, border_radius=8)
        rand_text = self.font_normal.render("🎲 Случайно", True, (255, 255, 255))
        rand_rect = rand_text.get_rect(center=rand_btn.center)
        self.screen.blit(rand_text, rand_rect)
        
        # Настройки (начинаем с y=160)
        y = 160
        labels = ['Горы:', 'Леса:', 'Реки:', 'Озёра:']
        keys = ['mountains', 'forests', 'rivers', 'lakes']
        level_names = ['Нет', 'Мало', 'Средне', 'Много']
        
        for label, key in zip(labels, keys):
            text = self.font_normal.render(label, True, (200, 200, 200))
            self.screen.blit(text, (30, y))
            current_val = self.params[key]
            for i, lname in enumerate(level_names):
                active = (['none','low','medium','high'][i] == current_val)
                self._draw_button(lname, 180 + i*80, y-2, 70, 22, active)
            y += 35  # каждая следующая группа на 35 пикселей ниже
        
        # Ресурсы (y=310)
        text = self.font_normal.render("Ресурсы:", True, (200, 200, 200))
        self.screen.blit(text, (30, y))
        res_names = ['Бедные', 'Средние', 'Богатые']
        for i, rname in enumerate(res_names):
            active = (['poor','medium','rich'][i] == self.params['resources'])
            self._draw_button(rname, 180 + i*90, y-2, 80, 22, active)
        y += 55
        
        # Море (y=365)
        text = self.font_normal.render("Море:", True, (200, 200, 200))
        self.screen.blit(text, (30, y))
        sea_opts = [('Нет', None), ('Север', 'north'), ('Юг', 'south'), ('Восток', 'east'), ('Запад', 'west')]
        for i, (sname, sval) in enumerate(sea_opts):
            active = (sval == self.params['sea'])
            self._draw_button(sname, 180 + i*85, y-2, 75, 22, active)
        
        # Предпросмотр
        if self.preview_surface:
            prev_x = SCREEN_WIDTH - 320
            prev_y = 80
            self.screen.blit(self.preview_surface, (prev_x, prev_y))
            pygame.draw.rect(self.screen, (100, 100, 100), (prev_x-1, prev_y-1, 282, 182), 1)
        
        # Кнопка НАЧАТЬ ИГРУ
        btn_x = SCREEN_WIDTH // 2 - 130
        btn_y = SCREEN_HEIGHT - 70
        
        pygame.draw.rect(self.screen, (20, 20, 25), (0, btn_y-10, SCREEN_WIDTH, 85))
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered = (btn_x <= mouse_x <= btn_x + 260 and btn_y <= mouse_y <= btn_y + 45)
        
        btn_rect = pygame.Rect(btn_x, btn_y, 260, 45)
        bg_color = (80, 180, 80) if hovered else (40, 140, 40)
        pygame.draw.rect(self.screen, bg_color, btn_rect, border_radius=12)
        border_color = (200, 255, 200) if hovered else (100, 200, 100)
        pygame.draw.rect(self.screen, border_color, btn_rect, 3, border_radius=12)
        
        btn_text = self.font_big.render("✅ НАЧАТЬ ИГРУ", True, (255, 255, 255))
        btn_text_rect = btn_text.get_rect(center=btn_rect.center)
        self.screen.blit(btn_text, btn_text_rect)
        
        hint = self.font_small.render("ENTER / ПРОБЕЛ / КЛИК — начать | ESC — выход", True, (160, 160, 160))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH//2, btn_y + 60))
        self.screen.blit(hint, hint_rect)
        
        pygame.display.flip()