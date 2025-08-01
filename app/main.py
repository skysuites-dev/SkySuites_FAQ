from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.faq_queries import load_faq_from_yaml, faq, get_answer_by_category_and_question

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def startup_event():
    load_faq_from_yaml()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state = "awaiting_category"
    selected_category = None

    await websocket.send_json({
        "reply": "Welcome! Please choose a category:",
        "options": list(faq.keys())
    })

    try:
        while True:
            data = await websocket.receive_json()
            msg = data.get("message", "").strip()

            if state == "awaiting_category":
                if msg in faq:
                    selected_category = msg
                    state = "awaiting_question"
                    await websocket.send_json({
                        "reply": f"Great! Choose a question from '{msg}':",
                        "options": list(faq[msg].keys())
                    })
                else:
                    await websocket.send_json({
                        "reply": "❌ Invalid category. Please choose again:",
                        "options": list(faq.keys())
                    })

            elif state == "awaiting_question":
                if selected_category and msg in faq[selected_category]:
                    answer = get_answer_by_category_and_question(selected_category, msg)
                    await websocket.send_json({ "reply": answer })

                    # Reset state to choose new category
                    state = "awaiting_category"
                    selected_category = None
                    await websocket.send_json({
                        "reply": "Would you like help with another category?",
                        "options": list(faq.keys())
                    })
                else:
                    await websocket.send_json({
                        "reply": "❌ Invalid question. Choose one below:",
                        "options": list(faq[selected_category].keys())
                    })

    except Exception as e:
        print("WebSocket closed or error:", e)
