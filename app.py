import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Run & Gun", layout="centered", page_icon="🪖")

st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    h1 { color: #2b4522; font-family: 'Impact', 'Courier New', sans-serif; text-align: center; font-weight: 900; letter-spacing: 2px;}
    .stMarkdown p { text-align: center; color: #4a5d23; font-family: 'Courier New', Courier, monospace; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.title("🪖 RUN & GUN: CÓDIGO PURO")
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

  // --- VARIABLES ---
  const SUELO_Y = 170;
  let jugador = { x: 50, y: SUELO_Y, velY: 0, ancho: 30, alto: 45, agachado: false };
  let obstaculo = { x: 600, y: SUELO_Y + 10, ancho: 40, alto: 35, tipo: 'tanque' };
  let nubes = [ {x: 100, y: 40, vel: 0.5}, {x: 350, y: 70, vel: 0.3}, {x: 550, y: 30, vel: 0.4} ];
  
  let balas = []; 
  let explosion = { activa: false, x: 0, y: 0, timer: 0 };
  
  let gravedad = 1.3;
  let puntuacion = 0;
  let maxPuntuacion = 0;
  
  // Protección contra bloqueos del navegador al leer la memoria
  try { maxPuntuacion = localStorage.getItem("soldierHighScore") || 0; } catch(e) {}
  
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
      if((e.code === "KeyX" || e.key === "x") && estado === 'JUGANDO') {
          if (balas.length < 3) {
              let alturaFuego = jugador.agachado ? jugador.y + 25 : jugador.y + 15;
              balas.push({ x: jugador.x + 30, y: alturaFuego, w: 15, h: 4 });
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
    obstaculo.x = 600; obstaculo.tipo = 'tanque'; obstaculo.y = SUELO_Y + 10;
    balas = []; explosion.activa = false;
    puntuacion = 0; velocidadJuego = 6;
    estado = 'JUGANDO';
  }

  function generarObstaculo() {
      obstaculo.x = canvas.width + 50 + Math.random() * 200;
      if (Math.random() < 0.5) {
          obstaculo.tipo = 'helicoptero';
          obstaculo.y = SUELO_Y - 20; obstaculo.ancho = 55; obstaculo.alto = 25;
      } else {
          obstaculo.tipo = 'tanque';
          obstaculo.y = SUELO_Y + 10; obstaculo.ancho = 40; obstaculo.alto = 35;
      }
  }

  // --- DIBUJO MATEMÁTICO (PIXEL ART) ---
  function dibujarSoldado(x, y, agachado) {
      if(estado === 'GAMEOVER') {
          // Calavera simple
          ctx.fillStyle = '#fff'; ctx.fillRect(x+5, y+25, 20, 20);
          ctx.fillStyle = '#000'; ctx.fillRect(x+10, y+30, 4, 4); ctx.fillRect(x+16, y+30, 4, 4);
          return;
      }
      ctx.fillStyle = '#4a5d23';
      if(agachado) {
          ctx.fillRect(x, y+20, 25, 25); // Cuerpo agachado
          ctx.fillStyle = '#ffcc99'; ctx.fillRect(x+10, y+10, 12, 12); // Cara
          ctx.fillStyle = '#2b4522'; ctx.fillRect(x+8, y+5, 16, 6); // Casco
          ctx.fillRect(x+20, y+25, 15, 4); // Arma
      } else {
          ctx.fillRect(x+5, y+15, 15, 20); // Cuerpo
          ctx.fillStyle = '#ffcc99'; ctx.fillRect(x+5, y+5, 12, 10); // Cara
          ctx.fillStyle = '#2b4522'; ctx.fillRect(x+3, y, 16, 6); // Casco
          ctx.fillRect(x+20, y+20, 15, 4); // Arma
          ctx.fillRect(x+5, y+35, 6, 10); ctx.fillRect(x+14, y+35, 6, 10); // Piernas
      }
  }

  function dibujarTanque(x, y) {
      ctx.fillStyle = '#1a2e12'; ctx.fillRect(x, y+20, 40, 15); // Orugas
      ctx.fillStyle = '#4a5d23'; ctx.fillRect(x+5, y+5, 30, 15); // Chasis
      ctx.fillStyle = '#2b4522'; ctx.fillRect(x-10, y+10, 20, 5); // Cañon
      ctx.fillStyle = '#000'; ctx.fillRect(x+5, y+25, 30, 5); // Detalle ruedas
  }

  function dibujarHeli(x, y) {
      ctx.fillStyle = '#4a5d23'; ctx.fillRect(x+10, y+10, 30, 15); // Cabina
      ctx.fillStyle = '#87cefa'; ctx.fillRect(x+10, y+10, 10, 10); // Cristal
      ctx.fillStyle = '#2b4522'; ctx.fillRect(x+40, y+15, 15, 5); // Cola
      ctx.fillRect(x+50, y+5, 5, 10); // Rotor cola
      ctx.fillStyle = '#1a2e12'; ctx.fillRect(x+15, y, 20, 3); // Hélice
      ctx.fillRect(x+24, y+3, 2, 7); // Eje
  }

  function dibujarExplosion(x, y) {
      ctx.fillStyle = '#ff4500'; ctx.beginPath(); ctx.arc(x+20, y+15, 25, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = '#ffa500'; ctx.beginPath(); ctx.arc(x+20, y+15, 15, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = '#ffff00'; ctx.beginPath(); ctx.arc(x+20, y+15, 8, 0, Math.PI*2); ctx.fill();
  }

  function dibujarBala(x, y) {
      ctx.fillStyle = '#ffff00'; ctx.fillRect(x, y, 15, 4);
      ctx.fillStyle = '#ff4500'; ctx.fillRect(x-5, y, 5, 4);
  }

  function dibujarNube(x, y) {
      ctx.fillStyle = "rgba(255, 255, 255, 0.7)";
      ctx.fillRect(x, y, 40, 15); ctx.fillRect(x + 10, y - 10, 20, 10);
  }

  // --- RENDERIZADO GENERAL ---
  function dibujar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    nubes.forEach(n => dibujarNube(n.x, n.y));

    // Suelo
    ctx.fillStyle = "#637c3b"; ctx.fillRect(0, SUELO_Y + 45, canvas.width, canvas.height);
    ctx.strokeStyle = "#2b4522"; ctx.lineWidth = 4; ctx.beginPath(); 
    ctx.moveTo(0, SUELO_Y + 45); ctx.lineTo(canvas.width, SUELO_Y + 45); ctx.stroke();

    ctx.fillStyle = "#2b4522"; ctx.font = "bold 16px 'Courier New'"; ctx.textAlign = "right";
    ctx.fillText("RÉCORD: " + Math.floor(maxPuntuacion).toString().padStart(5, '0') + "  BAJAS: " + Math.floor(puntuacion).toString().padStart(5, '0'), canvas.width - 20, 20);
    ctx.textAlign = "left";

    // Enemigos
    if (obstaculo.tipo === 'tanque') { dibujarTanque(obstaculo.x, obstaculo.y); } 
    else { dibujarHeli(obstaculo.x, obstaculo.y); }

    // Efectos y balas
    if (explosion.activa) { dibujarExplosion(explosion.x, explosion.y); }
    balas.forEach(b => dibujarBala(b.x, b.y));

    // Jugador
    dibujarSoldado(jugador.x, jugador.y, jugador.agachado);

    // Menús
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
    if (obstaculo.x < -60) { generarObstaculo(); }
    
    nubes.forEach(n => { n.x -= n.vel; if (n.x < -60) n.x = canvas.width + Math.random() * 100; });

    puntuacion += 0.1;
    velocidadJuego += 0.002; 

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

    let dH = { x: jugador.x + 5, y: jugador.y + 5, w: 20, h: 35 };
    if (jugador.agachado && jugador.y === SUELO_Y) {
        dH.y = jugador.y + 20; dH.h = 25; 
    }

    if (dH.x < cH.x + cH.w && dH.x + dH.w > cH.x && dH.y < cH.y + cH.h && dH.h + dH.y > cH.y) {
        estado = 'GAMEOVER';
        if (puntuacion > maxPuntuacion) {
            maxPuntuacion = puntuacion;
            try { localStorage.setItem("soldierHighScore", maxPuntuacion); } catch(e) {}
        }
    }

    dibujar();
    if (estado === 'JUGANDO') { requestAnimationFrame(bucle); }
  }

  // Dibujar inmediatamente
  dibujar();

</script>
</body>
</html>
"""

components.html(codigo_juego, height=280)
