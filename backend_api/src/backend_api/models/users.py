from sqlmodel import SQLModel, Field
from pydantic import field_validator, validate_email

class UserBase(SQLModel):
    wallet_address: str = Field(index=True, sa_column_kwargs={"unique": True}, max_length=42)

class User(UserBase, table=True):
    __tablename__ = "users"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    email: str = Field(index=True, sa_column_kwargs={"unique": True}, nullable=True)

    @field_validator("email")
    @classmethod
    def _validate_email(cls, v: str) -> str:
        validate_email(v)

        return v
