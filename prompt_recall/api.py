from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from prompt_recall.db import connect
from prompt_recall.vectorstore import query_similar

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = ""):
    results = []
    if q:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM chat_turns WHERE content ILIKE %s LIMIT 50", (f"%{q}%",))
                results = cur.fetchall()
    return templates.TemplateResponse("index.html", {"request": request, "results": results, "query": q})

@app.post("/semantic-search", response_class=HTMLResponse)
async def semantic_search(request: Request, q: str = Form(...)):
    results = query_similar(q, limit=50)
    return templates.TemplateResponse("index.html", {"request": request, "results": results, "query": q})

@app.get("/session/{session_id}", response_class=HTMLResponse)
async def session_view(request: Request, session_id: str):
    with connect() as conn:
        with conn.cursor() as cur:
            # Get user + original assistant messages
            cur.execute("""
                SELECT id, turn_index, role, content
                FROM chat_turns
                WHERE session_id = %s
                ORDER BY turn_index, role
            """, (session_id,))
            all_turns = cur.fetchall()

            # Group by turn_index
            grouped = {}
            for row in all_turns:
                turn_id, turn_index, role, content = row
                grouped.setdefault(turn_index, {"user": "", "assistant": "", "turn_id": turn_id})
                grouped[turn_index][role] = content
                grouped[turn_index]["turn_id"] = turn_id

            # Get alternates
            cur.execute("""
                SELECT turn_id, model_name, alt_response, rating, flagged
                FROM alt_completions
                WHERE turn_id IN %s
            """, (tuple([v["turn_id"] for v in grouped.values()]),))
            alts = cur.fetchall()

            # Attach alternates to each turn
            for turn in grouped.values():
                turn["alternates"] = []

            for alt in alts:
                turn_id, model_name, alt_response, rating, flagged = alt
                for turn in grouped.values():
                    if turn["turn_id"] == turn_id:
                        turn["alternates"].append({
                            "model_name": model_name,
                            "alt_response": alt_response,
                            "rating": rating,
                            "flagged": flagged
                        })

            # Sort by turn index
            sorted_turns = [grouped[i] for i in sorted(grouped)]

    return templates.TemplateResponse("session.html", {
        "request": request,
        "session_id": session_id,
        "turns": sorted_turns
    })
