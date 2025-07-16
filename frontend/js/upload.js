async function uploadDoc() {
      const file = document.getElementById("file").files[0];
      const user_id = document.getElementById("user_id").value.trim();

      if (!file || !user_id) {
        alert("Selecciona un archivo y escribe tu ID.");
        return;
      }

      const formData = new FormData();
      formData.append("file", file);
      formData.append("user_id", user_id);

      const res = await fetch("/upload-doc", {
        method: "POST",
        body: formData
      });

      const data = await res.json();
      alert("✅ Documento subido. Chunks creados: " + data.chunks);
    }