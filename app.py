import streamlit as st
import streamlit.components.v1 as components

# Configuración de página
st.set_page_config(page_title="Pixel T-Rex Runner", layout="centered", page_icon="🦖")

# Estilo CSS para la página de Streamlit
st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    h1 { color: #535353; font-family: 'Courier New', Courier, monospace; text-align: center; }
    .stMarkdown p { text-align: center; color: #757575; font-family: 'Courier New', Courier, monospace;}
</style>
""", unsafe_allow_html=True)

st.title("🦖 PIXEL T-REX RUNNER")
st.write("Haz **clic** en el recuadro o pulsa **Espacio** para saltar.")

# --- EL MOTOR DEL JUEGO (HTML/JS) CON GRÁFICOS INCRUSTADOS ---
codigo_juego = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { display: flex; justify-content: center; margin: 0; background-color: #f7f7f7; overflow: hidden; user-select: none; font-family: 'Courier New', Courier, monospace; }
  canvas { border-bottom: 2px solid #535353; background-color: #ffffff; cursor: pointer; }
</style>
</head>
<body>
<canvas id="juego" width="600" height="200" tabindex="1"></canvas>
<script>
  const canvas = document.getElementById("juego");
  const ctx = canvas.getContext("2d");

  // --- GRÁFICOS (IMÁGENES ENCRIPTADAS EN BASE64) ---
  const imgDinoQuieto = new Image();
  imgDinoQuieto.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACQAAAAoAgMAAADeAnXQAAAACVBMVEUAAAAzMzP///86mZ7SAAAAAXRSTlMAQObYZgAAAFNJREFUGNNjYBgFhANMDIwMDEz/Gf4f4GBwYGB4//8fA8N/hv8HOAYwPPj/E8oCYf//A6kBGeCYD6SFZ4BjPpAWngGO+UBaeAY45gNpoRoYfAAAFZon82F4XzkAAAAASUVORK5CYII=";

  const imgDinoCorre1 = new Image();
  imgDinoCorre1.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACQAAAAoAgMAAADeAnXQAAAACVBMVEUAAAAzMzP///86mZ7SAAAAAXRSTlMAQObYZgAAAFhJREFUGNNjYBgFhANMDIwMDEz/Gf4f4GBwYGB4//8fA8N/hv8HOAYwPPj/E8oCYf//A6kBGeCYD6SFZ4BjPpAWngGO+UBaeAY45gNpoRoY5gNpYToYpQEAF8EnD5e0WlQAAAAASUVORK5CYII=";

  const imgDinoCorre2 = new Image();
  imgDinoCorre2.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACQAAAAoAgMAAADeAnXQAAAACVBMVEUAAAAzMzP///86mZ7SAAAAAXRSTlMAQObYZgAAAFhJREFUGNNjYBgFhANMDIwMDEz/Gf4f4GBwYGB4//8fA8N/hv8HOAYwPPj/E8oCYf//A6kBGeCYD6SFZ4BjPpAWngGO+UBaeAY45gNpoRoY5gNpYRoYmQEAG9UnD/1628UAAAAASUVORK5CYII=";

  const imgDinoChoca = new Image();
  imgDinoChoca.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACQAAAAoAgMAAADeAnXQAAAACVBMVEUAAAAzMzP///86mZ7SAAAAAXRSTlMAQObYZgAAAFBJREFUGNNjYBgFhANMDIwMDEz/Gf4f4GBwYGB4//8fA8N/hv8HOAYwPPj/E8oCYf//A6kBGeCYD6SFZ4BjPpAWngGO+UBaeAY45gNpoRoY5gMACVkoM8R4eK0AAAAASUVORK5CYII=";

  const imgCactus = new Image();
  imgCactus.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAoAgMAAAA96F9bAAAACVBMVEUAAAAzMzP///86mZ7SAAAAAXRSTlMAQObYZgAAADlJREFUGNNjYMAOGDAAByYGAZAEZidAOYLEmYDSGEpY5YgS5f8ZSmBKEMU4FUhVjCpxYpAnmBlIMwMAtH4Tf0Fj6UIAAAAASUVORK5CYII=";

  const imgNube = new Image();
  imgNube.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAANAgMAAADbM4PMAAAACVBMVEUAAADMzMz///959M45AAAAAXRSTlMAQObYZgAAAD5JREFUGNNjYBAEYSNDY4MHA8OChv+DDP8ZGP4zMvwPAGJDGf4bMfxnAGIsBf7/D0AGKDD8D2DYf2DAWAcBAF09E76Zp5T3AAAAA4RSTlMAQObYZgAAAFVJREFUGNNjYBgFhANMDIwMDFz/Gf4fYGB4z/D/AIMjA8v/fwYGA8OChv+DGBgFGB48fOigqKhoKKGoCKEGCR88hEgj9P///z8Gg/8M///DBMCEGB4AFvIat3N0B+MAAAAASUVORK5CYII=";

  // --- VARIABLES Y ESTADO ---
  let frame = 0;
  const SUELO_Y = 150;
  let dino = { x: 50, y: SUELO_Y, velY: 0, ancho: 36, alto: 40, frameAnim: 0 };
  let cactus = { x: 600, y: SUELO_Y + 5, ancho: 20, alto: 35 };
  let nubes = [ {x: 150, y: 50, vel: 0.5}, {x: 400, y: 30, vel: 0.3}, {x: 550, y: 70, vel: 0.4} ];
  let sueloOffset = 0;

  let gravedad = 1.3;
  let puntuacion = 0;
  let velocidadJuego = 6;
  let estado = 'INICIO'; // INICIO, JUGANDO, GAMEOVER

  // --- CONTROLES ---
  function saltar() {
    if (estado === 'INICIO') { estado = 'JUGANDO'; }
    else if (estado === 'GAMEOVER') { reiniciar(); }
    else if (estado === 'JUGANDO' && dino.y === SUELO_Y) {
      dino.velY = -15;
    }
  }
  canvas.addEventListener("keydown", (e) => { if(e.code === "Space") { e.preventDefault(); saltar(); }});
  canvas.addEventListener("mousedown", saltar);
  canvas.focus();

  function reiniciar() {
    dino.y = SUELO_Y; dino.velY = 0;
    cactus.x = 600;
    puntuacion = 0; velocidadJuego = 6;
    estado = 'JUGANDO';
  }

  // --- BUCLE PRINCIPAL ---
  function bucle() {
    frame++;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. Dibujar elementos estáticos de fondo
    dibujarSuelo();
    nubes.forEach(n => dibujarNube(n));

    if (estado === 'JUGANDO') {
        // Logica
        actualizarDino();
        actualizarCactus();
        actualizarEntorno();
        detectarColision();
        puntuacion += 0.1;
        velocidadJuego += 0.001;

        // Dibujar
        dibujarDinoCorre();
        dibujarCactus();
    } 
    else if (estado === 'INICIO') {
        dibujarDinoQuieto();
        dibujarTextoCentrado("HAZ CLIC PARA EMPEZAR", "20px", 100);
    }
    else if (estado === 'GAMEOVER') {
        dibujarDinoChoca();
        dibujarCactus();
        dibujarTextoCentrado("G A M E  O V E R", "30px", 90);
        dibujarTextoCentrado("Clic para reintentar", "16px", 120);
    }

    dibujarPuntuacion();
    requestAnimationFrame(bucle);
  }

  // --- FUNCIONES DE ACTUALIZACIÓN Y DIBUJO ---

  function actualizarDino() {
    dino.velY += gravedad;
    dino.y += dino.velY;
    if (dino.y > SUELO_Y) { dino.y = SUELO_Y; dino.velY = 0; }
    // Animación de correr
    if (frame % 8 === 0) { dino.frameAnim = (dino.frameAnim === 0) ? 1 : 0; }
  }

  function actualizarCactus() {
    cactus.x -= velocidadJuego;
    if (cactus.x < -cactus.ancho) {
        cactus.x = canvas.width + Math.random() * 200;
    }
  }

  function actualizarEntorno() {
    // Mover suelo
    sueloOffset -= velocidadJuego;
    if (sueloOffset <= -20) sueloOffset = 0;
    // Mover nubes
    nubes.forEach(n => {
        n.x -= n.vel;
        if (n.x < -40) n.x = canvas.width + 10;
    });
  }

  function detectarColision() {
    // Hitbox ajustada para ser justa
    let dH = { x: dino.x + 5, y: dino.y + 5, w: dino.ancho - 10, h: dino.alto - 5 };
    let cH = { x: cactus.x + 2, y: cactus.y + 2, w: cactus.ancho - 4, h: cactus.alto - 2 };

    if (dH.x < cH.x + cH.w && dH.x + dH.w > cH.x && dH.y < cH.y + cH.h && dH.h + dH.y > cH.y) {
        estado = 'GAMEOVER';
    }
  }

  // --- DIBUJANTES ---
  function dibujarDinoQuieto() { ctx.drawImage(imgDinoQuieto, dino.x, dino.y, dino.ancho, dino.alto); }
  function dibujarDinoChoca() { ctx.drawImage(imgDinoChoca, dino.x, dino.y, dino.ancho, dino.alto); }
  function dibujarDinoCorre() {
    // Si está en el aire, quieto. Si no, alterna patas.
    if (dino.y < SUELO_Y) { dibujarDinoQuieto(); }
    else {
        let img = (dino.frameAnim === 0) ? imgDinoCorre1 : imgDinoCorre2;
        ctx.drawImage(img, dino.x, dino.y, dino.ancho, dino.alto);
    }
  }
  function dibujarCactus() { ctx.drawImage(imgCactus, cactus.x, cactus.y, cactus.ancho, cactus.alto); }
  function dibujarNube(n) { ctx.drawImage(imgNube, n.x, n.y); }

  function dibujarSuelo() {
    ctx.strokeStyle = "#535353"; ctx.lineWidth = 2; ctx.beginPath();
    ctx.moveTo(0, SUELO_Y + dino.alto); ctx.lineTo(canvas.width, SUELO_Y + dino.alto); ctx.stroke();
    // Puntos de textura del suelo (efecto parallax simple)
    ctx.fillStyle = "#f0f0f0";
    for(let i=0; i<30; i++) {
        let px = (i*25 + sueloOffset) % canvas.width;
        if (px < 0) px += canvas.width;
        ctx.fillRect(px, SUELO_Y + dino.alto + 5, 2, 2);
    }
  }

  function dibujarPuntuacion() {
    ctx.fillStyle = "#535353"; ctx.font = "16px 'Courier New'"; ctx.textAlign = "right";
    let puntos = Math.floor(puntuacion).toString().padStart(5, '0');
    ctx.fillText(puntos, canvas.width - 10, 25);
  }

  function dibujarTextoCentrado(texto, tamaño, y) {
    ctx.fillStyle = "#535353"; ctx.font = `bold ${tamaño} 'Courier New'`;
    ctx.textAlign = "center"; ctx.fillText(texto, canvas.width/2, y);
  }

  // Iniciar
  bucle();
</script>
</body>
</html>
"""

# Renderizar
components.html(codigo_juego, height=220)

# Botón de reinicio de Streamlit como plan B
if st.button("🔄 Reiniciar App"):
    st.rerun()

st.markdown("---")
st.caption("Gráficos Pixel-Art por IA | Inspirado en el juego de Google Chrome.")
