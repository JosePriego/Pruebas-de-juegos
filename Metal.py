import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(page_title="Boss Rush: Ultimate Edition", layout="centered", page_icon="💀")

st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    h1 { color: #8b0000; font-family: 'Impact', 'Courier New', sans-serif; text-align: center; font-weight: 900; letter-spacing: 3px; text-shadow: 2px 2px 0px #000;}
    .stMarkdown p { text-align: center; color: #444; font-family: 'Courier New', Courier, monospace; font-weight: bold; font-size: 14px;}
</style>
""", unsafe_allow_html=True)

st.title("💀 BOSS RUSH: ULTIMATE EDITION")
st.write("**A / D** = Mover | **ESPACIO** = Saltar | **S** = Agacharse | **X** = Disparar | **C** = Dash | **Z** = Granada | **M** = Música")

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
  body { display: flex; justify-content: center; margin: 0; background-color: #1a1a1a; overflow: hidden; user-select: none; font-family: 'Courier New', Courier, monospace; }
  canvas { border: 4px solid #111; background-color: #7a8a99; border-radius: 5px; cursor: pointer; box-shadow: 0px 8px 0px #000; }
</style>
</head>
<body>
<canvas id="juego" width="600" height="280" tabindex="1"></canvas>
<script>
  const canvas = document.getElementById("juego");
  const ctx = canvas.getContext("2d");

  const imgSoldado = new Image(); let srcSol = "INYECTAR_SOLDADO"; if(srcSol.length > 50) imgSoldado.src = srcSol;
  const imgTanque = new Image(); let srcTan = "INYECTAR_TANQUE"; if(srcTan.length > 50) imgTanque.src = srcTan;
  const imgHeli = new Image(); let srcHel = "INYECTAR_HELI"; if(srcHel.length > 50) imgHeli.src = srcHel;

  // --- AUDIO DE 8-BITS ---
  const AudioContext = window.AudioContext || window.webkitAudioContext;
  let audioCtx; let musicaMuted = false;

  function initAudio() {
      if (!audioCtx) { audioCtx = new AudioContext(); }
      if (audioCtx.state === 'suspended') { audioCtx.resume(); }
  }

  function playSound(tipo) {
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator();
      const gainNode = audioCtx.createGain();
      osc.connect(gainNode); gainNode.connect(audioCtx.destination);
      const now = audioCtx.currentTime;

      if (tipo === 'shoot') {
          osc.type = 'square'; osc.frequency.setValueAtTime(600, now); osc.frequency.exponentialRampToValueAtTime(100, now + 0.1);
          gainNode.gain.setValueAtTime(0.04, now); gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
          osc.start(now); osc.stop(now + 0.1);
      } else if (tipo === 'shotgun') {
          osc.type = 'sawtooth'; osc.frequency.setValueAtTime(300, now); osc.frequency.exponentialRampToValueAtTime(50, now + 0.2);
          gainNode.gain.setValueAtTime(0.08, now); gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
          osc.start(now); osc.stop(now + 0.2);
      } else if (tipo === 'laser') {
          osc.type = 'sine'; osc.frequency.setValueAtTime(1200, now); osc.frequency.linearRampToValueAtTime(800, now + 0.1);
          gainNode.gain.setValueAtTime(0.05, now); gainNode.gain.linearRampToValueAtTime(0.001, now + 0.1);
          osc.start(now); osc.stop(now + 0.1);
      } else if (tipo === 'hit') {
          osc.type = 'sawtooth'; osc.frequency.setValueAtTime(200, now);
          gainNode.gain.setValueAtTime(0.05, now); gainNode.gain.linearRampToValueAtTime(0.001, now + 0.1);
          osc.start(now); osc.stop(now + 0.1);
      } else if (tipo === 'explosion' || tipo === 'grenade') {
          osc.type = 'square'; osc.frequency.setValueAtTime(100, now); osc.frequency.exponentialRampToValueAtTime(10, now + 0.5);
          gainNode.gain.setValueAtTime(tipo==='grenade'? 0.3 : 0.15, now); gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.5);
          osc.start(now); osc.stop(now + 0.5);
      } else if (tipo === 'dash') {
          osc.type = 'sine'; osc.frequency.setValueAtTime(300, now); osc.frequency.linearRampToValueAtTime(800, now + 0.2);
          gainNode.gain.setValueAtTime(0.05, now); gainNode.gain.linearRampToValueAtTime(0.001, now + 0.2);
          osc.start(now); osc.stop(now + 0.2);
      } else if (tipo === 'caja') {
          osc.type = 'sine'; osc.frequency.setValueAtTime(500, now); osc.frequency.setValueAtTime(800, now + 0.1);
          gainNode.gain.setValueAtTime(0.1, now); gainNode.gain.linearRampToValueAtTime(0.001, now + 0.3);
          osc.start(now); osc.stop(now + 0.3);
      }
  }

  const melodia = [130.81, 130.81, 155.56, 130.81, 174.61, 185.00, 174.61, 155.56]; 
  let notaActual = 0; let idMusica = null;

  function tocarNotaMusical() {
      if (musicaMuted || !audioCtx || (estadoJuego !== 'JUGANDO' && estadoJuego !== 'TRANSICION')) return;
      const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
      osc.connect(gain); gain.connect(audioCtx.destination);
      osc.type = 'square'; osc.frequency.value = melodia[notaActual];
      gain.gain.setValueAtTime(0.02, audioCtx.currentTime); gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.15);
      osc.start(audioCtx.currentTime); osc.stop(audioCtx.currentTime + 0.15);
      notaActual = (notaActual + 1) % melodia.length;
  }
  function arrancarMusica() { if (idMusica) clearInterval(idMusica); idMusica = setInterval(tocarNotaMusical, 200); }

  // --- VARIABLES DEL JUEGO ---
  const SUELO_Y = 200;
  let jugador = { x: 50, y: SUELO_Y, velY: 0, ancho: 45, alto: 55, agachado: false, vidas: 5, invencible: 0, dir: 1, arma: 'normal', armaTimer: 0, dashTimer: 0, dashCooldown: 0, granadas: 1 };
  let jefe = { x: 450, y: SUELO_Y, ancho: 80, alto: 60, tipo: 'tanque', hp: 10, maxHp: 10, timer: 0, estado: 0, escudo: false, visible: true, hitFlash: 0 };
  let nivel = 1;
  let nombresJefes = ["", "NIVEL 1: EL NOVATO", "NIVEL 2: EL CÓNDOR", "NIVEL 3: EL ESCUDO", "NIVEL 4: EL FANTASMA", "NIVEL 5: EL MEGA-COLOSO"];
  
  let balas = []; let balasEnemigas = []; let explosiones = []; let cajas = []; 
  let casquillos = []; let lluvia = [];
  
  // Generar gotas de lluvia
  for(let i=0; i<60; i++) lluvia.push({x: Math.random()*600, y: Math.random()*280, velY: Math.random()*5+10});

  let estadoJuego = 'INICIO'; let transicionTimer = 0; let cooldownDisparo = 0;
  let puntuacion = 0; let siguienteCaja = 100; let modoDificil = false;
  let shakeTimer = 0; let shakeMag = 0;

  function hacerTemblar(duracion, magnitud) { shakeTimer = duracion; shakeMag = magnitud; }
  
  const teclas = {};
  window.addEventListener('keydown', (e) => {
      teclas[e.code] = true;
      if ((e.code === "Space" || e.code === "ArrowUp" || e.code === "KeyW")) {
          e.preventDefault(); initAudio(); 
          if (estadoJuego === 'INICIO' || estadoJuego === 'GAMEOVER') { modoDificil = false; iniciarNivel(1); } 
          else if (estadoJuego === 'VICTORIA') { modoDificil = false; iniciarNivel(1); }
          else if (estadoJuego === 'JUGANDO' && jugador.y === SUELO_Y && !jugador.agachado && jugador.dashTimer <= 0) { jugador.velY = -15; }
      }
      if (e.code === "KeyH" && estadoJuego === 'VICTORIA') { modoDificil = true; iniciarNivel(1); }
      if (e.code === "KeyM" || e.key === "m") { musicaMuted = !musicaMuted; }

      // Disparar
      if ((e.code === "KeyX" || e.key === "x") && estadoJuego === 'JUGANDO' && jugador.dashTimer <= 0) {
          if (cooldownDisparo <= 0) {
              let alt = jugador.agachado ? jugador.y + 30 : jugador.y + 20;
              let px = jugador.dir === 1 ? jugador.x + 40 : jugador.x - 10;
              
              if (jugador.arma === 'escopeta') {
                  balas.push({ x: px, y: alt, w: 12, h: 4, dir: jugador.dir, velY: 0, tipo: 'normal', dmg: 1 });
                  balas.push({ x: px, y: alt, w: 12, h: 4, dir: jugador.dir, velY: -1.5, tipo: 'normal', dmg: 1 });
                  balas.push({ x: px, y: alt, w: 12, h: 4, dir: jugador.dir, velY: 1.5, tipo: 'normal', dmg: 1 });
                  cooldownDisparo = 25; playSound('shotgun');
              } else if (jugador.arma === 'laser') {
                  balas.push({ x: px, y: alt-2, w: 40, h: 6, dir: jugador.dir, velY: 0, tipo: 'laser', dmg: 1 });
                  cooldownDisparo = 10; playSound('laser');
              } else {
                  balas.push({ x: px, y: alt, w: 15, h: 4, dir: jugador.dir, velY: 0, tipo: 'normal', dmg: 1 });
                  cooldownDisparo = jugador.armaTimer > 0 ? 5 : 15; playSound('shoot'); 
              }
              // Generar casquillo
              casquillos.push({x: jugador.x + 20, y: alt, velX: -jugador.dir * (Math.random()*2+2), velY: -(Math.random()*3+2)});
          }
      }

      // Granada (Botón de Pánico)
      if ((e.code === "KeyZ" || e.key === "z") && estadoJuego === 'JUGANDO') {
          if (jugador.granadas > 0) {
              jugador.granadas--;
              balasEnemigas = []; // Limpia la pantalla
              playSound('grenade');
              hacerTemblar(40, 20);
              for(let i=0; i<15; i++) explosiones.push({x: Math.random()*canvas.width, y: Math.random()*SUELO_Y, timer: 20 + Math.random()*20, color: '#ff4500'});
              danarJefe(6); // Daño masivo
          }
      }

      // Dash
      if ((e.code === "ShiftLeft" || e.code === "ShiftRight" || e.code === "KeyC" || e.key === "c") && estadoJuego === 'JUGANDO') {
          if (jugador.dashCooldown <= 0 && jugador.dashTimer <= 0) {
              jugador.dashTimer = 12; jugador.dashCooldown = 60; jugador.invencible = 12; jugador.agachado = false; playSound('dash'); 
          }
      }
  });
  window.addEventListener('keyup', (e) => { teclas[e.code] = false; });
  canvas.addEventListener('mousedown', () => { initAudio(); });
  canvas.focus();

  function iniciarNivel(n) {
      nivel = n;
      jugador.x = 50; jugador.y = SUELO_Y; jugador.velY = 0; jugador.dir = 1; jugador.dashTimer = 0; jugador.dashCooldown = 0;
      jugador.granadas = 1; // 1 Granada por nivel
      
      if(n === 1) {
          jugador.vidas = modoDificil ? 3 : 5; 
          puntuacion = 0; siguienteCaja = 100; jugador.armaTimer = 0; jugador.arma = 'normal';
          arrancarMusica();
      }
      
      balas = []; balasEnemigas = []; explosiones = []; cajas = []; casquillos = [];
      jefe.timer = 0; jefe.escudo = false; jefe.visible = true; shakeTimer = 0;
      
      let mult = modoDificil ? 1.5 : 1; 
      if (nivel === 1) { jefe.tipo='tanque'; jefe.maxHp=Math.floor(20*mult); jefe.x=450; jefe.y=SUELO_Y; jefe.ancho=80; jefe.alto=60; }
      if (nivel === 2) { jefe.tipo='helicoptero'; jefe.maxHp=Math.floor(25*mult); jefe.x=400; jefe.y=50; jefe.ancho=90; jefe.alto=50; }
      if (nivel === 3) { jefe.tipo='tanque'; jefe.maxHp=Math.floor(35*mult); jefe.x=450; jefe.y=SUELO_Y; jefe.ancho=80; jefe.alto=60; jefe.escudo=true;}
      if (nivel === 4) { jefe.tipo='helicoptero'; jefe.maxHp=Math.floor(40*mult); jefe.x=400; jefe.y=100; jefe.ancho=90; jefe.alto=50; jefe.visible=false;}
      if (nivel === 5) { jefe.tipo='coloso'; jefe.maxHp=Math.floor(70*mult); jefe.x=450; jefe.y=SUELO_Y-40; jefe.ancho=100; jefe.alto=100; }
      
      jefe.hp = jefe.maxHp;
      estadoJuego = 'TRANSICION'; transicionTimer = 150;
      if (n === 1) requestAnimationFrame(bucle); 
  }

  function recibirDano() {
      if (jugador.invencible <= 0) {
          jugador.vidas--; puntuacion -= 25; jugador.invencible = 60; hacerTemblar(15, 12); playSound('explosion'); 
          explosiones.push({x: jugador.x, y: jugador.y, timer: 15, color: '#ff0000'});
          if (jugador.vidas <= 0) estadoJuego = 'GAMEOVER';
      }
  }

  function danarJefe(dmg) {
      if (!jefe.visible || estadoJuego !== 'JUGANDO') return;
      jefe.hp -= dmg;
      jefe.hitFlash = 3; // Flash blanco
      if (jefe.hp <= 0) {
          puntuacion += 50; chequearCaja(); playSound('explosion'); hacerTemblar(35, 15); 
          explosiones.push({ x: jefe.x, y: jefe.y, timer: 30, color: '#ff4500' });
          explosiones.push({ x: jefe.x+40, y: jefe.y+20, timer: 35, color: '#ff4500' });
          if (nivel < 5) {
              estadoJuego = 'TRANSICION'; transicionTimer = 100;
              setTimeout(() => iniciarNivel(nivel + 1), 1500);
          } else { estadoJuego = 'VICTORIA'; }
      }
  }

  function chequearCaja() {
      if (!modoDificil && puntuacion >= siguienteCaja) {
          let r = Math.random();
          let t = 'vida';
          if (r > 0.3) t = 'rafaga';
          if (r > 0.6) t = 'escopeta';
          if (r > 0.85) t = 'laser';
          cajas.push({ x: Math.random() * 300 + 100, y: -30, velY: 3, tipo: t });
          siguienteCaja += 100;
      }
  }

  function dispararJefe(x, y, vx, vy, tipo) {
      if (tipo.startsWith('bomba')) balasEnemigas.push({ x: x, y: y, velX: vx, velY: -2, tipo: tipo, w: 10, h: 10, rebotes: 0 });
      else balasEnemigas.push({ x: x, y: y, velX: vx, velY: vy, tipo: tipo, w: 10, h: 10 });
  }

  function actualizarIAJefe() {
      jefe.timer++; let velDisp = modoDificil ? 0.7 : 1; 
      if (jefe.hitFlash > 0) jefe.hitFlash--;

      if (nivel === 1) { 
          jefe.x += Math.sin(jefe.timer * 0.05) * 1.5; 
          if (jefe.timer % Math.floor(80 * velDisp) === 0) dispararJefe(jefe.x, jefe.y + 25, -5, 0, 'obus');
      } else if (nivel === 2) { 
          let ciclo = Math.floor(250 * velDisp); let t = jefe.timer % ciclo;
          if (t < ciclo * 0.4) { jefe.y = 50; } else if (t < ciclo * 0.6) { jefe.y += 3; } 
          else if (t < ciclo * 0.8) {
              jefe.y = SUELO_Y - 20; 
              if (t === Math.floor(ciclo * 0.7)) dispararJefe(jefe.x, jefe.y + 25, -6, 0, 'obus');
          } else { jefe.y -= 3; } 
      } else if (nivel === 3) { 
          jefe.x += Math.sin(jefe.timer * 0.03) * 1;
          if (jefe.timer % Math.floor(250 * velDisp) < 150 * velDisp) { jefe.escudo = true; } 
          else {
              jefe.escudo = false; 
              if (jefe.timer % 20 === 0) dispararJefe(jefe.x, jefe.y + 25, -7, 0, 'obus'); 
          }
      } else if (nivel === 4) { 
          let t = jefe.timer % Math.floor(150 * velDisp);
          if (t === 0) { jefe.x = Math.random() * 300 + 200; jefe.y = Math.random() * 100 + 40; jefe.visible = true; }
          if (t === Math.floor(60 * velDisp)) {
              dispararJefe(jefe.x + 20, jefe.y + 30, -3, 0, 'bomba_fantasma');
              dispararJefe(jefe.x + 20, jefe.y + 30, -1, 0, 'bomba_fantasma');
          }
          if (t > 90 * velDisp) jefe.visible = false;
      } else if (nivel === 5) { 
          jefe.x += Math.sin(jefe.timer * 0.02) * 0.5;
          if (jefe.timer % Math.floor(60 * velDisp) === 0) { dispararJefe(jefe.x, jefe.y + 70, -6, 0, 'obus'); hacerTemblar(4, 3); }
          if (jefe.timer % Math.floor(90 * velDisp) === 0) { dispararJefe(jefe.x + 30, jefe.y + 20, -4, 0, 'bomba_coloso'); }
      }
  }

  function dibujarEntidad(img, x, y, w, h, invertido) {
      if (!img.complete || img.naturalHeight === 0) return;
      if (invertido) { ctx.save(); ctx.translate(x + w, y); ctx.scale(-1, 1); ctx.drawImage(img, 0, 0, w, h); ctx.restore(); } 
      else { ctx.drawImage(img, x, y, w, h); }
  }

  function dibujar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    if (shakeTimer > 0) { ctx.translate((Math.random()-0.5)*shakeMag, (Math.random()-0.5)*shakeMag); }

    // Clima dinámico
    let climaMalo = (nivel % 2 === 0);
    ctx.fillStyle = climaMalo ? "#2a3a4a" : "#4a5a6a"; 
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Relámpagos
    if (climaMalo && Math.random() < 0.01) { ctx.fillStyle = "rgba(255,255,255,0.7)"; ctx.fillRect(0,0,canvas.width,canvas.height); }

    ctx.fillStyle = "#222"; ctx.fillRect(0, SUELO_Y + 50, canvas.width, canvas.height);
    ctx.fillStyle = "#111"; ctx.fillRect(0, SUELO_Y + 50, canvas.width, 10);

    // Lluvia
    if (climaMalo) {
        ctx.strokeStyle = "rgba(255,255,255,0.3)"; ctx.lineWidth = 1; ctx.beginPath();
        lluvia.forEach(l => { ctx.moveTo(l.x, l.y); ctx.lineTo(l.x - 2, l.y + 10); }); ctx.stroke();
    }

    // UI
    ctx.fillStyle = "#d32f2f"; ctx.font = "20px Arial";
    let corazones = ""; for(let v=0; v<jugador.vidas; v++) corazones += "❤️";
    ctx.fillText(corazones, 10, 20);

    ctx.fillStyle = "#fff"; ctx.font = "bold 16px 'Courier New'"; ctx.textAlign = "right";
    ctx.fillText("PUNTOS: " + puntuacion, canvas.width - 10, 20); ctx.textAlign = "left";

    // Textos de Armas y Granadas
    let uiY = 40;
    if (jugador.granadas > 0) { ctx.fillStyle = "#00ff00"; ctx.font = "bold 14px 'Courier New'"; ctx.fillText("💣 GRANADAS: " + jugador.granadas, 10, uiY); uiY+=20; }
    if (jugador.armaTimer > 0) {
        ctx.fillStyle = "#ffff00"; ctx.font = "bold 14px 'Courier New'"; 
        let nom = jugador.arma === 'escopeta' ? 'ESCOPETA' : (jugador.arma === 'laser' ? 'LÁSER' : 'RÁFAGA');
        ctx.fillText("⚡ " + nom + " ACTIVA", 10, uiY);
    } else if (jugador.dashCooldown <= 0) {
        ctx.fillStyle = "#00ffff"; ctx.font = "bold 14px 'Courier New'"; ctx.fillText("💨 DASH LISTO", 10, uiY);
    }

    ctx.fillStyle = musicaMuted ? "#888" : "#fff"; ctx.font = "14px 'Courier New'"; ctx.textAlign = "right";
    ctx.fillText(musicaMuted ? "🔇" : "🔊", canvas.width - 10, 45); ctx.textAlign = "left";

    if (modoDificil) { ctx.fillStyle = "#ff4500"; ctx.font = "bold 14px 'Courier New'"; ctx.textAlign = "center"; ctx.fillText("MODO DIFÍCIL", canvas.width/2, 50); ctx.textAlign = "left"; }

    if (estadoJuego === 'JUGANDO') {
        ctx.fillStyle = "#333"; ctx.fillRect(150, 15, 300, 15);
        ctx.fillStyle = "#8b0000"; ctx.fillRect(152, 17, 296 * (Math.max(0, jefe.hp) / jefe.maxHp), 11);
        ctx.fillStyle = "#fff"; ctx.font = "bold 14px 'Courier New'"; ctx.textAlign = "center";
        ctx.fillText(nombresJefes[nivel], canvas.width/2, 27); ctx.textAlign = "left";
    }

    // Dibujar Casquillos
    ctx.fillStyle = '#ffd700'; casquillos.forEach(c => ctx.fillRect(c.x, c.y, 4, 2));

    // Cajas
    cajas.forEach(c => { ctx.font = "24px Arial"; ctx.fillText("🎁", c.x, c.y); });

    // Jefe
    if ((estadoJuego === 'JUGANDO' || estadoJuego === 'TRANSICION') && jefe.visible) {
        // Flash blanco por daño
        if (jefe.hitFlash > 0) { ctx.globalCompositeOperation = "source-atop"; ctx.filter = "brightness(200%) grayscale(100%)"; }
        
        if (jefe.tipo === 'tanque') {
            dibujarEntidad(imgTanque, jefe.x, jefe.y, jefe.ancho, jefe.alto, false);
            if (jefe.escudo) { ctx.strokeStyle = "#00ffff"; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(jefe.x, jefe.y + 30, 40, Math.PI*0.5, Math.PI*1.5); ctx.stroke(); }
        } else if (jefe.tipo === 'helicoptero') { dibujarEntidad(imgHeli, jefe.x, jefe.y, jefe.ancho, jefe.alto, false);
        } else if (jefe.tipo === 'coloso') { dibujarEntidad(imgHeli, jefe.x + 10, jefe.y - 10, 80, 50, false); dibujarEntidad(imgTanque, jefe.x, jefe.y + 30, 100, 70, false); }
        
        ctx.filter = "none"; ctx.globalCompositeOperation = "source-over"; // Resetear filtros
    }

    // Balas
    balas.forEach(b => { 
        ctx.fillStyle = b.tipo==='laser' ? '#00ffff' : '#ffaa00'; 
        ctx.fillRect(b.x, b.y, b.w, b.h); 
    });
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
        let invertido = jugador.dir === -1;
        if (jugador.dashTimer > 0) {
            ctx.globalAlpha = 0.4; let offset = 20 * jugador.dir;
            dibujarEntidad(imgSoldado, jugador.x - offset, jugador.y, jugador.ancho, jugador.alto, invertido);
            dibujarEntidad(imgSoldado, jugador.x - offset*2, jugador.y, jugador.ancho, jugador.alto, invertido); ctx.globalAlpha = 1.0;
        }

        if (jugador.invencible === 0 || jugador.dashTimer > 0 || Math.floor(jugador.invencible / 4) % 2 === 0) {
            if (jugador.agachado && jugador.y === SUELO_Y) {
                if(invertido) { ctx.save(); ctx.translate(jugador.x + jugador.ancho, jugador.y + 25); ctx.scale(-1, 1); ctx.drawImage(imgSoldado, 0, 0, jugador.ancho, jugador.alto - 25); ctx.restore(); } 
                else if (imgSoldado.complete && imgSoldado.naturalHeight !== 0) ctx.drawImage(imgSoldado, jugador.x, jugador.y + 25, jugador.ancho, jugador.alto - 25);
            } else { dibujarEntidad(imgSoldado, jugador.x, jugador.y, jugador.ancho, jugador.alto, invertido); }
        }
    } else {
        ctx.fillStyle = '#555'; ctx.fillRect(jugador.x+10, jugador.y+30, 20, 30);
        ctx.fillStyle = '#fff'; ctx.font = "20px Arial"; ctx.fillText("💀", jugador.x+8, jugador.y+40);
    }

    ctx.restore();

    if (estadoJuego === 'INICIO') {
        ctx.fillStyle = "rgba(0, 0, 0, 0.8)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 24px 'Courier New'";
        ctx.fillText("CLIC PARA ACTIVAR AUDIO Y EMPEZAR", canvas.width/2, canvas.height/2);
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
    if (jugador.armaTimer > 0) { jugador.armaTimer--; if (jugador.armaTimer<=0) jugador.arma = 'normal'; }
    if (jugador.dashCooldown > 0) jugador.dashCooldown--;
    if (shakeTimer > 0) shakeTimer--; 

    // Lluvia y partículas
    if (nivel % 2 === 0) {
        lluvia.forEach(l => { l.y += l.velY; l.x -= 2; if(l.y>canvas.height) {l.y=-10; l.x=Math.random()*canvas.width+50;} });
    }
    for(let i=casquillos.length-1; i>=0; i--) {
        let c = casquillos[i]; c.velY += 0.5; c.x += c.velX; c.y += c.velY; 
        if(c.y > SUELO_Y+40) { c.y = SUELO_Y+40; c.velY = -c.velY*0.5; }
        if(c.x < 0 || c.x > canvas.width || Math.abs(c.velY) < 0.1) casquillos.splice(i,1);
    }

    if (jugador.dashTimer > 0) { jugador.dashTimer--; jugador.x += 12 * jugador.dir; } 
    else {
        jugador.agachado = (teclas['ArrowDown'] || teclas['KeyS']) && jugador.y === SUELO_Y;
        if (!jugador.agachado) {
            if (teclas['ArrowRight'] || teclas['KeyD']) { jugador.x += 4; jugador.dir = 1; }
            if (teclas['ArrowLeft'] || teclas['KeyA']) { jugador.x -= 4; jugador.dir = -1; }
        }
    }

    if (jugador.x < 0) jugador.x = 0; if (jugador.x > canvas.width - jugador.ancho) jugador.x = canvas.width - jugador.ancho;

    if (!jugador.agachado || jugador.y < SUELO_Y) { jugador.velY += 1.0; jugador.y += jugador.velY; } 
    else { jugador.velY += 2.0; jugador.y += jugador.velY; }
    if (jugador.y > SUELO_Y) { jugador.y = SUELO_Y; jugador.velY = 0; }

    actualizarIAJefe();

    let jH = { x: jefe.x, y: jefe.y, w: jefe.ancho, h: jefe.alto };
    let dH = { x: jugador.x + 10, y: jugador.y + 5, w: jugador.ancho - 20, h: jugador.alto - 10 };
    if (jugador.agachado && jugador.y === SUELO_Y) { dH.y = jugador.y + 35; dH.h = jugador.alto - 35; }

    for (let i = cajas.length - 1; i >= 0; i--) {
        let c = cajas[i]; if (c.y < SUELO_Y + 20) c.y += c.velY; 
        if (dH.x < c.x + 24 && dH.x + dH.w > c.x && dH.y < c.y + 24 && dH.h + dH.y > c.y) {
            if (c.tipo === 'vida') jugador.vidas++;
            else { jugador.armaTimer = 400; jugador.arma = c.tipo; } 
            playSound('caja'); explosiones.push({ x: c.x, y: c.y, timer: 10, color: '#00ff00' }); cajas.splice(i, 1);
        }
    }

    for (let i = balas.length - 1; i >= 0; i--) {
        let b = balas[i];
        b.x += (b.tipo==='laser'? 25 : 14) * b.dir; 
        b.y += b.velY;
        
        if (jefe.visible && b.x < jH.x + jH.w && b.x + b.w > jH.x && b.y < jH.y + jH.h && b.h + b.y > jH.y) {
            let haceDano = true;
            if (nivel === 2 && jefe.y < 100) haceDano = false; 
            if (nivel === 3 && jefe.escudo && b.x < jefe.x) haceDano = false; 
            
            if (haceDano) {
                playSound('hit'); explosiones.push({ x: b.x, y: b.y - 10, timer: 5, color: '#ffff00' });
                puntuacion += 10; chequearCaja(); danarJefe(b.dmg);
            } else { explosiones.push({ x: b.x, y: b.y - 10, timer: 5, color: '#aaaaaa' }); }
            balas.splice(i, 1); continue;
        }
        if (b.x < -20 || b.x > canvas.width + 20) { puntuacion -= 1; balas.splice(i, 1); }
    }

    for (let i = balasEnemigas.length - 1; i >= 0; i--) {
        let be = balasEnemigas[i];
        if (be.tipo === 'obus') { be.x += be.velX; be.y += be.velY; } 
        else if (be.tipo.startsWith('bomba')) {
            be.velY += 0.3; be.x += be.velX; be.y += be.velY;
            if (be.y >= SUELO_Y + 20) {
                be.y = SUELO_Y + 20; be.velY = -be.velY * 0.7; be.rebotes++;
                if (be.tipo === 'bomba_fantasma' && be.rebotes >= 2) {
                    explosiones.push({ x: be.x, y: be.y, timer: 5, color: '#555' }); balasEnemigas.splice(i, 1); continue;
                }
            }
        }
        
        if (be.x < dH.x + dH.w && be.x + be.w > dH.x && be.y < dH.y + dH.h && be.h + be.y > dH.y) { recibirDano(); balasEnemigas.splice(i, 1); continue; }
        if (be.x < -20 || be.x > canvas.width + 20 || be.y > canvas.height + 50) balasEnemigas.splice(i, 1);
    }

    for (let i = explosiones.length - 1; i >= 0; i--) {
        explosiones[i].timer--; if (explosiones[i].timer <= 0) explosiones.splice(i, 1); 
    }

    dibujar();
    if (estadoJuego === 'JUGANDO' || estadoJuego === 'TRANSICION') { requestAnimationFrame(bucle); }
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
