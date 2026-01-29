from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    """
    Base schema class with common configuration for all models.
    Enables ORM mode for database model compatibility.
    """
    model_config = ConfigDict(from_attributes=True) 