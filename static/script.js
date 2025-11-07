const socket = io();

const consoleDiv = document.getElementById("console");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");

function addMessage(msg) {
    consoleDiv.innerHTML += msg + "<br>";
    consoleDiv.scrollTop = consoleDiv.scrollHeight;
}

sendBtn.addEventListener("click", () => {
    const msg = input.value.trim();
    if(msg === "") return;
    socket.emit("send_message", msg);
    input.value = "";
});

input.addEventListener("keypress", e => {
    if(e.key === "Enter") sendBtn.click();
});

socket.on("receive_message", msg => {
    addMessage(msg);
});
