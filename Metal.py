import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(page_title="Boss Rush Definitivo", layout="centered", page_icon="💀")

st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    h1 { color: #8b0000; font-family: 'Impact', 'Courier New', sans-serif; text-align: center; font-weight: 900; letter-spacing: 3px; text-shadow: 2px 2px 0px #000;}
    .stMarkdown p { text-align: center; color: #444; font-family: 'Courier New', Courier, monospace; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.title("💀 BOSS RUSH: MODO LEYENDA")
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
  let jugador = { x: 50, y: SUELO_Y, velY: 0, ancho: 45, alto: 55, agachado: false, vidas: 5, invencible: 0, dir: 1, armaTimer: 0 };
  
  let jefe = { x: 450, y: SUELO_Y, ancho: 80, alto: 60, tipo: 'tanque', hp: 10, maxHp: 10, timer: 0, estado: 0, escudo: false, visible: true };
  let nivel = 1;
  let nombresJefes = ["", "NIVEL 1: EL NOVATO", "NIVEL 2: EL CÓNDOR", "NIVEL 3: EL ESCUDO", "NIVEL 4: EL FANTASMA", "NIVEL 5: EL COLOSO"];
  
  let balas = []; let balasEnemigas = []; let explosiones = []; let cajas = [];
  
  let estadoJuego = 'INICIO'; 
  let transicionTimer = 0;
  let cooldownDisparo = 0;
  
  // Novedades Puntuación y Dificultad
  let puntuacion = 0;
  let siguienteCaja = 100;
  let modoDificil = false;
  
  const teclas = {};
  window.addEventListener('keydown', (e) => {
      teclas[e.code] = true;
      if ((e.code === "Space" || e.code === "ArrowUp" || e.code === "KeyW")) {
          e.preventDefault();
          if (estadoJuego === 'INICIO' || estadoJuego === 'GAMEOVER') { 
              modoDificil = false; iniciarNivel(1); 
          } 
          else if (estadoJuego === 'VICTORIA') {
              // Si presiona espacio en victoria, juega normal
              modoDificil = false; iniciarNivel(1);
          }
          else if (estadoJuego === 'JUGANDO' && jugador.y === SUELO_Y && !jugador.agachado) { jugador.velY = -15; }
      }
      
      // Tecla H para el modo difícil
      if (e.code === "KeyH" && estadoJuego === 'VICTORIA') {
          modoDificil = true; iniciarNivel(1);
      }

      if ((e.code === "KeyX" || e.key === "x") && estadoJuego === 'JUGANDO') {
          if (cooldownDisparo <= 0) {
              let limite = jugador.armaTimer > 0 ? 8 : 4; // Doble de balas en pantalla si tienes ráfaga
              if (balas.length < limite) {
                  let alturaFuego = jugador.agachado ? jugador.y + 30 : jugador.y + 20;
                  let posX = jugador.dir === 1 ? jugador.x + 40 : jugador.x - 10;
                  balas.push({ x: posX, y: alturaFuego, w: 15, h: 4, dir: jugador.dir });
                  cooldownDisparo = jugador.armaTimer > 0 ? 5 : 15; // Dispara 3 veces más rápido
              }
          }
      }
  });
  window.addEventListener('keyup', (e) => { teclas[e.code] = false; });
  canvas.focus();

  function iniciarNivel(n) {
      nivel = n;
      jugador.x = 50; jugador.y = SUELO_Y; jugador.velY = 0; jugador.dir = 1;
      
      if(n === 1) {
          jugador.vidas = modoDificil ? 3 : 5; 
          puntuacion = 0;
          siguienteCaja = 100;
          jugador.armaTimer = 0;
      }
      
      balas = []; balasEnemigas = []; explosiones = []; cajas = [];
      jefe.timer = 0; jefe.escudo = false; jefe.visible = true;
      
      let mult = modoDificil ? 1.5 : 1; // +50% de vida en difícil
      
      if (nivel === 1) { jefe.tipo='tanque'; jefe.maxHp=Math.floor(15*mult); jefe.x=450; jefe.y=SUELO_Y; jefe.ancho=80; jefe.alto=60; }
      if (nivel === 2) { jefe.tipo='helicoptero'; jefe.maxHp=Math.floor(20*mult); jefe.x=400; jefe.y=50; jefe.ancho=90; jefe.alto=50; }
      if (nivel === 3) { jefe.tipo='tanque'; jefe.maxHp=Math.floor(25*mult); jefe.x=450; jefe.y=SUELO_Y; jefe.ancho=80; jefe.alto=60; jefe.escudo=true;}
      if (nivel === 4) { jefe.tipo='helicoptero'; jefe.maxHp=Math.floor(30*mult); jefe.x=400; jefe.y=100; jefe.ancho=90; jefe.alto=50; jefe.visible=false;}
      if (nivel === 5) { jefe.tipo='coloso'; jefe.maxHp=Math.floor(50*mult); jefe.x=450; jefe.y=SUELO_Y-40; jefe.ancho=100; jefe.alto=100; }
      
      jefe.hp = jefe.maxHp;
      estadoJuego = 'TRANSICION'; transicionTimer = 150;
      if (n === 1) requestAnimationFrame(bucle); // Solo iniciamos bucle en nivel 1
  }

  function recibirDano() {
      if (jugador.invencible <= 0) {
          jugador.vidas--;
          puntuacion -= 25; // Penalización de puntos
          jugador.invencible = 60; 
          explosiones.push({x: jugador.x, y: jugador.y, timer: 15, color: '#ff0000'});
          if (jugador.vidas <= 0) estadoJuego = 'GAMEOVER';
      }
  }

  function chequearCaja() {
      if (!modoDificil && puntuacion >= siguienteCaja) {
          cajas.push({ 
              x: Math.random() * 300 + 100, y: -30, velY: 3, 
              tipo: Math.random() < 0.5 ? 'vida' : 'arma' 
          });
          siguienteCaja += 100;
      }
  }

  function dispararJefe(x, y, vx, vy, tipo) {
      // Las bombas ahora nacen con velocidad Y negativa para caer con gravedad
      if (tipo === 'bomba_fantasma' || tipo === 'bomba_coloso') {
          balasEnemigas.push({ x: x, y: y, velX: vx, velY: -2, tipo: tipo, w: 10, h: 10, rebotes: 0 });
      } else {
          balasEnemigas.push({ x: x, y: y, velX: vx, velY: vy, tipo: tipo, w: 10, h: 10 });
      }
  }

  // --- LÓGICA DE IA DEL JEFE ---
  function actualizarIAJefe() {
      jefe.timer++;
      let velDisp = modoDificil ? 0.7 : 1; // En difícil disparan más rápido (temporizadores más cortos)
      
      if (nivel === 1) { // EL NOVATO
          jefe.x += Math.sin(jefe.timer * 0.05) * 1.5; 
          if (jefe.timer % Math.floor(80 * velDisp) === 0) dispararJefe(jefe.x, jefe.y + 25, -5, 0, 'obus');
      }
      else if (nivel === 2) { // EL CÓNDOR
          let ciclo = Math.floor(250 * velDisp);
          let t = jefe.timer % ciclo;
          if (t < ciclo * 0.4) { jefe.y = 50; } // Vuela alto
          else if (t < ciclo * 0.6) { jefe.y += 3; } // Baja
          else if (t < ciclo * 0.8) {
              jefe.y = SUELO_Y - 20; // A ras de suelo
              if (t === Math.floor(ciclo * 0.7)) dispararJefe(jefe.x, jefe.y + 25, -6, 0, 'obus');
          }
          else { jefe.y -= 3; } // Sube
      }
      else if (nivel === 3) { // EL ESCUDO
          jefe.x += Math.sin(jefe.timer * 0.03) * 1;
          let t = jefe.timer % Math.floor(250 * velDisp);
          if (t < 150 * velDisp) { jefe.escudo = true; } 
          else {
              jefe.escudo = false; // Baja el escudo
              if (t % 20 === 0) dispararJefe(jefe.x, jefe.y + 25, -7, 0, 'obus'); // Ráfaga
          }
      }
      else if (nivel === 4) { // EL FANTASMA
          let t = jefe.timer % Math.floor(150 * velDisp);
          if (t === 0) {
              jefe.x = Math.random() * 300 + 200; jefe.y = Math.random() * 100 + 40; jefe.visible = true;
          }
          if (t === Math.floor(60 * velDisp)) {
              // El fantasma lanza bombas con físicas de rebote
              dispararJefe(jefe.x + 20, jefe.y + 30, -3, 0, 'bomba_fantasma');
              dispararJefe(jefe.x + 20, jefe.y + 30, -1, 0, 'bomba_fantasma');
          }
          if (t > 90 * velDisp) jefe.visible = false;
      }
      else if (nivel === 5) { // EL COLOSO
          jefe.x += Math.sin(jefe.timer * 0.02) * 0.5;
          if (jefe.timer % Math.floor(60 * velDisp) === 0) dispararJefe(jefe.x, jefe.y + 70, -6, 0, 'obus');
          if (jefe.timer % Math.floor(90 * velDisp) === 0) {
              // El coloso lanza bombas que rebotan infinitamente
              dispararJefe(jefe.x + 30, jefe.y + 20, -4, 0, 'bomba_coloso'); 
          }
      }
  }

  function dibujarEntidad(img, x, y, w, h, invertido) {
      if (!img.complete || img.naturalHeight === 0) return;
      if (invertido) { ctx.save(); ctx.translate(x + w, y); ctx.scale(-1, 1); ctx.drawImage(img, 0, 0, w, h); ctx.restore(); } 
      else { ctx.drawImage(img, x, y, w, h); }
  }

  // --- RENDERIZADO ---
  function dibujar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = modoDificil ? "#3a2a2a" : "#4a5a6a"; ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#222"; ctx.fillRect(0, SUELO_Y + 50, canvas.width, canvas.height);
    ctx.fillStyle = "#111"; ctx.fillRect(0, SUELO_Y + 50, canvas.width, 10);

    // UI Superior
    ctx.fillStyle = "#d32f2f"; ctx.font = "20px Arial";
    let corazones = ""; for(let v=0; v<jugador.vidas; v++) corazones += "❤️";
    ctx.fillText(corazones, 10, 20);

    ctx.fillStyle = "#fff"; ctx.font = "bold 16px 'Courier New'"; ctx.textAlign = "right";
    ctx.fillText("PUNTOS: " + puntuacion, canvas.width - 10, 20);
    ctx.textAlign = "left";

    if (jugador.armaTimer > 0) {
        ctx.fillStyle = "#ffff00"; ctx.font = "bold 14px 'Courier New'";
        ctx.fillText("⚡ RÁFAGA ACTIVA", 10, 45);
    }

    if (modoDificil) {
        ctx.fillStyle = "#ff4500"; ctx.font = "bold 14px 'Courier New'"; ctx.textAlign = "center";
        ctx.fillText("MODO DIFÍCIL", canvas.width/2, 50); ctx.textAlign = "left";
    }

    if (estadoJuego === 'JUGANDO') {
        ctx.fillStyle = "#333"; ctx.fillRect(150, 15, 300, 15);
        ctx.fillStyle = "#8b0000"; ctx.fillRect(152, 17, 296 * (jefe.hp / jefe.maxHp), 11);
        ctx.fillStyle = "#fff"; ctx.font = "bold 14px 'Courier New'"; ctx.textAlign = "center";
        ctx.fillText(nombresJefes[nivel], canvas.width/2, 27); ctx.textAlign = "left";
    }

    // Dibujar Cajas
    cajas.forEach(c => {
        ctx.font = "24px Arial"; ctx.fillText("🎁", c.x, c.y);
    });

    // Dibujar Jefe
    if ((estadoJuego === 'JUGANDO' || estadoJuego === 'TRANSICION') && jefe.visible) {
        if (jefe.tipo === 'tanque') {
            dibujarEntidad(imgTanque, jefe.x, jefe.y, jefe.ancho, jefe.alto, false);
            if (jefe.escudo) {
                ctx.strokeStyle = "#00ffff"; ctx.lineWidth = 4; ctx.beginPath();
                ctx.arc(jefe.x, jefe.y + 30, 40, Math.PI*0.5, Math.PI*1.5); ctx.stroke();
            }
        } else if (jefe.tipo === 'helicoptero') {
            dibujarEntidad(imgHeli, jefe.x, jefe.y, jefe.ancho, jefe.alto, false);
        } else if (jefe.tipo === 'coloso') {
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
            } else { dibujarEntidad(imgSoldado, jugador.x, jugador.y, jugador.ancho, jugador.alto, invertido); }
        }
    } else {
        ctx.fillStyle = '#555'; ctx.fillRect(jugador.x+10, jugador.y+30, 20, 30);
        ctx.fillStyle = '#fff'; ctx.font = "20px Arial"; ctx.fillText("💀", jugador.x+8, jugador.y+40);
    }

    // Pantallas
    if (estadoJuego === 'INICIO') {
        ctx.fillStyle = "rgba(0, 0, 0, 0.8)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 24px 'Courier New'";
        ctx.fillText("CLIC O ESPACIO PARA INICIAR", canvas.width/2, canvas.height/2);
    } else if (estadoJuego === 'TRANSICION') {
        ctx.fillStyle = "rgba(0, 0, 0, 0.7)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 32px 'Courier New'";
        ctx.fillText(nombresJefes[nivel], canvas.width/2, canvas.height/2);
    } else if (estadoJuego === 'GAMEOVER') {
        ctx.fillStyle = "rgba(100, 0, 0, 0.85)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 36px 'Courier New'";
        ctx.fillText("HAS CAÍDO", canvas.width/2, canvas.height/2 - 25);
        ctx.font = "bold 18px 'Courier New'"; ctx.fillText("PUNTUACIÓN FINAL: " + puntuacion, canvas.width/2, canvas.height/2 + 10);
        ctx.fillText("Presiona ESPACIO para reiniciar", canvas.width/2, canvas.height/2 + 40);
    } else if (estadoJuego === 'VICTORIA') {
        ctx.fillStyle = "rgba(0, 50, 0, 0.9)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#ffd700"; ctx.textAlign = "center"; ctx.font = "bold 36px 'Courier New'";
        ctx.fillText("¡MISIÓN CUMPLIDA!", canvas.width/2, canvas.height/2 - 40);
        ctx.fillStyle = "#fff"; ctx.font = "bold 20px 'Courier New'"; 
        ctx.fillText("PUNTUACIÓN TOTAL: " + puntuacion, canvas.width/2, canvas.height/2 - 5);
        ctx.font = "bold 16px 'Courier New'"; 
        ctx.fillText("[ESPACIO] Jugar Normal  |  [H] MODO DIFÍCIL", canvas.width/2, canvas.height/2 + 40);
    }
  }

  // --- BUCLE DE LÓGICA ---
  function bucle() {
    if (estadoJuego === 'TRANSICION') {
        transicionTimer--;
        if (transicionTimer <= 0) estadoJuego = 'JUGANDO';
        dibujar(); requestAnimationFrame(bucle); return;
    }
    if (estadoJuego !== 'JUGANDO') return;

    if (jugador.invencible > 0) jugador.invencible--;
    if (cooldownDisparo > 0) cooldownDisparo--;
    if (jugador.armaTimer > 0) jugador.armaTimer--;

    // Controles Jugador
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

    // Físicas Cajas (Airdrops)
    for (let i = cajas.length - 1; i >= 0; i--) {
        let c = cajas[i];
        if (c.y < SUELO_Y + 20) c.y += c.velY; // Cae hasta el suelo
        
        // Colisión Jugador vs Caja
        if (dH.x < c.x + 24 && dH.x + dH.w > c.x && dH.y < c.y + 24 && dH.h + dH.y > c.y) {
            if (c.tipo === 'vida') jugador.vidas++;
            else jugador.armaTimer = 400; // Unos 10 segundos de ráfaga
            
            explosiones.push({ x: c.x, y: c.y, timer: 10, color: '#00ff00' });
            cajas.splice(i, 1);
        }
    }

    // Balas Jugador vs Jefe
    for (let i = balas.length - 1; i >= 0; i--) {
        balas[i].x += 14 * balas[i].dir; 
        let b = balas[i];
        
        if (jefe.visible && b.x < jH.x + jH.w && b.x + b.w > jH.x && b.y < jH.y + jH.h && b.h + b.y > jH.y) {
            let haceDano = true;
            if (nivel === 2 && jefe.y < 100) haceDano = false; 
            if (nivel === 3 && jefe.escudo && b.x < jefe.x) haceDano = false; 
            
            if (haceDano) {
                explosiones.push({ x: b.x, y: b.y - 10, timer: 5, color: '#ffff00' });
                jefe.hp--;
                puntuacion += 10; // +10 Puntos por impacto
                chequearCaja();
                
                if (jefe.hp <= 0) {
                    puntuacion += 50; // +50 Puntos por derrotar al jefe
                    chequearCaja();
                    explosiones.push({ x: jefe.x, y: jefe.y, timer: 30, color: '#ff4500' });
                    explosiones.push({ x: jefe.x+40, y: jefe.y+20, timer: 35, color: '#ff4500' });
                    if (nivel < 5) {
                        estadoJuego = 'TRANSICION'; transicionTimer = 100;
                        setTimeout(() => iniciarNivel(nivel + 1), 1500);
                    } else { estadoJuego = 'VICTORIA'; }
                }
            } else { explosiones.push({ x: b.x, y: b.y - 10, timer: 5, color: '#aaaaaa' }); }
            balas.splice(i, 1); continue;
        }
        
        // Penalización por fallar balas (-1 Punto)
        if (b.x < -20 || b.x > canvas.width + 20) {
            puntuacion -= 1; 
            balas.splice(i, 1);
        }
    }

    // Físicas Balas Enemigas vs Jugador (Gravedad y Rebotes)
    for (let i = balasEnemigas.length - 1; i >= 0; i--) {
        let be = balasEnemigas[i];
        
        if (be.tipo === 'obus') {
            be.x += be.velX; be.y += be.velY;
        } else if (be.tipo.startsWith('bomba')) {
            be.velY += 0.3; // Gravedad
            be.x += be.velX; be.y += be.velY;
            
            // Lógica de rebote en el suelo
            if (be.y >= SUELO_Y + 20) {
                be.y = SUELO_Y + 20;
                be.velY = -be.velY * 0.7; // Absorción de impacto
                be.rebotes++;
                
                // Fantasma: rebota una vez y a la segunda se elimina
                if (be.tipo === 'bomba_fantasma' && be.rebotes >= 2) {
                    explosiones.push({ x: be.x, y: be.y, timer: 5, color: '#555' });
                    balasEnemigas.splice(i, 1); continue;
                }
                // Coloso: rebota infinitamente hasta salir de pantalla (no hacemos break aquí)
            }
        }
        
        if (be.x < dH.x + dH.w && be.x + be.w > dH.x && be.y < dH.y + dH.h && be.h + be.y > dH.y) {
            recibirDano(); balasEnemigas.splice(i, 1); continue;
        }
        
        if (be.x < -20 || be.x > canvas.width + 20 || be.y > canvas.height + 50) balasEnemigas.splice(i, 1);
    }

    for (let i = explosiones.length - 1; i >= 0; i--) {
        explosiones[i].timer--; if (explosiones[i].timer <= 0) explosiones.splice(i, 1); 
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
