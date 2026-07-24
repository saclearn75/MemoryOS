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


from modules.handleSamples import populateDBsWithSamples, clearDBsOfSamples
from modules.relational_db import insertNoteIntoRelDB, retrieveNotesByIds
from modules.vector_db import upsertNoteToVectorDB, searchVectorDB
from modules.datamodels import NoteInternal, SearchQuery, AnalyzeTicketResponse

import modules.classifier as classifier
import modules.extractor as extractor 
import modules.recommendor as recommendor


origins=origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI(root_path=os.getenv("ROOT_PATH",""))
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.post('/populateDBs')
def populateDBs():
    print ('populateDBs: inside func')
    populateDBsWithSamples()

@app.post('/clearDBs')
def clearDBs():
    print ('clearDBs: inside func')    
    clearDBsOfSamples()


@app.post('/processTicket')
def processTicket(note:NoteInternal)->NoteInternal:
    print(f'processTicket: recived {note}')
    insertNoteIntoRelDB(note)
    upsertNoteToVectorDB(note)
    return note

@app.post('/retrieveTickets')
def retrieveTickets(searchQuery:SearchQuery)->list[NoteInternal]:
    print(f'retrieveTickets: received {searchQuery=}')
    listOfIDs=searchVectorDB(searchQuery)
    listOfNotes= retrieveNotesByIds(listOfIDs)

    return listOfNotes

@app.post('/analyzeTicket')
def analyzeTicket(note:NoteInternal):
    print (f'analyzeTicket: {note=} \n')
    classification = classifier.classify_ticket(note.content)
    info = extractor.extract_info(note.content)
    next_steps = recommendor.recommend_next_steps(classification, info)
    print (f'{classification=}')    
    # print (f'{classification=}, \n {info=}, \n {next_steps=}')
    return AnalyzeTicketResponse(
        classification=classification,
        extracted_info=info,
        recommendation=next_steps
    )


# Unit Testing sandbox
if __name__ == '__main__':

    pass
    # mynote = NoteInternal(title='test note 1', content='content 1', tags=['t1', 't11'])
    # insertNoteIntoRelDB(mynote)

    # use UI to test other functions. 


