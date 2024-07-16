from enum import Enum


class ProviderEnum(str, Enum):
    REPLICATE = "replicate"

    def __str__(self):
        return self.value

    def capitalize(self):
        return self.value.capitalize()
