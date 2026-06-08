import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(page_title="Boss Rush", layout="centered", page_icon="💀")

st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    h1 { color: #8b0000; font-family: 'Impact', 'Courier New', sans-serif; text-align: center; font-weight: 900; letter-spacing: 3px; text-shadow: 2px 2px 0px #000;}
    .stMarkdown p { text-align: center; color: #444; font-family: 'Courier New', Courier, monospace; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.title("💀 BOSS RUSH: SHADOW OF PIXEL")
st.write("**A / D** = Moverse | **W / ESPACIO** = Saltar | **S** = Cubrirse | **X** = Disparar")

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
  canvas { border: 4px solid #111; background-color: #7a8a99; border-radius: 5px; cursor: pointer; box-shadow: 0px 8px 0px #000; }
</style>
</head>
<body>
<canvas id="juego" width="600" height="280" tabindex="1"></canvas>
<script>
  const canvas = document.getElementById("juego");
  const ctx = canvas.getContext("2d");

  // Inyección de imágenes
  const imgSoldado = new Image(); let srcSol = "INYECTAR_SOLDADO"; if(srcSol.length > 50) imgSoldado.src = srcSol;
  const imgTanque = new Image(); let srcTan = "INYECTAR_TANQUE"; if(srcTan.length > 50) imgTanque.src = srcTan;
  const imgHeli = new Image(); let srcHel = "INYECTAR_HELI"; if(srcHel.length > 50) imgHeli.src = srcHel;

  // --- VARIABLES ---
  const SUELO_Y = 200;
  let jugador = { x: 50, y: SUELO_Y, velY: 0, ancho: 45, alto: 55, agachado: false, vidas: 5, invencible: 0, dir: 1 };
  
  let jefe = { x: 450, y: SUELO_Y, ancho: 80, alto: 60, tipo: 'tanque', hp: 10, maxHp: 10, timer: 0, estado: 0, escudo: false, visible: true };
  let nivel = 1;
  let nombresJefes = ["", "NIVEL 1: EL NOVATO", "NIVEL 2: EL CÓNDOR", "NIVEL 3: EL ESCUDO", "NIVEL 4: EL FANTASMA", "NIVEL 5: EL COLOSO"];
  
  let balas = []; let balasEnemigas = []; let explosiones = []; 
  let estadoJuego = 'INICIO'; // INICIO, JUGANDO, TRANSICION, GAMEOVER, VICTORIA
  let transicionTimer = 0;
  
  const teclas = {};
  window.addEventListener('keydown', (e) => {
      teclas[e.code] = true;
      if ((e.code === "Space" || e.code === "ArrowUp" || e.code === "KeyW")) {
          e.preventDefault();
          if (estadoJuego === 'INICIO') { iniciarNivel(1); } 
          else if (estadoJuego === 'GAMEOVER' || estadoJuego === 'VICTORIA') { iniciarNivel(1); } 
          else if (estadoJuego === 'JUGANDO' && jugador.y === SUELO_Y && !jugador.agachado) { jugador.velY = -15; }
      }
      if ((e.code === "KeyX" || e.key === "x") && estadoJuego === 'JUGANDO') {
          if (balas.length < 4) {
              let alturaFuego = jugador.agachado ? jugador.y + 30 : jugador.y + 20;
              let posX = jugador.dir === 1 ? jugador.x + 40 : jugador.x - 10;
              balas.push({ x: posX, y: alturaFuego, w: 15, h: 4, dir: jugador.dir });
          }
      }
  });
  window.addEventListener('keyup', (e) => { teclas[e.code] = false; });
  canvas.focus();

  function iniciarNivel(n) {
      nivel = n;
      jugador.x = 50; jugador.y = SUELO_Y; jugador.velY = 0; jugador.dir = 1;
      if(n === 1) jugador.vidas = 5; // Reinicia vidas si empiezas de cero
      
      balas = []; balasEnemigas = []; explosiones = [];
      jefe.timer = 0; jefe.escudo = false; jefe.visible = true; jefe.dir = -1;
      
      if (nivel === 1) { jefe.tipo='tanque'; jefe.hp=15; jefe.maxHp=15; jefe.x=450; jefe.y=SUELO_Y; jefe.ancho=80; jefe.alto=60; }
      if (nivel === 2) { jefe.tipo='helicoptero'; jefe.hp=20; jefe.maxHp=20; jefe.x=400; jefe.y=50; jefe.ancho=90; jefe.alto=50; }
      if (nivel === 3) { jefe.tipo='tanque'; jefe.hp=25; jefe.maxHp=25; jefe.x=450; jefe.y=SUELO_Y; jefe.ancho=80; jefe.alto=60; jefe.escudo=true;}
      if (nivel === 4) { jefe.tipo='helicoptero'; jefe.hp=30; jefe.maxHp=30; jefe.x=400; jefe.y=100; jefe.ancho=90; jefe.alto=50; jefe.visible=false;}
      if (nivel === 5) { jefe.tipo='coloso'; jefe.hp=50; jefe.maxHp=50; jefe.x=450; jefe.y=SUELO_Y-40; jefe.ancho=100; jefe.alto=100; }
      
      estadoJuego = 'TRANSICION';
      transicionTimer = 150;
      requestAnimationFrame(bucle);
  }

  function recibirDano() {
      if (jugador.invencible <= 0) {
          jugador.vidas--;
          jugador.invencible = 60; 
          explosiones.push({x: jugador.x, y: jugador.y, timer: 15, color: '#ff0000'});
          if (jugador.vidas <= 0) estadoJuego = 'GAMEOVER';
      }
  }

  function dispararJefe(x, y, vx, vy, tipo) {
      balasEnemigas.push({ x: x, y: y, velX: vx, velY: vy, tipo: tipo, w: 10, h: 10 });
  }

  function dibujarEntidad(img, x, y, w, h, invertido) {
      if (!img.complete || img.naturalHeight === 0) return;
      if (invertido) {
          ctx.save(); ctx.translate(x + w, y); ctx.scale(-1, 1); ctx.drawImage(img, 0, 0, w, h); ctx.restore();
      } else { ctx.drawImage(img, x, y, w, h); }
  }

  // --- LÓGICA DE IA DEL JEFE ---
  function actualizarIAJefe() {
      jefe.timer++;
      
      if (nivel === 1) { // EL NOVATO
          jefe.x += Math.sin(jefe.timer * 0.05) * 1.5; // Se mueve un poco
          if (jefe.timer % 80 === 0) dispararJefe(jefe.x, jefe.y + 25, -5, 0, 'obus');
      }
      else if (nivel === 2) { // EL CÓNDOR
          if (jefe.timer < 100) { jefe.y = 50; } // Vuela alto (invulnerable)
          else if (jefe.timer < 150) { jefe.y += 3; } // Baja
          else if (jefe.timer < 200) {
              jefe.y = SUELO_Y - 20; // A ras de suelo (Vulnerable)
              if (jefe.timer === 175) dispararJefe(jefe.x, jefe.y + 25, -6, 0, 'obus');
          }
          else if (jefe.timer < 250) { jefe.y -= 3; } // Sube
          else { jefe.timer = 0; }
      }
      else if (nivel === 3) { // EL ESCUDO
          jefe.x += Math.sin(jefe.timer * 0.03) * 1;
          if (jefe.timer < 150) {
              jefe.escudo = true;
          } else if (jefe.timer < 250) {
              jefe.escudo = false; // Baja el escudo
              if (jefe.timer % 20 === 0) dispararJefe(jefe.x, jefe.y + 25, -7, 0, 'obus'); // Ráfaga
          } else { jefe.timer = 0; }
      }
      else if (nivel === 4) { // EL FANTASMA
          if (jefe.timer % 150 === 0) {
              jefe.x = Math.random() * 300 + 200;
              jefe.y = Math.random() * 100 + 40;
              jefe.visible = true; // Se hace visible
          }
          if (jefe.timer % 150 === 60) {
              dispararJefe(jefe.x + 20, jefe.y + 30, -3, 4, 'bomba');
              dispararJefe(jefe.x + 20, jefe.y + 30, 3, 4, 'bomba');
          }
          if (jefe.timer % 150 > 90) jefe.visible = false; // Desaparece
      }
      else if (nivel === 5) { // EL COLOSO
          jefe.x += Math.sin(jefe.timer * 0.02) * 0.5;
          if (jefe.timer % 60 === 0) dispararJefe(jefe.x, jefe.y + 70, -6, 0, 'obus'); // Disparo tanque
          if (jefe.timer % 90 === 0) dispararJefe(jefe.x + 30, jefe.y + 20, -4, 3, 'bomba'); // Disparo heli
      }
  }

  // --- RENDERIZADO ---
  function dibujar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Fondo y Suelo
    ctx.fillStyle = "#4a5a6a"; ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#222"; ctx.fillRect(0, SUELO_Y + 50, canvas.width, canvas.height);
    ctx.fillStyle = "#111"; ctx.fillRect(0, SUELO_Y + 50, canvas.width, 10);

    // UI: Corazones
    ctx.fillStyle = "#d32f2f"; ctx.font = "20px Arial";
    let corazones = ""; for(let v=0; v<jugador.vidas; v++) corazones += "❤️";
    ctx.fillText(corazones, 10, 20);

    // UI: BARRA DE VIDA DEL JEFE
    if (estadoJuego === 'JUGANDO') {
        ctx.fillStyle = "#333"; ctx.fillRect(150, 15, 300, 20); // Fondo barra
        ctx.fillStyle = "#8b0000"; ctx.fillRect(152, 17, 296 * (jefe.hp / jefe.maxHp), 16); // Vida
        ctx.fillStyle = "#fff"; ctx.font = "bold 14px 'Courier New'"; ctx.textAlign = "center";
        ctx.fillText(nombresJefes[nivel], canvas.width/2, 30);
        ctx.textAlign = "left";
    }

    // Dibujar Jefe
    if ((estadoJuego === 'JUGANDO' || estadoJuego === 'TRANSICION') && jefe.visible) {
        if (jefe.tipo === 'tanque') {
            dibujarEntidad(imgTanque, jefe.x, jefe.y, jefe.ancho, jefe.alto, false);
            if (jefe.escudo) {
                ctx.strokeStyle = "#00ffff"; ctx.lineWidth = 4; ctx.beginPath();
                ctx.arc(jefe.x, jefe.y + 30, 40, Math.PI*0.5, Math.PI*1.5); ctx.stroke(); // Escudo frontal
            }
        } 
        else if (jefe.tipo === 'helicoptero') {
            dibujarEntidad(imgHeli, jefe.x, jefe.y, jefe.ancho, jefe.alto, false);
        }
        else if (jefe.tipo === 'coloso') {
            // Fusión de tanque y heli
            dibujarEntidad(imgHeli, jefe.x + 10, jefe.y - 10, 80, 50, false);
            dibujarEntidad(imgTanque, jefe.x, jefe.y + 30, 100, 70, false);
        }
    }

    // Proyectiles
    balas.forEach(b => { ctx.fillStyle = '#ffaa00'; ctx.fillRect(b.x, b.y, b.w, b.h); });
    balasEnemigas.forEach(be => {
        if (be.tipo === 'obus') { ctx.fillStyle = '#ff0000'; ctx.beginPath(); ctx.arc(be.x, be.y, 6, 0, Math.PI*2); ctx.fill(); } 
        else { ctx.fillStyle = '#111'; ctx.beginPath(); ctx.arc(be.x, be.y, 6, 0, Math.PI*2); ctx.fill(); }
    });

    // Explosiones
    explosiones.forEach(exp => {
        ctx.fillStyle = exp.color || '#ff4500'; ctx.beginPath(); ctx.arc(exp.x + 20, exp.y + 20, 30, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = '#ffa500'; ctx.beginPath(); ctx.arc(exp.x + 20, exp.y + 20, 15, 0, Math.PI*2); ctx.fill();
    });

    // Jugador
    if (estadoJuego !== 'GAMEOVER') {
        if (jugador.invencible === 0 || Math.floor(jugador.invencible / 4) % 2 === 0) {
            let invertido = jugador.dir === -1;
            if (jugador.agachado && jugador.y === SUELO_Y) {
                if(invertido) { ctx.save(); ctx.translate(jugador.x + jugador.ancho, jugador.y + 25); ctx.scale(-1, 1); ctx.drawImage(imgSoldado, 0, 0, jugador.ancho, jugador.alto - 25); ctx.restore(); } 
                else if (imgSoldado.complete && imgSoldado.naturalHeight !== 0) ctx.drawImage(imgSoldado, jugador.x, jugador.y + 25, jugador.ancho, jugador.alto - 25);
            } else {
                dibujarEntidad(imgSoldado, jugador.x, jugador.y, jugador.ancho, jugador.alto, invertido);
            }
        }
    } else {
        ctx.fillStyle = '#555'; ctx.fillRect(jugador.x+10, jugador.y+30, 20, 30);
        ctx.fillStyle = '#fff'; ctx.font = "20px Arial"; ctx.fillText("💀", jugador.x+8, jugador.y+40);
    }

    // Pantallas Superpuestas
    if (estadoJuego === 'INICIO') {
        ctx.fillStyle = "rgba(0, 0, 0, 0.8)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 24px 'Courier New'";
        ctx.fillText("CLIC O ESPACIO PARA INICIAR", canvas.width/2, canvas.height/2);
    }
    else if (estadoJuego === 'TRANSICION') {
        ctx.fillStyle = "rgba(0, 0, 0, 0.7)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 32px 'Courier New'";
        ctx.fillText(nombresJefes[nivel], canvas.width/2, canvas.height/2);
    }
    else if (estadoJuego === 'GAMEOVER') {
        ctx.fillStyle = "rgba(100, 0, 0, 0.85)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 36px 'Courier New'";
        ctx.fillText("HAS CAÍDO", canvas.width/2, canvas.height/2 - 25);
        ctx.font = "bold 18px 'Courier New'"; ctx.fillText("Presiona ESPACIO para reiniciar", canvas.width/2, canvas.height/2 + 20);
    }
    else if (estadoJuego === 'VICTORIA') {
        ctx.fillStyle = "rgba(0, 50, 0, 0.85)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#ffd700"; ctx.textAlign = "center"; ctx.font = "bold 36px 'Courier New'";
        ctx.fillText("¡MISIÓN CUMPLIDA!", canvas.width/2, canvas.height/2 - 25);
        ctx.font = "bold 18px 'Courier New'"; ctx.fillText("Eres una leyenda. ESPACIO para jugar de nuevo.", canvas.width/2, canvas.height/2 + 20);
    }
  }

  // --- BUCLE DE LÓGICA ---
  function bucle() {
    if (estadoJuego === 'TRANSICION') {
        transicionTimer--;
        if (transicionTimer <= 0) estadoJuego = 'JUGANDO';
        dibujar();
        requestAnimationFrame(bucle);
        return;
    }
    if (estadoJuego !== 'JUGANDO') return;

    if (jugador.invencible > 0) jugador.invencible--;

    // Controles de Jugador
    jugador.agachado = (teclas['ArrowDown'] || teclas['KeyS']) && jugador.y === SUELO_Y;
    if (!jugador.agachado) {
        if (teclas['ArrowRight'] || teclas['KeyD']) { jugador.x += 4; jugador.dir = 1; }
        if (teclas['ArrowLeft'] || teclas['KeyA']) { jugador.x -= 4; jugador.dir = -1; }
    }
    if (jugador.x < 0) jugador.x = 0;
    if (jugador.x > canvas.width - jugador.ancho) jugador.x = canvas.width - jugador.ancho;

    // Físicas salto
    if (!jugador.agachado || jugador.y < SUELO_Y) { jugador.velY += 1.0; jugador.y += jugador.velY; } 
    else { jugador.velY += 2.0; jugador.y += jugador.velY; }
    if (jugador.y > SUELO_Y) { jugador.y = SUELO_Y; jugador.velY = 0; }

    actualizarIAJefe();

    let jH = { x: jefe.x, y: jefe.y, w: jefe.ancho, h: jefe.alto };
    let dH = { x: jugador.x + 10, y: jugador.y + 5, w: jugador.ancho - 20, h: jugador.alto - 10 };
    if (jugador.agachado && jugador.y === SUELO_Y) { dH.y = jugador.y + 35; dH.h = jugador.alto - 35; }

    // Balas Jugador vs Jefe
    for (let i = balas.length - 1; i >= 0; i--) {
        balas[i].x += 12 * balas[i].dir; 
        let b = balas[i];
        
        // Comprobar hit con el jefe
        if (jefe.visible && b.x < jH.x + jH.w && b.x + b.w > jH.x && b.y < jH.y + jH.h && b.h + b.y > jH.y) {
            // Mecánicas de vulnerabilidad
            let haceDano = true;
            if (nivel === 2 && jefe.y < 100) haceDano = false; // Inmune si vuela alto
            if (nivel === 3 && jefe.escudo && b.x < jefe.x) haceDano = false; // Escudo frontal bloquea balas
            
            if (haceDano) {
                explosiones.push({ x: b.x, y: b.y - 10, timer: 5, color: '#ffff00' });
                jefe.hp--;
                if (jefe.hp <= 0) {
                    explosiones.push({ x: jefe.x, y: jefe.y, timer: 30, color: '#ff4500' });
                    explosiones.push({ x: jefe.x+40, y: jefe.y+20, timer: 35, color: '#ff4500' });
                    if (nivel < 5) {
                        estadoJuego = 'TRANSICION'; transicionTimer = 100;
                        setTimeout(() => iniciarNivel(nivel + 1), 1500);
                    } else { estadoJuego = 'VICTORIA'; }
                }
            } else {
                // Chispa gris si es invulnerable
                explosiones.push({ x: b.x, y: b.y - 10, timer: 5, color: '#aaaaaa' });
            }
            balas.splice(i, 1); continue;
        }
        if (b.x < -20 || b.x > canvas.width + 20) balas.splice(i, 1);
    }

    // Balas Enemigas vs Jugador
    for (let i = balasEnemigas.length - 1; i >= 0; i--) {
        balasEnemigas[i].x += balasEnemigas[i].velX;
        balasEnemigas[i].y += balasEnemigas[i].velY;
        let be = balasEnemigas[i];
        
        if (be.x < dH.x + dH.w && be.x + be.w > dH.x && be.y < dH.y + dH.h && be.h + be.y > dH.y) {
            recibirDano(); balasEnemigas.splice(i, 1); continue;
        }
        if (be.x < -20 || be.x > canvas.width + 20 || be.y > SUELO_Y + 50) balasEnemigas.splice(i, 1);
    }

    for (let i = explosiones.length - 1; i >= 0; i--) {
        explosiones[i].timer--; 
        if (explosiones[i].timer <= 0) explosiones.splice(i, 1); 
    }

    dibujar();
    if (estadoJuego === 'JUGANDO') requestAnimationFrame(bucle);
  }

  dibujar();
</script>
</body>
</html>
"""

codigo_juego = codigo_juego.replace("INYECTAR_SOLDADO", codigo_soldado)
codigo_juego = codigo_juego.replace("INYECTAR_TANQUE", codigo_tanque)
codigo_juego = codigo_juego.replace("INYECTAR_HELI", codigo_heli)

components.html(codigo_juego, height=310)
