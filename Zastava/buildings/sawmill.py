# buildings/sawmill.py — лесопилка

from . import Building

class Sawmill(Building):
    def __init__(self, x, y):
        super().__init__("Лесопилка", x, y, width=2, height=2)
        self.max_workers = 3
        self.produces = "доски"
        self.rate = 2
        self.color = (139, 90, 43)
        self.category = "industry"
        self.cost = {"камень": 10, "доски": 15}
    
    def update(self, city):
        if self.workers > 0:
            wood_needed = self.workers * 3 / city.ticks_per_day
            if city.resources.has("лес", wood_needed):
                city.resources.spend("лес", wood_needed)
                produced = self.workers * self.rate / city.ticks_per_day
                city.resources.add("доски", produced)