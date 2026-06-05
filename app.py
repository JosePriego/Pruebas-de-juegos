import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Juego del T-Rex", layout="centered")

st.title("🦖 Juego del Dinosaurio")
st.write("Haz **clic** dentro del recuadro o usa la **barra espaciadora** para saltar.")

codigo_juego = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { display: flex; justify-content: center; margin: 0; background-color: #f0f2f6; overflow: hidden; user-select: none; }
  canvas { border: 2px solid #333; background-color: #ffffff; border-radius: 5px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); cursor: pointer; }
</style>
</head>
<body>
<canvas id="pantallaJuego" width="600" height="200" tabindex="1"></canvas>
<script>
  const canvas = document.getElementById("pantallaJuego");
  const ctx = canvas.getContext("2d");
  
  let dinoY = 150;
  let velY = 0;
  let gravedad = 1.2;
  let enSalto = false;
  let cactusX = 600;
  let puntuacion = 0;
  let gameOver = false;
  let juegoIniciado = false;

  // Función principal para saltar o iniciar el juego
  function accionSaltar() {
      // Si el juego no ha empezado, lo iniciamos
      if (!juegoIniciado) {
          juegoIniciado = true;
          gameOver = false;
          requestAnimationFrame(actualizar);
          return;
      }
      
      // Si hemos perdido, reiniciamos las variables
      if (gameOver) {
          dinoY = 150;
          velY = 0;
          cactusX = 600;
          puntuacion = 0;
          gameOver = false;
          enSalto = false;
          requestAnimationFrame(actualizar);
          return;
      }

      // Si estamos jugando y no estamos en el aire, saltamos
      if (!enSalto) {
          velY = -14;
          enSalto = true;
      }
  }

  // Controles: Teclado (Barra espaciadora)
  canvas.addEventListener("keydown", function(e) {
      if(e.code === "Space") {
          e.preventDefault();
          accionSaltar();
      }
  });

  // Controles: Ratón o Pantalla táctil (Clic)
  window.addEventListener("mousedown", accionSaltar);
  window.addEventListener("touchstart", function(e) {
      e.preventDefault(); // Evita hacer zoom en móviles
      accionSaltar();
  }, {passive: false});

  // Dibujar la pantalla de inicio
  function dibujarPantallaInicio() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Suelo
      ctx.beginPath();
      ctx.moveTo(0, 190);
      ctx.lineTo(600, 190);
      ctx.stroke();

      // Dinosaurio
      ctx.fillStyle = "#333333";
      ctx.fillRect(50, dinoY, 30, 40);

      // Mensaje
      ctx.fillStyle = "black";
      ctx.font = "24px Arial";
      ctx.textAlign = "center";
      ctx.fillText("Haz clic aquí para empezar", canvas.width / 2, 100);
  }

  // Bucle principal del juego
  function actualizar() {
      if (!juegoIniciado) return;

      velY += gravedad;
      dinoY += velY;
      if (dinoY >= 150) { 
          dinoY = 150;
          enSalto = false;
          velY = 0;
      }

      cactusX -= 7 + (puntuacion * 0.1); 
      if (cactusX < -20) {
          cactusX = 600;
          puntuacion++;
      }

      let dinoRect = {x: 50, y: dinoY, w: 30, h: 40};
      let cactusRect = {x: cactusX, y: 160, w: 20, h: 30};

      if (dinoRect.x < cactusRect.x + cactusRect.w &&
          dinoRect.x + dinoRect.w > cactusRect.x &&
          dinoRect.y < cactusRect.y + cactusRect.h &&
          dinoRect.h + dinoRect.y > cactusRect.y) {
          gameOver = true;
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      ctx.beginPath();
      ctx.moveTo(0, 190);
      ctx.lineTo(600, 190);
      ctx.stroke();

      ctx.fillStyle = "#333333";
      ctx.fillRect(50, dinoY, 30, 40);

      ctx.fillStyle = "green";
      ctx.fillRect(cactusX, 160, 20, 30);

      ctx.fillStyle = "black";
      ctx.font = "20px Arial";
      ctx.textAlign = "left";
      ctx.fillText("Puntuación: " + puntuacion, 10, 30);

      if (gameOver) {
          ctx.fillStyle = "red";
          ctx.font = "30px Arial";
          ctx.textAlign = "center";
          ctx.fillText("¡JUEGO TERMINADO!", canvas.width / 2, 90);
          
          ctx.fillStyle = "black";
          ctx.font = "16px Arial";
          ctx.fillText("Haz clic para intentar de nuevo", canvas.width / 2, 130);
      } else {
          requestAnimationFrame(actualizar);
      }
  }

  // Llamamos a la pantalla de inicio al cargar
  dibujarPantallaInicio();
</script>
</body>
</html>
"""

components.html(codigo_juego, height=250)
