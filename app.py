import streamlit as st
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(page_title="Juego del T-Rex", layout="centered")

st.title("🦖 Juego del Dinosaurio")
st.write("Haz clic dentro del recuadro del juego y usa la **barra espaciadora** para saltar.")

# Código en HTML + JavaScript para el motor del juego en el navegador
codigo_juego = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { display: flex; justify-content: center; margin: 0; background-color: #f0f2f6; }
  canvas { border: 2px solid #333; background-color: #ffffff; border-radius: 5px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
</style>
</head>
<body>
<canvas id="pantallaJuego" width="600" height="200" tabindex="1"></canvas>
<script>
  const canvas = document.getElementById("pantallaJuego");
  const ctx = canvas.getContext("2d");
  
  // Variables del juego
  let dinoY = 150;
  let velY = 0;
  let gravedad = 1.2;
  let enSalto = false;
  let cactusX = 600;
  let puntuacion = 0;
  let gameOver = false;

  // Escuchar la barra espaciadora
  canvas.addEventListener("keydown", function(e) {
      if(e.code === "Space") {
          e.preventDefault(); // Evita que la página baje
          if(!enSalto && !gameOver) {
              velY = -14;
              enSalto = true;
          }
      }
  });

  // Para que el canvas registre las teclas, debe estar enfocado
  canvas.focus();

  function actualizar() {
      if (gameOver) return;

      // Físicas del Dinosaurio
      velY += gravedad;
      dinoY += velY;
      if (dinoY >= 150) { // Suelo
          dinoY = 150;
          enSalto = false;
          velY = 0;
      }

      // Movimiento del Cactus
      cactusX -= 7 + (puntuacion * 0.1); // Aumenta la velocidad gradualmente
      if (cactusX < -20) {
          cactusX = 600;
          puntuacion++;
      }

      // Colisiones
      let dinoRect = {x: 50, y: dinoY, w: 30, h: 40};
      let cactusRect = {x: cactusX, y: 160, w: 20, h: 30};

      if (dinoRect.x < cactusRect.x + cactusRect.w &&
          dinoRect.x + dinoRect.w > cactusRect.x &&
          dinoRect.y < cactusRect.y + cactusRect.h &&
          dinoRect.h + dinoRect.y > cactusRect.y) {
          gameOver = true;
      }

      // --- DIBUJAR (Render) ---
      ctx.clearRect(0, 0, canvas.width, canvas.height); // Limpiar

      // Suelo
      ctx.beginPath();
      ctx.moveTo(0, 190);
      ctx.lineTo(600, 190);
      ctx.stroke();

      // Dinosaurio
      ctx.fillStyle = "#333333";
      ctx.fillRect(50, dinoY, 30, 40);

      // Cactus
      ctx.fillStyle = "green";
      ctx.fillRect(cactusX, 160, 20, 30);

      // Puntuación
      ctx.fillStyle = "black";
      ctx.font = "20px Arial";
      ctx.fillText("Puntuación: " + puntuacion, 10, 30);

      if (gameOver) {
          ctx.fillStyle = "red";
          ctx.font = "30px Arial";
          ctx.fillText("¡JUEGO TERMINADO!", 150, 100);
      } else {
          requestAnimationFrame(actualizar); // Bucle a 60 FPS
      }
  }

  // Iniciar el juego
  requestAnimationFrame(actualizar);
</script>
</body>
</html>
"""

# Renderizar el HTML en Streamlit
components.html(codigo_juego, height=250)

if st.button("Reiniciar Juego"):
    # Streamlit recargará la página al pulsar este botón, reiniciando el HTML
    st.rerun()
