from enum import Enum


class ProviderEnum(str, Enum):
    REPLICATE = "replicate"

    def __str__(self):
        return self.value
    
    def as_prefix(self):
        return f"/{self.value}"
    
    def as_tag(self):
        return f"{self.value.capitalize()} Endpoints"


class ProviderRunStateEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

    def __str__(self):
        return self.value
