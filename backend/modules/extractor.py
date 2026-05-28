import json
from openai import OpenAI

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv (find_dotenv())
api_key=os.getenv("OPENAI_KEY")

client = OpenAI(api_key = api_key)

PEOPLE = [
    "Physician",
    "Nurse",
    "Housekeeping",
    "Intake",
]




def extract_info(ticket_text: str) -> dict:

    prompt = f"""

        Extract the following information from the healthcare incident ticket.

        Fields:
        - event_summary: summarize the incident while preserving the most relevant operational details
        - actions_taken: summarize any actions already taken, if stated
        - patient_harm: briefly state any harm, injury, or patient condition mentioned
        - people_involved: list the non-patient roles involved, using only the allowed role labels
        - uncertainties: list any missing, unclear, or uncertain clinical or operational details mentioned in the ticket

        Rules:
        - event_summary and actions_taken should each be a short single-sentence summary
        - this output is for quick triage, so concise wording is preferred over perfect grammar
        - use only information stated in the ticket
        - for people_involved, if a role is not explicitly named but is strongly implied, map it to the closest allowed role
        - do not invent facts that are not present or strongly implied
        - if a string field has no evidence, return "N/A"
        - if a list field has no evidence, return an empty list

        Ticket:
        {ticket_text}

    """


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
                "name": "extract_info",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "event_summary": {
                            "type": "string",
                        },
                        "actions_taken": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                        "patient_harm": {
                            "type": "string",
                        },
                        "people_involved": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": PEOPLE,
                            },
                        },
                        "uncertainties": {
                            "type": "array",
                            "items": {
                                "type":"string",
                            },
                        },
                    },
                    "required": [
                        "event_summary",
                        "actions_taken",
                        "patient_harm",
                        "people_involved",
                        "uncertainties",
                    ],
                    "additionalProperties": False,
                },
            },
        },
    )

    # print(f'\n{response.output_text=}\n\n')
    return json.loads(response.output_text)


if __name__ == "__main__":
    ticket = (
        "Patient attempted to walk unassisted, fell near bedside, "
        "and was later found to have received the wrong evening medication "
        "due to a charting error. Physician notified. Patient stable."
    )

    result = extract_info(ticket)
    print(json.dumps(result, indent=2))
