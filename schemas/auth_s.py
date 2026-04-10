from pydantic import BaseModel
from typing import Optional


class pyd_login(BaseModel):
    email: str
    password: str

class pyd_register(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = None
    course: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = None
    college_id: Optional[str] = None