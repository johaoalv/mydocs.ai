async function uploadDoc() {
  const fileInput = document.getElementById("file");
  const file = fileInput.files[0];
  const user_id = document.getElementById("user_id").value.trim();
  const statusDiv = document.getElementById("upload-status");

  if (!file || !user_id) {
    statusDiv.textContent = "❌ Por favor, selecciona un archivo.";
    statusDiv.style.color = "red";
    return;
  }

  statusDiv.textContent = "Subiendo y procesando...";
  statusDiv.style.color = "blue";

  const formData = new FormData();
  formData.append("file", file);
  formData.append("user_id", user_id);

  try {
    const res = await fetch("/upload-doc", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    statusDiv.textContent = `✅ Documento subido con éxito. Chunks creados: ${data.chunks}`;
    statusDiv.style.color = "green";
    fileInput.value = ""; // Limpiar el input de archivo
  } catch (error) {
    statusDiv.textContent = "❌ Error al subir el documento.";
    statusDiv.style.color = "red";
    console.error("Error en upload:", error);
  }
}