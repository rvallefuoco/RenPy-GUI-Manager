class Location:
    def __init__(self, id_name, name, images=None):
        self.id_name = id_name  # es. "bg camera"
        self.name = name  # es. "Camera da Letto"
        # Lista di dizionari: {"attribute": "day", "path": "images/bg/day.png"}
        self.images = images if images else []

    def to_dict(self):
        return {
            "id_name": self.id_name,
            "name": self.name,
            "images": self.images
        }

    def to_renpy_code(self):
        code = f"# Location: {self.name}\n"
        if not self.images:
            # Fallback se non ci sono immagini
            code += f'# image {self.id_name} = "..."\n'

        for img in self.images:
            # Costruisce: image bg camera day = "path..."
            # Se l'attributo è vuoto (base), non mette lo spazio extra
            attr = f" {img['attribute']}" if img['attribute'] else ""
            code += f'image {self.id_name}{attr} = "{img["path"]}"\n'

        return code

    @classmethod
    def from_dict(cls, data):
        return cls(
            id_name=data.get("id_name", "bg new"),
            name=data.get("name", "Nuovo Luogo"),
            images=data.get("images", [])
        )