'''
This Module encapsulates helper functions to convert the pydantic models to 
the chromadb (vector) database. 
The Pydantic models are defined in datamodels.py
'''


import json
from typing import List
import uuid
import chromadb
from pathlib import Path

try:
    # Works when running via main.py or 'python -m modules.relational_db'
    from modules.datamodels import NoteInternal, SearchQuery
except (ImportError, ModuleNotFoundError):
    # Works when running 'python relational_db.py' directly for unit testing
    from datamodels import NoteInternal


# Define the directory
DB_DIR = Path(__file__).parent / 'databases'

# This line is the magic: it creates the folder if it doesn't exist
# parents=True handles nested folders; exist_ok=True prevents errors if it's already there
DB_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_NAME = DB_DIR/'vector_db'

try:
    client =chromadb.PersistentClient (VECTOR_DB_NAME)
    print(f'[ Global ]: creating collection ')
    collection = client.get_or_create_collection('medical_notes')
except Exception as e:
    print(f' 👿👿😈 [ Global ]: ChromaDB operation failure {e}')


def peekVectorDB(n_results=10):
    res=collection.peek(n_results)
    return res

def upsertNoteToVectorDB(note: NoteInternal):
    """
    Inserts a single note into the collection 
    """
    
    # using this function instead of add() - if a note already exists its update the note
    try:    
        collection.upsert(
            ids=[str(note.id)],
            documents=[note.content],
            metadatas=[{
                "all_tags": note.tags
            }]
        )
        print(f'upsertNoteToVectorDB: successfully upserted note to vector DB {str(note.id)}')
    except Exception as e:
        print(f' 👿👿😈 upsertNoteToVectorDB: ChromaDB operation failure {e}')


def batchUpsertNotes(notes: list[NoteInternal]):
    """
    Efficiently handles a list of NoteInternal objects.
    This function ensures that multiple connections are not needed to insert 
    a large collection of notes
    """
    print(f'\nbatchUpsertNotes: {len(notes)=}')
   
    try: 
        collection.upsert(
            ids=[str(n.id) for n in notes],
            documents=[n.content for n in notes],
            metadatas=[{
                # "all_tags": f"|{'|'.join(n.tags)}|"  # Convert ["tag1", "tag2"] -> "|tag1|tag2|"
                "all_tags": n.tags
            } for n in notes]
        )

    except Exception as e:
        print(f' 👿👿😈 batchUpsertNotes: ChromaDB operation failure {e}')


def searchVectorDB(searchQuery:SearchQuery, n_results=10):
    """
    Handles Text Search, Tag Search, or Hybrid Search.
    """

    # print (peekVectorDB(5))
    # return

    queryText = searchQuery.query_text
    nResults = n_results
    
    print(f'searchVectorDB: {queryText=}, {searchQuery.tags=}')

    # Base filter
    # target_tag = tags[0] if tags and len(tags) > 0 else None

    tagArrLen = len(searchQuery.tags)   #[{"all_tags": {"$contains": f"|{t}|"}} for t in searchQuery.tags]

    # if not tag_conditions:
    #     where_filter = {} 
    # elif len(tag_conditions) == 1:
    #     where_filter = tag_conditions[0]
    # else:
    #     # This ensures Chroma looks for each tag independently 
    #     where_filter = {"$and": tag_conditions}

    if not tagArrLen: where_filter = {}
    elif tagArrLen == 1 : where_filter = {"all_tags":{"$contains" : searchQuery.tags[0] }} 
    else:
        where_filter = {
            "$or" : [   {"all_tags":{"$contains" : searchQuery.tags[i] }}   for i in range(len(searchQuery.tags))    ] 
            }

    print(f'searchVectorDB: {where_filter=}')

    # CASE A: User provided search text (Semantic + Filter)
    if not (queryText and queryText.strip()) and  not tagArrLen:
        print (f'searchVectorDB: Case1: Query text & Tag Array is empty so returning empty list ')
        return []
    
    elif (queryText and queryText.strip()) and not tagArrLen: 
        print (f'searchVectorDB: Case 2: Query text is NOT empty but tag array is so following QUERY Route. ')
        results = collection.query(
            query_texts=[queryText],
            n_results=nResults,
            include=['distances', 'metadatas']
        )
        print(f'vectordb.searchVectorDB: {results=}')
        return results['ids'][0] if results['ids'] else []

    elif (queryText and queryText.strip()) and tagArrLen: 
        print (f'searchVectorDB: Case 3: Query text and tag array are NOT EMPTY so following QUERY Route. ')
        results = collection.query(
            query_texts=[queryText],
            n_results=nResults,
            where=where_filter,
            include=['distances', 'metadatas']
        )

        print(f'vectordb.searchVectorDB: {results=}')
        return results['ids'][0] if results['ids'] else []


    elif not (queryText and queryText.strip()) and tagArrLen:
        print (f'searchVectorDB: 4. Query text IS empty but tag array is not so following GET Route.')
        results = collection.get(
            where=where_filter,
            limit=nResults,
            include=['metadatas'] # get doesn't have 'distances'
        )
        print(f'vectordb.searchVectorDB: {results=}')
        return results['ids'] if results['ids'] else []


def deleteNoteFromVectorDB(note_id):
    """Deletes a single note by its UUID or string ID."""
    try:
        collection.delete(ids=[str(note_id)])
    except Exception as e:
        print(f' 👿👿😈 deleteNoteFromVectorDB: ChromaDB operation failure {e}')
        

def batchDeleteNotes(note_ids: list):
    """Deletes multiple notes at once."""
    try:
        collection.delete(ids=[str(i) for i in note_ids])
    except Exception as e:
        print(f' 👿👿😈 batchDeleteNotes: ChromaDB operation failure {e}')

def clearVectorDB():
    global collection 
    try: 
        # Delete the collection entirely
        client.delete_collection(name="medical_notes")
  

        # Recreate it immediately
        collection = client.get_or_create_collection(name="medical_notes")
    except Exception as e:
        print(f' 👿👿😈 clearVectorDB: ChromaDB operation failure {e}') 