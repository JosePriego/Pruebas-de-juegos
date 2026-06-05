import streamlit as st
import streamlit.components.v1 as components

# Configuración de página
st.set_page_config(page_title="Emoji T-Rex", layout="centered", page_icon="🦖")

# Estilos para que parezca un juego de verdad
st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    h1 { color: #333; font-family: 'Courier New', Courier, monospace; text-align: center; }
    .stMarkdown p { text-align: center; color: #666; font-family: 'Courier New', Courier, monospace;}
</style>
""", unsafe_allow_html=True)

st.title("🦖 EMOJI T-REX RUNNER")
st.write("Haz **clic** en el recuadro o pulsa **Espacio** para saltar.")

# --- EL MOTOR DEL JUEGO CON EMOJIS ---
codigo_juego = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { display: flex; justify-content: center; margin: 0; background-color: #f0f2f6; overflow: hidden; user-select: none; font-family: 'Courier New', Courier, monospace; }
  canvas { border: 3px solid #333; background-color: #ffffff; border-radius: 10px; cursor: pointer; box-shadow: 4px 4px 0px #cccccc; }
</style>
</head>
<body>
<canvas id="juego" width="600" height="250" tabindex="1"></canvas>
<script>
  const canvas = document.getElementById("juego");
  const ctx = canvas.getContext("2d");
  ctx.textBaseline = "top"; // Hace que las coordenadas de los emojis sean exactas

  // --- VARIABLES ---
  const SUELO_Y = 170;
  let dino = { x: 50, y: SUELO_Y, velY: 0, ancho: 35, alto: 40 };
  let cactus = { x: 600, y: SUELO_Y + 5, ancho: 25, alto: 35 };
  let nubes = [ {x: 100, y: 40, vel: 0.5}, {x: 350, y: 70, vel: 0.3}, {x: 550, y: 30, vel: 0.4} ];
  
  let gravedad = 1.2;
  let puntuacion = 0;
  let velocidadJuego = 5.5;
  let estado = 'INICIO'; // INICIO, JUGANDO, GAMEOVER

  // --- CONTROLES ---
  function saltar() {
    if (estado === 'INICIO') { 
        estado = 'JUGANDO'; 
        requestAnimationFrame(bucle); 
    }
    else if (estado === 'GAMEOVER') { 
        reiniciar(); 
        requestAnimationFrame(bucle); 
    }
    else if (estado === 'JUGANDO' && dino.y === SUELO_Y) {
        dino.velY = -15; // Fuerza del salto
    }
  }

  canvas.addEventListener("keydown", (e) => { if(e.code === "Space") { e.preventDefault(); saltar(); }});
  canvas.addEventListener("mousedown", saltar);
  canvas.addEventListener("touchstart", (e) => { e.preventDefault(); saltar(); }, {passive: false});
  canvas.focus();

  function reiniciar() {
    dino.y = SUELO_Y; 
    dino.velY = 0;
    cactus.x = 600;
    puntuacion = 0; 
    velocidadJuego = 5.5;
    estado = 'JUGANDO';
  }

  // --- RENDERIZADO ---
  function dibujar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Dibujar Nubes
    ctx.font = "40px Arial";
    nubes.forEach(n => { ctx.fillText("☁️", n.x, n.y); });

    // Dibujar Suelo
    ctx.strokeStyle = "#333"; 
    ctx.lineWidth = 3;
    ctx.beginPath(); 
    ctx.moveTo(0, SUELO_Y + 40); 
    ctx.lineTo(canvas.width, SUELO_Y + 40); 
    ctx.stroke();

    // Puntuación
    ctx.fillStyle = "#333"; 
    ctx.font = "bold 20px 'Courier New'"; 
    ctx.textAlign = "right";
    ctx.fillText("Puntos: " + Math.floor(puntuacion), canvas.width - 20, 20);
    ctx.textAlign = "left"; // Restaurar

    // Dibujar Cactus
    ctx.font = "40px Arial";
    ctx.fillText("🌵", cactus.x, cactus.y);

    // Dibujar Dino (Cambia de cara si chocas)
    ctx.font = "40px Arial";
    ctx.fillText(estado === 'GAMEOVER' ? "😵" : "🦖", dino.x, dino.y);

    // Pantallas superpuestas (Textos)
    if (estado === 'INICIO') {
        ctx.fillStyle = "rgba(255,255,255,0.7)";
        ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#333"; ctx.textAlign = "center"; ctx.font = "bold 24px 'Courier New'";
        ctx.fillText("HAZ CLIC PARA EMPEZAR", canvas.width/2, canvas.height/2 - 10);
    }

    if (estado === 'GAMEOVER') {
        ctx.fillStyle = "rgba(255,255,255,0.7)";
        ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#d32f2f"; ctx.textAlign = "center"; ctx.font = "bold 36px 'Courier New'";
        ctx.fillText("¡CRASH!", canvas.width/2, canvas.height/2 - 25);
        ctx.fillStyle = "#333"; ctx.font = "bold 18px 'Courier New'";
        ctx.fillText("Haz clic para reintentar", canvas.width/2, canvas.height/2 + 20);
    }
  }

  // --- BUCLE DE LÓGICA ---
  function bucle() {
    if (estado !== 'JUGANDO') return;

    // Físicas del Dinosaurio
    dino.velY += gravedad;
    dino.y += dino.velY;
    if (dino.y > SUELO_Y) { dino.y = SUELO_Y; dino.velY = 0; }

    // Movimiento del entorno
    cactus.x -= velocidadJuego;
    if (cactus.x < -40) { cactus.x = canvas.width + Math.random() * 300; }
    
    nubes.forEach(n => {
        n.x -= n.vel;
        if (n.x < -60) n.x = canvas.width + Math.random() * 100;
    });

    // Dificultad progresiva
    puntuacion += 0.1;
    velocidadJuego += 0.002;

    // Colisiones (Hitboxes invisibles)
    let dH = { x: dino.x + 5, y: dino.y + 5, w: dino.ancho - 10, h: dino.alto - 10 };
    let cH = { x: cactus.x + 10, y: cactus.y + 10, w: cactus.ancho - 15, h: cactus.alto - 10 };

    if (dH.x < cH.x + cH.w && dH.x + dH.w > cH.x && dH.y < cH.y + cH.h && dH.h + dH.y > cH.y) {
        estado = 'GAMEOVER';
    }

    dibujar();

    if (estado === 'JUGANDO') {
        requestAnimationFrame(bucle); // Siguiente fotograma
    }
  }

  // Dibujar la pantalla de inicio nada más cargar
  dibujar();

</script>
</body>
</html>
"""

components.html(codigo_juego, height=280)
