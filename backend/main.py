from openai import OpenAI
import json

from pydantic import BaseModel
from typing import Any
import os
from dotenv import load_dotenv, find_dotenv		

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import chromadb
import csv, pprint

from modules.relational_db import insertNoteIntoRelDB
from modules.datamodels import NoteInternal

origins=origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


# Unit Testing sandbox
if __name__ == '__main__':

    mynote = NoteInternal(title='test note 1', content='content 1', tags=['t1', 't11'])
    insertNoteIntoRelDB(mynote)

    # use UI to test other functions. 


