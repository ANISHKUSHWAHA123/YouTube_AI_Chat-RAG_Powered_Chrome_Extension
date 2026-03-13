document.addEventListener("DOMContentLoaded", () => {

let sessionId = crypto.randomUUID();

const sendBtn = document.getElementById("send-btn");
const questionInput = document.getElementById("question-input");
const chatDiv = document.getElementById("chat-messages");

async function getCurrentVideoId() {

const tabs = await chrome.tabs.query({
active: true,
currentWindow: true
});

if (!tabs.length) return null;

const url = tabs[0].url;

if (!url) return null;

const parsedUrl = new URL(url);

return parsedUrl.searchParams.get("v");
}

function addMessage(role, content) {

  const message = document.createElement("div");

  message.classList.add("message", role);

  if (role === "Bot") {

    if (typeof marked !== "undefined") {
      message.innerHTML = marked.parse(content);
    } else {
      message.textContent = content;
    }

  } else {
    message.textContent = content;
  }

  chatDiv.appendChild(message);

  chatDiv.scrollTop = chatDiv.scrollHeight;
}

async function sendMessage() {

const question = questionInput.value.trim();

if (!question) return;

addMessage("You", question);

questionInput.value = "";

const videoId = await getCurrentVideoId();

if (!videoId) {

addMessage("System", "No YouTube video detected.");

return;
}

const loading = document.createElement("div");

loading.classList.add("message", "Bot");

loading.id = "loading-msg";

loading.textContent = "Thinking...";

chatDiv.appendChild(loading);

chatDiv.scrollTop = chatDiv.scrollHeight;

try {

const res = await fetch("http://localhost:8000/ask", {

method: "POST",

headers: {

"Content-Type": "application/json"

},

body: JSON.stringify({

video_id: videoId,

question: question,

session_id: sessionId

})

});

if (!res.ok) {
    throw new Error("HTTP error " + res.status);
}
    
const data = await res.json();

document.getElementById("loading-msg")?.remove();

addMessage("Bot", data.answer);

} catch (error) {

console.error("FETCH ERROR:", error);

document.getElementById("loading-msg")?.remove();

addMessage("Error", "Backend error: " + error.message);

}
}

sendBtn.addEventListener("click", sendMessage);

questionInput.addEventListener("keypress", (e) => {

if (e.key === "Enter" && !e.shiftKey) {

e.preventDefault();

sendMessage();

}

});

});