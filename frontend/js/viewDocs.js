async function cargarDocs() {
  // Usa la variable global 'currentUserId' definida en index.html
  const user_id = currentUserId;
  if (!user_id) return;

  const res = await fetch(`/docs/${user_id}`);
  const data = await res.json();
  const list = document.getElementById("docItems");
  list.innerHTML = "";

  data.docs.forEach((doc) => {
    list.innerHTML += `<li>✅ ${doc}</li>`;
  });
}
