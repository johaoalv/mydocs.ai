async function sendMessage() {
  const input = document.getElementById("userInput");
  const userIdInput = document.getElementById("user_id");
  const messages = document.getElementById("messages");

  const question = input.value.trim();
  const user_id = userIdInput.value.trim();

  if (!question || !user_id) {
    alert("Escribe tu pregunta y tu ID de usuario.");
    return;
  }

  messages.innerHTML += `<p><strong>Tú:</strong> ${question}</p>`;
  input.value = "";

  const formData = new FormData();
  formData.append("user_id", user_id);
  formData.append("question", question);

  const response = await fetch("/ask", {
  method: "POST",
  body: formData,
});

if (!response.ok) {
  const errorText = await response.text();
  console.error("Error en backend:", errorText);
  messages.innerHTML += `<p><strong>Bot:</strong> ❌ Error del servidor: ${errorText}</p>`;
  return;
}

const data = await response.json();
messages.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;

}
