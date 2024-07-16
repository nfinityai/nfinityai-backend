from sqlmodel import SQLModel, Field

class UserBase(SQLModel):
    address: str = Field(index=True, sa_column_kwargs={"unique": True}, max_length=42)


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
