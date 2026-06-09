import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(page_title="Boss Rush: Arcade Edition", layout="centered", page_icon="💀")

st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    h1 { color: #ff4500; font-family: 'Impact', 'Courier New', sans-serif; text-align: center; font-weight: 900; letter-spacing: 3px; text-shadow: 3px 3px 0px #000;}
    .stMarkdown p { text-align: center; color: #aaa; font-family: 'Courier New', Courier, monospace; font-weight: bold; font-size: 13px;}
</style>
""", unsafe_allow_html=True)

st.title("💥 SHADOW OF PIXEL: ULTIMATE ARCADE")
st.write("**A/D** = Mover | **ESPACIO** = Saltar | **S** = Agacharse | **X** = Disparar | **C** = Dash | **Z** = Granada | **P** = Pausa")

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
  body { display: flex; flex-direction: column; align-items: center; margin: 0; padding-top: 5px; background-color: #111; overflow: hidden; user-select: none; font-family: 'Courier New', Courier, monospace; }
  
  .btn-fs { background: #8b0000; color: white; border: 2px solid #ff4500; padding: 5px 15px; margin-bottom: 8px; cursor: pointer; font-family: 'Courier New', monospace; font-weight: bold; border-radius: 5px; transition: 0.2s; outline: none; }
  .btn-fs:hover { background: #ff4500; color: black; }
  
  .arcade-container { position: relative; border: 4px solid #333; border-radius: 5px; box-shadow: 0px 8px 0px #000; overflow: hidden; }
  .arcade-container::after {
      content: " "; display: block; position: absolute; top: 0; left: 0; bottom: 0; right: 0;
      background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
      z-index: 10; background-size: 100% 3px, 3px 100%; pointer-events: none;
  }
  
  canvas { background-color: #7a8a99; cursor: pointer; display: block; outline: none; }
  canvas:fullscreen { width: 100vw; height: 100vh; object-fit: contain; background-color: #000; }
</style>
</head>
<body>

<button class="btn-fs" id="btn-fs">🔲 PANTALLA COMPLETA</button>

<div class="arcade-container">
    <canvas id="juego" width="600" height="280" tabindex="1"></canvas>
</div>

<script>
  const canvas = document.getElementById("juego");
  const ctx = canvas.getContext("2d");
  const btnFs = document.getElementById("btn-fs");

  btnFs.addEventListener('click', () => {
      if (!document.fullscreenElement) { canvas.requestFullscreen().catch(err => { alert("Error: " + err.message); }); } 
      else { document.exitFullscreen(); }
      canvas.focus();
  });

  const imgSoldado = new Image(); let srcSol = "INYECTAR_SOLDADO"; if(srcSol.length > 50) imgSoldado.src = srcSol;
  const imgTanque = new Image(); let srcTan = "INYECTAR_TANQUE"; if(srcTan.length > 50) imgTanque.src = srcTan;
  const imgHeli = new Image(); let srcHel = "INYECTAR_HELI"; if(srcHel.length > 50) imgHeli.src = srcHel;

  // --- AUDIO SINTETIZADO ---
  const AudioContext = window.AudioContext || window.webkitAudioContext;
  let audioCtx; let musicaMuted = false;

  function initAudio() {
      if (!audioCtx) { audioCtx = new AudioContext(); }
      if (audioCtx.state === 'suspended') { audioCtx.resume(); }
  }

  function playSound(tipo) {
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator(); const gainNode = audioCtx.createGain();
      osc.connect(gainNode); gainNode.connect(audioCtx.destination); const now = audioCtx.currentTime;

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
          osc.type = 'sawtooth'; osc.frequency.setValueAtTime(240, now);
          gainNode.gain.setValueAtTime(0.05, now); gainNode.gain.linearRampToValueAtTime(0.001, now + 0.1);
          osc.start(now); osc.stop(now + 0.1);
      } else if (tipo === 'parry') {
          osc.type = 'sine'; osc.frequency.setValueAtTime(400, now); osc.frequency.linearRampToValueAtTime(1500, now + 0.3);
          gainNode.gain.setValueAtTime(0.15, now); gainNode.gain.linearRampToValueAtTime(0.001, now + 0.3);
          osc.start(now); osc.stop(now + 0.3);
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
  function pararMusica() { if (idMusica) clearInterval(idMusica); }

  // --- VARIABLES ---
  const SUELO_Y = 200;
  
  let jugador = { x: 50, y: SUELO_Y, velY: 0, ancho: 45, alto: 55, agachado: false, vidas: 5, maxVidas: 5, invencible: 0, dir: 1, arma: 'normal', armaTimer: 0, dashTimer: 0, dashCooldown: 0, granadas: 1, velocidad: 4, maxBalas: 4 };
  let jefe = { x: 450, y: SUELO_Y, ancho: 80, alto: 60, tipo: 'tanque', hp: 10, maxHp: 10, timer: 0, escudo: false, visible: true, hitFlash: 0 };
  
  let nivel = 1; let nombresJefes = ["", "NIVEL 1: EL NOVATO", "NIVEL 2: EL CÓNDOR", "NIVEL 3: EL ESCUDO", "NIVEL 4: EL FANTASMA", "NIVEL 5: EL MEGA-COLOSO"];
  let balas = []; let balasEnemigas = []; let explosiones = []; let cajas = []; let casquillos = []; let lluvia = []; let humo = []; let secuaces = [];
  
  for(let i=0; i<60; i++) lluvia.push({x: Math.random()*600, y: Math.random()*280, velY: Math.random()*5+10});

  let estadoJuego = 'INICIO'; let transicionTimer = 0; let cooldownDisparo = 0;
  let puntuacion = 0; let siguienteCaja = 100; let modoDificil = false;
  let shakeTimer = 0; let shakeMag = 0;
  
  let combo = 1;
  let impactosRecibidos = 0;
  
  // SOLUCIÓN DEL BUG: Variable de control del motor
  let animando = false;

  function hacerTemblar(duracion, magnitud) { shakeTimer = duracion; shakeMag = magnitud; }
  
  const teclas = {};
  window.addEventListener('keydown', (e) => {
      teclas[e.code] = true;
      
      if (e.code === "KeyP" || e.code === "Escape") {
          if (estadoJuego === 'JUGANDO') { 
              estadoJuego = 'PAUSA'; pararMusica(); dibujarPausa(); return; 
          } 
          else if (estadoJuego === 'PAUSA') { 
              estadoJuego = 'JUGANDO'; arrancarMusica(); 
              if (!animando) { animando = true; requestAnimationFrame(bucle); }
              return; 
          }
      }

      if (estadoJuego === 'PAUSA') return;

      if (estadoJuego === 'TIENDA') {
          if (e.code === "Digit1" || e.code === "Numpad1") { jugador.maxVidas++; jugador.vidas = jugador.maxVidas; pasarSiguienteNivel(); }
          if (e.code === "Digit2" || e.code === "Numpad2") { jugador.velocidad += 1.5; pasarSiguienteNivel(); }
          if (e.code === "Digit3" || e.code === "Numpad3") { jugador.maxBalas += 2; pasarSiguienteNivel(); }
          return;
      }

      if ((e.code === "Space" || e.code === "ArrowUp" || e.code === "KeyW")) {
          e.preventDefault(); initAudio(); 
          if (estadoJuego === 'INICIO' || estadoJuego === 'GAMEOVER') { modoDificil = false; iniciarNivel(1); } 
          else if (estadoJuego === 'VICTORIA') { modoDificil = false; iniciarNivel(1); }
          else if (estadoJuego === 'JUGANDO' && jugador.y === SUELO_Y && !jugador.agachado && jugador.dashTimer <= 0) { jugador.velY = -15; }
      }
      if (e.code === "KeyH" && estadoJuego === 'VICTORIA') { modoDificil = true; iniciarNivel(1); }
      if (e.code === "KeyM" || e.key === "m") { musicaMuted = !musicaMuted; }

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
                  if (balas.length < jugador.maxBalas) {
                      balas.push({ x: px, y: alt, w: 15, h: 4, dir: jugador.dir, velY: 0, tipo: 'normal', dmg: 1 });
                      cooldownDisparo = jugador.armaTimer > 0 ? 5 : 15; playSound('shoot'); 
                  }
              }
              casquillos.push({x: jugador.x + 20, y: alt, velX: -jugador.dir * (Math.random()*2+2), velY: -(Math.random()*3+2)});
          }
      }

      if ((e.code === "KeyZ" || e.key === "z") && estadoJuego === 'JUGANDO') {
          if (jugador.granadas > 0) {
              jugador.granadas--; balasEnemigas = []; playSound('grenade'); hacerTemblar(40, 20);
              for(let i=0; i<15; i++) explosiones.push({x: Math.random()*canvas.width, y: Math.random()*SUELO_Y, timer: 20 + Math.random()*20, color: '#ff4500'});
              secuaces = []; danarJefe(8); 
          }
      }

      if ((e.code === "ShiftLeft" || e.code === "ShiftRight" || e.code === "KeyC" || e.key === "c") && estadoJuego === 'JUGANDO') {
          if (jugador.dashCooldown <= 0 && jugador.dashTimer <= 0) {
              jugador.dashTimer = 12; jugador.dashCooldown = 60; jugador.invencible = 12; jugador.agachado = false; playSound('dash'); 
          }
      }
  });
  window.addEventListener('keyup', (e) => { teclas[e.code] = false; });
  
  canvas.addEventListener('mousedown', (e) => { 
      initAudio(); 
      canvas.focus();
      
      if (estadoJuego === 'INICIO' || estadoJuego === 'GAMEOVER' || estadoJuego === 'VICTORIA') {
          modoDificil = false; 
          iniciarNivel(1);
      } else if (estadoJuego === 'TIENDA') {
          const rect = canvas.getBoundingClientRect();
          const y = (e.clientY - rect.top) * (canvas.height / rect.height);
          
          if (y > 90 && y < 130) { jugador.maxVidas++; jugador.vidas = jugador.maxVidas; pasarSiguienteNivel(); }
          else if (y > 130 && y < 170) { jugador.velocidad += 1.5; pasarSiguienteNivel(); }
          else if (y > 170 && y < 220) { jugador.maxBalas += 2; pasarSiguienteNivel(); }
      }
  });
  
  document.addEventListener('fullscreenchange', () => { canvas.focus(); });
  canvas.focus();

  function iniciarNivel(n) {
      nivel = n;
      jugador.x = 50; jugador.y = SUELO_Y; jugador.velY = 0; jugador.dir = 1; jugador.dashTimer = 0; jugador.dashCooldown = 0;
      jugador.granadas = 1;
      
      if(n === 1) {
          jugador.maxVidas = modoDificil ? 3 : 5; jugador.vidas = jugador.maxVidas;
          jugador.velocidad = 4; jugador.maxBalas = 4;
          puntuacion = 0; siguienteCaja = 100; jugador.armaTimer = 0; jugador.arma = 'normal';
          combo = 1; impactosRecibidos = 0;
          arrancarMusica();
      }
      
      balas = []; balasEnemigas = []; explosiones = []; cajas = []; casquillos = []; humo = []; secuaces = [];
      jefe.timer = 0; jefe.escudo = false; jefe.visible = true; shakeTimer = 0;
      
      let mult = modoDificil ? 1.5 : 1; 
      if (nivel === 1) { jefe.tipo='tanque'; jefe.maxHp=Math.floor(20*mult); jefe.x=450; jefe.y=SUELO_Y; jefe.ancho=80; jefe.alto=60; }
      if (nivel === 2) { jefe.tipo='helicoptero'; jefe.maxHp=Math.floor(25*mult); jefe.x=400; jefe.y=50; jefe.ancho=90; jefe.alto=50; }
      if (nivel === 3) { jefe.tipo='tanque'; jefe.maxHp=Math.floor(35*mult); jefe.x=450; jefe.y=SUELO_Y; jefe.ancho=80; jefe.alto=60; jefe.escudo=true;}
      if (nivel === 4) { jefe.tipo='helicoptero'; jefe.maxHp=Math.floor(40*mult); jefe.x=400; jefe.y=100; jefe.ancho=90; jefe.alto=50; jefe.visible=false;}
      if (nivel === 5) { jefe.tipo='coloso'; jefe.maxHp=Math.floor(70*mult); jefe.x=450; jefe.y=SUELO_Y-40; jefe.ancho=100; jefe.alto=100; }
      
      jefe.hp = jefe.maxHp; estadoJuego = 'TRANSICION'; transicionTimer = 150;
      
      if (n === 1 && !animando) { animando = true; requestAnimationFrame(bucle); } 
  }

  function recibirDano() {
      if (jugador.invencible <= 0) {
          jugador.vidas--; puntuacion = Math.max(0, puntuacion - 25); jugador.invencible = 60; combo = 1; impactosRecibidos++;
          hacerTemblar(15, 12); playSound('explosion'); 
          explosiones.push({x: jugador.x, y: jugador.y, timer: 15, color: '#ff0000'});
          if (jugador.vidas <= 0) estadoJuego = 'GAMEOVER';
      }
  }

  function danarJefe(dmg) {
      if (!jefe.visible || estadoJuego !== 'JUGANDO') return;
      jefe.hp -= dmg; jefe.hitFlash = 3; 
      if (jefe.hp <= 0) {
          puntuacion += 50; chequearCaja(); playSound('explosion'); hacerTemblar(35, 15); 
          explosiones.push({ x: jefe.x, y: jefe.y, timer: 30, color: '#ff4500' });
          
          if (nivel < 5) {
              if (modoDificil) { pasarSiguienteNivel(); } 
              else { estadoJuego = 'TIENDA'; }
          } else { estadoJuego = 'VICTORIA'; }
      }
  }

  function pasarSiguienteNivel() {
      estadoJuego = 'TRANSICION'; transicionTimer = 100;
      if (!animando) { animando = true; requestAnimationFrame(bucle); }
      setTimeout(() => iniciarNivel(nivel + 1), 500);
  }

  function calcularRango() {
      if (impactosRecibidos === 0) return 'S (PERFECTO)';
      if (impactosRecibidos <= 2) return 'A (COLOSAL)';
      if (impactosRecibidos <= 5) return 'B (GUERRERO)';
      if (impactosRecibidos <= 8) return 'C (SOLDADO)';
      return 'D (RECLUTA)';
  }

  function chequearCaja() {
      if (!modoDificil && puntuacion >= siguienteCaja) {
          let r = Math.random(); let t = 'vida';
          if (r > 0.3) t = 'rafaga'; if (r > 0.6) t = 'escopeta'; if (r > 0.85) t = 'laser';
          cajas.push({ x: Math.random() * 300 + 100, y: -30, velY: 3, tipo: t }); siguienteCaja += 100;
      }
  }

  function dispararJefe(x, y, vx, vy, tipo) {
      if (tipo.startsWith('bomba')) {
          let esRosa = (Math.random() < 0.25 && (nivel === 2 || nivel === 5));
          balasEnemigas.push({ x: x, y: y, velX: vx, velY: -2, tipo: tipo, w: 12, h: 12, rebotes: 0, rosa: esRosa });
      } else {
          balasEnemigas.push({ x: x, y: y, velX: vx, velY: vy, tipo: tipo, w: 10, h: 10, rosa: false });
      }
  }

  function actualizarIAJefe() {
      jefe.timer++; 
      let enFase2 = (jefe.hp <= jefe.maxHp * 0.5);
      let velDisp = modoDificil ? 0.7 : 1; if (enFase2) velDisp *= 0.6; 
      if (jefe.hitFlash > 0) jefe.hitFlash--;

      if (enFase2 && jefe.visible && Math.random() < 0.3) {
          humo.push({ x: jefe.x + 20 + Math.random()*40, y: jefe.y + 10, velY: -2 - Math.random(), life: 30 });
      }

      if ((nivel === 3 || nivel === 5) && Math.random() < (modoDificil ? 0.015 : 0.005)) {
          let ladoDer = Math.random() < 0.5;
          secuaces.push({ x: ladoDer ? canvas.width + 20 : -30, y: SUELO_Y + 20, w: 20, h: 35, velX: ladoDer ? -2 : 2 });
      }

      if (nivel === 1) { 
          jefe.x += Math.sin(jefe.timer * 0.05) * 1.5; if (jefe.timer % Math.floor(80 * velDisp) === 0) dispararJefe(jefe.x, jefe.y + 25, -5, 0, 'obus');
      } else if (nivel === 2) { 
          let ciclo = Math.floor(250 * velDisp); let t = jefe.timer % ciclo;
          if (t < ciclo * 0.4) { jefe.y = 50; } else if (t < ciclo * 0.6) { jefe.y += 3; } 
          else if (t < ciclo * 0.8) {
              jefe.y = SUELO_Y - 20; if (t === Math.floor(ciclo * 0.7)) dispararJefe(jefe.x, jefe.y + 25, -6, 0, 'bomba_normal');
          } else { jefe.y -= 3; } 
      } else if (nivel === 3) { 
          jefe.x += Math.sin(jefe.timer * 0.03) * 1;
          if (jefe.timer % Math.floor(250 * velDisp) < 150 * velDisp) { jefe.escudo = true; } 
          else { jefe.escudo = false; if (jefe.timer % 20 === 0) dispararJefe(jefe.x, jefe.y + 25, -7, 0, 'obus'); }
      } else if (nivel === 4) { 
          let t = jefe.timer % Math.floor(150 * velDisp);
          if (t === 0) { jefe.x = Math.random() * 300 + 200; jefe.y = Math.random() * 100 + 40; jefe.visible = true; }
          if (t === Math.floor(60 * velDisp)) { dispararJefe(jefe.x + 20, jefe.y + 30, -3, 0, 'bomba_fantasma'); }
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

  function dibujarPausa() {
      ctx.fillStyle = "rgba(0, 0, 0, 0.6)"; ctx.fillRect(0,0,canvas.width, canvas.height);
      ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 40px 'Courier New'";
      ctx.fillText("P A U S A", canvas.width/2, canvas.height/2);
      ctx.font = "16px 'Courier New'"; ctx.fillText("Presiona P para continuar", canvas.width/2, canvas.height/2 + 30);
      ctx.textAlign = "left";
  }

  function dibujar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    if (shakeTimer > 0) { ctx.translate((Math.random()-0.5)*shakeMag, (Math.random()-0.5)*shakeMag); }

    let climaMalo = (nivel % 2 === 0); ctx.fillStyle = climaMalo ? "#2a3a4a" : "#4a5a6a"; ctx.fillRect(0, 0, canvas.width, canvas.height);
    if (climaMalo && Math.random() < 0.01) { ctx.fillStyle = "rgba(255,255,255,0.7)"; ctx.fillRect(0,0,canvas.width,canvas.height); }

    ctx.fillStyle = "#222"; ctx.fillRect(0, SUELO_Y + 50, canvas.width, canvas.height);
    ctx.fillStyle = "#111"; ctx.fillRect(0, SUELO_Y + 50, canvas.width, 10);

    if (climaMalo) {
        ctx.strokeStyle = "rgba(255,255,255,0.3)"; ctx.lineWidth = 1; ctx.beginPath();
        lluvia.forEach(l => { ctx.moveTo(l.x, l.y); ctx.lineTo(l.x - 2, l.y + 10); }); ctx.stroke();
    }

    ctx.fillStyle = "#d32f2f"; ctx.font = "20px Arial";
    let corazones = ""; for(let v=0; v<jugador.vidas; v++) corazones += "❤️"; ctx.fillText(corazones, 10, 20);

    ctx.fillStyle = "#fff"; ctx.font = "bold 15px 'Courier New'"; ctx.textAlign = "right";
    ctx.fillText("PUNTOS: " + puntuacion + " (x" + combo + ")", canvas.width - 10, 20); ctx.textAlign = "left";

    let uiY = 40;
    if (jugador.granadas > 0) { ctx.fillStyle = "#00ff00"; ctx.font = "bold 13px 'Courier New'"; ctx.fillText("💣 GRANADAS: " + jugador.granadas, 10, uiY); uiY+=18; }
    if (jugador.armaTimer > 0) {
        ctx.fillStyle = "#ffff00"; ctx.font = "bold 13px 'Courier New'"; 
        let nom = jugador.arma === 'escopeta' ? 'ESCOPETA' : (jugador.arma === 'laser' ? 'LÁSER' : 'RÁFAGA');
        ctx.fillText("⚡ " + nom, 10, uiY);
    } else if (jugador.dashCooldown <= 0) { ctx.fillStyle = "#00ffff"; ctx.font = "bold 13px 'Courier New'"; ctx.fillText("💨 DASH/PARRY LISTO", 10, uiY); }

    if (estadoJuego === 'JUGANDO') {
        ctx.fillStyle = "#333"; ctx.fillRect(150, 12, 300, 14);
        ctx.fillStyle = (jefe.hp <= jefe.maxHp*0.5) ? "#ff4500" : "#8b0000"; 
        ctx.fillRect(152, 14, 296 * (Math.max(0, jefe.hp) / jefe.maxHp), 10);
        ctx.fillStyle = "#fff"; ctx.font = "bold 12px 'Courier New'"; ctx.textAlign = "center";
        ctx.fillText(nombresJefes[nivel] + ((jefe.hp <= jefe.maxHp*0.5)?" [FASE 2]":""), canvas.width/2, 23); ctx.textAlign = "left";
    }

    humo.forEach(h => { ctx.fillStyle = `rgba(40,40,40,${h.life/30})`; ctx.beginPath(); ctx.arc(h.x, h.y, 8, 0, Math.PI*2); ctx.fill(); });
    ctx.fillStyle = '#ffd700'; casquillos.forEach(c => ctx.fillRect(c.x, c.y, 4, 2));
    cajas.forEach(c => { ctx.font = "24px Arial"; ctx.fillText("🎁", c.x, c.y); });
    secuaces.forEach(s => { ctx.fillStyle = '#8b0000'; ctx.fillRect(s.x, s.y, s.w, s.h); ctx.fillStyle = '#ffcc99'; ctx.fillRect(s.x+4, s.y+4, 12, 10); });

    if ((estadoJuego === 'JUGANDO' || estadoJuego === 'TRANSICION') && jefe.visible) {
        if (jefe.hitFlash > 0) { ctx.globalCompositeOperation = "source-atop"; ctx.filter = "brightness(200%) grayscale(100%)"; }
        if (jefe.tipo === 'tanque') {
            dibujarEntidad(imgTanque, jefe.x, jefe.y, jefe.ancho, jefe.alto, false);
            if (jefe.escudo) { ctx.strokeStyle = "#00ffff"; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(jefe.x, jefe.y + 30, 40, Math.PI*0.5, Math.PI*1.5); ctx.stroke(); }
        } else if (jefe.tipo === 'helicoptero') { dibujarEntidad(imgHeli, jefe.x, jefe.y, jefe.ancho, jefe.alto, false);
        } else if (jefe.tipo === 'coloso') { dibujarEntidad(imgHeli, jefe.x + 10, jefe.y - 10, 80, 50, false); dibujarEntidad(imgTanque, jefe.x, jefe.y + 30, 100, 70, false); }
        ctx.filter = "none"; ctx.globalCompositeOperation = "source-over"; 
    }

    balas.forEach(b => { ctx.fillStyle = b.tipo==='laser' ? '#00ffff' : (b.tipo==='parry_return'?'#ff00ff':'#ffaa00'); ctx.fillRect(b.x, b.y, b.w, b.h); });
    balasEnemigas.forEach(be => {
        ctx.fillStyle = be.rosa ? '#ff00ff' : (be.tipo === 'obus' ? '#ff0000' : '#111'); 
        ctx.beginPath(); ctx.arc(be.x, be.y, be.rosa ? 7 : 6, 0, Math.PI*2); ctx.fill();
    });

    explosiones.forEach(exp => { ctx.fillStyle = exp.color || '#ff4500'; ctx.beginPath(); ctx.arc(exp.x + 20, exp.y + 20, 30, 0, Math.PI*2); ctx.fill(); });

    if (estadoJuego !== 'GAMEOVER') {
        let invertido = jugador.dir === -1;
        if (jugador.dashTimer > 0) {
            ctx.globalAlpha = 0.4; let offset = 20 * jugador.dir;
            dibujarEntidad(imgSoldado, jugador.x - offset, jugador.y, jugador.ancho, jugador.alto, invertido); ctx.globalAlpha = 1.0;
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
        ctx.fillStyle = "rgba(0, 0, 0, 0.85)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 20px 'Courier New'"; ctx.fillText("CLIC AQUÍ PARA JUGAR", canvas.width/2, canvas.height/2);
    } else if (estadoJuego === 'TRANSICION') {
        ctx.fillStyle = "rgba(0, 0, 0, 0.75)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 28px 'Courier New'"; ctx.fillText(nombresJefes[nivel], canvas.width/2, canvas.height/2);
    } else if (estadoJuego === 'GAMEOVER') {
        ctx.fillStyle = "rgba(100, 0, 0, 0.85)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "bold 32px 'Courier New'"; ctx.fillText("HAS CAÍDO", canvas.width/2, canvas.height/2 - 25);
        ctx.font = "bold 16px 'Courier New'"; ctx.fillText("PUNTUACIÓN FINAL: " + puntuacion, canvas.width/2, canvas.height/2 + 10); ctx.fillText("Haz clic o presiona ESPACIO para reintentar", canvas.width/2, canvas.height/2 + 40);
    } else if (estadoJuego === 'VICTORIA') {
        ctx.fillStyle = "rgba(0, 40, 0, 0.95)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#ffd700"; ctx.textAlign = "center"; ctx.font = "bold 32px 'Courier New'"; ctx.fillText("¡MISIÓN CUMPLIDA!", canvas.width/2, canvas.height/2 - 50);
        ctx.fillStyle = "#fff"; ctx.font = "bold 18px 'Courier New'"; ctx.fillText("PUNTUACIÓN TOTAL: " + puntuacion, canvas.width/2, canvas.height/2 - 10);
        ctx.fillStyle = "#00ffff"; ctx.fillText("RANGO OBTENIDO: " + calcularRango(), canvas.width/2, canvas.height/2 + 15);
        ctx.fillStyle = "#fff"; ctx.font = "bold 13px 'Courier New'"; ctx.fillText("[ESPACIO/CLIC] Jugar Normal  |  [H] MODO DIFÍCIL (Sin cajas)", canvas.width/2, canvas.height/2 + 55);
    } else if (estadoJuego === 'TIENDA') {
        ctx.fillStyle = "rgba(20, 30, 40, 0.95)"; ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#ffff00"; ctx.textAlign = "center"; ctx.font = "bold 22px 'Courier New'"; ctx.fillText("¡JEFE DERROTADO! ELIGE TU RECOMPENSA:", canvas.width/2, 50);
        ctx.fillStyle = "#fff"; ctx.font = "bold 14px 'Courier New'";
        
        ctx.fillStyle = "rgba(255,255,255,0.1)"; ctx.fillRect(50, 90, 500, 40);
        ctx.fillStyle = "rgba(255,255,255,0.1)"; ctx.fillRect(50, 135, 500, 40);
        ctx.fillStyle = "rgba(255,255,255,0.1)"; ctx.fillRect(50, 180, 500, 40);
        
        ctx.fillStyle = "#fff";
        ctx.fillText("[1] BLINDAJE PESADO (+1 Vida Máxima y Cura)", canvas.width/2, 115);
        ctx.fillText("[2] BOTAS LIGERAS (+Velocidad de Movimiento)", canvas.width/2, 160);
        ctx.fillText("[3] CARGADOR AMPLIADO (+2 Balas en pantalla)", canvas.width/2, 205);
    }
  }

  function bucle() {
    if (estadoJuego === 'PAUSA' || estadoJuego === 'TIENDA') { animando = false; return; } 
    if (estadoJuego === 'TRANSICION') { transicionTimer--; if (transicionTimer <= 0) estadoJuego = 'JUGANDO'; dibujar(); requestAnimationFrame(bucle); return; }
    if (estadoJuego !== 'JUGANDO') { animando = false; return; }
    
    animando = true; // El motor está girando seguro

    if (jugador.invencible > 0) jugador.invencible--;
    if (cooldownDisparo > 0) cooldownDisparo--;
    if (jugador.armaTimer > 0) { jugador.armaTimer--; if (jugador.armaTimer<=0) jugador.arma = 'normal'; }
    if (jugador.dashCooldown > 0) jugador.dashCooldown--;
    if (shakeTimer > 0) shakeTimer--; 

    if (nivel % 2 === 0) { lluvia.forEach(l => { l.y += l.velY; l.x -= 2; if(l.y>canvas.height) {l.y=-10; l.x=Math.random()*canvas.width+50;} }); }
    for(let i=casquillos.length-1; i>=0; i--) {
        let c = casquillos[i]; c.velY += 0.5; c.x += c.velX; c.y += c.velY; if(c.y > SUELO_Y+40) { c.y = SUELO_Y+40; c.velY = -c.velY*0.5; }
        if(c.x < 0 || c.x > canvas.width || Math.abs(c.velY) < 0.1) casquillos.splice(i,1);
    }
    for(let i=humo.length-1; i>=0; i--) { humo[i].y += humo[i].velY; humo[i].life--; if(humo[i].life<=0) humo.splice(i,1); }

    // Movimiento
    if (jugador.dashTimer > 0) {
        jugador.dashTimer--; jugador.x += 12 * jugador.dir; 
    } else {
        jugador.agachado = (teclas['ArrowDown'] || teclas['KeyS']) && jugador.y === SUELO_Y;
        if (!jugador.agachado) {
            if (teclas['ArrowRight'] || teclas['KeyD']) { jugador.x += jugador.velocidad; jugador.dir = 1; }
            if (teclas['ArrowLeft'] || teclas['KeyA']) { jugador.x -= jugador.velocidad; jugador.dir = -1; }
        }
    }
    if (jugador.x < 0) jugador.x = 0; if (jugador.x > canvas.width - jugador.ancho) jugador.x = canvas.width - jugador.ancho;

    if (!jugador.agachado || jugador.y < SUELO_Y) { jugador.velY += 1.0; jugador.y += jugador.velY; } else { jugador.velY += 2.0; jugador.y += jugador.velY; }
    if (jugador.y > SUELO_Y) { jugador.y = SUELO_Y; jugador.velY = 0; }

    actualizarIAJefe();

    let jH = { x: jefe.x, y: jefe.y, w: jefe.ancho, h: jefe.alto };
    let dH = { x: jugador.x + 10, y: jugador.y + 5, w: jugador.ancho - 20, h: jugador.alto - 10 };
    if (jugador.agachado && jugador.y === SUELO_Y) { dH.y = jugador.y + 35; dH.h = jugador.alto - 35; }

    // Secuaces
    for (let i = secuaces.length - 1; i >= 0; i--) {
        let s = secuaces[i]; s.x += s.velX;
        if (s.x < dH.x + dH.w && s.x + s.w > dH.x && s.y < dH.y + dH.h && s.h + s.y > dH.y) {
            recibirDano(); secuaces.splice(i, 1); continue;
        }
        if (s.x < -50 || s.x > canvas.width + 50) secuaces.splice(i, 1);
    }

    // Cajas
    for (let i = cajas.length - 1; i >= 0; i--) {
        let c = cajas[i]; if (c.y < SUELO_Y + 20) c.y += c.velY; 
        if (dH.x < c.x + 24 && dH.x + dH.w > c.x && dH.y < c.y + 24 && dH.h + dH.y > c.y) {
            if (c.tipo === 'vida') { jugador.vidas = Math.min(jugador.maxVidas, jugador.vidas + 1); } 
            else { jugador.armaTimer = 400; jugador.arma = c.tipo; } 
            playSound('caja'); explosiones.push({ x: c.x, y: c.y, timer: 10, color: '#00ff00' }); cajas.splice(i, 1);
        }
    }

    // Balas Jugador
    for (let i = balas.length - 1; i >= 0; i--) {
        let b = balas[i]; b.x += (b.tipo==='laser'? 25 : 14) * b.dir; b.y += b.velY; let hit = false;

        for (let j = secuaces.length - 1; j >= 0; j--) {
            let s = secuaces[j];
            if (b.x < s.x + s.w && b.x + b.w > s.x && b.y < s.y + s.h && b.h + b.y > s.y) {
                explosiones.push({x: s.x, y: s.y, timer: 5, color: '#ff4500'}); 
                combo = Math.min(4, combo + 1); // CAP DE COMBO (MÁXIMO X4)
                puntuacion += 5 * combo;
                secuaces.splice(j, 1); hit = true; break;
            }
        }
        
        if (!hit && jefe.visible && b.x < jH.x + jH.w && b.x + b.w > jH.x && b.y < jH.y + jH.h && b.h + b.y > jH.y) {
            let haceDano = true; if (nivel === 2 && jefe.y < 100) haceDano = false; if (nivel === 3 && jefe.escudo && b.x < jefe.x) haceDano = false; 
            if (haceDano) {
                let daño = b.tipo === 'parry_return' ? 5 : b.dmg; 
                combo = Math.min(4, combo + 1); // CAP DE COMBO AL ACERTAR AL JEFE (MÁXIMO X4)
                puntuacion += 10 * combo; chequearCaja(); danarJefe(daño);
            } else { combo = 1; explosiones.push({ x: b.x, y: b.y - 10, timer: 5, color: '#aaaaaa' }); }
            hit = true;
        }

        if (hit) { balas.splice(i, 1); continue; }
        if (b.x < -20 || b.x > canvas.width + 20) { combo = 1; puntuacion = Math.max(0, puntuacion - 1); balas.splice(i, 1); }
    }

    // Balas Enemigas
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
        
        if (be.x < dH.x + dH.w && be.x + be.w > dH.x && be.y < dH.y + dH.h && be.h + be.y > dH.y) {
            if (jugador.dashTimer > 0 && be.rosa) {
                playSound('parry'); hacerTemblar(10, 8);
                explosiones.push({ x: be.x, y: be.y, timer: 10, color: '#00ffff' });
                balas.push({ x: jugador.x + 30, y: jugador.y + 10, w: 25, h: 8, dir: 1, velY: -1, tipo: 'parry_return', dmg: 5 });
                balasEnemigas.splice(i, 1); continue;
            }
            recibirDano(); balasEnemigas.splice(i, 1); continue;
        }
        if (be.x < -20 || be.x > canvas.width + 20 || be.y > canvas.height + 50) balasEnemigas.splice(i, 1);
    }

    for (let i = explosiones.length - 1; i >= 0; i--) { explosiones[i].timer--; if (explosiones[i].timer <= 0)  explosiones.splice(i, 1); }

    dibujar();
    requestAnimationFrame(bucle); 
  }

  dibujar();
</script>
</body>
</html>
"""

codigo_juego = codigo_juego.replace("INYECTAR_SOLDADO", codigo_soldado)
codigo_juego = codigo_juego.replace("INYECTAR_TANQUE", codigo_tanque)
codigo_juego = codigo_juego.replace("INYECTAR_HELI", codigo_heli)

components.html(codigo_juego, height=360)
