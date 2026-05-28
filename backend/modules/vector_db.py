'''
This Module encapsulates helper functions to convert the pydantic models to 
the chromadb (vector) database. 
The Pydantic models are defined in datamodels.py
'''


import json
from typing import List
import uuid
import chromadb

try:
    # Works when running via main.py or 'python -m modules.relational_db'
    from modules.datamodels import NoteInternal, SearchQuery
except (ImportError, ModuleNotFoundError):
    # Works when running 'python relational_db.py' directly for unit testing
    from datamodels import NoteInternal


VECTOR_DB_NAME = 'vector_db'

try:
    client =chromadb.PersistentClient (VECTOR_DB_NAME)
except Exception as e: 
    print (f'*** Failed to create or connect to Vector Database {VECTOR_DB_NAME}: e')
    client = None

try:
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
                "all_tags": ", ".join(note.tags),
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
    print(f'batchUpsertNotes: {len(notes)=}')

    try: 
        collection.upsert(
            ids=[str(n.id) for n in notes],
            documents=[n.content for n in notes],
            metadatas=[{
                "all_tags": ", ".join(n.tags),
            } for n in notes]
        )

    except Exception as e:
        print(f' 👿👿😈 batchUpsertNotes: ChromaDB operation failure {e}')


def searchVectorDB(searchQuery:SearchQuery, n_results=10):
    """
    Handles Text Search, Tag Search, or Hybrid Search.
    """

    print(f'vectordb.searchVectorDB: received - {SearchQuery=}')

    queryText = searchQuery.query_text
    tags=        searchQuery.tags
    nResults = 5
    
    print(f'searchVectorDB: {queryText=}, {tags=}')

    # Base filter
    target_tag = tags[0] if tags and len(tags) > 0 else None

    # CASE A: User provided search text (Semantic + Filter)
    if queryText and queryText.strip():
        # Temporary diagnostic
        # peek = collection.get(limit=1)
        # print(f"DEBUG PEEK: ids={peek['ids']}, metadatas={peek['metadatas']}")

        print (f'searchVectorDB: Query text is NOT empty so following QUERY Route. {tags=}')
        where_filter = {"all_tags": {"$eq": target_tag}} if target_tag else None
        print(f'searchVectorDB: {where_filter=}')

        results = collection.query(
            query_texts=[queryText],
            n_results=nResults,
            where=where_filter,
            include=["distances"]
        )

        print(f'vectordb.searchVectorDB: {results=}')
        return results['ids'][0] if results['ids'] else []

    # CASE B: Tag only (No semantic search)
    else:

        # Temporary diagnostic
        # peek = collection.get(limit=1)
        # print(f"DEBUG PEEK: ids={peek['ids']}, metadatas={peek['metadatas']}")

        # print (f'searchVectorDB: Query text IS empty so following GET Route. {tags=}')
        where_filter = {"all_tags": {"$contains": target_tag}} if target_tag else None
        print(f'searchVectorDB: {where_filter=}')

        results = collection.get(
            where=where_filter,
            limit=nResults,
            include=["metadatas"] # get doesn't have 'distances'
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