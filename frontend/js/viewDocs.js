async function cargarDocs() {
    try {
      const sessionStr = localStorage.getItem("session");
      if (!sessionStr) {
        console.log("ℹ️ No hay sesión activa.");
        return;
      }

      const session = JSON.parse(sessionStr);
      const user_id = session.user.id;
      console.log("🔎 Buscando documentos para:", user_id);

      const res = await fetch(`/docs/${user_id}`);
      const data = await res.json();

      console.log("📄 Documentos encontrados:", data.docs);

      const docList = document.getElementById("docItems");
      docList.innerHTML = ""; // Limpiar antes

      data.docs.forEach((doc) => {
        const li = document.createElement("li");
        li.textContent = doc.filename;
        docList.appendChild(li);
      });
    } catch (error) {
      console.error("❌ Error al cargar documentos:", error);
    }
  }

  // Ejecutar cuando la página cargue
  window.addEventListener("DOMContentLoaded", cargarDocs);
