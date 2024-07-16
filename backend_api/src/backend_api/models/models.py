from sqlmodel import Field, SQLModel


class Model(SQLModel):
    id: int = Field(default=None, primary_key=True)
    