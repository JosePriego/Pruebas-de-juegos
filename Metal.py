import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(page_title="Metal Slug Arena", layout="centered", page_icon="💥")

st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    h1 { color: #8b0000; font-family: 'Impact', 'Courier New', sans-serif; text-align: center; font-weight: 900; letter-spacing: 3px; text-shadow: 2px 2px 0px #000;}
    .stMarkdown p { text-align: center; color: #444; font-family: 'Courier New', Courier, monospace; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.title("💥 OPERACIÓN: ARENA TOTAL")
st.write("**A / D** = Moverse | **W / ESPACIO** = Saltar | **S** = Cubrirse | **X** = Disparar")

# --- LA MAGIA DE PYTHON ---
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

  // --- VARIABLES DE ARENA ---
  const SUELO_Y = 170;
  
  // direccion: 1 es derecha, -1 es izquierda
  let jugador = { x: 270, y: SUELO_Y, velY: 0, ancho: 55, alto: 65, agachado: false, vidas: 3, invencible: 0, direccion: 1 };
  
  // Ahora manejamos listas de enemigos en lugar de solo uno
  let enemigos = [];
  let timerEnemigos = 0;
  
  let balas = []; 
  let balasEnemigas = []; 
  let explosiones = []; 
  let fondoNubes = 0;
  
  let gravedad = 1.3;
  let puntuacion = 0;
  let maxPuntuacion = 0;
  try { maxPuntuacion = localStorage.getItem("arenaHighScore") || 0; } catch(e) {}
  
  let estado = 'INICIO';

  // --- CONTROLES DE MOVIMIENTO CONTINUO ---
  const teclas = {};
  
  window.addEventListener('keydown', (e) => {
      teclas[e.code] = true;
      
      // Saltar
      if ((e.code === "Space" || e.code === "ArrowUp" || e.code === "KeyW")) {
          e.preventDefault();
          if (estado === 'INICIO') { estado = 'JUGANDO'; requestAnimationFrame(bucle); } 
          else if (estado === 'GAMEOVER') { reiniciar(); requestAnimationFrame(bucle); } 
          else if (estado === 'JUGANDO' && jugador.y === SUELO_Y && !jugador.agachado) { jugador.velY = -16.5; }
      }
      
      // Disparar
      if ((e.code === "KeyX" || e.key === "x") && estado === 'JUGANDO') {
          if (balas.length < 5) {
              let alturaFuego = jugador.agachado ? jugador.y + 35 : jugador.y + 25;
              let posX = jugador.direccion === 1 ? jugador.x + 45 : jugador.x - 5;
              balas.push({ x: posX, y: alturaFuego, w: 12, h: 4, dir: jugador.direccion });
          }
      }
  });

  window.addEventListener('keyup', (e) => { teclas[e.code] = false; });
  canvas.focus();

  function reiniciar() {
    jugador = { x: 270, y: SUELO_Y, velY: 0, ancho: 55, alto: 65, agachado: false, vidas: 3, invencible: 0, direccion: 1 };
    enemigos = []; balas = []; balasEnemigas = []; explosiones = [];
    puntuacion = 0; estado = 'JUGANDO';
  }

  function generarEnemigo() {
      let porDerecha = Math.random() < 0.5;
      let esHeli = Math.random() < 0.4;
      
      enemigos.push({
          x: porDerecha ? canvas.width + 50 : -90,
          y: esHeli ? SUELO_Y - 40 : SUELO_Y,
          ancho: esHeli ? 90 : 70,
          alto: esHeli ? 45 : 50,
          tipo: esHeli ? 'helicoptero' : 'tanque',
          dirX: porDerecha ? -1 : 1, // -1 se mueve a la izq, 1 a la der
          vida: esHeli ? 1 : 2 // Los tanques aguantan 2 tiros
      });
  }
  
  function recibirDano() {
      if (jugador.invencible <= 0) {
          jugador.vidas--;
          jugador.invencible = 60; // 1 segundo invulnerable
          explosiones.push({x: jugador.x, y: jugador.y, timer: 15});
          if (jugador.vidas <= 0) {
              estado = 'GAMEOVER';
              if (puntuacion > maxPuntuacion) {
                  maxPuntuacion = puntuacion;
                  try { localStorage.setItem("arenaHighScore", maxPuntuacion); } catch(e) {}
              }
          }
      }
  }

  // Función mágica para dibujar imágenes invertidas
  function dibujarEntidad(img, x, y, w, h, invertir) {
      if (!img.complete || img.naturalHeight === 0) return; // Si no hay imagen, no dibuja
      
      if (invertir) {
          ctx.save();
          ctx.translate(x + w, y);
          ctx.scale(-1, 1);
          ctx.drawImage(img, 0, 0, w, h);
          ctx.restore();
      } else {
          ctx.drawImage(img, x, y, w, h);
      }
  }

  // --- RENDERIZADO ---
  function dibujar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Fondo ambiental
    ctx.fillStyle = "#5c6b69";
    fondoNubes += 0.5;
    for(let i=0; i<10; i++) {
        let posX = ((i * 120) - fondoNubes) % 720;
        if(posX < -120) posX += 720;
        ctx.fillRect(posX, SUELO_Y - 80 + (i%3)*20, 60, 150);
        ctx.fillRect(posX+60, SUELO_Y - 50, 40, 100);
    }

    ctx.fillStyle = "#333"; ctx.fillRect(0, SUELO_Y + 50, canvas.width, canvas.height);
    ctx.fillStyle = "#111"; ctx.fillRect(0, SUELO_Y + 50, canvas.width, 10);

    ctx.fillStyle = "#111"; ctx.font = "bold 16px 'Courier New'"; ctx.textAlign = "right";
    ctx.fillText("HI: " + Math.floor(maxPuntuacion).toString().padStart(5, '0') + "  PTS: " + Math.floor(puntuacion).toString().padStart(5, '0'), canvas.width - 10, 20);
    ctx.textAlign = "left";

    ctx.fillStyle = "#d32f2f"; ctx.font = "20px Arial";
    let corazones = "";
    for(let v=0; v<jugador.vidas; v++) corazones += "❤️";
    ctx.fillText(corazones, 10, 15);

    // Dibujar Enemigos
    enemigos.forEach(ene => {
        let invertido = ene.dirX === 1; // La imagen original mira a la izquierda, la invertimos si va a la derecha
        if (ene.tipo === 'tanque') dibujarEntidad(imgTanque, ene.x, ene.y, ene.ancho, ene.alto, invertido);
        else dibujarEntidad(imgHeli, ene.x, ene.y, ene.ancho, ene.alto, invertido);
    });

    balas.forEach(b => { ctx.fillStyle = '#ffaa00'; ctx.fillRect(b.x, b.y, b.w, b.h); });
    
    balasEnemigas.forEach(be => {
        if (be.tipo === 'obus') {
            ctx.fillStyle = '#ff0000'; ctx.beginPath(); ctx.arc(be.x, be.y, 6, 0, Math.PI*2); ctx.fill(); 
        } else {
            ctx.fillStyle = '#333'; ctx.fillRect(be.x, be.y, 8, 12); 
        }
    });

    explosiones.forEach(exp => {
        ctx.fillStyle = '#ff4500'; ctx.beginPath(); ctx.arc(exp.x + 20, exp.y + 20, 40, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = '#ffa500'; ctx.beginPath(); ctx.arc(exp.x + 20, exp.y + 20, 20, 0, Math.PI*2); ctx.fill();
    });

    // Dibujar Jugador
    if (estado !== 'GAMEOVER') {
        if (jugador.invencible === 0 || Math.floor(jugador.invencible / 4) % 2 === 0) {
            let invertido = jugador.direccion === -1;
            if (jugador.agachado && jugador.y === SUELO_Y) {
                // Truco de aplastar imagen + rotación si aplica
                if(invertido) { ctx.save(); ctx.translate(jugador.x + jugador.ancho, jugador.y + 25); ctx.scale(-1, 1); ctx.drawImage(imgSoldado, 0, 0, jugador.ancho, jugador.alto - 25); ctx.restore(); } 
                else { ctx.drawImage(imgSoldado, jugador.x, jugador.y + 25, jugador.ancho, jugador.alto - 25); }
            } else {
                dibujarEntidad(imgSoldado, jugador.x, jugador.y, jugador.ancho, jugador.alto, invertido);
            }
        }
    } else {
        ctx.fillStyle = '#555'; ctx.fillRect(jugador.x+10, jugador.y+30, 20, 30);
        ctx.fillStyle = '#fff'; ctx.font = "20px Arial"; ctx.fillText("💀", jugador.x+8, jugador.y+40);
    }

    if (estado === 'INICIO') {
        ctx.fillStyle = "rgba(0, 0, 0, 0.8)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 24px 'Courier New'";
        ctx.fillText("CLIC O ESPACIO PARA INICIAR", canvas.width/2, canvas.height/2);
    }
    if (estado === 'GAMEOVER') {
        ctx.fillStyle = "rgba(100, 0, 0, 0.85)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 36px 'Courier New'";
        ctx.fillText("M I S I Ó N   F A L L I D A", canvas.width/2, canvas.height/2 - 25);
        ctx.font = "bold 18px 'Courier New'"; ctx.fillText("Presiona ESPACIO para continuar", canvas.width/2, canvas.height/2 + 20);
    }
  }

  // --- BUCLE DE LÓGICA ---
  function bucle() {
    if (estado !== 'JUGANDO') return;

    if (jugador.invencible > 0) jugador.invencible--;

    // Gestión de Controles de Movimiento Lateral
    jugador.agachado = (teclas['ArrowDown'] || teclas['KeyS']) && jugador.y === SUELO_Y;
    
    if (!jugador.agachado) {
        if (teclas['ArrowRight'] || teclas['KeyD']) { jugador.x += 5; jugador.direccion = 1; }
        if (teclas['ArrowLeft'] || teclas['KeyA']) { jugador.x -= 5; jugador.direccion = -1; }
    }
    
    // Limites de la pantalla para el jugador
    if (jugador.x < 0) jugador.x = 0;
    if (jugador.x > canvas.width - jugador.ancho) jugador.x = canvas.width - jugador.ancho;

    // Físicas salto
    if (!jugador.agachado || jugador.y < SUELO_Y) { jugador.velY += gravedad; jugador.y += jugador.velY; } 
    else { jugador.velY += gravedad * 2; jugador.y += jugador.velY; }
    if (jugador.y > SUELO_Y) { jugador.y = SUELO_Y; jugador.velY = 0; }

    puntuacion += 0.05; 
    let velEnemigos = 4 + (puntuacion * 0.01);

    // Sistema de Oleadas (Spawns)
    timerEnemigos++;
    let limiteTimer = Math.max(50, 150 - puntuacion); // Cada vez salen más rápido
    if (timerEnemigos >= limiteTimer) {
        generarEnemigo();
        timerEnemigos = 0;
    }

    let dH = { x: jugador.x + 10, y: jugador.y + 5, w: jugador.ancho - 20, h: jugador.alto - 10 };
    if (jugador.agachado && jugador.y === SUELO_Y) { dH.y = jugador.y + 35; dH.h = jugador.alto - 35; }

    // Actualizar Enemigos
    for(let i = enemigos.length - 1; i >= 0; i--) {
        let ene = enemigos[i];
        ene.x += velEnemigos * ene.dirX;

        // IA Disparo
        if (ene.x > 50 && ene.x < canvas.width - 50) {
            if (ene.tipo === 'tanque' && Math.random() < 0.015) {
                let startX = ene.dirX === -1 ? ene.x : ene.x + ene.ancho;
                balasEnemigas.push({ x: startX, y: ene.y + 15, w: 12, h: 12, velX: 8 * ene.dirX, velY: 0, tipo: 'obus' });
            } else if (ene.tipo === 'helicoptero' && Math.random() < 0.02) {
                balasEnemigas.push({ x: ene.x + 40, y: ene.y + 30, w: 8, h: 12, velX: 2 * ene.dirX, velY: 5, tipo: 'bomba' });
            }
        }

        // Colisión cuerpo a cuerpo
        let cH = { x: ene.x + 10, y: ene.y + 10, w: ene.ancho - 20, h: ene.alto - 20 };
        if (dH.x < cH.x + cH.w && dH.x + dH.w > cH.x && dH.y < cH.y + cH.h && dH.h + dH.y > cH.y) {
            recibirDano();
        }

        // Limpiar si salen mucho de la pantalla
        if (ene.x < -150 || ene.x > canvas.width + 150) enemigos.splice(i, 1);
    }

    // Físicas Balas Jugador vs Enemigos
    for (let i = balas.length - 1; i >= 0; i--) {
        balas[i].x += 16 * balas[i].dir; 
        let b = balas[i];
        let hit = false;
        
        for (let j = enemigos.length - 1; j >= 0; j--) {
            let ene = enemigos[j];
            let cH = { x: ene.x + 10, y: ene.y + 10, w: ene.ancho - 20, h: ene.alto - 20 };
            
            if (b.x < cH.x + cH.w && b.x + b.w > cH.x && b.y < cH.y + cH.h && b.h + b.y > cH.y) {
                explosiones.push({ x: ene.x, y: ene.y, timer: 10 });
                ene.vida--;
                if(ene.vida <= 0) {
                    puntuacion += 20; 
                    enemigos.splice(j, 1);
                }
                hit = true;
                break; // La bala solo golpea a uno
            }
        }
        
        if (hit) { balas.splice(i, 1); continue; }
        if (b.x < -20 || b.x > canvas.width + 20) balas.splice(i, 1);
    }

    // Físicas Balas Enemigas vs Jugador
    for (let i = balasEnemigas.length - 1; i >= 0; i--) {
        balasEnemigas[i].x += balasEnemigas[i].velX;
        balasEnemigas[i].y += balasEnemigas[i].velY;
        let be = balasEnemigas[i];
        
        if (be.x < dH.x + dH.w && be.x + be.w > dH.x && be.y < dH.y + dH.h && be.h + be.y > dH.y) {
            recibirDano();
            balasEnemigas.splice(i, 1);
            continue;
        }
        
        if (be.x < -20 || be.x > canvas.width + 20 || be.y > SUELO_Y + 50) balasEnemigas.splice(i, 1);
    }

    for (let i = explosiones.length - 1; i >= 0; i--) {
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
