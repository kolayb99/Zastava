# buildings/coal_mine.py — угольный разрез

from . import Building

class CoalMine(Building):
    def __init__(self, x, y):
        super().__init__("Угольный разрез", x, y, width=3, height=2)
        self.max_workers = 5
        self.produces = "уголь"
        self.rate = 3
        self.color = (60, 60, 60)
        self.category = "industry"
        self.cost = {"камень": 20, "доски": 10}
    
    def update(self, city):
        if self.workers > 0:
            produced = self.workers * self.rate / city.ticks_per_day
            city.resources.add("уголь", produced)