import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(page_title="Metal Slug Demo", layout="centered", page_icon="💥")

st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    h1 { color: #8b0000; font-family: 'Impact', 'Courier New', sans-serif; text-align: center; font-weight: 900; letter-spacing: 3px; text-shadow: 2px 2px 0px #000;}
    .stMarkdown p { text-align: center; color: #444; font-family: 'Courier New', Courier, monospace; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.title("💥 OPERACIÓN: METAL PIXEL")
st.write("ESPACIO = Saltar | ABAJO = Cubrirse | TECLA X = Disparar")

# --- LA MAGIA DE PYTHON (INYECCIÓN DE IMÁGENES) ---
def cargar_imagen_local(nombre_archivo):
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, "rb") as f:
            data = f.read()
            return "data:image/png;base64," + base64.b64encode(data).decode()
    return "" 

codigo_soldado = cargar_imagen_local("soldado.png")
codigo_tanque = cargar_imagen_local("tanque.png")
codigo_heli = cargar_imagen_local("helicoptero.png")

# --- MOTOR DEL JUEGO WEB ---
codigo_juego = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { display: flex; justify-content: center; margin: 0; background-color: #2c2c2c; overflow: hidden; user-select: none; font-family: 'Courier New', Courier, monospace; }
  canvas { border: 4px solid #111; background-color: #8c9c9a; border-radius: 5px; cursor: pointer; box-shadow: 0px 8px 0px #000; }
</style>
</head>
<body>
<canvas id="juego" width="600" height="250" tabindex="1"></canvas>
<script>
  const canvas = document.getElementById("juego");
  const ctx = canvas.getContext("2d");

  // Inyección de imágenes
  const imgSoldado = new Image(); let srcSol = "INYECTAR_SOLDADO"; if(srcSol.length > 50) imgSoldado.src = srcSol;
  const imgTanque = new Image(); let srcTan = "INYECTAR_TANQUE"; if(srcTan.length > 50) imgTanque.src = srcTan;
  const imgHeli = new Image(); let srcHel = "INYECTAR_HELI"; if(srcHel.length > 50) imgHeli.src = srcHel;

  // --- VARIABLES ---
  const SUELO_Y = 170;
  
  // Jugador ahora tiene Vidas e Invulnerabilidad temporal
  let jugador = { x: 50, y: SUELO_Y, velY: 0, ancho: 55, alto: 65, agachado: false, vidas: 3, invencible: 0 };
  let obstaculo = { x: 600, y: SUELO_Y, ancho: 70, alto: 50, tipo: 'tanque' };
  
  let balas = []; 
  let balasEnemigas = []; // ¡Los enemigos disparan!
  let explosiones = []; // Múltiples explosiones a la vez
  
  let fondoEdificios = 0; // Para el efecto Parallax
  
  let gravedad = 1.3;
  let puntuacion = 0;
  let maxPuntuacion = 0;
  try { maxPuntuacion = localStorage.getItem("metalHighScore") || 0; } catch(e) {}
  
  let velocidadJuego = 6; 
  let estado = 'INICIO';

  // --- CONTROLES ---
  function saltar() {
    if (estado === 'INICIO') { estado = 'JUGANDO'; requestAnimationFrame(bucle); } 
    else if (estado === 'GAMEOVER') { reiniciar(); requestAnimationFrame(bucle); } 
    else if (estado === 'JUGANDO' && jugador.y === SUELO_Y && !jugador.agachado) { jugador.velY = -16.5; }
  }

  canvas.addEventListener("keydown", (e) => { 
      if(e.code === "Space" || e.code === "ArrowUp") { e.preventDefault(); saltar(); }
      if(e.code === "ArrowDown" && estado === 'JUGANDO') { e.preventDefault(); jugador.agachado = true; }
      if((e.code === "KeyX" || e.key === "x") && estado === 'JUGANDO') {
          // Cadencia de fuego más alta
          if (balas.length < 5) {
              let alturaFuego = jugador.agachado ? jugador.y + 35 : jugador.y + 25;
              balas.push({ x: jugador.x + 45, y: alturaFuego, w: 12, h: 4 });
          }
      }
  });
  canvas.addEventListener("keyup", (e) => { if(e.code === "ArrowDown") { jugador.agachado = false; } });
  canvas.addEventListener("mousedown", saltar);
  canvas.addEventListener("touchstart", (e) => { e.preventDefault(); saltar(); }, {passive: false});
  canvas.focus();

  function reiniciar() {
    jugador = { x: 50, y: SUELO_Y, velY: 0, ancho: 55, alto: 65, agachado: false, vidas: 3, invencible: 0 };
    obstaculo.x = 800; obstaculo.tipo = 'tanque'; obstaculo.y = SUELO_Y;
    balas = []; balasEnemigas = []; explosiones = [];
    puntuacion = 0; velocidadJuego = 6; estado = 'JUGANDO';
  }

  function generarObstaculo() {
      obstaculo.x = canvas.width + 100 + Math.random() * 200;
      if (Math.random() < 0.5) {
          obstaculo.tipo = 'helicoptero';
          obstaculo.y = SUELO_Y - 40; 
          obstaculo.ancho = 90; obstaculo.alto = 45;
      } else {
          obstaculo.tipo = 'tanque';
          obstaculo.y = SUELO_Y; 
          obstaculo.ancho = 70; obstaculo.alto = 50;
      }
  }
  
  function recibirDano() {
      if (jugador.invencible <= 0) {
          jugador.vidas--;
          jugador.invencible = 60; // 60 frames (1 segundo) de invulnerabilidad
          explosiones.push({x: jugador.x, y: jugador.y, timer: 15}); // Explosión en ti
          if (jugador.vidas <= 0) {
              estado = 'GAMEOVER';
              if (puntuacion > maxPuntuacion) {
                  maxPuntuacion = puntuacion;
                  try { localStorage.setItem("metalHighScore", maxPuntuacion); } catch(e) {}
              }
          }
      }
  }

  // --- RENDERIZADO ---
  function dibujar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Fondo Parallax (Edificios en ruinas)
    ctx.fillStyle = "#5c6b69";
    for(let i=0; i<10; i++) {
        let posX = ((i * 120) - fondoEdificios) % 720;
        if(posX < -120) posX += 720;
        // Dibujamos rascacielos simples
        ctx.fillRect(posX, SUELO_Y - 80 + (i%3)*20, 60, 150);
        ctx.fillRect(posX+60, SUELO_Y - 50, 40, 100);
    }

    // Suelo
    ctx.fillStyle = "#333"; ctx.fillRect(0, SUELO_Y + 50, canvas.width, canvas.height);
    ctx.fillStyle = "#111"; ctx.fillRect(0, SUELO_Y + 50, canvas.width, 10);

    // UI: Puntos
    ctx.fillStyle = "#111"; ctx.font = "bold 16px 'Courier New'"; ctx.textAlign = "right";
    ctx.fillText("HI: " + Math.floor(maxPuntuacion).toString().padStart(5, '0') + "  PTS: " + Math.floor(puntuacion).toString().padStart(5, '0'), canvas.width - 10, 20);
    ctx.textAlign = "left";

    // UI: Vidas (Corazones)
    ctx.fillStyle = "#d32f2f"; ctx.font = "20px Arial";
    let corazones = "";
    for(let v=0; v<jugador.vidas; v++) corazones += "❤️";
    ctx.fillText(corazones, 10, 15);

    // Enemigo
    if (obstaculo.tipo === 'tanque') {
        if(imgTanque.complete && imgTanque.naturalHeight !== 0) ctx.drawImage(imgTanque, obstaculo.x, obstaculo.y, obstaculo.ancho, obstaculo.alto);
        else { ctx.fillStyle = 'black'; ctx.fillRect(obstaculo.x, obstaculo.y, obstaculo.ancho, obstaculo.alto); }
    } else {
        if(imgHeli.complete && imgHeli.naturalHeight !== 0) ctx.drawImage(imgHeli, obstaculo.x, obstaculo.y, obstaculo.ancho, obstaculo.alto);
        else { ctx.fillStyle = 'black'; ctx.fillRect(obstaculo.x, obstaculo.y, obstaculo.ancho, obstaculo.alto); }
    }

    // Proyectiles Jugador
    balas.forEach(b => { ctx.fillStyle = '#ffaa00'; ctx.fillRect(b.x, b.y, b.w, b.h); });
    
    // Proyectiles Enemigos
    balasEnemigas.forEach(be => {
        if (be.tipo === 'obus') {
            ctx.fillStyle = '#ff0000'; ctx.beginPath(); ctx.arc(be.x, be.y, 6, 0, Math.PI*2); ctx.fill(); // Obús rojo
        } else {
            ctx.fillStyle = '#333'; ctx.fillRect(be.x, be.y, 8, 12); // Bomba de helicóptero
        }
    });

    // Explosiones
    explosiones.forEach(exp => {
        ctx.fillStyle = '#ff4500'; ctx.beginPath(); ctx.arc(exp.x + 20, exp.y + 20, 40, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = '#ffa500'; ctx.beginPath(); ctx.arc(exp.x + 20, exp.y + 20, 20, 0, Math.PI*2); ctx.fill();
    });

    // Jugador (Parpadeo si es invencible)
    if (estado !== 'GAMEOVER') {
        if (jugador.invencible === 0 || Math.floor(jugador.invencible / 4) % 2 === 0) {
            if (imgSoldado.complete && imgSoldado.naturalHeight !== 0) {
                if (jugador.agachado && jugador.y === SUELO_Y) ctx.drawImage(imgSoldado, jugador.x, jugador.y + 25, jugador.ancho, jugador.alto - 25);
                else ctx.drawImage(imgSoldado, jugador.x, jugador.y, jugador.ancho, jugador.alto);
            } else {
                ctx.fillStyle = 'blue'; 
                if (jugador.agachado && jugador.y === SUELO_Y) ctx.fillRect(jugador.x, jugador.y + 25, jugador.ancho, jugador.alto - 25);
                else ctx.fillRect(jugador.x, jugador.y, jugador.ancho, jugador.alto);
            }
        }
    } else {
        // Tumba
        ctx.fillStyle = '#555'; ctx.fillRect(jugador.x+10, jugador.y+30, 20, 30);
        ctx.fillStyle = '#fff'; ctx.font = "20px Arial"; ctx.fillText("💀", jugador.x+8, jugador.y+40);
    }

    // Menús
    if (estado === 'INICIO') {
        ctx.fillStyle = "rgba(0, 0, 0, 0.8)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 24px 'Courier New'";
        ctx.fillText("CLIC PARA INSERTAR MONEDA", canvas.width/2, canvas.height/2);
    }
    if (estado === 'GAMEOVER') {
        ctx.fillStyle = "rgba(100, 0, 0, 0.85)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 36px 'Courier New'";
        ctx.fillText("M I S I Ó N   F A L L I D A", canvas.width/2, canvas.height/2 - 25);
        ctx.font = "bold 18px 'Courier New'"; ctx.fillText("Haz clic para continuar", canvas.width/2, canvas.height/2 + 20);
    }
  }

  // --- BUCLE DE LÓGICA ---
  function bucle() {
    if (estado !== 'JUGANDO') return;

    if (jugador.invencible > 0) jugador.invencible--;

    // Físicas salto
    if (!jugador.agachado || jugador.y < SUELO_Y) { jugador.velY += gravedad; jugador.y += jugador.velY; } 
    else { jugador.velY += gravedad * 2; jugador.y += jugador.velY; }
    if (jugador.y > SUELO_Y) { jugador.y = SUELO_Y; jugador.velY = 0; }

    // Entorno
    obstaculo.x -= velocidadJuego;
    fondoEdificios += velocidadJuego * 0.3; // Parallax de fondo
    if (obstaculo.x < -100) { generarObstaculo(); puntuacion += 5; } // Puntos por sobrevivir

    puntuacion += 0.05; velocidadJuego += 0.001; 

    // IA Enemiga: ¡Disparar!
    if (obstaculo.x > 100 && obstaculo.x < 500) {
        if (obstaculo.tipo === 'tanque' && Math.random() < 0.02) {
            // El tanque dispara recto hacia ti
            balasEnemigas.push({ x: obstaculo.x, y: obstaculo.y + 15, w: 12, h: 12, velX: -8, velY: 0, tipo: 'obus' });
        } else if (obstaculo.tipo === 'helicoptero' && Math.random() < 0.03) {
            // El helicóptero deja caer bombas en diagonal
            balasEnemigas.push({ x: obstaculo.x + 40, y: obstaculo.y + 30, w: 8, h: 12, velX: -3, velY: 5, tipo: 'bomba' });
        }
    }

    let cH = { x: obstaculo.x + 10, y: obstaculo.y + 10, w: obstaculo.ancho - 20, h: obstaculo.alto - 20 };
    let dH = { x: jugador.x + 10, y: jugador.y + 5, w: jugador.ancho - 20, h: jugador.alto - 10 };
    if (jugador.agachado && jugador.y === SUELO_Y) { dH.y = jugador.y + 35; dH.h = jugador.alto - 35; }

    // Choque cuerpo a cuerpo
    if (dH.x < cH.x + cH.w && dH.x + dH.w > cH.x && dH.y < cH.y + cH.h && dH.h + dH.y > cH.y) {
        recibirDano();
    }

    // Físicas Balas Jugador
    for (let i = balas.length - 1; i >= 0; i--) {
        balas[i].x += 16; 
        let b = balas[i];
        if (b.x < cH.x + cH.w && b.x + b.w > cH.x && b.y < cH.y + cH.h && b.h + b.y > cH.y) {
            explosiones.push({ x: obstaculo.x, y: obstaculo.y, timer: 10 });
            puntuacion += 20; generarObstaculo(); balas.splice(i, 1); continue;
        }
        if (b.x > canvas.width) balas.splice(i, 1);
    }

    // Físicas Balas Enemigas
    for (let i = balasEnemigas.length - 1; i >= 0; i--) {
        balasEnemigas[i].x += balasEnemigas[i].velX;
        balasEnemigas[i].y += balasEnemigas[i].velY;
        let be = balasEnemigas[i];
        
        // Colisión Bala Enemiga vs Jugador
        if (be.x < dH.x + dH.w && be.x + be.w > dH.x && be.y < dH.y + dH.h && be.h + be.y > dH.y) {
            recibirDano();
            balasEnemigas.splice(i, 1);
            continue;
        }
        
        // Borrar si tocan el suelo o salen de pantalla
        if (be.x < -20 || be.y > SUELO_Y + 50) balasEnemigas.splice(i, 1);
    }

    // Gestionar Explosiones
    for (let i = explosiones.length - 1; i >= 0; i--) {
        explosiones[i].x -= velocidadJuego; 
        explosiones[i].timer--; 
        if (explosiones[i].timer <= 0) explosiones.splice(i, 1); 
    }

    dibujar();
    if (estado === 'JUGANDO') requestAnimationFrame(bucle);
  }

  dibujar();
</script>
</body>
</html>
"""

codigo_juego = codigo_juego.replace("INYECTAR_SOLDADO", codigo_soldado)
codigo_juego = codigo_juego.replace("INYECTAR_TANQUE", codigo_tanque)
codigo_juego = codigo_juego.replace("INYECTAR_HELI", codigo_heli)

components.html(codigo_juego, height=280)
