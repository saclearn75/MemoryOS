from pydantic import BaseModel, Field
from typing import Any
from  datetime import datetime
import uuid


# Class Note is used to ingest data from the React App
class Note (BaseModel):
    title :str
    content: str
    tags: list[str]


# Class NoteInternal is used to create some unique metadata to identify the note -
#   id - uuid to serve as primary key in the dbs
#   create_at - note created at
class NoteInternal(Note):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.now)    


class SearchQuery(BaseModel):
    query_text:str = None
    tags:list[str] = []