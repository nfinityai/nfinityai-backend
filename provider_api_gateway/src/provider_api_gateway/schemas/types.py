from enum import Enum


class ProviderEnum(str, Enum):
    REPLICATE = "replicate"

    def __str__(self):
        return self.value

    def capitalize(self):
        return self.value.capitalize()


class ProviderRunStateEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

    def __str__(self):
        return self.value
