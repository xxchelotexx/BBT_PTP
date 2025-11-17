from bybit_p2p import P2P
from dotenv import load_dotenv
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import os
from collections import defaultdict

load_dotenv()
api = P2P(
    testnet=False,
    api_key=os.getenv("BYBIT_API_KEY"),
    api_secret=os.getenv("BYBIT_API_SECRET")
)

estados = [1,0]
for estado in estados:

    items = []
    for page in range(1, 3):  # páginas 1 a 4 inclusive
        response = api.get_online_ads(
            tokenId="USDT",
            currencyId="BOB",
            side=estado,
            page=str(page)
        )
        if response.get("result") and response["result"].get("items"):
            items.extend(response["result"]["items"])
    #print (items)
    #print(f"Total registros: {len(items)}")

    agrupado = {}
    vol_total = 0.0
    for item in items:
        precio = float(item["price"])
        cantidad = float(item["lastQuantity"])
        vol_total+=cantidad
        if precio not in agrupado:
            agrupado[precio] = {"suma": 0.0, "conteo": 0}

        agrupado[precio]["suma"] += cantidad
        agrupado[precio]["conteo"] += 1


    # Mostrar resultados
    modulo = 0
    if estado == 0: 
        print (f"Volumen de 🔴 compras: {vol_total}")
        for precio, valores in sorted(agrupado.items(), reverse=True):
            print(f"🔴: {precio:.2f}  | 👤: {valores['conteo']} | 💰: {valores['suma']:.4f} ")
            modulo = int ((valores['suma'] / vol_total)*20)
            print ("⬜"*modulo)

    if estado == 1: 
        print (f"Volumen de 🟢 ventas: {vol_total}")
        for precio, valores in sorted(agrupado.items(), reverse=False):
            print(f"🟢: {precio:.2f}  | 👤: {valores['conteo']} | 💰: {valores['suma']:.4f} ")
            modulo = int ((valores['suma'] / vol_total)*20)
            print ("⬜"*modulo)

