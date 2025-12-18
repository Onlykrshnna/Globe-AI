const chatContainer = document.getElementById("chat-container");
const input = document.getElementById("user-input");

function handleEnter(event) {
  if (event.key === "Enter") {
    sendMessage();
  }
}

function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = `message ${type}`;
  div.innerHTML = `<p>${text}</p>`;
  chatContainer.appendChild(div);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage() {
  const question = input.value.trim();
  if (!question) return;

  addMessage(question, "user");
  input.value = "";

  const thinking = document.createElement("div");
  thinking.className = "message ai";
  thinking.innerHTML = "<p>Thinking...</p>";
  chatContainer.appendChild(thinking);
  chatContainer.scrollTop = chatContainer.scrollHeight;

  try {
    const response = await fetch("http://127.0.0.1:8000/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question: question })
    });

    const data = await response.json();
    chatContainer.removeChild(thinking);

    addMessage(data.answer.replace(/\n/g, "<br>"), "ai");

  } catch (error) {
    chatContainer.removeChild(thinking);
    addMessage("❌ Unable to connect to GlobeAI backend.", "ai");
  }
}
