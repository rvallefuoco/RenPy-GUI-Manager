class Character:
    def __init__(self, id_name, name, color="#ffffff", image_tag="", side_images=None):
        self.id_name = id_name
        self.name = name
        self.color = color
        self.image_tag = image_tag  # Es. "eileen"
        self.side_images = side_images if side_images else []  # Lista di {"tag": "happy", "path": "images/e_happy.png"}

    def to_dict(self):
        return {
            "id_name": self.id_name,
            "name": self.name,
            "color": self.color,
            "image_tag": self.image_tag,
            "side_images": self.side_images
        }

    def to_renpy_code(self):
        img_param = f', image="{self.image_tag}"' if self.image_tag else ""
        code = f'define {self.id_name} = Character("{self.name}", color="{self.color}"{img_param})\n'

        if self.image_tag and self.side_images:
            code += "\n"
            for side in self.side_images:
                attr = f" {side['tag']}" if side['tag'] else ""
                code += f'image side {self.image_tag}{attr} = "{side["path"]}"\n'

        return code

    @classmethod
    def from_dict(cls, data):
        return cls(
            id_name=data.get("id_name", "u"),
            name=data.get("name", "Unknown"),
            color=data.get("color", "#ffffff"),
            image_tag=data.get("image_tag", ""),
            side_images=data.get("side_images", [])
        )