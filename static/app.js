
let chatId = null;
let chats = [];

window.onload = async () => {
    await loadModels();
    await loadChatList();
    await newChat();
};

async function loadModels() {
    const res = await fetch('/api/start', { method: 'POST' });
    const data = await res.json();
    chatId = data.chat_id;

    const modelSelect = document.getElementById("model");
    const models = await fetchModels();
    modelSelect.innerHTML = "";
    models.forEach(m => {
        const opt = document.createElement("option");
        opt.value = m;
        opt.innerText = m;
        modelSelect.appendChild(opt);
    });
}

async function fetchModels() {
    const res = await fetch("/api/models");
    const models = await res.json();
    return models;
}

function checkEnter(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
}

async function newChat() {
    const res = await fetch('/api/start', { method: 'POST' });
    const data = await res.json();
    chatId = data.chat_id;
    document.getElementById("chat-box").innerHTML = "";
}

async function loadChatList() {
    const res = await fetch('/api/chats');
    const data = await res.json();
    chats = data;
    const list = document.getElementById("chat-list");
    list.innerHTML = "";
    chats.forEach(c => {
        const li = document.createElement("li");
        li.className = "flex justify-between items-center";
        li.innerHTML = `
            <button class="text-left text-blue-600 hover:underline" onclick="loadChat('${c.id}')">${c.title}</button>
            <button onclick="deleteChat('${c.id}')" class="text-red-500 text-sm ml-2">✖</button>
        `;
        list.appendChild(li);
    });
}

async function loadChat(id) {
    const res = await fetch(`/api/chats/${id}`);
    const data = await res.json();
    chatId = id;
    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML = "";
    data.history.split("\n").forEach(line => {
        if (line.trim().startsWith("User:")) {
            chatBox.innerHTML += `<div class="mb-2"><strong>You:</strong> ${line.replace("User:", "").trim()}</div>`;
        } else if (line.trim().startsWith("Bot:")) {
            const formatted = marked.parse(line.replace("Bot:", "").trim());
            chatBox.innerHTML += `<div class="mb-2"><strong>Bot:</strong><br>${formatted}</div>`;
        }
    });
}
async function uploadPDF() {
    const input = document.getElementById("pdf-upload");
    const file = input.files[0];
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/api/upload-pdf", {
        method: "POST",
        body: formData
    });

    if (res.ok) {
        alert("✅ PDF uploaded and ready to use.");
    } else {
        alert("❌ Failed to upload PDF.");
    }
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<div class="mb-2"><strong>You:</strong> ${message}</div>`;
    input.value = "";
    document.getElementById("loading").classList.remove("hidden");

    const res = await fetch("/api/message", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        chat_id: chatId,
        message: message,
        model: document.getElementById("model").value,
        use_web: useWebSearch
    })
});

    const data = await res.json();
    document.getElementById("loading").classList.add("hidden");

    if (data.error) {
        chatBox.innerHTML += `<div class="text-red-500">Error: ${data.error}</div>`;
    } else {
        const formatted = marked.parse(data.response);
        chatBox.innerHTML += `<div class="mb-2"><strong>Bot:</strong><br>${formatted}</div>`;
        await loadChatList();
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}
function toggleAbout() {
    const modal = document.getElementById("about-modal");
    modal.classList.toggle("hidden");
}

async function deleteChat(id) {
    if (!confirm("Are you sure you want to delete this chat?")) return;
    const res = await fetch(`/api/chats/${id}`, { method: "DELETE" });
    if (res.ok) {
        if (chatId === id) {
            await newChat();
        }
        await loadChatList();
    } else {
        alert("Error deleting chat.");
    }
}

let useWebSearch = false;

function toggleWebSearch() {
    useWebSearch = document.getElementById("web-toggle").checked;
}

