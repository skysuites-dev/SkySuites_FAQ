from app.faq_queries import get_answer_by_id

async def handle_question_id(question_id: str) -> dict:
    answer = get_answer_by_id(question_id)
    if answer:
        return {"id": question_id, "answer": answer}
    return {"id": question_id, "answer": "❌ Answer not found."}
 
