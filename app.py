import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Run & Gun", layout="centered", page_icon="🪖")

# Estilo de la página
st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    h1 { color: #2b4522; font-family: 'Impact', 'Courier New', sans-serif; text-align: center; font-weight: 900; letter-spacing: 2px;}
    .stMarkdown p { text-align: center; color: #4a5d23; font-family: 'Courier New', Courier, monospace; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.title("🪖 RUN & GUN: OPERACIÓN PIXEL")
st.write("ESPACIO = Saltar | ABAJO = Cubrirse | TECLA X = ¡Disparar!")

codigo_juego = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { display: flex; justify-content: center; margin: 0; background-color: #f0f4f0; overflow: hidden; user-select: none; font-family: 'Courier New', Courier, monospace; }
  canvas { border: 4px solid #2b4522; background-color: #d1dcc3; border-radius: 5px; cursor: pointer; box-shadow: 0px 8px 0px #1a2e12; }
</style>
</head>
<body>
<canvas id="juego" width="600" height="250" tabindex="1"></canvas>
<script>
  const canvas = document.getElementById("juego");
  const ctx = canvas.getContext("2d");

  // --- CARGA DE IMÁGENES EXTERNAS (PNG) ---
  const imgSoldado = new Image(); imgSoldado.src = "https://img.icons8.com/color/48/soldier-male.png";
  const imgTanque = new Image(); imgTanque.src = "https://img.icons8.com/color/48/tank.png";
  const imgHeli = new Image(); imgHeli.src = "https://img.icons8.com/color/48/helicopter.png";
  const imgMisil = new Image(); imgMisil.src = "https://img.icons8.com/color/48/missile.png";
  const imgExplosion = new Image(); imgExplosion.src = "https://img.icons8.com/color/48/boom.png";
  const imgCalavera = new Image(); imgCalavera.src = "https://img.icons8.com/color/48/skull.png";

  // --- VARIABLES ---
  const SUELO_Y = 170;
  let jugador = { x: 50, y: SUELO_Y, velY: 0, ancho: 40, alto: 45, agachado: false };
  let obstaculo = { x: 600, y: SUELO_Y + 5, ancho: 45, alto: 40, tipo: 'tanque' };
  let nubes = [ {x: 100, y: 40, vel: 0.5}, {x: 350, y: 70, vel: 0.3}, {x: 550, y: 30, vel: 0.4} ];
  
  let balas = []; 
  let explosion = { activa: false, x: 0, y: 0, timer: 0 };
  
  let gravedad = 1.3;
  let puntuacion = 0;
  let maxPuntuacion = localStorage.getItem("soldierHighScore") || 0; 
  let velocidadJuego = 6;
  let estado = 'INICIO';

  // --- CONTROLES ---
  function saltar() {
    if (estado === 'INICIO') { 
        estado = 'JUGANDO'; requestAnimationFrame(bucle); 
    } else if (estado === 'GAMEOVER') { 
        reiniciar(); requestAnimationFrame(bucle); 
    } else if (estado === 'JUGANDO' && jugador.y === SUELO_Y && !jugador.agachado) {
        jugador.velY = -15; 
    }
  }

  canvas.addEventListener("keydown", (e) => { 
      if(e.code === "Space" || e.code === "ArrowUp") { e.preventDefault(); saltar(); }
      if(e.code === "ArrowDown" && estado === 'JUGANDO') { e.preventDefault(); jugador.agachado = true; }
      
      // Disparar
      if((e.code === "KeyX" || e.key === "x") && estado === 'JUGANDO') {
          if (balas.length < 3) {
              let alturaFuego = jugador.agachado ? jugador.y + 25 : jugador.y + 15;
              balas.push({ x: jugador.x + 35, y: alturaFuego, w: 25, h: 10 });
          }
      }
  });
  
  canvas.addEventListener("keyup", (e) => {
      if(e.code === "ArrowDown") { jugador.agachado = false; }
  });

  canvas.addEventListener("mousedown", saltar);
  canvas.addEventListener("touchstart", (e) => { e.preventDefault(); saltar(); }, {passive: false});
  canvas.focus();

  function reiniciar() {
    jugador.y = SUELO_Y; jugador.velY = 0; jugador.agachado = false;
    obstaculo.x = 600; obstaculo.tipo = 'tanque'; obstaculo.y = SUELO_Y + 5;
    balas = []; 
    explosion.activa = false;
    puntuacion = 0; velocidadJuego = 6;
    estado = 'JUGANDO';
  }

  function generarObstaculo() {
      obstaculo.x = canvas.width + 50 + Math.random() * 200;
      if (Math.random() < 0.5) {
          obstaculo.tipo = 'helicoptero';
          obstaculo.y = SUELO_Y - 20; 
          obstaculo.ancho = 50; 
          obstaculo.alto = 35;
      } else {
          obstaculo.tipo = 'tanque';
          obstaculo.y = SUELO_Y + 10;
          obstaculo.ancho = 45;
          obstaculo.alto = 35;
      }
  }

  // --- RENDERIZADO ---
  function dibujar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Nubes (usamos rectángulos para simular nubes retro)
    ctx.fillStyle = "rgba(255, 255, 255, 0.7)";
    nubes.forEach(n => { 
        ctx.fillRect(n.x, n.y, 40, 15);
        ctx.fillRect(n.x + 10, n.y - 10, 20, 10);
    });

    // Suelo
    ctx.fillStyle = "#637c3b";
    ctx.fillRect(0, SUELO_Y + 45, canvas.width, canvas.height);
    ctx.strokeStyle = "#2b4522"; ctx.lineWidth = 4; ctx.beginPath(); 
    ctx.moveTo(0, SUELO_Y + 45); ctx.lineTo(canvas.width, SUELO_Y + 45); ctx.stroke();

    // Textos de Puntuación
    ctx.fillStyle = "#2b4522"; ctx.font = "bold 16px 'Courier New'"; 
    ctx.textAlign = "right";
    ctx.fillText("RÉCORD: " + Math.floor(maxPuntuacion).toString().padStart(5, '0') + "  BAJAS: " + Math.floor(puntuacion).toString().padStart(5, '0'), canvas.width - 20, 20);
    ctx.textAlign = "left";

    // Dibujar Enemigo (Tanque o Helicóptero)
    if (obstaculo.tipo === 'tanque' && imgTanque.complete) { 
        ctx.drawImage(imgTanque, obstaculo.x, obstaculo.y, obstaculo.ancho, obstaculo.alto); 
    } else if (obstaculo.tipo === 'helicoptero' && imgHeli.complete) { 
        ctx.drawImage(imgHeli, obstaculo.x, obstaculo.y, obstaculo.ancho, obstaculo.alto); 
    }

    // Dibujar Explosión
    if (explosion.activa && imgExplosion.complete) {
        ctx.drawImage(imgExplosion, explosion.x, explosion.y, 50, 50);
    }

    // Dibujar Proyectiles
    balas.forEach(b => { 
        if(imgMisil.complete) ctx.drawImage(imgMisil, b.x, b.y - 10, 30, 30); 
    });

    // Dibujar Soldado
    if (estado === 'GAMEOVER' && imgCalavera.complete) { 
        ctx.drawImage(imgCalavera, jugador.x, jugador.y, jugador.ancho, jugador.alto); 
    } else if (jugador.agachado && jugador.y === SUELO_Y && imgSoldado.complete) { 
        // Truco retro: aplastar la imagen para simular que se agacha
        ctx.drawImage(imgSoldado, jugador.x, jugador.y + 20, jugador.ancho, jugador.alto - 20); 
    } else if (imgSoldado.complete) { 
        ctx.drawImage(imgSoldado, jugador.x, jugador.y, jugador.ancho, jugador.alto); 
    }

    // Pantallas de menú
    if (estado === 'INICIO') {
        ctx.fillStyle = "rgba(43, 69, 34, 0.85)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 24px 'Courier New'";
        ctx.fillText("CLIC PARA INICIAR MISIÓN", canvas.width/2, canvas.height/2 - 10);
    }
    if (estado === 'GAMEOVER') {
        ctx.fillStyle = "rgba(139, 0, 0, 0.85)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 36px 'Courier New'";
        ctx.fillText("M I S I Ó N   F A L L I D A", canvas.width/2, canvas.height/2 - 25);
        ctx.font = "bold 18px 'Courier New'";
        ctx.fillText("Haz clic para solicitar refuerzos", canvas.width/2, canvas.height/2 + 20);
    }
  }

  // --- BUCLE DE LÓGICA ---
  function bucle() {
    if (estado !== 'JUGANDO') return;

    if (!jugador.agachado || jugador.y < SUELO_Y) { jugador.velY += gravedad; jugador.y += jugador.velY; } 
    else { jugador.velY += gravedad * 2; jugador.y += jugador.velY; }
    if (jugador.y > SUELO_Y) { jugador.y = SUELO_Y; jugador.velY = 0; }

    obstaculo.x -= velocidadJuego;
    if (obstaculo.x < -50) { generarObstaculo(); }
    
    nubes.forEach(n => { n.x -= n.vel; if (n.x < -60) n.x = canvas.width + Math.random() * 100; });

    puntuacion += 0.1;
    velocidadJuego += 0.002; 

    // Hitboxes ajustadas a las imágenes PNG
    let cH = { x: obstaculo.x + 5, y: obstaculo.y + 5, w: obstaculo.ancho - 10, h: obstaculo.alto - 10 };

    for (let i = balas.length - 1; i >= 0; i--) {
        balas[i].x += 12; 
        
        let b = balas[i];
        let bH = { x: b.x, y: b.y, w: b.w, h: b.h };

        if (bH.x < cH.x + cH.w && bH.x + bH.w > cH.x && bH.y < cH.y + cH.h && bH.h + bH.y > cH.y) {
            explosion = { activa: true, x: obstaculo.x, y: obstaculo.y - 10, timer: 10 };
            puntuacion += 10; 
            generarObstaculo(); 
            balas.splice(i, 1); 
            continue;
        }

        if (b.x > canvas.width) { balas.splice(i, 1); }
    }

    if (explosion.activa) {
        explosion.x -= velocidadJuego; 
        explosion.timer--;
        if (explosion.timer <= 0) explosion.activa = false;
    }

    let dH = { x: jugador.x + 10, y: jugador.y + 5, w: jugador.ancho - 20, h: jugador.alto - 10 };
    if (jugador.agachado && jugador.y === SUELO_Y) {
        dH.y = jugador.y + 25; 
        dH.h = jugador.alto - 25; 
    }

    if (dH.x < cH.x + cH.w && dH.x + dH.w > cH.x && dH.y < cH.y + cH.h && dH.h + dH.y > cH.y) {
        estado = 'GAMEOVER';
        if (puntuacion > maxPuntuacion) {
            maxPuntuacion = puntuacion;
            localStorage.setItem("soldierHighScore", maxPuntuacion);
        }
    }

    dibujar();

    if (estado === 'JUGANDO') {
        requestAnimationFrame(bucle);
    }
  }

  // Esperar un poquito a que carguen las imágenes antes de dibujar el inicio
  setTimeout(dibujar, 500);

</script>
</body>
</html>
"""

components.html(codigo_juego, height=280)
