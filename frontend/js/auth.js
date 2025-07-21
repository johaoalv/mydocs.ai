// 👉 Configuración del proyecto Supabase
const SUPABASE_URL = "https://rzsuzsgdogvpdgllqzwl.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6c3V6c2dkb2d2cGRnbGxxendsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI3MDIxODMsImV4cCI6MjA2ODI3ODE4M30.hHpKwcCwyWgmx9IYedNFyuy5eaqNPcZXZuMRCB28BW0";
const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

console.log("✅ Supabase inicializado");

// 👉 Listener para el botón "Continuar con Google"
const googleLoginBtn = document.getElementById("google-login-btn");

if (googleLoginBtn) {
  googleLoginBtn.addEventListener("click", async () => {
    console.log("🟡 Iniciando login con Google...");

    const { data, error } = await supabaseClient.auth.signInWithOAuth({
      provider: "google",
    });

    if (error) {
      console.error("❌ Error en login con Google:", error);
    } else {
      console.log("🔁 Redirección en curso hacia Google Auth...", data);
    }
  });
}

// 👉 Al volver del login (cuando se carga login.html otra vez)
window.addEventListener("DOMContentLoaded", async () => {
  const { data, error } = await supabaseClient.auth.getSession();

  if (error) {
    console.error("❌ Error obteniendo sesión:", error);
    return;
  }

  if (data.session) {
    const user = data.session.user;
    console.log("✅ Usuario autenticado:", user);

    // Guardar en localStorage para usar luego
    localStorage.setItem("session", JSON.stringify(data.session));

    // Redirigir al chat
    console.log("🚀 Redirigiendo a /chat...");
    window.location.href = "/chat";
  } else {
    console.log("ℹ️ No hay sesión activa.");
  }
});
