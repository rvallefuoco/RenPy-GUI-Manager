from src.models.block import Block


class StoryLabel:
    def __init__(self, id_name, blocks=None):
        self.id_name = id_name
        self.blocks = blocks if blocks else []

    def to_dict(self):
        return {
            "id_name": self.id_name,
            "blocks": [b.to_dict() for b in self.blocks]
        }

    def to_renpy(self):
        code = f"label {self.id_name}:\n"
        if not self.blocks:
            code += "    pass\n"
            return code

        for block in self.blocks:
            code += f"    {block.to_renpy()}\n"

        return code

    @classmethod
    def from_dict(cls, data):
        label = cls(data.get("id_name", "new_label"))
        raw_blocks = data.get("blocks", [])
        for b_data in raw_blocks:
            label.blocks.append(Block.from_dict(b_data))
        return label