from enum import StrEnum


class Base(StrEnum):
    @classmethod
    def choices(cls):
        return [(tag.value, tag.name.capitalize()) for tag in cls]
