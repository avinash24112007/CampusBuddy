from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID

class UserContextOut(BaseModel):
    id: UUID
    name: str
    email: str
    avatar: Optional[str] = Field(validation_alias="avatar_url", default=None)
    course: Optional[str] = None
    semester: Optional[int] = None
    dept: Optional[str] = Field(validation_alias="department", default=None)
    collegeId: Optional[str] = Field(validation_alias="college_id", default=None)
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
