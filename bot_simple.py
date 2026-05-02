import asyncio
import os
import random
import json
import time
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIGURACIÓN TELEGRAM ---
TOKEN = "8729822305:AAGdrnB6ayAADhPWUOR-WOayfMeaySbfLrY"
CANAL_UNICO = "-1003833165052"  # ⬅️ PON AQUÍ EL ID DE TU CANAL ÚNICO

bot = Bot(token=TOKEN)
ARCHIVO_DATOS = "estadisticas_permanentes.json"

# --- SISTEMA DE PERSISTENCIA (MEMORIA) ---
def cargar_historial():
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"wins": 0, "losses": 0, "pasos": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0}}

def guardar_historial(datos):
    with open(ARCHIVO_DATOS, 'w') as f:
        json.dump(datos, f, indent=4)

stats_global = cargar_historial()

# --- GENERADOR DE REPORTE ESTILO PREMIUM ---
def generar_reporte_stats():
    datos = cargar_historial()
    total = datos["wins"] + datos["losses"]
    
    if total == 0: 
        return "📊 **Sin datos registrados aún.**"
    
    reporte = "⚜️ **REPORTE DE RENDIMIENTO** ⚜️\n"
    reporte += f"⏳ **Total de Señales:** `{total}`\n\n"
    reporte += "📊 **Distribución de Aciertos:**\n"
    
    colores = ["🟢", "🟡", "🟠", "🔵", "🟣", "🔴"]
    iconos_arbol = ["├", "├", "├", "├", "├", "└"]
    
    for i in range(1, 7):
        paso_str = str(i)
        wins_paso = datos["pasos"].get(paso_str, 0)
        porcentaje_intento = (wins_paso / total) * 100 if total > 0 else 0
        emoji = colores[i-1]
        rama = iconos_arbol[i-1]
        reporte += f"{rama} {emoji} Paso {i}: `{wins_paso}` ➔ ({porcentaje_intento:.1f}%)\n"

    reporte += "\n📈 **Resumen General:**\n"
    reporte += f"🏆 **Victorias:** `{datos['wins']}`\n"
    reporte += f"❌ **Fallos:** `{datos['losses']}`\n\n"
    
    efectividad = (datos["wins"] / total) * 100 if total > 0 else 0
    bloques_llenos = int(efectividad / 10)
    barra = ("🟩" * bloques_llenos) + ("⬜️" * (10 - bloques_llenos))
    
    reporte += f"🎯 **Efectividad:** `{efectividad:.2f}%`\n"
    reporte += f"{barra}"
    
    return reporte

# --- BUCLE PRINCIPAL DE COMANDOS ---
async def main():
    print(f"🚀 BOT SIMPLE ACTIVO (Modo Todo en Uno / Canal Único)")
    global stats_global
    
    offset = 0
    while True:
        try:
            updates = await bot.get_updates(offset=offset, timeout=10)
            for update in updates:
                offset = update.update_id + 1
                
                # --- 1. DETECCIÓN DE BOTONES TOCADOS ---
                if update.callback_query:
                    query = update.callback_query
                    data = query.data
                    
                    try:
                        await query.answer() 
                    except:
                        pass

                    if data.startswith("win_"):
                        paso = int(data.split("_")[1])
                        stats_global["wins"] += 1
                        stats_global["pasos"][str(paso)] += 1
                        guardar_historial(stats_global)
                        
                        colores = ["🟢", "🟡", "🟠", "🔵", "🟣", "🔴"]
                        emoji_paso = colores[paso - 1]
                        total_sesion = stats_global['wins'] + stats_global['losses']
                        efectividad_actual = (stats_global['wins'] / total_sesion) * 100 if total_sesion > 0 else 0
                        
                        msg_win = (
                            f"✅ **SEÑAL GANADA** ✅\n\n"
                            f"🎯 **Ganancia en:** Paso {paso} {emoji_paso}\n"
                            f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                            f"📊 **Marcador:** {stats_global['wins']} 🏆 - {stats_global['losses']} ❌\n"
                            f"📈 **Efectividad Actual:** `{efectividad_actual:.1f}%`\n"
                        )
                        
                        # Reemplaza el mensaje original de la señal por el reporte de victoria y quita los botones
                        await query.edit_message_text(text=msg_win, parse_mode="Markdown")

                    elif data == "loss":
                        stats_global["losses"] += 1
                        guardar_historial(stats_global)
                        
                        msg_loss = (
                            f"❌ **STOP LOSS ALCANZADO** ❌\n\n"
                            f"Lamentablemente la secuencia no se cumplió.\n"
                            f"⚠️ *Mantén la calma y respeta tu plan de trading.*\n"
                            f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                            f"📊 **Marcador Actualizado:** {stats_global['wins']} 🏆 - {stats_global['losses']} ❌"
                        )
                            
                        # Reemplaza el mensaje original por el de pérdida y quita los botones
                        await query.edit_message_text(text=msg_loss, parse_mode="Markdown")

                # --- 2. DETECCIÓN DE COMANDOS DE TEXTO ---
                elif update.message and update.message.text:
                    texto = update.message.text.lower().strip()
                    chat_id = str(update.message.chat_id)
                    
                    # Permite comandos desde el chat privado o desde el canal (si lo agregas como mensaje)
                    if texto == "/stats":
                        await bot.send_message(chat_id=chat_id, text=generar_reporte_stats(), parse_mode="Markdown")
                    
                    elif texto == "/senal":
                        secuencia = [random.choice(["JUGADOR", "BANCA"]) for _ in range(6)]
                        iconos_numeros = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]
                        lineas_secuencia = []
                        for i, s in enumerate(secuencia):
                            color = "🔵 JUGADOR" if s == "JUGADOR" else "🔴 BANCA"
                            lineas_secuencia.append(f"{iconos_numeros[i]} {color}")
                        
                        visual = "\n".join(lineas_secuencia)
                        caption_start = (
                            f"⚡️ **NUEVA SEÑAL DETECTADA** ⚡️\n\n"
                            f"🔮 **Secuencia a seguir:**\n"
                            f"{visual}\n\n"
                        )
                        
                        # Creamos los botones
                        keyboard = [
                            [
                                InlineKeyboardButton("✅ Win 1", callback_data="win_1"),
                                InlineKeyboardButton("✅ Win 2", callback_data="win_2"),
                                InlineKeyboardButton("✅ Win 3", callback_data="win_3")
                            ],
                            [
                                InlineKeyboardButton("✅ Win 4", callback_data="win_4"),
                                InlineKeyboardButton("✅ Win 5", callback_data="win_5"),
                                InlineKeyboardButton("✅ Win 6", callback_data="win_6")
                            ],
                            [
                                InlineKeyboardButton("❌ Loss (Ciclo Roto)", callback_data="loss")
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        # Enviar la señal CON los botones directamente al canal
                        try: 
                            await bot.send_message(
                                chat_id=CANAL_UNICO, 
                                text=caption_start, 
                                parse_mode="Markdown",
                                reply_markup=reply_markup
                            )
                        except Exception as e:
                            await bot.send_message(chat_id=chat_id, text=f"⚠️ Error al enviar al canal. Revisa los permisos o el ID del canal. Error: {e}")

        except Exception as e:
            if "Timeout" not in str(e):
                print(f"Error: {e}")
                
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())

