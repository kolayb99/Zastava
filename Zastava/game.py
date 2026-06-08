# game.py — основной класс игры с исправленной сеткой

import pygame
from settings import *
from map import GameMap
from resources import Resources
from buildings.coal_mine import CoalMine
from buildings.sawmill import Sawmill
from buildings.barracks import Barracks
from ui import UI
from logger import log_event
import logging

class Game:
    def __init__(self, world=None, region_coords=None):
        log_event("Инициализация Pygame...")
        pygame.init()
        
        try:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("ЗАСТАВА — Градостроительный симулятор")
        except pygame.error as e:
            logging.error(f"Не удалось создать окно: {e}")
            raise
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.world = world
        
        log_event("Создание локальной карты...")
        
        if region_coords and world:
            region = world.get_region(*region_coords)
            world.set_player_region(*region_coords)
            
            # Определяем с какой стороны море (для прибрежных регионов)
            sea_direction = None
            if region.biome in ('ocean', 'deep_ocean'):
                # Сам регион — вода, ищем ближайшую сушу
                pass
            else:
                # Проверяем соседей — есть ли океан рядом
                for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                    nx, ny = region_coords[0] + dx, region_coords[1] + dy
                    neighbor = world.get_region(nx, ny)
                    if neighbor and neighbor.biome in ('ocean', 'deep_ocean'):
                        if dy == -1: sea_direction = 'north'
                        elif dy == 1: sea_direction = 'south'
                        elif dx == -1: sea_direction = 'west'
                        elif dx == 1: sea_direction = 'east'
                        break
            
            # Параметры для генератора локальной карты
            biome_params = {
                'plains': {'mountains': 'low', 'forests': 'medium', 'rivers': 'medium'},
                'forest': {'mountains': 'low', 'forests': 'high', 'rivers': 'medium'},
                'taiga': {'mountains': 'medium', 'forests': 'high', 'rivers': 'medium'},
                'jungle': {'mountains': 'low', 'forests': 'high', 'rivers': 'high'},
                'steppe': {'mountains': 'low', 'forests': 'low', 'rivers': 'low'},
                'savanna': {'mountains': 'low', 'forests': 'low', 'rivers': 'low'},
                'desert': {'mountains': 'low', 'forests': 'none', 'rivers': 'none'},
                'tundra': {'mountains': 'low', 'forests': 'low', 'rivers': 'low'},
                'mountains': {'mountains': 'high', 'forests': 'medium', 'rivers': 'high'},
            }
            
            biome_config = biome_params.get(region.biome, {'mountains': 'medium', 'forests': 'medium', 'rivers': 'medium'})
            
            resource_level = 'rich' if len(region.resources) >= 3 else 'medium' if region.resources else 'poor'
            
            params = {
                'width': MAP_WIDTH,
                'height': MAP_HEIGHT,
                'seed': world.seed + region_coords[0] * 1000 + region_coords[1],
                'biome': region.biome,
                'climate': region.climate_zone,
                'mountains': biome_config['mountains'],
                'forests': biome_config['forests'],
                'rivers': biome_config['rivers'],
                'lakes': 'medium',
                'sea': sea_direction,
                'sea_size': 0.3 if sea_direction else 0,
                'resources': resource_level,
            }
            
            from map import GameMap
            self.map = GameMap(generator_params=params)
        else:
            from map import GameMap
            self.map = GameMap()
        
        log_event("Инициализация ресурсов...")
        from resources import Resources
        self.resources = Resources()
        
        from ui import UI
        self.ui = UI(self.screen)
        self.ticks_per_day = TICKS_PER_DAY
        
        self.game_tick = 0
        self.day = 1
        
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_tile_x = 0
        self.mouse_tile_y = 0
        self.mouse_screen_x = 0
        self.mouse_screen_y = 0
        
        self.zoom = 1.0
        self.cam_x = 0.0
        self.cam_y = 0.0
        
        self.is_panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.pan_cam_start_x = 0
        self.pan_cam_start_y = 0
        
        self.building_mode = None
        self.view_mode = VIEW_NORMAL
        self.show_grid = True
        
        self.center_camera()
        log_event(f"Локальная карта создана. Биом: {region.biome if region_coords else 'стандартный'}")
    
    def center_camera(self):
        map_pixel_w = MAP_WIDTH * BASE_TILE_SIZE * self.zoom
        map_pixel_h = MAP_HEIGHT * BASE_TILE_SIZE * self.zoom
        self.cam_x = (map_pixel_w - SCREEN_WIDTH) / 2
        self.cam_y = (map_pixel_h - SCREEN_HEIGHT) / 2
    
    def world_to_screen(self, world_x, world_y):
        tile_size = BASE_TILE_SIZE * self.zoom
        screen_x = world_x * tile_size - self.cam_x
        screen_y = world_y * tile_size - self.cam_y
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x, screen_y):
        tile_size = BASE_TILE_SIZE * self.zoom
        world_x = (screen_x + self.cam_x) / tile_size
        world_y = (screen_y + self.cam_y) / tile_size
        return int(world_x), int(world_y)
    
    def run(self):
        log_event("Главный цикл запущен")
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)
        except Exception as e:
            logging.error(f"Ошибка в главном цикле: {e}", exc_info=True)
            raise
        finally:
            log_event("Выход из главного цикла")
            pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            try:
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.MOUSEMOTION:
                    # Берём координаты напрямую из события
                    self.mouse_screen_x = event.pos[0]
                    self.mouse_screen_y = event.pos[1]
                    self.mouse_x = event.pos[0]
                    self.mouse_y = event.pos[1]
                    if self.is_panning:
                        dx = self.mouse_screen_x - self.pan_start_x
                        dy = self.mouse_screen_y - self.pan_start_y
                        self.cam_x = self.pan_cam_start_x - dx
                        self.cam_y = self.pan_cam_start_y - dy
                    self.mouse_tile_x, self.mouse_tile_y = self.screen_to_world(
                        self.mouse_screen_x, self.mouse_screen_y)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Используем event.pos
                    mx, my = event.pos
                    self.mouse_screen_x = mx
                    self.mouse_screen_y = my
                    self.mouse_tile_x, self.mouse_tile_y = self.screen_to_world(mx, my)
                    
                    if event.button == 1 and not self.is_panning:
                        self.handle_click()
                    elif event.button == 2:
                        self.center_camera()
                    elif event.button == 3:
                        self.start_panning()
                    elif event.button == 4:
                        self.zoom_in()
                    elif event.button == 5:
                        self.zoom_out()
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:
                        self.stop_panning()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.building_mode = 'coal_mine'
                    elif event.key == pygame.K_2:
                        self.building_mode = 'sawmill'
                    elif event.key == pygame.K_3:
                        self.building_mode = 'barracks'
                    elif event.key == pygame.K_r:
                        log_event("Генерация новой карты")
                        self.map = GameMap()
                        self.day = 1
                        self.game_tick = 0
                        self.center_camera()
                    elif event.key == pygame.K_ESCAPE:
                        self.building_mode = None
                    elif event.key == pygame.K_F1:
                        self.view_mode = VIEW_NORMAL
                    elif event.key == pygame.K_F2:
                        self.view_mode = VIEW_BUILD
                    elif event.key == pygame.K_F3:
                        self.view_mode = VIEW_RESOURCES
                    elif event.key == pygame.K_g:
                        self.show_grid = not self.show_grid
            except Exception as e:
                logging.warning(f"Ошибка обработки события: {e}")
    
    def start_panning(self):
        self.is_panning = True
        self.pan_start_x = self.mouse_screen_x
        self.pan_start_y = self.mouse_screen_y
        self.pan_cam_start_x = self.cam_x
        self.pan_cam_start_y = self.cam_y
    
    def stop_panning(self):
        self.is_panning = False
    
    def zoom_in(self):
        old_zoom = self.zoom
        self.zoom = min(ZOOM_MAX, self.zoom + ZOOM_STEP)
        if old_zoom != self.zoom:
            ratio = self.zoom / old_zoom
            self.cam_x = (self.cam_x + self.mouse_screen_x) * ratio - self.mouse_screen_x
            self.cam_y = (self.cam_y + self.mouse_screen_y) * ratio - self.mouse_screen_y
    
    def zoom_out(self):
        old_zoom = self.zoom
        self.zoom = max(ZOOM_MIN, self.zoom - ZOOM_STEP)
        if old_zoom != self.zoom:
            ratio = self.zoom / old_zoom
            self.cam_x = (self.cam_x + self.mouse_screen_x) * ratio - self.mouse_screen_x
            self.cam_y = (self.cam_y + self.mouse_screen_y) * ratio - self.mouse_screen_y
    
    def handle_click(self):
        tx, ty = self.mouse_tile_x, self.mouse_tile_y
        try:
            if self.building_mode == 'coal_mine':
                building = CoalMine(tx, ty)
            elif self.building_mode == 'sawmill':
                building = Sawmill(tx, ty)
            elif self.building_mode == 'barracks':
                building = Barracks(tx, ty)
            else:
                return
            success, message = self.map.add_building(building, self.resources)
            print(message)
            log_event(f"Строительство: {message}")
        except Exception as e:
            logging.error(f"Ошибка строительства: {e}")
    
    def update(self):
        try:
            self.game_tick += 1
            if self.game_tick >= self.ticks_per_day:
                self.game_tick = 0
                self.day += 1
            for building in self.map.buildings:
                building.update(self)
            total_workers = sum(b.workers for b in self.map.buildings)
            food_needed = total_workers / self.ticks_per_day
            if self.resources.has("еда", food_needed):
                self.resources.spend("еда", food_needed)
        except Exception as e:
            logging.error(f"Ошибка обновления: {e}")
    
    def draw(self):
        try:
            self.screen.fill((20, 20, 20))
            tile_size = BASE_TILE_SIZE * self.zoom
            
            start_col = max(0, int(self.cam_x / tile_size) - 1)
            start_row = max(0, int(self.cam_y / tile_size) - 1)
            end_col = min(MAP_WIDTH, int((self.cam_x + SCREEN_WIDTH) / tile_size) + 2)
            end_row = min(MAP_HEIGHT, int((self.cam_y + SCREEN_HEIGHT) / tile_size) + 2)
            
            # 1. ОТРИСОВКА ТАЙЛОВ
            for row in range(start_row, end_row):
                for col in range(start_col, end_col):
                    screen_x, screen_y = self.world_to_screen(col, row)
                    color = self.map.get_display_tile(col, row, self.view_mode)
                    rect = pygame.Rect(screen_x, screen_y, max(1, tile_size + 1), max(1, tile_size + 1))
                    pygame.draw.rect(self.screen, color, rect)
            
            # 2. СЕТКА (РИСУЕТСЯ ПОД ЗДАНИЯМИ)
            if self.show_grid:
                self._draw_grid(tile_size, start_col, start_row, end_col, end_row)
            
            # 3. ЗДАНИЯ (ПОВЕРХ СЕТКИ)
            for b in self.map.buildings:
                screen_x, screen_y = self.world_to_screen(b.x, b.y)
                w = max(1, b.width * tile_size)
                h = max(1, b.height * tile_size)
                rect = pygame.Rect(screen_x, screen_y, w, h)
                pygame.draw.rect(self.screen, b.color, rect)
                # Рамка здания (толще при большом зуме)
                border_width = max(1, int(self.zoom * 1.5))
                pygame.draw.rect(self.screen, (0, 0, 0), rect, border_width)
                
                if self.zoom >= 1.0:
                    text = self.ui.font_small.render(b.name[:8], True, (255, 255, 255))
                    self.screen.blit(text, (screen_x + 2, screen_y + 2))
            
            # 4. ПРЕДПРОСМОТР ПОСТРОЙКИ
            if self.building_mode:
                pw, ph = 2, 2
                if self.building_mode == 'coal_mine':
                    pw, ph = 3, 2
                screen_x, screen_y = self.world_to_screen(self.mouse_tile_x, self.mouse_tile_y)
                rect = pygame.Rect(screen_x, screen_y, pw * tile_size, ph * tile_size)
                preview_border = max(1, int(self.zoom * 2))
                pygame.draw.rect(self.screen, (255, 255, 255), rect, preview_border)
            
            # 5. ПОДСВЕТКА ТАЙЛА ПОД МЫШКОЙ
            screen_x, screen_y = self.world_to_screen(self.mouse_tile_x, self.mouse_tile_y)
            rect = pygame.Rect(screen_x, screen_y, max(1, tile_size), max(1, tile_size))
            highlight_border = max(1, int(self.zoom))
            pygame.draw.rect(self.screen, (255, 255, 255), rect, highlight_border)
            
            # 6. ПАНЕЛИ
            tile_name = self.map.get_tile_name(self.mouse_tile_x, self.mouse_tile_y)
            self.ui.draw_top_panel(self.day, self.resources, self.zoom, self.view_mode)
            self.ui.draw_bottom_panel(self.building_mode, tile_name,
                                      self.mouse_tile_x, self.mouse_tile_y, self.zoom)
            
            pygame.display.flip()
        except Exception as e:
            logging.error(f"Ошибка отрисовки: {e}")
    
    def _draw_grid(self, tile_size, start_col, start_row, end_col, end_row):
        """Рисует адаптивную сетку под зданиями"""
        
        # Определяем шаг сетки и прозрачность в зависимости от зума
        if self.zoom >= 3.0:
            grid_step = 5
            alpha = 40
        elif self.zoom >= 1.5:
            grid_step = 10
            alpha = 55
        elif self.zoom >= 0.7:
            grid_step = 20
            alpha = 70
        elif self.zoom >= 0.3:
            grid_step = 50
            alpha = 85
        else:
            grid_step = 100
            alpha = 100
        
        grid_color = (40, 40, 40, alpha)
        
        # Вертикальные линии
        first_col = (start_col // grid_step) * grid_step
        for col in range(first_col, end_col + grid_step, grid_step):
            screen_x, _ = self.world_to_screen(col, 0)
            if 0 <= screen_x <= SCREEN_WIDTH:
                pygame.draw.line(self.screen, grid_color, (screen_x, 0), (screen_x, SCREEN_HEIGHT), 1)
        
        # Горизонтальные линии
        first_row = (start_row // grid_step) * grid_step
        for row in range(first_row, end_row + grid_step, grid_step):
            _, screen_y = self.world_to_screen(0, row)
            if 0 <= screen_y <= SCREEN_HEIGHT:
                pygame.draw.line(self.screen, grid_color, (0, screen_y), (SCREEN_WIDTH, screen_y), 1)
        
        # Координаты (при достаточном зуме)
        if self.zoom >= 0.7:
            font = pygame.font.Font(None, 14)
            coord_color = (150, 150, 150)
            for col in range(first_col, end_col + grid_step, grid_step):
                screen_x, _ = self.world_to_screen(col, 0)
                if 0 <= screen_x <= SCREEN_WIDTH:
                    text = font.render(str(col), True, coord_color)
                    self.screen.blit(text, (screen_x + 2, 30))
            for row in range(first_row, end_row + grid_step, grid_step):
                _, screen_y = self.world_to_screen(0, row)
                if 0 <= screen_y <= SCREEN_HEIGHT:
                    text = font.render(str(row), True, coord_color)
                    self.screen.blit(text, (2, screen_y + 30))