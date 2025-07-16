async function sendMessage() {
  const input = document.getElementById("userInput");
  const messages = document.getElementById("messages");
  const question = input.value.trim();
  
  // Usamos la variable global currentUserId definida en index.html
  if (!question || !currentUserId) {
    alert("Escribe una pregunta.");
    return;
  }

  // Muestra el mensaje del usuario inmediatamente
  messages.innerHTML += `<p><strong>Tú:</strong> ${question}</p>`;
  input.value = "";

  // Añade un mensaje de "cargando"
  const thinkingMessage = document.createElement('p');
  thinkingMessage.innerHTML = "<strong>Bot:</strong> Pensando...";
  messages.appendChild(thinkingMessage);

  try {
    // Usamos el endpoint principal del chat, pasando el ID en la URL
    const response = await fetch(`/chat/${currentUserId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: question }),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Error del servidor: ${errorText}`);
    }
    
    const data = await response.json();
    thinkingMessage.innerHTML = `<strong>Bot:</strong> ${data.response}`;
  } catch (error) {
    console.error("Error en la petición:", error);
    thinkingMessage.innerHTML = `<strong>Bot:</strong> ❌ ${error.message}`;
  }
}
