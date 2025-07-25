
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi import File, UploadFile
from langchain_community.llms import Ollama
import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse, unquote

import subprocess
import uuid
import json
import os
import numpy as np

from pdf_utils import (
    extract_text_from_pdf,
    split_text_into_chunks,
    embed_text_chunks,
    create_faiss_index,
    retrieve_top_chunks,
    ask_question_with_context
)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

DATA_DIR = "chats"
os.makedirs(DATA_DIR, exist_ok=True)
chats = {}

pdf_index = None
pdf_embedder = None
pdf_chunks = None
pdf_uploaded = False

@app.get("/api/models")
async def get_models():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[1:]
        models = [line.split()[0] for line in lines]
        return models
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

def list_ollama_models():
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')[1:]
    return [line.split()[0] for line in lines]

@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    models = list_ollama_models()
    model_options = "".join([f"<option value='{m}'>{m}</option>" for m in models])
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read().replace("<!--MODEL_OPTIONS-->", model_options)

@app.post("/api/start")
async def start_chat():
    chat_id = str(uuid.uuid4())
    chats[chat_id] = {"history": "You are a helpful assistantnamed PrivyBot.\n"}
    return {"chat_id": chat_id}

@app.post("/api/message")
async def message(data: dict):
    chat_id = data["chat_id"]
    user_input = data["message"]
    model = data["model"]
    use_web = data.get("use_web", False)

    if chat_id not in chats:
        # Try loading from disk if not in memory
        path = os.path.join(DATA_DIR, f"{chat_id}.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                chats[chat_id] = json.load(f)
        else:
            return JSONResponse(status_code=400, content={"error": "Invalid chat ID"})

    try:
        response = ""
        web_context = ""
        pdf_context = ""

        # 🌐 Use DuckDuckGo if enabled
        if use_web:
            context_text, links = duckduckgo_extract(user_input)
            if context_text.strip():
                web_context = context_text
                sources = "\n".join(links)
                web_context += f"\n\nSources:\n{sources}"

        # 📄 Add PDF context if available
        if pdf_uploaded:
            pdf_context = retrieve_top_chunks(user_input, pdf_index, pdf_embedder, pdf_chunks)

        # 🤖 Build composite prompt
        history = chats[chat_id]["history"]
        full_prompt = (
            f"{history.strip()}\n\n"
            "You are a helpful assistant named PrivyBot. Use the information below to answer the user's question clearly.\n\n"
                )
        if web_context:
            full_prompt += f"### Web Search Context:\n{web_context}\n\n"
        if pdf_context:
            full_prompt += f"### PDF Context:\n{pdf_context}\n\n"

        full_prompt += f"### Question:\n{user_input}\n\nAnswer:"

        # Call LLM
        llm = Ollama(model=model)
        response = llm.invoke(full_prompt)
        # Append clickable links if web search was used
        if use_web and links:
            formatted_links = "\n".join([f'<a href="{link}" target="_blank" style="color:blue; text-decoration:underline;">{urlparse(link).netloc}</a>' for link in links])
            response += f"\n\n🌐 Sources:<br>{formatted_links}"
        # Add to history
        chats[chat_id]["history"] += f"User: {user_input}\nBot: {response}\n"

        # Generate title from first user message
        if "title" not in chats[chat_id]:
            first_line = user_input.strip().split("\n")[0]
            chats[chat_id]["title"] = first_line[:40] + ("..." if len(first_line) > 40 else "")

        # Save chat to file
        with open(os.path.join(DATA_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
            json.dump(chats[chat_id], f, ensure_ascii=False, indent=2)

        return {"response": response}

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/chats")
async def get_chat_list():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    result = []
    for fname in files:
        path = os.path.join(DATA_DIR, fname)
        with open(path, encoding="utf-8") as f:
            content = json.load(f)
            result.append({
                "id": fname.replace(".json", ""),
                "title": content.get("title", "Untitled")
            })
    return result

@app.get("/api/chats/{chat_id}")
async def get_chat_by_id(chat_id: str):
    path = os.path.join(DATA_DIR, f"{chat_id}.json")
    if not os.path.exists(path):
        return JSONResponse(status_code=404, content={"error": "Chat not found"})
    with open(path, encoding="utf-8") as f:
        return json.load(f)

@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    path = os.path.join(DATA_DIR, f"{chat_id}.json")
    if os.path.exists(path):
        os.remove(path)
        chats.pop(chat_id, None)
        return {"status": "deleted"}
    return JSONResponse(status_code=404, content={"error": "Chat not found"})

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    global pdf_index, pdf_embedder, pdf_chunks, pdf_uploaded
    contents = await file.read()
    file_path = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(contents)

    raw_text = extract_text_from_pdf(file_path)
    pdf_chunks = split_text_into_chunks(raw_text)
    embeddings, pdf_embedder = embed_text_chunks(pdf_chunks)
    pdf_index = create_faiss_index(np.array(embeddings))
    pdf_uploaded = True
    return {"status": "PDF uploaded and processed."}

def duckduckgo_extract(query):
    url = f"https://html.duckduckgo.com/html/?q={query}"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    snippets = soup.select(".result__snippet")
    raw_links = soup.select(".result__url")

    text_snippets = []
    clean_links = []

    for snippet, raw_link in zip(snippets[:3], raw_links[:3]):
        text = snippet.text.strip()
        href = raw_link.get("href")
        parsed = urlparse(href)
        params = parse_qs(parsed.query)
        real_url = unquote(params.get("uddg", [""])[0])

        if real_url:
            text_snippets.append(text)
            clean_links.append(real_url)

    return "\n".join(text_snippets), clean_links