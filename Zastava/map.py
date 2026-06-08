# map.py — карта, использующая MapGenerator

from settings import *
from map_generator import MapGenerator

class GameMap:
    def __init__(self, seed=None, generator_params=None):
        self.tiles = []
        self.resource_layer = []
        self.buildings = []
        self.seed = seed or __import__('random').randint(0, 1000000)
        self.generator_params = generator_params or {'seed': self.seed, 'width': MAP_WIDTH, 'height': MAP_HEIGHT}
        self.generate()
            
    def generate(self):
        gen = MapGenerator(self.generator_params)
        self.tiles, self.resource_layer = gen.generate()
    
    def get_display_tile(self, x, y, view_mode):
        if view_mode == VIEW_NORMAL:
            tile = self.get_tile(x, y)
            return TILE_COLORS.get(tile, COLOR_GRASS)
        
        elif view_mode == VIEW_BUILD:
            if self.can_build(x, y, 1, 1):
                return (80, 160, 80)
            else:
                tile = self.get_tile(x, y)
                if tile in (TILE_WATER, TILE_MOUNTAIN, TILE_SNOW, TILE_BORDER, TILE_SEA, TILE_SHALLOW):
                    return (180, 60, 60)
                return (100, 100, 100)
        
        elif view_mode == VIEW_RESOURCES:
            resource = self.get_resource(x, y)
            if resource == 'coal':
                return COLOR_COAL
            elif resource == 'iron':
                return COLOR_IRON
            elif resource == 'clay':
                return COLOR_CLAY
            else:
                tile = self.get_tile(x, y)
                if tile == TILE_FERTILE:
                    return COLOR_FERTILE
                return (80, 80, 70)
        
        return COLOR_GRASS
    
    def get_resource(self, x, y):
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            return self.resource_layer[y][x]
        return None
    
    def can_build(self, x, y, width, height):
        for dy in range(height):
            for dx in range(width):
                nx, ny = x + dx, y + dy
                if nx < 0 or nx >= MAP_WIDTH or ny < 0 or ny >= MAP_HEIGHT:
                    return False
                if self.tiles[ny][nx] in (TILE_WATER, TILE_MOUNTAIN, TILE_SNOW, TILE_BORDER, TILE_SEA, TILE_SHALLOW):
                    return False
                for b in self.buildings:
                    if nx >= b.x and nx < b.x + b.width and ny >= b.y and ny < b.y + b.height:
                        return False
        return True
    
    def add_building(self, building, resources):
        if not self.can_build(building.x, building.y, building.width, building.height):
            return False, "Нельзя здесь строить!"
        if hasattr(building, 'cost'):
            for res_name, amount in building.cost.items():
                if not resources.has(res_name, amount):
                    return False, f"Не хватает {res_name}!"
        if hasattr(building, 'cost'):
            for res_name, amount in building.cost.items():
                resources.spend(res_name, amount)
        self.buildings.append(building)
        return True, f"{building.name} построен!"
    
    def get_tile(self, x, y):
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            return self.tiles[y][x]
        return TILE_BORDER
    
    def get_tile_name(self, x, y):
        tile = self.get_tile(x, y)
        name = TILE_NAMES.get(tile, "Неизвестно")
        resource = self.get_resource(x, y)
        if resource:
            res_names = {'coal': 'Уголь', 'iron': 'Руда', 'clay': 'Глина'}
            name += f" ({res_names.get(resource, resource)})"
        return name