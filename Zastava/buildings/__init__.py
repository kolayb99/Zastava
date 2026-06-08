# buildings/__init__.py — базовый класс для всех зданий

class Building:
    """Базовый класс здания"""
    def __init__(self, name, x, y, width=2, height=2):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.workers = 0
        self.max_workers = 5
        self.produces = None
        self.rate = 0
        self.color = (128, 128, 128)
        self.category = "other"
    
    def update(self, city):
        """Обновление производства (вызывается каждый тик)"""
        pass
    
    def get_info(self):
        """Возвращает строку с информацией о здании"""
        return f"{self.name} | Рабочих: {self.workers}/{self.max_workers}"