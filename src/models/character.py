class Character:
    def __init__(self, id_name, name, color="#ffffff"):
        self.id_name = id_name
        self.name = name
        self.color = color

    def to_dict(self):
        return {
            "id_name": self.id_name,
            "name": self.name,
            "color": self.color
        }
    
    def to_renpy_code(self):
        return f'define {self.id_name} = Character("{self.name}", color="{self.color}")'

    @classmethod
    def from_dict(cls, data):
        return cls(
            id_name=data.get("id_name", "u"),
            name=data.get("name", "Unknown"),
            color=data.get("color", "#ffffff")
        )