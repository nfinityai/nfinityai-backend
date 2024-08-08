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


class ProviderHardwareEnum(str, Enum):
    CPU = "cpu"
    GPU_A100_LARGE = "gpu-a100-large"
    GPU_A100_LARGE_X2 = "gpu-a100-large-2x"
    GPU_A100_LARGE_X4 = "gpu-a100-large-4x"
    GPU_A100_LARGE_X8 = "gpu-a100-large-8x"
    GPU_A40_LARGE = "gpu-a40-large"
    GPU_A40_LARGE_X2 = "gpu-a40-large-2x"
    GPU_A40_LARGE_X4 = "gpu-a40-large-4x"
    GPU_A40_SMALL = "gpu-a40-small"
    GPU_T4 = "gpu-t4"
    GPU_V100 = "gpu-v100"
    GPU_A40_LARGE_LARGE = "gpu-a40-large"
    GPU_A40_LARGE_SMALL = "gpu-a40-small"

    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_text(cls, text: str | None) -> "ProviderHardwareEnum | None":
        if text is None:
            return None
        if not isinstance(text, str):
            raise ValueError("Expected string for `text`, got `%s` instead." % type(text))
        lower_text = text.lower()
        if "cpu" in lower_text:
            return cls.CPU
        if "a100" in lower_text:
            return cls.GPU_A100_LARGE
        if "t4" in lower_text:
            return cls.GPU_T4
        if "v100" in lower_text:
            return cls.GPU_V100
        if "a40" in lower_text and "large" in lower_text:
            return cls.GPU_A40_LARGE_LARGE
        if "a40" in lower_text and "small" in lower_text:
            return cls.GPU_A40_LARGE_SMALL
        raise ValueError("Invalid value for `provider_hardware` (%s)." % text)
