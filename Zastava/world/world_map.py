# world/world_map.py — карта мира с правильной генерацией материков

import random
import math
from world.region import Region

class WorldMap:
    def __init__(self, seed=None, width=160, height=120):
        self.seed = seed or random.randint(0, 1000000)
        self.width = width
        self.height = height
        self.regions = {}
        self.cities = []
        self.rivers = []
        self.player_region = None
        self.generate()
    
    def generate(self):
        random.seed(self.seed)
        
        # Шаг 1: Создаём базовую карту высот
        elevation = self._generate_base_terrain()
        
        # Шаг 2: Определяем климат
        climate_zones = self._generate_climate_zones()
        
        # Шаг 3: Генерируем реки
        self.rivers = self._generate_rivers(elevation)
        
        # Шаг 4: Создаём регионы с биомами
        for y in range(self.height):
            for x in range(self.width):
                elev = elevation[y][x]
                climate = climate_zones[y]
                biome = self._get_biome(elev, climate, x, y, elevation)
                
                region = Region(x, y, biome, climate)
                region.resources = self._get_resources(biome, x, y)
                self.regions[(x, y)] = region
        
        # Шаг 5: Чужие города
        self._generate_cities()
    
    def _generate_base_terrain(self):
        """Генерирует высоты: низкие = океан, высокие = горы"""
        elevation = [[0.0] * self.width for _ in range(self.height)]
        
        # Создаём 3-5 континентальных плит
        num_continents = random.randint(3, 5)
        continents = []
        
        for _ in range(num_continents):
            cx = random.uniform(0.15, 0.85) * self.width
            cy = random.uniform(0.15, 0.85) * self.height
            rx = random.uniform(35, 55)
            ry = random.uniform(25, 40)
            height = random.uniform(0.6, 0.95)
            continents.append((cx, cy, rx, ry, height))
        
        # Заполняем карту на основе континентов
        for y in range(self.height):
            for x in range(self.width):
                max_value = 0.0
                
                for cx, cy, rx, ry, height in continents:
                    dx = (x - cx) / rx
                    dy = (y - cy) / ry
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    if dist < 1.0:
                        value = height * (1.0 - dist*dist)
                    elif dist < 1.3:
                        t = (dist - 1.0) / 0.3
                        value = height * (1.0 - 1.0) * (1.0 - t)
                    else:
                        value = 0.0
                    
                    max_value = max(max_value, value)
                
                # Добавляем шум для неровной береговой линии
                noise = self._simple_noise(x * 0.3, y * 0.3, self.seed)
                noise2 = self._simple_noise(x * 0.8 + 10, y * 0.8 + 10, self.seed + 1)
                
                max_value += noise * 0.15 + noise2 * 0.08
                
                # Плавный переход от океана к суше
                if max_value < 0.25:
                    max_value = max_value * 0.7
                elif max_value < 0.45:
                    max_value = 0.25 + (max_value - 0.25) * 1.5
                
                elevation[y][x] = max(0.0, min(1.0, max_value))
        
        return elevation
    
    def _simple_noise(self, x, y, seed):
        """Простой шум на основе синусов с разными частотами"""
        n = math.sin(x * 1.5 + seed * 0.1) * math.cos(y * 2.1 + seed * 0.15)
        n += math.sin(x * 3.7 - y * 2.3 + seed * 0.2) * 0.5
        n += math.sin(x * 7.1 + y * 5.9 + seed * 0.3) * 0.3
        n += math.cos(x * 11.3 - y * 8.7 + seed * 0.4) * 0.2
        return n / 2.0
    
    def _generate_climate_zones(self):
        """Климатические пояса по широте"""
        zones = []
        for y in range(self.height):
            lat = y / self.height
            if lat < 0.08 or lat > 0.92:
                zones.append('arctic')
            elif lat < 0.18 or lat > 0.82:
                zones.append('subarctic')
            elif lat < 0.35 or lat > 0.65:
                zones.append('temperate')
            elif lat < 0.45 or lat > 0.55:
                zones.append('subtropical')
            else:
                zones.append('tropical')
        return zones
    
    def _get_biome(self, elev, climate, x, y, elevation):
        """Определяет биом по высоте и климату"""
        
        # Океан (всё что ниже уровня моря)
        if elev < 0.3:
            return 'deep_ocean' if elev < 0.15 else 'ocean'
        
        # Пляж / побережье
        if elev < 0.35:
            return 'plains'
        
        # Горы
        if elev > 0.75:
            if climate in ('arctic', 'subarctic'):
                return 'snow'
            return 'mountains'
        
        # Холмы
        if elev > 0.6:
            if climate == 'arctic':
                return 'tundra'
            elif climate == 'subarctic':
                return 'taiga'
            elif climate == 'tropical':
                return 'jungle'
            return 'forest'
        
        # Равнины
        if climate == 'arctic':
            return 'arctic'
        elif climate == 'subarctic':
            return 'tundra'
        elif climate == 'temperate':
            r = random.random() * 100 + (x * 7 + y * 13) % 100
            if r < 30:
                return 'forest'
            elif r < 70:
                return 'plains'
            return 'steppe'
        elif climate == 'subtropical':
            r = random.random() * 100 + (x * 3 + y * 17) % 100
            if r < 25:
                return 'desert'
            elif r < 50:
                return 'steppe'
            elif r < 80:
                return 'savanna'
            return 'forest'
        elif climate == 'tropical':
            r = random.random() * 100 + (x * 11 + y * 5) % 100
            if r < 20:
                return 'desert'
            elif r < 45:
                return 'savanna'
            return 'jungle'
        
        return 'plains'
    
    def _generate_rivers(self, elevation):
        """Генерирует реки от гор к океану"""
        rivers = []
        
        # Находим точки с высотой > 0.7 (горы/холмы)
        high_points = []
        for y in range(self.height):
            for x in range(self.width):
                if 0.6 < elevation[y][x] < 0.8:
                    high_points.append((x, y))
        
        if not high_points:
            return rivers
        
        random.shuffle(high_points)
        num_rivers = min(8, len(high_points))
        
        for i in range(num_rivers):
            x, y = high_points[i]
            path = [(x, y)]
            
            for _ in range(150):
                if elevation[y][x] < 0.32:  # достиг воды
                    break
                
                # Ищем куда течь (наименьшая высота)
                best_x, best_y = x, y
                best_elev = elevation[y][x]
                
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if elevation[ny][nx] < best_elev:
                                best_elev = elevation[ny][nx]
                                best_x, best_y = nx, ny
                
                if best_x == x and best_y == y:
                    break
                
                x, y = best_x, best_y
                if (x, y) in path:
                    break
                path.append((x, y))
            
            if len(path) > 10:
                rivers.append(path)
        
        return rivers
    
    def _get_resources(self, biome, x, y):
        """Возвращает ресурсы для биома"""
        r = (x * 7 + y * 13 + self.seed) % 100
        resources = []
        
        if biome == 'mountains':
            if r < 55: resources.append('coal')
            if r < 35: resources.append('iron')
            if r < 20: resources.append('stone')
        elif biome == 'forest':
            if r < 75: resources.append('wood')
            if r < 25: resources.append('stone')
        elif biome == 'taiga':
            if r < 65: resources.append('wood')
            if r < 45: resources.append('coal')
        elif biome in ('plains', 'steppe'):
            if r < 50: resources.append('fertile_land')
            if r < 30: resources.append('clay')
        elif biome == 'savanna':
            if r < 40: resources.append('fertile_land')
            if r < 25: resources.append('oil')
        elif biome == 'jungle':
            if r < 70: resources.append('wood')
            if r < 20: resources.append('oil')
        elif biome == 'desert':
            if r < 35: resources.append('oil')
            if r < 20: resources.append('stone')
        elif biome in ('tundra', 'arctic'):
            if r < 45: resources.append('coal')
            if r < 25: resources.append('oil')
        
        if biome not in ('ocean', 'deep_ocean', 'desert', 'arctic', 'snow'):
            if r < 35:
                resources.append('water')
        
        return resources[:3]
    
    def _generate_cities(self):
        """Создаёт 4-6 чужих городов на суше"""
        land = [(x, y) for (x, y), r in self.regions.items()
               if r.biome not in ('ocean', 'deep_ocean', 'arctic', 'snow', 'mountains', 'desert')]
        
        num = random.randint(4, 6)
        random.shuffle(land)
        
        names = ['Северск', 'Заречный', 'Краснокаменск', 'Приозёрск', 'Белогорск',
                 'Новинск', 'Старый Бор', 'Верхнереченск', 'Солнечный', 'Лесной']
        
        placed = 0
        for x, y in land:
            if placed >= num:
                break
            
            too_close = False
            for city in self.cities:
                if abs(city['x'] - x) < 6 and abs(city['y'] - y) < 6:
                    too_close = True
                    break
            if too_close:
                continue
            
            region = self.regions[(x, y)]
            city = {
                'name': names[placed % len(names)],
                'x': x, 'y': y,
                'population': random.randint(2000, 20000),
                'specialization': random.choice(['mining', 'farming', 'industrial', 'trading']),
            }
            region.city = city
            self.cities.append(city)
            placed += 1
    
    def get_region(self, x, y):
        return self.regions.get((x, y))
    
    def set_player_region(self, x, y):
        if self.player_region:
            old = self.regions.get(self.player_region)
            if old:
                old.player_city = False
        self.player_region = (x, y)
        region = self.regions.get((x, y))
        if region:
            region.player_city = True
    
    def get_available_regions(self):
        available = []
        for region in self.regions.values():
            if region.biome not in ('ocean', 'deep_ocean', 'arctic', 'snow', 'mountains'):
                if region.city is None and not region.player_city:
                    available.append(region)
        return available