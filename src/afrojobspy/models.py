from typing import Optional
from pydantic import BaseModel, Field
import uuid

class JobPost(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    company: Optional[str] = "N/A"
    location: Optional[str] = "Ethiopia"
    site_name: str
    job_url: str
    description: Optional[str] = None
    date_posted: Optional[str] = None