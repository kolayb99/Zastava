# map_generator.py — генератор карт с настройками

import random
from settings import *

class MapGenerator:
    """Генерирует карту по заданным параметрам"""
    
    def __init__(self, params=None):
        # Параметры по умолчанию
        self.params = {
            'seed': random.randint(0, 1000000),
            'width': MAP_WIDTH,
            'height': MAP_HEIGHT,
            'mountains': 'medium',     # none, low, medium, high
            'forests': 'medium',       # none, low, medium, high
            'rivers': 'medium',        # none, low, medium, high
            'lakes': 'medium',         # none, low, medium, high
            'sea': None,              # None, 'north', 'south', 'east', 'west', 'north_south', 'east_west'
            'sea_size': 0.3,          # доля карты занятая морем (0.1 - 0.5)
            'resources': 'medium',     # poor, medium, rich
        }
        
        if params:
            self.params.update(params)
    
    def generate(self):
        """Генерирует карту и возвращает tiles + resource_layer"""
        random.seed(self.params['seed'])
        
        w = self.params['width']
        h = self.params['height']
        
        # Инициализация
        tiles = []
        resource_layer = []
        for y in range(h):
            tiles.append([TILE_GRASS] * w)
            resource_layer.append([None] * w)
        
        # === МОРЕ ===
        if self.params['sea']:
            self._generate_sea(tiles, w, h)
        
        # === ГОРЫ ===
        if self.params['mountains'] != 'none':
            self._generate_mountains(tiles, w, h)
        
        # === ОЗЁРА ===
        if self.params['lakes'] != 'none':
            self._generate_lakes(tiles, w, h)
        
        # === РЕКИ ===
        if self.params['rivers'] != 'none':
            self._generate_rivers(tiles, w, h)
        
        # === ПЕСОК (по берегам) ===
        self._generate_sand(tiles, w, h)
        
        # === ПЛОДОРОДНАЯ ЗЕМЛЯ (вдоль рек) ===
        self._generate_fertile(tiles, w, h)
        
        # === ЛЕСА ===
        if self.params['forests'] != 'none':
            self._generate_forests(tiles, w, h)
        
        # === РЕСУРСЫ ===
        if self.params['resources'] != 'poor':
            self._generate_resources(tiles, resource_layer, w, h)
        
        # === ГРАНИЦЫ (где нет моря) ===
        self._generate_borders(tiles, w, h)
        
        return tiles, resource_layer
    
    def _get_count(self, level, counts):
        """Переводит уровень в количество"""
        if isinstance(counts, dict):
            return counts.get(level, counts.get('medium', 0))
        return level
    
    def _generate_sea(self, tiles, w, h):
        """Генерирует море с одной или двух сторон"""
        sea_type = self.params['sea']
        sea_ratio = self.params['sea_size']
        
        if sea_type in ('north', 'north_south'):
            sea_depth = int(h * sea_ratio)
            for y in range(sea_depth):
                for x in range(w):
                    if y < sea_depth * 0.3:
                        tiles[y][x] = TILE_SEA
                    elif y < sea_depth * 0.6:
                        tiles[y][x] = TILE_SEA if random.random() < 0.9 else TILE_SHALLOW
                    else:
                        tiles[y][x] = TILE_SHALLOW
                    # Извилистая береговая линия
                    if y == int(sea_depth * 0.8) and random.random() < 0.3:
                        for dx in range(-2, 3):
                            nx = x + dx
                            if 0 <= nx < w:
                                tiles[y][nx] = TILE_SHALLOW
        
        if sea_type in ('south', 'north_south'):
            sea_depth = int(h * sea_ratio)
            for y in range(h - sea_depth, h):
                for x in range(w):
                    dist_from_bottom = h - y
                    if dist_from_bottom < sea_depth * 0.3:
                        tiles[y][x] = TILE_SEA
                    elif dist_from_bottom < sea_depth * 0.6:
                        tiles[y][x] = TILE_SEA if random.random() < 0.9 else TILE_SHALLOW
                    else:
                        tiles[y][x] = TILE_SHALLOW
        
        if sea_type in ('east', 'east_west'):
            sea_depth = int(w * sea_ratio)
            for y in range(h):
                for x in range(w - sea_depth, w):
                    dist_from_edge = w - x
                    if dist_from_edge < sea_depth * 0.3:
                        tiles[y][x] = TILE_SEA
                    elif dist_from_edge < sea_depth * 0.6:
                        tiles[y][x] = TILE_SEA if random.random() < 0.9 else TILE_SHALLOW
                    else:
                        tiles[y][x] = TILE_SHALLOW
        
        if sea_type in ('west', 'east_west'):
            sea_depth = int(w * sea_ratio)
            for y in range(h):
                for x in range(sea_depth):
                    if x < sea_depth * 0.3:
                        tiles[y][x] = TILE_SEA
                    elif x < sea_depth * 0.6:
                        tiles[y][x] = TILE_SEA if random.random() < 0.9 else TILE_SHALLOW
                    else:
                        tiles[y][x] = TILE_SHALLOW
    
    def _generate_mountains(self, tiles, w, h):
        counts = {'low': 2, 'medium': 5, 'high': 8}
        num = self._get_count(self.params['mountains'], counts)
        
        for _ in range(num):
            cx = random.randint(10, w - 10)
            cy = random.randint(10, h - 10)
            rx = random.randint(5, 12)
            ry = random.randint(3, 7)
            
            for y in range(cy - ry, cy + ry + 1):
                for x in range(cx - rx, cx + rx + 1):
                    if 0 <= x < w and 0 <= y < h:
                        if tiles[y][x] in (TILE_GRASS, TILE_FOREST):
                            dx = abs(x - cx) / max(1, rx)
                            dy = abs(y - cy) / max(1, ry)
                            if (dx**2 + dy**2)**0.5 < 1 and random.random() < 0.65:
                                tiles[y][x] = TILE_MOUNTAIN
        
        # Снежные вершины
        for y in range(h):
            for x in range(w):
                if tiles[y][x] == TILE_MOUNTAIN:
                    neighbors = sum(1 for dy in (-1,0,1) for dx in (-1,0,1)
                                  if 0<=x+dx<w and 0<=y+dy<h and tiles[y+dy][x+dx] in (TILE_MOUNTAIN, TILE_SNOW))
                    if neighbors >= 6:
                        tiles[y][x] = TILE_SNOW
    
    def _generate_lakes(self, tiles, w, h):
        counts = {'low': 1, 'medium': 4, 'high': 7}
        num = self._get_count(self.params['lakes'], counts)
        
        for _ in range(num):
            cx = random.randint(5, w - 5)
            cy = random.randint(5, h - 5)
            radius = random.randint(2, 6)
            
            if tiles[cy][cx] in (TILE_MOUNTAIN, TILE_SNOW, TILE_SEA, TILE_SHALLOW):
                continue
            
            for y in range(cy - radius, cy + radius + 1):
                for x in range(cx - radius, cx + radius + 1):
                    if 0 <= x < w and 0 <= y < h:
                        if ((x-cx)**2 + (y-cy)**2)**0.5 < radius:
                            if tiles[y][x] not in (TILE_MOUNTAIN, TILE_SNOW, TILE_SEA):
                                tiles[y][x] = TILE_WATER
    
    def _generate_rivers(self, tiles, w, h):
        counts = {'low': 1, 'medium': 3, 'high': 5}
        num = self._get_count(self.params['rivers'], counts)
        
        for _ in range(num):
            x = random.randint(5, w - 5)
            y = random.randint(5, h - 5)
            
            # Направление к морю если есть
            sea = self.params['sea']
            dir_x = 0
            dir_y = 0
            if sea == 'north':
                dir_y = -1
            elif sea == 'south':
                dir_y = 1
            elif sea == 'east':
                dir_x = 1
            elif sea == 'west':
                dir_x = -1
            else:
                dir_x = 1 if x < w/2 else -1
                dir_y = 1 if y < h/2 else -1
            
            length = random.randint(100, 200)
            for _ in range(length):
                if 0 <= x < w and 0 <= y < h:
                    rw = random.randint(2, 3)
                    for wy in range(-rw, rw+1):
                        for wx in range(-rw, rw+1):
                            nx, ny = x+wx, y+wy
                            if 0<=nx<w and 0<=ny<h:
                                if (wx**2+wy**2)**0.5 <= rw:
                                    if tiles[ny][nx] not in (TILE_MOUNTAIN, TILE_SNOW, TILE_SEA, TILE_SHALLOW):
                                        tiles[ny][nx] = TILE_WATER
                
                if random.random() < 0.1:
                    dir_x += random.choice([-1,0,1])
                    dir_y += random.choice([-1,0,1])
                
                x += dir_x
                y += dir_y
                x = max(1, min(w-2, x))
                y = max(1, min(h-2, y))
    
    def _generate_sand(self, tiles, w, h):
        for y in range(h):
            for x in range(w):
                if tiles[y][x] == TILE_GRASS:
                    water_count = sum(1 for dy in (-1,0,1) for dx in (-1,0,1)
                                    if 0<=x+dx<w and 0<=y+dy<h and tiles[y+dy][x+dx] in (TILE_WATER, TILE_SEA, TILE_SHALLOW))
                    if water_count >= 3:
                        tiles[y][x] = TILE_SAND
                    elif water_count >= 1 and random.random() < 0.5:
                        tiles[y][x] = TILE_SAND
        
        for y in range(h):
            for x in range(w):
                if tiles[y][x] == TILE_GRASS:
                    if any(0<=x+dx<w and 0<=y+dy<h and tiles[y+dy][x+dx]==TILE_SAND for dy in (-1,0,1) for dx in (-1,0,1)):
                        if random.random() < 0.2:
                            tiles[y][x] = TILE_SAND
    
    def _generate_fertile(self, tiles, w, h):
        for y in range(h):
            for x in range(w):
                if tiles[y][x] == TILE_GRASS:
                    if any(0<=x+dx<w and 0<=y+dy<h and tiles[y+dy][x+dx]==TILE_WATER for dy in (-1,0,1) for dx in (-1,0,1)):
                        if random.random() < 0.5:
                            tiles[y][x] = TILE_FERTILE
    
    def _generate_forests(self, tiles, w, h):
        counts = {'low': 15, 'medium': 40, 'high': 70}
        num = self._get_count(self.params['forests'], counts)
        
        for _ in range(num):
            cx = random.randint(3, w-3)
            cy = random.randint(3, h-3)
            if tiles[cy][cx] != TILE_GRASS:
                continue
            
            radius = random.randint(3, 8)
            density = random.uniform(0.3, 0.6)
            
            for y in range(cy-radius, cy+radius+1):
                for x in range(cx-radius, cx+radius+1):
                    if 0<=x<w and 0<=y<h:
                        if tiles[y][x] == TILE_GRASS and random.random() < density:
                            tiles[y][x] = TILE_FOREST
    
    def _generate_resources(self, tiles, resource_layer, w, h):
        multipliers = {'poor': 0.5, 'medium': 1.0, 'rich': 1.5}
        mult = multipliers.get(self.params['resources'], 1.0)
        
        for y in range(h):
            for x in range(w):
                if tiles[y][x] == TILE_MOUNTAIN:
                    if random.random() < 0.3 * mult:
                        resource_layer[y][x] = 'coal'
                    if random.random() < 0.2 * mult:
                        resource_layer[y][x] = 'iron'
                elif tiles[y][x] == TILE_GRASS:
                    if random.random() < 0.08 * mult:
                        resource_layer[y][x] = 'clay'
    
    def _generate_borders(self, tiles, w, h):
        sea = self.params['sea']
        
        for x in range(w):
            if tiles[0][x] not in (TILE_WATER, TILE_SEA, TILE_SHALLOW):
                if sea not in ('north', 'north_south'):
                    tiles[0][x] = TILE_BORDER
            if tiles[h-1][x] not in (TILE_WATER, TILE_SEA, TILE_SHALLOW):
                if sea not in ('south', 'north_south'):
                    tiles[h-1][x] = TILE_BORDER
        
        for y in range(h):
            if tiles[y][0] not in (TILE_WATER, TILE_SEA, TILE_SHALLOW):
                if sea not in ('west', 'east_west'):
                    tiles[y][0] = TILE_BORDER
            if tiles[y][w-1] not in (TILE_WATER, TILE_SEA, TILE_SHALLOW):
                if sea not in ('east', 'east_west'):
                    tiles[y][w-1] = TILE_BORDER