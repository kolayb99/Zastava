# ui/world_select.py — экран карты мира и выбора региона

import pygame
from settings import *
from world.world_map import WorldMap

class WorldSelectScreen:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.Font(None, 16)
        self.font_normal = pygame.font.Font(None, 20)
        self.font_big = pygame.font.Font(None, 26)
        
        self.world = WorldMap()
        self.region_size = min(SCREEN_WIDTH // self.world.width, 
                               SCREEN_HEIGHT // self.world.height)
        
        self.hovered_region = None
        self.selected_region = None
        
        # Панорама карты мира
        self.offset_x = 0
        self.offset_y = 0
        self.is_panning = False
        self.pan_start = (0, 0)
    
    def run(self):
        """Возвращает выбранный регион или None"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key == pygame.K_RETURN and self.selected_region:
                        return self.selected_region
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # левая кнопка
                        self._handle_click(event.pos)
                    elif event.button == 3:  # правая — панорама
                        self.is_panning = True
                        self.pan_start = event.pos
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:
                        self.is_panning = False
                
                if event.type == pygame.MOUSEMOTION:
                    if self.is_panning:
                        dx = event.pos[0] - self.pan_start[0]
                        dy = event.pos[1] - self.pan_start[1]
                        self.offset_x += dx
                        self.offset_y += dy
                        self.pan_start = event.pos
                    else:
                        self.hovered_region = self._get_region_at(event.pos)
            
            self._draw()
            self.clock.tick(FPS)
        
        return None
    
    def _get_region_at(self, pos):
        mx, my = pos
        x = (mx - self.offset_x) // self.region_size
        y = (my - self.offset_y) // self.region_size
        if 0 <= x < self.world.width and 0 <= y < self.world.height:
            return (x, y)
        return None
    
    def _handle_click(self, pos):
        region = self._get_region_at(pos)
        if region:
            reg = self.world.get_region(*region)
            if reg and reg.biome not in ('ocean', 'deep_ocean', 'arctic', 'snow', 'mountains'):
                if not reg.city or reg.player_city:
                    self.selected_region = region
    
    def _draw(self):
        self.screen.fill((20, 25, 35))
        
        # Рисуем регионы
        for y in range(self.world.height):
            for x in range(self.world.width):
                region = self.world.get_region(x, y)
                if not region:
                    continue
                
                rx = self.offset_x + x * self.region_size
                ry = self.offset_y + y * self.region_size
                
                color = region.get_color()
                rect = pygame.Rect(rx, ry, self.region_size, self.region_size)
                pygame.draw.rect(self.screen, color, rect)
                
                # Города
                if region.city:
                    city_color = (255, 200, 50) if region.player_city else (255, 100, 100)
                    cx = rx + self.region_size // 2
                    cy = ry + self.region_size // 2
                    pygame.draw.circle(self.screen, city_color, (cx, cy), 
                                     max(2, self.region_size // 3))
                
                # Ресурсы
                if region.resources and self.region_size >= 6:
                    for i, res in enumerate(region.resources[:3]):
                        dot_x = rx + 3 + i * 4
                        dot_y = ry + self.region_size - 4
                        res_colors = {'coal': (60, 50, 40), 'iron': (160, 100, 60),
                                     'oil': (80, 60, 40), 'wood': (40, 100, 30),
                                     'stone': (150, 150, 150), 'water': (80, 150, 220),
                                     'fertile_land': (100, 160, 60), 'clay': (180, 160, 120)}
                        color = res_colors.get(res, (200, 200, 200))
                        pygame.draw.circle(self.screen, color, (dot_x, dot_y), 2)
        
        # === РЕКИ (яркие, заметные) ===
        if self.world.rivers:
            for river in self.world.rivers:
                if len(river) < 2:
                    continue
                points = []
                for rx, ry in river:
                    px = self.offset_x + rx * self.region_size + self.region_size // 2
                    py = self.offset_y + ry * self.region_size + self.region_size // 2
                    points.append((px, py))
                
                if len(points) >= 2:
                    # Широкая тёмная подложка (берега реки)
                    pygame.draw.lines(self.screen, (25, 60, 100), False, points, 
                                    max(3, self.region_size // 2 + 2))
                    # Средняя линия (русло)
                    pygame.draw.lines(self.screen, (40, 120, 200), False, points, 
                                    max(2, self.region_size // 2))
                    # Яркий центр (поток воды)
                    pygame.draw.lines(self.screen, (120, 210, 255), False, points, 
                                    max(1, self.region_size // 6))
                    
                    # Устье реки (кружок в конце)
                    if len(points) >= 2:
                        last_point = points[-1]
                        pygame.draw.circle(self.screen, (40, 120, 200), 
                                         (int(last_point[0]), int(last_point[1])), 
                                         max(3, self.region_size // 3))
                        pygame.draw.circle(self.screen, (120, 210, 255), 
                                         (int(last_point[0]), int(last_point[1])), 
                                         max(1, self.region_size // 6))
    
        
        # Подсветка выбранного региона
        if self.selected_region:
            sx, sy = self.selected_region
            
            # Увеличенная область вокруг выбранного региона
            zoom_factor = 2.5
            zoom_size = int(self.region_size * zoom_factor)
            zx = self.offset_x + sx * self.region_size - (zoom_size - self.region_size) // 2
            zy = self.offset_y + sy * self.region_size - (zoom_size - self.region_size) // 2
            
            # Рамка
            pygame.draw.rect(self.screen, (255, 255, 255), 
                           (zx - 2, zy - 2, zoom_size + 4, zoom_size + 4), 3)
            
            # Информационная панель
            region = self.world.get_region(sx, sy)
            if region:
                info_lines = [
                    f"📍 Регион [{sx}, {sy}]",
                    f"🌍 {region._biome_name()}",
                    f"🌡️ {region._climate_name()}",
                ]
                if region.resources:
                    info_lines.append(f"⛏️ {', '.join(region.resources)}")
                if region.city:
                    info_lines.append(f"🏙️ {region.city['name']} (нас. {region.city['population']})")
                else:
                    info_lines.append("✅ Доступно для строительства")
                
                # Рисуем подложку
                panel_h = len(info_lines) * 18 + 14
                panel_rect = pygame.Rect(10, SCREEN_HEIGHT - panel_h - 10, 280, panel_h)
                pygame.draw.rect(self.screen, (0, 0, 0, 180), panel_rect)
                pygame.draw.rect(self.screen, (100, 100, 100), panel_rect, 1)
                
                # Текст
                for i, line in enumerate(info_lines):
                    text = self.font_small.render(line, True, (255, 255, 255))
                    self.screen.blit(text, (18, SCREEN_HEIGHT - panel_h + 4 + i * 18))
        
        # Подсветка региона под мышкой
        if self.hovered_region and self.hovered_region != self.selected_region:
            hx, hy = self.hovered_region
            rx = self.offset_x + hx * self.region_size
            ry = self.offset_y + hy * self.region_size
            pygame.draw.rect(self.screen, (255, 255, 150), 
                           (rx, ry, self.region_size, self.region_size), 1)
        
        # Заголовок
        title = self.font_big.render("ВЫБЕРИТЕ РЕГИОН ДЛЯ ГОРОДА", True, (255, 220, 80))
        self.screen.blit(title, (SCREEN_WIDTH//2 - 180, 8))
        
        # Подсказка
        hint = self.font_small.render("Клик — выбрать | ENTER — начать | ESC — назад | ПКМ — двигать карту", 
                                      True, (180, 180, 180))
        self.screen.blit(hint, (SCREEN_WIDTH//2 - 260, SCREEN_HEIGHT - 25))
        
        pygame.display.flip()