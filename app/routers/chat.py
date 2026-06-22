from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    clinic_id: int
    message: str


@router.post("/")
def chat(request: ChatRequest):
    message = request.message.lower()

    if "ցավ" in message or "ցավում" in message:
        answer = (
            "Եթե ատամը ցավում է, խորհուրդ ենք տալիս գրանցվել բժշկի մոտ։ "
            "Խնդրում եմ նշեք Ձեր անունը և հարմար օրը։"
        )
    elif "գին" in message or "արժե" in message:
        answer = (
            "Գինը կախված է ծառայությունից և բժշկի զննումից։ "
            "Խնդրում եմ նշեք՝ որ ծառայության մասին եք հարցնում։"
        )
    elif "ժամ" in message or "գրանց" in message:
        answer = (
            "Կարող եմ օգնել գրանցվել բժշկի մոտ։ "
            "Խնդրում եմ նշեք Ձեր անունը, հեռախոսահամարը և հարմար օրը։"
        )
    else:
        answer = (
            "Ես ատամնաբուժական կենտրոնի AI օգնականն եմ։ "
            "Կարող եմ օգնել գների, ծառայությունների և գրանցման հարցերով։"
        )

    return {
        "clinic_id": request.clinic_id,
        "answer": answer
    }