from pydantic import BaseModel


class pyd_login(BaseModel):
    email: str

    password: str