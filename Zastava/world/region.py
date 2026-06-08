# world/region.py — один регион на карте мира

class Region:
    def __init__(self, x, y, biome, climate_zone):
        self.x = x
        self.y = y
        self.biome = biome
        self.climate_zone = climate_zone
        self.resources = []
        self.city = None  # чужой город или None
        self.player_city = False  # True если игрок здесь построился
    
    def get_color(self):
        """Цвет региона на карте мира"""
        colors = {
            'ocean': (40, 80, 160),
            'deep_ocean': (20, 50, 120),
            'arctic': (240, 245, 250),
            'tundra': (200, 210, 180),
            'taiga': (60, 100, 70),
            'forest': (50, 120, 60),
            'plains': (100, 160, 70),
            'steppe': (160, 170, 100),
            'savanna': (180, 180, 100),
            'desert': (210, 190, 140),
            'jungle': (40, 130, 50),
            'mountains': (140, 140, 140),
            'snow': (250, 252, 255),
        }
        return colors.get(self.biome, (100, 100, 100))
    
    def get_info(self):
        """Информация о регионе для отображения"""
        info = f"Биом: {self._biome_name()}\n"
        info += f"Климат: {self._climate_name()}\n"
        if self.resources:
            info += f"Ресурсы: {', '.join(self.resources)}\n"
        if self.city:
            info += f"🏙️ {self.city['name']} (нас. {self.city['population']})\n"
        if self.player_city:
            info += "⭐ ВАШ ГОРОД\n"
        return info
    
    def _biome_name(self):
        names = {
            'ocean': 'Океан', 'deep_ocean': 'Глубокий океан',
            'arctic': 'Арктика', 'tundra': 'Тундра',
            'taiga': 'Тайга', 'forest': 'Лес',
            'plains': 'Равнина', 'steppe': 'Степь',
            'savanna': 'Саванна', 'desert': 'Пустыня',
            'jungle': 'Джунгли', 'mountains': 'Горы', 'snow': 'Снег',
        }
        return names.get(self.biome, self.biome)
    
    def _climate_name(self):
        names = {
            'arctic': 'Арктический', 'subarctic': 'Субарктический',
            'temperate': 'Умеренный', 'subtropical': 'Субтропический',
            'tropical': 'Тропический',
        }
        return names.get(self.climate_zone, self.climate_zone)