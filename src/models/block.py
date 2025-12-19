class Block:

    def __init__(self, block_type):
        self.block_type = block_type

    def to_dict(self):
        return {"type": self.block_type}

    def to_renpy(self):
        return "# Generic Block"

    @staticmethod
    def from_dict(data):
        t = data.get("type")
        if t == "dialogue":
            return BlockDialogue.from_dict(data)
        elif t == "scene":
            return BlockScene.from_dict(data)
        return Block("unknown")


class BlockDialogue(Block):
    def __init__(self, char_id, text, expression=""):
        super().__init__("dialogue")
        self.char_id = char_id
        self.text = text
        self.expression = expression

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "char_id": self.char_id,
            "text": self.text,
            "expression": self.expression
        })
        return d

    def to_renpy(self):
        who = self.char_id if self.char_id and self.char_id != "narrator" else ""
        expr = f" {self.expression}" if self.expression and who else ""

        if who:
            return f'{who}{expr} "{self.text}"'
        else:
            return f'"{self.text}"'

    @classmethod
    def from_dict(cls, data):
        return cls(
            char_id=data.get("char_id", ""),
            text=data.get("text", ""),
            expression=data.get("expression", "")
        )


class BlockScene(Block):
    def __init__(self, location_id, variation=""):
        super().__init__("scene")
        self.location_id = location_id
        self.variation = variation

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "location_id": self.location_id,
            "variation": self.variation
        })
        return d

    def to_renpy(self):
        attr = f" {self.variation}" if self.variation else ""
        return f'scene {self.location_id}{attr}'

    @classmethod
    def from_dict(cls, data):
        return cls(
            location_id=data.get("location_id", ""),
            variation=data.get("variation", "")
        )