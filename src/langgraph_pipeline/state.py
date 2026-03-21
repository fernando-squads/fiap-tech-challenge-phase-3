from typing import TypedDict, List


class GraphState(TypedDict):
    query: str
    patient_id: str
    patient_data: str
    documents: List[str]
    response: str
    validated_response: str
    final_answer: str