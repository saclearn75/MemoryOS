'''
This Module encapsulates helper functions to convert the pydantic models to 
the relational SQLite database. 
The Pydantic models are defined in datamodels.py
'''

import sqlite3
from typing import List
import uuid

# learning: if running from main.py, '.' (ie backend ) is added to syspath so 
# importing this module looks for datamodels within backend/modules. 
# thats why we need an 'explicit' import below 
# for unit testing, cd to backend and run ' python -m modules.relational_db '
# or  add the following codeblock 

# try:
#     # Works when running via main.py or 'python -m modules.relational_db'
#     from modules import datamodels
# except (ImportError, ModuleNotFoundError):
#     # Works when running 'python relational_db.py' directly for unit testing
#     import datamodels

try:
    # Works when running via main.py or 'python -m modules.relational_db'
    from modules.datamodels import NoteInternal
except (ImportError, ModuleNotFoundError):
    # Works when running 'python relational_db.py' directly for unit testing
    from datamodels import NoteInternal


import json
from pathlib import Path

MODULE_DIR = Path(__file__).parent
REL_DB_NAME = MODULE_DIR / 'notes_rel.db'

with sqlite3.connect (REL_DB_NAME) as connection:
    cursor = connection.cursor()
    try: 
        cursor.execute (''' 
            CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    title TEXT, 
                    content TEXT NOT NULL,
                    tags TEXT,
                    created_at TEXT
                        )
                    ''')
    except Exception as e:
        print (e)
    

def insertNoteIntoRelDB(noteToInsert: NoteInternal): 

    """
    Inserts a single note in the sqlite db
    """
    conn = sqlite3.connect(REL_DB_NAME)
    cursor = conn.cursor()
  
    try :
        note_dict = noteToInsert.model_dump(mode="json")
    
        # Manually convert list of strings to a string since list[str] not supported in sqlite
        tags_str = json.dumps(note_dict["tags"])
        
        query = """
        INSERT INTO notes (id, title, content, tags, created_at)
        VALUES (?, ?, ?, ?, ?)
        """
        
        cursor.execute(query, (
            note_dict["id"], 
            note_dict["title"], 
            note_dict["content"],
            tags_str,
            note_dict["created_at"]
        ))
        print(f'insertNoteIntoRelDB: successfully inserted note: {str(noteToInsert.id)}')
    finally:     
        conn.commit()
    conn.close()

def retrieveNotesByIds(idList:List[str]) -> List[NoteInternal]:
    '''
    Function takes in an ordered IDs list (from the semantic search 
    and retrieves the notes data from the SQLite Database. 
    
    It presearves the order of the IDs list
    '''
    print(f'retrieveNotesByIds: {idList=} \n')
    if not idList:
        return []
    conn = sqlite3.connect(REL_DB_NAME)
    conn.row_factory = sqlite3.Row  # Enable name-based access
    cursor = conn.cursor()

    # Create placeholders for the WHERE IN clause: (?, ?, ?)
    placeholders = ', '.join(['?'] * len(idList))
    print(f'retrieveNotesByIds: {placeholders=} \n')
    # Build the CASE statement to preserve ChromaDB's order
    # Generates: CASE id WHEN ? THEN 0 WHEN ? THEN 1 ... END
    # Basically the number after THEN is a simple score that is 
    #   then use by ORDER BY to preserve the order
    whenClauses = []
    for i in range(len(idList)):
        whenClauses.append(f"WHEN ? THEN {i}")
    
    orderByCase = f"CASE id {' '.join(whenClauses)} END"
    print(f'retrieveNotesByIds: {orderByCase=} \n')
    
    # Construct the full SQL query
    sql = f"""
        SELECT id, title, tags, created_at, content 
        FROM notes 
        WHERE id IN ({placeholders}) 
        ORDER BY {orderByCase}
    """
    print(f'retrieveNotesByIds: {sql=} \n')

    #Combine params: idList for the WHERE clause + idList for the CASE clause
    params = idList + idList
    orderedNotes = []
    print(f'retrieveNotesByIds: {params=} \n')

    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall() 

        for row in rows:
            data = dict(row)
            data["tags"] = json.loads(data["tags"])
            note = NoteInternal.model_validate(data)
            orderedNotes.append(note)

    except Exception as e: 
        print (f"*** retrieveNotesBatchFromRelDb: Exception while retrieving :{e}")
    finally:
        conn.close()

    print(f'retrieveNotesByIds: {orderedNotes=} \n')

    return orderedNotes



