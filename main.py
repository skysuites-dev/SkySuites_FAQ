from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import yaml

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Replace "Back" with a true Home button
HOME_OPTION = "🏠 Return to Home"

@app.on_event("startup")
async def startup_event():
    load_faq_from_yaml()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Stack stores history of (node name, questions list)
    path_stack = []
    current_title = "Categories"
    current_questions = faq["categories"]

    def get_display_options(questions):
        return [q.get("question") or q.get("name") for q in questions] + [HOME_OPTION]

    async def send_options(title, questions):
        await websocket.send_json({
            "reply": f"Please choose an option under: {title}",
            "options": get_display_options(questions)
        })

    await send_options(current_title, current_questions)

    try:
        while True:
            data = await websocket.receive_json()
            msg = data.get("message", "").strip()

            if not msg:
                await websocket.send_json({
                    "reply": "⚠️ Please send a valid message.",
                    "options": get_display_options(current_questions)
                })
                continue

            # Handle "Return to Home"
            if msg == HOME_OPTION:
                path_stack.clear()
                current_title = "Categories"
                current_questions = faq["categories"]
                await send_options(current_title, current_questions)
                continue

            # Try to match the question in current list
            match = None
            for item in current_questions:
                label = item.get("question") or item.get("name")
                if label == msg:
                    match = item
                    break

            if not match:
                await websocket.send_json({
                    "reply": "❌ Invalid selection. Please choose again:",
                    "options": get_display_options(current_questions)
                })
                continue

            # Handle answer
            if "answer" in match:
                await websocket.send_json({ "reply": match["answer"] })

                # If related exists, dive into it
                if match.get("related"):
                    path_stack.append((current_title, current_questions))
                    current_title = f"Related to: {match.get('question')}"
                    current_questions = match["related"]
                    await send_options(current_title, current_questions)
                else:
                    # After answering, go home
                    path_stack.clear()
                    current_title = "Categories"
                    current_questions = faq["categories"]
                    await send_options(current_title, current_questions)

            # Handle nested categories
            elif match.get("questions"):
                path_stack.append((current_title, current_questions))
                current_title = match.get("name") or match.get("question")
                current_questions = match["questions"]
                await send_options(current_title, current_questions)

            else:
                await websocket.send_json({
                    "reply": "⚠️ Unexpected item format.",
                    "options": get_display_options(current_questions)
                })

    except Exception as e:
        print("WebSocket closed or error:", e)

 
faq = {}

def load_faq_from_yaml(path=r"vector_store/queries.yaml"):
    global faq
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        faq.clear()
        faq.update(data)



 
