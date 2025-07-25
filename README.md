# 🤖 PrivyBot – Your Local Chatbot

PrivyBot is a private, local-first chatbot interface powered by [Ollama](https://ollama.com) and [LangChain](https://www.langchain.com/). It runs in your browser and stores all conversations locally on your machine. No internet connection required after setup!
For up-to-date answers, you can optionally turn on internet search, which allows PrivyBot to retrieve relevant results using DuckDuckGo and include source links in its responses. When the feature is off, the chatbot relies solely on local knowledge and memory.
---

## 🖥️ Requirements

You need to install:

- Python 3.10+
- Ollama (to run local LLMs like LLaMA or Mistral)
- `pip` (Python's package manager)
- Terminal or Bash (e.g., PowerShell, Terminal.app, or Git Bash)

---

## 📥 Installation Instructions

### 🪟 For Windows Users

1. **Install Python 3.10+**  
   Download from: https://www.python.org/downloads/windows  
   ✅ Make sure to check the box: `Add Python to PATH` during installation.

2. **Install Git Bash (optional but recommended)**  
   Download from: https://gitforwindows.org  
   This gives you a Linux-like terminal.

3. **Install Ollama**  
   Download and run the installer: https://ollama.com/download  
   Then open a terminal (or PowerShell) and run:
   ```bash
   ollama run llama3
   ```

4. **Clone or unzip this repository**

5. **Install required Python libraries**
   In your terminal:
   ```bash
   pip install fastapi uvicorn langchain-community jinja2 requests beautifulsoup4 serpapi faiss-cpu python-multipart
   ```

6. **Start the server**
   ```bash
   python -m uvicorn main:app --reload
   ```

7. **Open your browser**
   Go to: http://127.0.0.1:8000

---

### 🍎 For macOS Users

1. **Install Homebrew (if not installed)**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python 3**
   ```bash
   brew install python
   ```

3. **Install Ollama**
   Download from: https://ollama.com/download  
   Or install via Homebrew:
   ```bash
   brew install ollama
   ```

4. **Run a model**
   ```bash
   ollama run llama3
   ```

5. **Navigate to your project directory**

6. **Install dependencies**
   ```bash
   pip3 install install fastapi uvicorn langchain-community jinja2 requests beautifulsoup4 serpapi faiss-cpu python-multipart
   ```

7. **Start the server**
   ```bash
   python3 -m uvicorn main:app --reload
   ```

8. **Open your browser**
   Visit: http://127.0.0.1:8000

---

## 🧠 Notes

- **All chats are stored locally** in the `chats/` folder.
- You can select from available Ollama models.
- You can delete or reload old chats from the sidebar.
- Nothing is sent to the cloud.

---

## 🛠 Example Models You Can Use

Make sure you’ve pulled a model via Ollama before running it:
```bash
ollama run mistral
ollama run llama3
ollama run gemma
```

You can check installed models with:
```bash
ollama list
```

---

## 🧾 License

This project is for personal and educational use. Modify and extend it as needed!
