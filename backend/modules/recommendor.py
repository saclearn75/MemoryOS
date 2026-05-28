import json
from openai import OpenAI

from dotenv import load_dotenv, find_dotenv
import os



load_dotenv (find_dotenv())
api_key=os.getenv("OPENAI_KEY")

client = OpenAI(api_key = api_key)

PRIORITY= [
    "Low",
    "Medium",
    "High",
]

PEOPLE = [
    "Physician",
    "Nurse",
    "Housekeeping",
    "Intake",
]

def recommend_next_steps(classification:dict, info: dict) -> dict:

    prompt = f'''

        You are a healthcare operations assistant.

        Based on the incident classification and extracted details, recommend appropriate next steps.

        Inputs:
        - Classification : (Description: type, severity){classification}
        - Extracted details (Description: summary, actions taken, patient condition) {info}

        Output:
        - recommended_actions: list of short, actionable steps
        - priority: low, medium, or high
        - escalation_target: who should be notified next
        - rationale: brief explanation

        Rules:
        - Focus on operational actions, not medical diagnosis
        - Do not repeat actions already taken unless critical
        - If patient harm is present or severity is high, recommend escalation
        - Keep actions concise and practical
    
    '''
    
    response = client.responses.create(
    
        model="gpt-4o",
        input=[
            {
                "role": "system",
                "content": (
                    "You extract relevant information from the healthcare record. "
                    "Return exactly the requested JSON structure."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "recommend_next_steps",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "recommended_actions": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                        "priority": {
                            "type": "string",
                            "enum": PRIORITY,
                        },
                        "escalation_target": {
                            "type": "string",
                            "enum":PEOPLE,
                        },
                        "rationale": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "recommended_actions",
                        "priority",
                        "escalation_target",
                        "rationale",
                    ],
                    "additionalProperties": False,
                },
            },
        },
    )

    # print(f'\n{response.output_text=}\n\n')
    return json.loads(response.output_text)



   




if __name__ == "__main__":

    import classifier 
    import extractor    
    
    ticket = (
        "Patient attempted to walk unassisted, fell near bedside, "
        "and was later found to have received the wrong evening medication "
        "due to a charting error. Physician notified. Patient stable."
    )
    json_classification = classifier.classify_ticket(ticket)
    json_info = extractor.extract_info(ticket)    

    json_next_steps = recommend_next_steps(json_classification, json_info)
    
    print(json.dumps(json_next_steps,indent = 3))