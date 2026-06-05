import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="T-Rex Acción", layout="centered", page_icon="🦖")

st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    h1 { color: #d32f2f; font-family: 'Courier New', Courier, monospace; text-align: center; font-weight: 900;}
    .stMarkdown p { text-align: center; color: #333; font-family: 'Courier New', Courier, monospace;}
</style>
""", unsafe_allow_html=True)

st.title("🦖 T-REX: ACCIÓN Y FUEGO 🔥")
st.write("**Espacio** = Saltar | **Abajo** = Agacharse | **Tecla X** = ¡Disparar Fuego!")

codigo_juego = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { display: flex; justify-content: center; margin: 0; background-color: #1a1a1a; overflow: hidden; user-select: none; font-family: 'Courier New', Courier, monospace; }
  canvas { border: 4px solid #d32f2f; background-color: #ffebee; border-radius: 10px; cursor: pointer; box-shadow: 0px 0px 15px #d32f2f; }
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
  let obstaculo = { x: 600, y: SUELO_Y + 5, ancho: 25, alto: 35, tipo: 'cactus' };
  let nubes = [ {x: 100, y: 40, vel: 0.5}, {x: 350, y: 70, vel: 0.3}, {x: 550, y: 30, vel: 0.4} ];
  
  // NUEVO: Array para guardar las bolas de fuego y efecto de explosión
  let balas = []; 
  let explosion = { activa: false, x: 0, y: 0, timer: 0 };
  
  let gravedad = 1.3;
  let puntuacion = 0;
  let maxPuntuacion = localStorage.getItem("dinoActionHighScore") || 0; 
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
      
      // NUEVO: Disparar con la tecla X
      if((e.code === "KeyX" || e.key === "x") && estado === 'JUGANDO') {
          // Evitar ametralladora infinita (máximo 3 balas en pantalla)
          if (balas.length < 3) {
              let alturaFuego = dino.agachado ? dino.y + 20 : dino.y + 10;
              balas.push({ x: dino.x + 35, y: alturaFuego, w: 20, h: 20 });
          }
      }
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
    balas = []; // Limpiar balas
    explosion.activa = false;
    puntuacion = 0; velocidadJuego = 6;
    estado = 'JUGANDO';
  }

  function generarObstaculo() {
      obstaculo.x = canvas.width + 50 + Math.random() * 200;
      if (Math.random() < 0.5) {
          obstaculo.tipo = 'pajaro';
          obstaculo.y = SUELO_Y - 10; 
          obstaculo.ancho = 35;
          obstaculo.alto = 25;
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

    ctx.fillStyle = "#333"; ctx.font = "bold 16px 'Courier New'"; 
    ctx.textAlign = "right";
    ctx.fillText("HI: " + Math.floor(maxPuntuacion).toString().padStart(5, '0') + "  " + Math.floor(puntuacion).toString().padStart(5, '0'), canvas.width - 20, 20);
    ctx.textAlign = "left";

    // Dibujar Enemigo
    ctx.font = "40px Arial";
    if (obstaculo.tipo === 'cactus') { ctx.fillText("🌵", obstaculo.x, obstaculo.y); } 
    else { ctx.fillText("🦅", obstaculo.x, obstaculo.y); }

    // Dibujar Explosión si está activa
    if (explosion.activa) {
        ctx.font = "40px Arial";
        ctx.fillText("💥", explosion.x, explosion.y);
    }

    // Dibujar Balas de Fuego
    ctx.font = "20px Arial";
    balas.forEach(b => { ctx.fillText("🔥", b.x, b.y - 5); });

    // Dibujar Dino
    ctx.font = "40px Arial";
    if (estado === 'GAMEOVER') { ctx.fillText("😵", dino.x, dino.y); } 
    else if (dino.agachado && dino.y === SUELO_Y) { ctx.fillText("🐊", dino.x, dino.y + 10); } 
    else { ctx.fillText("🦖", dino.x, dino.y); }

    // Pantallas de menú
    if (estado === 'INICIO') {
        ctx.fillStyle = "rgba(0,0,0,0.8)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 24px 'Courier New'";
        ctx.fillText("HAZ CLIC PARA EMPEZAR", canvas.width/2, canvas.height/2 - 10);
    }
    if (estado === 'GAMEOVER') {
        ctx.fillStyle = "rgba(200,0,0,0.8)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 36px 'Courier New'";
        ctx.fillText("¡ELIMINADO!", canvas.width/2, canvas.height/2 - 25);
        ctx.font = "bold 18px 'Courier New'";
        ctx.fillText("Haz clic para intentar de nuevo", canvas.width/2, canvas.height/2 + 20);
    }
  }

  // --- BUCLE DE LÓGICA ---
  function bucle() {
    if (estado !== 'JUGANDO') return;

    // Movimiento del Dino
    if (!dino.agachado || dino.y < SUELO_Y) { dino.velY += gravedad; dino.y += dino.velY; } 
    else { dino.velY += gravedad * 2; dino.y += dino.velY; }
    if (dino.y > SUELO_Y) { dino.y = SUELO_Y; dino.velY = 0; }

    // Movimiento Entorno
    obstaculo.x -= velocidadJuego;
    if (obstaculo.x < -50) { generarObstaculo(); }
    
    nubes.forEach(n => { n.x -= n.vel; if (n.x < -60) n.x = canvas.width + Math.random() * 100; });

    puntuacion += 0.1;
    velocidadJuego += 0.002; // Aumenta la velocidad

    // Hitbox del Enemigo (compartida para dino y balas)
    let cH = { x: obstaculo.x + 10, y: obstaculo.y + 10, w: obstaculo.ancho - 15, h: obstaculo.alto - 15 };

    // --- LÓGICA DE DISPAROS ---
    for (let i = balas.length - 1; i >= 0; i--) {
        balas[i].x += 10; // Velocidad de la bola de fuego
        
        let b = balas[i];
        let bH = { x: b.x, y: b.y, w: b.w, h: b.h };

        // Comprobar colisión Bala vs Enemigo
        if (bH.x < cH.x + cH.w && bH.x + bH.w > cH.x && bH.y < cH.y + cH.h && bH.h + bH.y > cH.y) {
            // ¡Impacto!
            explosion = { activa: true, x: obstaculo.x, y: obstaculo.y, timer: 10 };
            puntuacion += 10; // Bonus por destruir
            generarObstaculo(); // El enemigo reaparece lejos
            balas.splice(i, 1); // Destruir la bala
            continue;
        }

        // Eliminar bala si sale de la pantalla
        if (b.x > canvas.width) { balas.splice(i, 1); }
    }

    // Gestionar tiempo del emoji de explosión
    if (explosion.activa) {
        explosion.x -= velocidadJuego; // La explosión se mueve con el fondo
        explosion.timer--;
        if (explosion.timer <= 0) explosion.activa = false;
    }

    // --- LÓGICA COLISIÓN DEL DINO ---
    let dH = { x: dino.x + 5, y: dino.y + 5, w: dino.ancho - 10, h: dino.alto - 10 };
    if (dino.agachado && dino.y === SUELO_Y) {
        dH.y = dino.y + 20; 
        dH.h = dino.alto - 20; 
    }

    if (dH.x < cH.x + cH.w && dH.x + dH.w > cH.x && dH.y < cH.y + cH.h && dH.h + dH.y > cH.y) {
        estado = 'GAMEOVER';
        if (puntuacion > maxPuntuacion) {
            maxPuntuacion = puntuacion;
            localStorage.setItem("dinoActionHighScore", maxPuntuacion);
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
