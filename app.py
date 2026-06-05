import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Emoji T-Rex Pro", layout="centered", page_icon="🦖")

st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    h1 { color: #333; font-family: 'Courier New', Courier, monospace; text-align: center; }
    .stMarkdown p { text-align: center; color: #666; font-family: 'Courier New', Courier, monospace;}
</style>
""", unsafe_allow_html=True)

st.title("🦖 EMOJI T-REX: PRO")
st.write("Pulsa **Espacio** para saltar | Mantén **Flecha Abajo** para agacharte.")

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
  ctx.textBaseline = "top";

  // --- VARIABLES ---
  const SUELO_Y = 170;
  let dino = { x: 50, y: SUELO_Y, velY: 0, ancho: 35, alto: 40, agachado: false };
  
  // Obstáculo dinámico (Cactus o Pájaro)
  let obstaculo = { x: 600, y: SUELO_Y + 5, ancho: 25, alto: 35, tipo: 'cactus' };
  
  let nubes = [ {x: 100, y: 40, vel: 0.5}, {x: 350, y: 70, vel: 0.3}, {x: 550, y: 30, vel: 0.4} ];
  
  let gravedad = 1.3;
  let puntuacion = 0;
  // Recuperar récord del navegador
  let maxPuntuacion = localStorage.getItem("dinoHighScore") || 0; 
  let velocidadJuego = 6;
  let estado = 'INICIO';

  // --- CONTROLES ---
  function saltar() {
    if (estado === 'INICIO') { 
        estado = 'JUGANDO'; requestAnimationFrame(bucle); 
    } else if (estado === 'GAMEOVER') { 
        reiniciar(); requestAnimationFrame(bucle); 
    } else if (estado === 'JUGANDO' && dino.y === SUELO_Y && !dino.agachado) {
        dino.velY = -15; 
    }
  }

  canvas.addEventListener("keydown", (e) => { 
      if(e.code === "Space" || e.code === "ArrowUp") { e.preventDefault(); saltar(); }
      if(e.code === "ArrowDown" && estado === 'JUGANDO') { e.preventDefault(); dino.agachado = true; }
  });
  
  canvas.addEventListener("keyup", (e) => {
      if(e.code === "ArrowDown") { dino.agachado = false; }
  });

  canvas.addEventListener("mousedown", saltar);
  canvas.addEventListener("touchstart", (e) => { e.preventDefault(); saltar(); }, {passive: false});
  canvas.focus();

  function reiniciar() {
    dino.y = SUELO_Y; dino.velY = 0; dino.agachado = false;
    obstaculo.x = 600; obstaculo.tipo = 'cactus'; obstaculo.y = SUELO_Y + 5;
    puntuacion = 0; velocidadJuego = 6;
    estado = 'JUGANDO';
  }

  function generarObstaculo() {
      obstaculo.x = canvas.width + Math.random() * 200;
      // 30% de probabilidad de que sea un pájaro si la puntuación es mayor a 100
      if (puntuacion > 100 && Math.random() < 0.3) {
          obstaculo.tipo = 'pajaro';
          obstaculo.y = SUELO_Y - 30; // Vuela a media altura
          obstaculo.ancho = 35;
          obstaculo.alto = 20;
      } else {
          obstaculo.tipo = 'cactus';
          obstaculo.y = SUELO_Y + 5;
          obstaculo.ancho = 25;
          obstaculo.alto = 35;
      }
  }

  // --- RENDERIZADO ---
  function dibujar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.font = "40px Arial";
    nubes.forEach(n => { ctx.fillText("☁️", n.x, n.y); });

    ctx.strokeStyle = "#333"; ctx.lineWidth = 3; ctx.beginPath(); 
    ctx.moveTo(0, SUELO_Y + 40); ctx.lineTo(canvas.width, SUELO_Y + 40); ctx.stroke();

    // Textos de Puntuación
    ctx.fillStyle = "#333"; ctx.font = "bold 16px 'Courier New'"; 
    ctx.textAlign = "right";
    ctx.fillText("HI: " + Math.floor(maxPuntuacion).toString().padStart(5, '0') + "  " + Math.floor(puntuacion).toString().padStart(5, '0'), canvas.width - 20, 20);
    ctx.textAlign = "left";

    // Dibujar Obstáculo
    ctx.font = "40px Arial";
    if (obstaculo.tipo === 'cactus') {
        ctx.fillText("🌵", obstaculo.x, obstaculo.y);
    } else {
        ctx.fillText("🦅", obstaculo.x, obstaculo.y);
    }

    // Dibujar Dino
    ctx.font = "40px Arial";
    if (estado === 'GAMEOVER') {
        ctx.fillText("😵", dino.x, dino.y);
    } else if (dino.agachado && dino.y === SUELO_Y) {
        ctx.fillText("🐊", dino.x, dino.y + 10); // Cocodrilo más bajito
    } else {
        ctx.fillText("🦖", dino.x, dino.y);
    }

    // Pantallas superpuestas
    if (estado === 'INICIO') {
        ctx.fillStyle = "rgba(255,255,255,0.7)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#333"; ctx.textAlign = "center"; ctx.font = "bold 24px 'Courier New'";
        ctx.fillText("HAZ CLIC PARA EMPEZAR", canvas.width/2, canvas.height/2 - 10);
    }
    if (estado === 'GAMEOVER') {
        ctx.fillStyle = "rgba(255,255,255,0.7)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#d32f2f"; ctx.textAlign = "center"; ctx.font = "bold 36px 'Courier New'";
        ctx.fillText("¡CRASH!", canvas.width/2, canvas.height/2 - 25);
        ctx.fillStyle = "#333"; ctx.font = "bold 18px 'Courier New'";
        ctx.fillText("Haz clic para reintentar", canvas.width/2, canvas.height/2 + 20);
    }
  }

  // --- BUCLE DE LÓGICA ---
  function bucle() {
    if (estado !== 'JUGANDO') return;

    // Físicas
    if (!dino.agachado || dino.y < SUELO_Y) {
        dino.velY += gravedad;
        dino.y += dino.velY;
    } else {
        // Si se agacha, cae rápido
        dino.velY += gravedad * 2; 
        dino.y += dino.velY;
    }
    
    if (dino.y > SUELO_Y) { dino.y = SUELO_Y; dino.velY = 0; }

    // Movimiento
    obstaculo.x -= velocidadJuego;
    if (obstaculo.x < -50) { generarObstaculo(); }
    
    nubes.forEach(n => {
        n.x -= n.vel;
        if (n.x < -60) n.x = canvas.width + Math.random() * 100;
    });

    puntuacion += 0.1;
    velocidadJuego += 0.002;

    // Hitboxes (Diferentes si está agachado)
    let dH = { x: dino.x + 5, y: dino.y + 5, w: dino.ancho - 10, h: dino.alto - 10 };
    if (dino.agachado && dino.y === SUELO_Y) {
        dH.y = dino.y + 20; // Hitbox más baja
        dH.h = dino.alto - 20;
    }
    
    let cH = { x: obstaculo.x + 10, y: obstaculo.y + 10, w: obstaculo.ancho - 15, h: obstaculo.alto - 10 };

    // Detección de colisión
    if (dH.x < cH.x + cH.w && dH.x + dH.w > cH.x && dH.y < cH.y + cH.h && dH.h + dH.y > cH.y) {
        estado = 'GAMEOVER';
        if (puntuacion > maxPuntuacion) {
            maxPuntuacion = puntuacion;
            localStorage.setItem("dinoHighScore", maxPuntuacion);
        }
    }

    dibujar();

    if (estado === 'JUGANDO') {
        requestAnimationFrame(bucle);
    }
  }

  dibujar();

</script>
</body>
</html>
"""

components.html(codigo_juego, height=280)
