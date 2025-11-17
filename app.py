from bybit_p2p import P2P
from dotenv import load_dotenv
import os
from flask import Flask, render_template_string
from collections import defaultdict

# ----------------- CONFIGURACIÓN Y CLIENTE BYBIT -----------------
load_dotenv()
api = P2P(
    testnet=False,
    api_key=os.getenv("BYBIT_API_KEY"),
    api_secret=os.getenv("BYBIT_API_SECRET")
)

app = Flask(__name__)
# -----------------------------------------------------------------


def obtener_datos_p2p():
    """Ejecuta la lógica de tu script y devuelve una cadena HTML con los resultados."""
    output_html = "<h1>📈 Reporte P2P Bybit (USDT/BOB)</h1>"
    estados = [1, 0]  # 1: Ventas (Buy Side), 0: Compras (Sell Side)

    for estado in estados:
        items = []
        # Solo se recorre hasta la página 2 (rango 1, 3) como en tu código original
        for page in range(1, 10): 
            try:
                response = api.get_online_ads(
                    tokenId="USDT",
                    currencyId="BOB",
                    side=estado,
                    page=str(page)
                )
                if response.get("result") and response["result"].get("items"):
                    items.extend(response["result"]["items"])
            except Exception as e:
                # Manejo básico de errores de la API
                output_html += f"<p style='color: red;'>Error al obtener datos: {e}</p>"
                break # Salir del bucle de páginas si falla

        agrupado = {}
        vol_total = 0.0
        for item in items:
            try:
                precio = float(item["price"])
                cantidad = float(item["lastQuantity"])
                vol_total += cantidad
                
                if precio not in agrupado:
                    agrupado[precio] = {"suma": 0.0, "conteo": 0}

                agrupado[precio]["suma"] += cantidad
                agrupado[precio]["conteo"] += 1
            except (ValueError, KeyError):
                 # Ignorar items con datos inválidos si los hay
                continue 

        # --- Visualización ---
        if estado == 0:
            titulo = "🔴 Compras (Ofertas de Venta)"
            color = "red"
            reverse_sort = True
        else:
            titulo = "🟢 Ventas (Ofertas de Compra)"
            color = "green"
            reverse_sort = False
        
        output_html += f"<h2>{titulo}</h2>"
        output_html += f"<p>Volumen total: <strong>{vol_total:.4f} USDT</strong></p>"
        output_html += "<table border='1' style='width: 100%; border-collapse: collapse;'>"
        output_html += f"<tr style='background-color: #f2f2f2; font-weight: bold;'><td>Precio ({color})</td><td>👤 Anuncios</td><td>💰 Volumen</td><td>Distribución</td></tr>"

        datos_ordenados = sorted(agrupado.items(), key=lambda x: x[0], reverse=reverse_sort)
        
        for precio, valores in datos_ordenados:
            modulo = int((valores['suma'] / vol_total) * 50) if vol_total > 0 else 0
            barra = "⬛" * modulo
            
            output_html += f"<tr>"
            output_html += f"<td style='color: {color};'>{precio:.2f}</td>"
            output_html += f"<td>{valores['conteo']}</td>"
            output_html += f"<td>{valores['suma']:.4f}</td>"
            output_html += f"<td>{barra}</td>"
            output_html += f"</tr>"

        output_html += "</table><hr>"
    
    return output_html

@app.route('/')
def index():
    """Ruta principal que llama a la función de obtención de datos."""
    html_content = obtener_datos_p2p()
    
    # Añade la línea de meta refresh dentro de <head>
    full_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Reporte P2P</title>
        <meta http-equiv="refresh" content="10">  <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #333; }}
            table {{ margin-top: 15px; }}
            td, th {{ padding: 6px; text-align: left; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    return render_template_string(full_html)

if __name__ == '__main__':
    # Ejecuta el servidor Flask
    # Debug=True reinicia el servidor automáticamente al guardar cambios
    app.run(debug=True)