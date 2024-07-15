from sqlmodel import SQLModel, Field

class UserBase(SQLModel):
    address: str = Field(primary_key=True, index=True, sa_column_kwargs={"unique": True}, max_length=42)


class User(UserBase, table=True):
    pass
