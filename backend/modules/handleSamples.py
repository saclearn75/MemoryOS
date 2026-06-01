

'''
This module handles population of the relational and vector dbs for testing purposes
Sample tickets are stored in sampletickets.txt
'''
from typing import List
import random
from pathlib import Path
try:
    # Works when running via main.py or 'python -m modules.handleSamples'
    from modules.datamodels import NoteInternal
    from modules.relational_db import insertNotesBatchIntoRelDB, clearRelDB
    from modules.vector_db import batchUpsertNotes, clearVectorDB
    
except (ImportError, ModuleNotFoundError):
    # Works when running 'python handleSamples.py' directly for unit testing
    from datamodels import NoteInternal
    from relational_db import insertNotesBatchIntoRelDB, clearRelDB
    from vector_db import batchUpsertNotes, clearVectorDB


notesSamples : List[NoteInternal]= []


fileName = Path(__file__).parent/'sampletickets.txt'

def createRandomTags():
    '''
    Creates Random tags for testing 
    '''
    
    # this returns a random number  N E (1,6) both inclusive
    numTags=random.randint(1,7)

    # the if clause takes care of the case if the random function above is changed and 0 is a possibility
    arrTagNames = [f"tag {i}" for i in range (1,20)]
    
    # the following shuffles in-place. 
    listOfTags = random.choices(arrTagNames, k=numTags)
    # print (f'createRandomTags: {numTags=}, {listOfTags=}')

    return listOfTags



def readFromSamplesFile():
    '''
    This function simply popylates notesSamples array
    that will then be used to populate dbs
    '''
    global notesSamples
    notesSamples = []
    
    # we use the following method as the usual filename string method messes up
    # when you call this method as part of an POST API route. 
    # This fixes it .. also know that Pathlib overloads teh / Operator to make
    # code reading more intuitive :) 
    MODULE_DIR = Path(__file__).parent
    SAMPLES_FILE = MODULE_DIR / fileName

    try:
        if not SAMPLES_FILE.exists():
            # Helpful error that tells you exactly where it looked
            raise FileNotFoundError(f"readFromSamplesFile: ***  Could not find samples at: {SAMPLES_FILE.absolute()}")

        with open(SAMPLES_FILE, 'r') as f:
            print (f'opened {SAMPLES_FILE} succesfully')
            
            for line in f: 
                cleanline=line.strip() # to account for some weird anomaly where split() does not unpack lists. 
                
                # print (f'assessing line {cleanline}')
                
                # We only want the first occurence. The note is likely to contain text like '..A+ blood type...'
                # so only the first + separates title (also title cannot contain +)
                title, content = cleanline.split('+',1) 

                # print (f'\t {title=}, {content=}')
                arrTags =createRandomTags()
                    
                notesSamples.append(NoteInternal(title=title, content=content, tags=arrTags))
    except Exception as e: 
        print (f"readFromSamplesFile: *** File read issue: {SAMPLES_FILE.absolute()} {e}")
        notesSamples = []
        return 

    print ('readFromSamplesFile: Successfully read in {len(notesSamples)} samples from the file')


def populateDBsWithSamples():
    '''
    this function simply calls 'insert batch' functions for individual dbs
    WARNING - this function clears both databases and leaves only samples. 
    '''
    
    clearRelDB()
    clearVectorDB()

    readFromSamplesFile()

    insertNotesBatchIntoRelDB(notesSamples)
    batchUpsertNotes(notesSamples)


def clearDBsOfSamples():
    '''
    this function simply clears the individual and relational  dbs
    WARNING - this function clears both databases 
    '''
    clearRelDB()
    clearVectorDB()


if __name__ == '__main__':
    readFromSamplesFile()
    
    # notesIds=insertNotesBatchIntoRelDB (notesSamples)
        
    populateDBsWithSamples()

    # print(f'*** Successfully inserted {len(notesIds)} sample notes ***')    

