# buildings/barracks.py — времянка (жильё)

from . import Building

class Barracks(Building):
    def __init__(self, x, y):
        super().__init__("Времянка", x, y, width=2, height=2)
        self.max_workers = 0  # не производственное
        self.produces = None
        self.rate = 0
        self.color = (160, 140, 100)
        self.category = "housing"
        self.housing = 10  # сколько жителей вмещает
        self.cost = {"доски": 15}
    
    def update(self, city):
        pass  # жильё не производит ресурсы