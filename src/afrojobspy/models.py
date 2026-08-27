from typing import Optional
from pydantic import BaseModel

class JobPost(BaseModel):
    id: str
    title: str
    company: str
    location: str
    site_name: str
    job_url: str
    description: Optional[str] = None
    date_posted: Optional[str] = None
