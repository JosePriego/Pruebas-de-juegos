import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Run & Gun Realista", layout="centered", page_icon="🪖")

st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    h1 { color: #1a1a1a; font-family: 'Impact', 'Courier New', sans-serif; text-align: center; font-weight: 900; letter-spacing: 2px;}
    .stMarkdown p { text-align: center; color: #444; font-family: 'Courier New', Courier, monospace; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.title("🪖 RUN & GUN: REALISMO TOTAL")
st.write("ESPACIO = Saltar | ABAJO = Cubrirse | TECLA X = ¡Disparar!")

codigo_juego = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { display: flex; justify-content: center; margin: 0; background-color: #e0e0e0; overflow: hidden; user-select: none; font-family: 'Courier New', Courier, monospace; }
  canvas { border: 4px solid #333; background-color: #8fb8e6; border-radius: 5px; cursor: pointer; box-shadow: 0px 8px 0px #111; }
</style>
</head>
<body>
<canvas id="juego" width="600" height="250" tabindex="1"></canvas>
<script>
  const canvas = document.getElementById("juego");
  const ctx = canvas.getContext("2d");

  // --- ⚠️ PEGA TUS ENLACES RAW AQUÍ ⚠️ ---
  const urlSoldado = "https://raw.githubusercontent.com/JosePriego/Pruebas-de-juegos/main/soldado.png"; 
  const urlTanque = "https://raw.githubusercontent.com/JosePriego/Pruebas-de-juegos/main/tanque.png";
  const urlHelicoptero = "Phttps://raw.githubusercontent.com/JosePriego/Pruebas-de-juegos/main/helicoptero.png";

  // --- CARGA DE IMÁGENES SEGURA ---
  // crossOrigin = "anonymous" evita que el navegador bloquee el juego
  const imgSoldado = new Image(); imgSoldado.crossOrigin = "anonymous"; imgSoldado.src = urlSoldado;
  const imgTanque = new Image(); imgTanque.crossOrigin = "anonymous"; imgTanque.src = urlTanque;
  const imgHeli = new Image(); imgHeli.crossOrigin = "anonymous"; imgHeli.src = urlHelicoptero;

  // --- VARIABLES ---
  const SUELO_Y = 170;
  let jugador = { x: 50, y: SUELO_Y, velY: 0, ancho: 50, alto: 60, agachado: false };
  let obstaculo = { x: 600, y: SUELO_Y, ancho: 70, alto: 50, tipo: 'tanque' };
  
  let balas = []; 
  let explosion = { activa: false, x: 0, y: 0, timer: 0 };
  
  let gravedad = 1.3;
  let puntuacion = 0;
  let maxPuntuacion = 0;
  try { maxPuntuacion = localStorage.getItem("realHighScore") || 0; } catch(e) {}
  
  let velocidadJuego = 6;
  let estado = 'INICIO';

  // --- CONTROLES ---
  function saltar() {
    if (estado === 'INICIO') { estado = 'JUGANDO'; requestAnimationFrame(bucle); } 
    else if (estado === 'GAMEOVER') { reiniciar(); requestAnimationFrame(bucle); } 
    else if (estado === 'JUGANDO' && jugador.y === SUELO_Y && !jugador.agachado) { jugador.velY = -16; }
  }

  canvas.addEventListener("keydown", (e) => { 
      if(e.code === "Space" || e.code === "ArrowUp") { e.preventDefault(); saltar(); }
      if(e.code === "ArrowDown" && estado === 'JUGANDO') { e.preventDefault(); jugador.agachado = true; }
      if((e.code === "KeyX" || e.key === "x") && estado === 'JUGANDO') {
          if (balas.length < 3) {
              let alturaFuego = jugador.agachado ? jugador.y + 30 : jugador.y + 20;
              balas.push({ x: jugador.x + 40, y: alturaFuego, w: 15, h: 4 });
          }
      }
  });
  
  canvas.addEventListener("keyup", (e) => { if(e.code === "ArrowDown") { jugador.agachado = false; } });
  canvas.addEventListener("mousedown", saltar);
  canvas.addEventListener("touchstart", (e) => { e.preventDefault(); saltar(); }, {passive: false});
  canvas.focus();

  function reiniciar() {
    jugador.y = SUELO_Y; jugador.velY = 0; jugador.agachado = false;
    obstaculo.x = 600; obstaculo.tipo = 'tanque'; obstaculo.y = SUELO_Y;
    balas = []; explosion.activa = false;
    puntuacion = 0; velocidadJuego = 6; estado = 'JUGANDO';
  }

  function generarObstaculo() {
      obstaculo.x = canvas.width + 50 + Math.random() * 200;
      if (Math.random() < 0.5) {
          obstaculo.tipo = 'helicoptero';
          obstaculo.y = SUELO_Y - 40; obstaculo.ancho = 80; obstaculo.alto = 40;
      } else {
          obstaculo.tipo = 'tanque';
          obstaculo.y = SUELO_Y; obstaculo.ancho = 70; obstaculo.alto = 50;
      }
  }

  // --- RENDERIZADO ---
  function dibujar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Suelo realista (Carretera/Asfalto)
    ctx.fillStyle = "#555"; ctx.fillRect(0, SUELO_Y + 50, canvas.width, canvas.height);
    ctx.fillStyle = "#333"; ctx.fillRect(0, SUELO_Y + 50, canvas.width, 10);

    ctx.fillStyle = "#111"; ctx.font = "bold 16px 'Courier New'"; ctx.textAlign = "right";
    ctx.fillText("RÉCORD: " + Math.floor(maxPuntuacion).toString().padStart(5, '0') + "  BAJAS: " + Math.floor(puntuacion).toString().padStart(5, '0'), canvas.width - 20, 20);
    ctx.textAlign = "left";

    // Dibujar Enemigos (Si la URL falla o está vacía, dibuja un recuadro negro por seguridad)
    if (obstaculo.tipo === 'tanque') {
        if(imgTanque.complete && imgTanque.naturalHeight !== 0 && urlTanque !== "https://raw.githubusercontent.com/JosePriego/Pruebas-de-juegos/main/tanque.png") {
            ctx.drawImage(imgTanque, obstaculo.x, obstaculo.y, obstaculo.ancho, obstaculo.alto);
        } else {
            ctx.fillStyle = 'black'; ctx.fillRect(obstaculo.x, obstaculo.y, obstaculo.ancho, obstaculo.alto);
        }
    } else {
        if(imgHeli.complete && imgHeli.naturalHeight !== 0 && urlHelicoptero !== "https://raw.githubusercontent.com/JosePriego/Pruebas-de-juegos/main/helicoptero.png") {
            ctx.drawImage(imgHeli, obstaculo.x, obstaculo.y, obstaculo.ancho, obstaculo.alto);
        } else {
            ctx.fillStyle = 'black'; ctx.fillRect(obstaculo.x, obstaculo.y, obstaculo.ancho, obstaculo.alto);
        }
    }

    // Balas y explosión simple
    balas.forEach(b => { ctx.fillStyle = '#ffcc00'; ctx.fillRect(b.x, b.y, b.w, b.h); });
    if (explosion.activa) {
        ctx.fillStyle = '#ff4500'; ctx.beginPath(); ctx.arc(explosion.x + 30, explosion.y + 20, 30, 0, Math.PI*2); ctx.fill();
    }

    // Dibujar Jugador
    if (estado === 'GAMEOVER') {
        ctx.fillStyle = 'red'; ctx.fillRect(jugador.x, jugador.y + 30, jugador.ancho, jugador.alto - 30);
    } else if (imgSoldado.complete && imgSoldado.naturalHeight !== 0 && urlSoldado !== "https://raw.githubusercontent.com/JosePriego/Pruebas-de-juegos/main/soldado.png") {
        if (jugador.agachado && jugador.y === SUELO_Y) {
            ctx.drawImage(imgSoldado, jugador.x, jugador.y + 25, jugador.ancho, jugador.alto - 25);
        } else {
            ctx.drawImage(imgSoldado, jugador.x, jugador.y, jugador.ancho, jugador.alto);
        }
    } else {
        // Fallback: Si no hay imagen, dibuja un rectángulo azul
        ctx.fillStyle = 'blue'; 
        if (jugador.agachado && jugador.y === SUELO_Y) { ctx.fillRect(jugador.x, jugador.y + 25, jugador.ancho, jugador.alto - 25); } 
        else { ctx.fillRect(jugador.x, jugador.y, jugador.ancho, jugador.alto); }
    }

    // Menús
    if (estado === 'INICIO') {
        ctx.fillStyle = "rgba(0, 0, 0, 0.7)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 24px 'Courier New'";
        ctx.fillText("CLIC PARA EMPEZAR", canvas.width/2, canvas.height/2 - 10);
    }
    if (estado === 'GAMEOVER') {
        ctx.fillStyle = "rgba(150, 0, 0, 0.8)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 36px 'Courier New'";
        ctx.fillText("ELIMINADO", canvas.width/2, canvas.height/2 - 25);
        ctx.font = "bold 18px 'Courier New'"; ctx.fillText("Haz clic para intentar de nuevo", canvas.width/2, canvas.height/2 + 20);
    }
  }

  // --- BUCLE DE LÓGICA ---
  function bucle() {
    if (estado !== 'JUGANDO') return;

    if (!jugador.agachado || jugador.y < SUELO_Y) { jugador.velY += gravedad; jugador.y += jugador.velY; } 
    else { jugador.velY += gravedad * 2; jugador.y += jugador.velY; }
    if (jugador.y > SUELO_Y) { jugador.y = SUELO_Y; jugador.velY = 0; }

    obstaculo.x -= velocidadJuego;
    if (obstaculo.x < -100) { generarObstaculo(); }

    puntuacion += 0.1; velocidadJuego += 0.002; 

    // Hitbox adaptada a las nuevas proporciones
    let cH = { x: obstaculo.x + 10, y: obstaculo.y + 10, w: obstaculo.ancho - 20, h: obstaculo.alto - 20 };

    for (let i = balas.length - 1; i >= 0; i--) {
        balas[i].x += 14; 
        let b = balas[i];
        let bH = { x: b.x, y: b.y, w: b.w, h: b.h };

        if (bH.x < cH.x + cH.w && bH.x + bH.w > cH.x && bH.y < cH.y + cH.h && bH.h + bH.y > cH.y) {
            explosion = { activa: true, x: obstaculo.x, y: obstaculo.y, timer: 8 };
            puntuacion += 10; generarObstaculo(); balas.splice(i, 1); continue;
        }
        if (b.x > canvas.width) { balas.splice(i, 1); }
    }

    if (explosion.activa) { explosion.x -= velocidadJuego; explosion.timer--; if (explosion.timer <= 0) explosion.activa = false; }

    let dH = { x: jugador.x + 10, y: jugador.y + 5, w: jugador.ancho - 20, h: jugador.alto - 10 };
    if (jugador.agachado && jugador.y === SUELO_Y) { dH.y = jugador.y + 30; dH.h = jugador.alto - 30; }

    if (dH.x < cH.x + cH.w && dH.x + dH.w > cH.x && dH.y < cH.y + cH.h && dH.h + dH.y > cH.y) {
        estado = 'GAMEOVER';
        if (puntuacion > maxPuntuacion) {
            maxPuntuacion = puntuacion;
            try { localStorage.setItem("realHighScore", maxPuntuacion); } catch(e) {}
        }
    }

    dibujar();
    if (estado === 'JUGANDO') { requestAnimationFrame(bucle); }
  }

  // Render inicial seguro
  setTimeout(dibujar, 300);

</script>
</body>
</html>
"""

components.html(codigo_juego, height=280)
