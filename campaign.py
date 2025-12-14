# campaign.py
from typing import Dict
from bson import ObjectId

class Campaign:
    def __init__(self, name: str, localized_content: Dict[str, str], liquid_template: str, _id: ObjectId = None):
        self.id = _id or ObjectId()
        self.name = name
        self.localized_content = localized_content
        self.liquid_template = liquid_template

    def to_dict(self):
        return {
            "_id": self.id,
            "name": self.name,
            "localized_content": self.localized_content,
            "liquid_template": self.liquid_template
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            localized_content=data["localized_content"],
            liquid_template=data["liquid_template"],
            _id=data["_id"]
        )