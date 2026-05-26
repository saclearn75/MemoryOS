'''
This Module encapsulates helper functions to convert the pydantic models to 
the relational SQLite database. 
The Pydantic models are defined in datamodels.py
'''

import sqlite3
from typing import List

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

from modules.datamodels import NoteInternal
import json

with sqlite3.connect ('notes_rel.db') as connection:
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
    conn = sqlite3.connect("notes_rel.db")
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
    finally:     
        conn.commit()
    conn.close()

def retrieveNoteFromRelDb(note_id: str):
    """
    Fetches notes from SQLite and returns a NoteInternal object.
    Accepts note_id as a string (how it's stored in SQL).
    """
    conn = sqlite3.connect("notes.db")
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
    
    finally:
        conn.close()

def retrieveNotesBatchFromRelDb(note_ids: List[str]) -> List[NoteInternal]:
    """
    Fetches a batch of notes from SQLite using a list of IDs.
    Preserves the order of the input list.
    """
    if not note_ids:
        return []

    conn = sqlite3.connect("notes.db")
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

    finally:
        conn.close()


def deleteNoteFromRelDB(note_uuid: uuid.UUID):
    """
    Deletes a specific note row using its UUID.
    """
    conn = sqlite3.connect("notes.db")
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


def clearDB():
    """
    Removes all rows from the notes table.
    """
    conn = sqlite3.connect("notes.db")
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