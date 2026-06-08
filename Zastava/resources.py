# resources.py — хранилище ресурсов

class Resources:
    """Хранилище всех ресурсов города"""
    def __init__(self):
        self.data = {
            "уголь": 100,
            "руда": 50,
            "камень": 80,
            "лес": 60,
            "доски": 20,
            "кирпич": 30,
            "еда": 50,
        }
    
    def has(self, name, amount):
        return self.data.get(name, 0) >= amount
    
    def spend(self, name, amount):
        if self.has(name, amount):
            self.data[name] -= amount
            return True
        return False
    
    def add(self, name, amount):
        self.data[name] = self.data.get(name, 0) + amount
    
    def get(self, name):
        return self.data.get(name, 0)
    
    def get_all(self):
        """Возвращает все ресурсы для отображения"""
        return dict(self.data)