def retrieveNoteFromRelDb(note_id: str):
    """
    Fetches notes from SQLite and returns a NoteInternal object.
    Accepts note_id as a string (how it's stored in SQL).
    """
    conn = sqlite3.connect(REL_DB_NAME)
    conn.row_factory = sqlite3.Row  # Enable name-based access
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        
        if row:
            data = dict(row)
            # Re-parse the tags string into a list
            data["tags"] = json.loads(data["tags"])
            # Reconstruct the Pydantic object
            return NoteInternal.model_validate(data)
        return None
    except Exception as e: 
        print (f"*** retrieveNoteFromRelDb: Exception while retrieving :{e}")
    finally:
        conn.close()


def insertNotesBatchIntoRelDB(notes:List[NoteInternal])->List[str]: 
    """
    WARNING: Clears the db of previously inserted notes
    Inserts a batch of notes into SQLite 
    Primarily used for testing, returns a list of the inserted uuids
    """
  
    if not notes:
        return []

    idsToReturn:List[str] = []

    for eachNote in notes:
        idsToReturn.append(eachNote.id)
        insertNoteIntoRelDB(eachNote)
    

    return idsToReturn


def retrieveNotesBatchFromRelDb(note_ids: List[str]) -> List[NoteInternal]:
    """
    Fetches a batch of notes from SQLite using a list of IDs.
    Preserves the order of the input list.
    """
    if not note_ids:
        return []

    conn = sqlite3.connect(REL_DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Prepare placeholders (?, ?, ?) for the IN clause
    placeholders = ", ".join(["?"] * len(note_ids))
    query = f"SELECT * FROM notes WHERE id IN ({placeholders})"

    try:
        cursor.execute(query, note_ids)
        rows = cursor.fetchall()
        
        # Convert rows to Pydantic objects and store in a dict for easy lookup
        # This makes re-sorting much faster than nested loops.
        notes_map = {}
        for row in rows:
            data = dict(row)
            data["tags"] = json.loads(data["tags"])
            note = NoteInternal.model_validate(data)
            notes_map[str(note.id)] = note

        # We need to re-sort the notes to match the order ChromaDB gave us
        # (Handling the case where a Chroma ID might not exist in SQLite)
        ordered_notes = [notes_map[nid] for nid in note_ids if nid in notes_map]
        
        return ordered_notes
    except Exception as e: 
        print (f"*** retrieveNotesBatchFromRelDb: Exception while retrieving :{e}")
    finally:
        conn.close()


def deleteNoteFromRelDB(note_uuid: uuid.UUID):
    """
    Deletes a specific note row using its UUID.
    """
    conn = sqlite3.connect(REL_DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Convert UUID object to string for the query
        cursor.execute("DELETE FROM notes WHERE id = ?", (str(note_uuid),))
        conn.commit()
        print(f"Successfully deleted note {note_uuid} from Relational DB.")
    except Exception as e:
        print(f"Error deleting note: {e}")
        conn.rollback()
    finally:
        conn.close()


def clearRelDB():
    """
    Removes all rows from the notes table.
    """
    conn = sqlite3.connect(REL_DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM notes")
        conn.commit()
        print("Relational Database cleared.")
    except Exception as e:
        print(f"Error clearing database: {e}")
        conn.rollback()
    finally:
        conn.close()

