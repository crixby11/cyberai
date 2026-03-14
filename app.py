from flask import Flask, json, request, render_template, jsonify
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = Groq(api_key="GROQ_API_KEY")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RESPUESTAS FIJAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
respuestas_fijas = {
    "hola": "👾 Acceso concedido. Soy TopoIA, tu asistente de ciberseguridad. ¿En qué puedo ayudarte?",
    "quien eres": "Soy TopoIA, un asistente especializado en ciberseguridad creado para ayudarte con hacking ético, análisis de vulnerabilidades, CTF y más.",
    "que puedes hacer": "Puedo ayudarte con:\n\n• 🔍 Seguridad de redes\n• 🦠 Análisis de malware\n• 🔐 Criptografía\n• 🎯 Pentesting\n• 🚩 CTF challenges\n• 🌐 Vulnerabilidades web",
    "adios": "🔒 Sesión cerrada. Hasta pronto, hacker.",
    "gracias": "De nada. Recuerda: la seguridad es responsabilidad de todos. 🛡️",
    "quien es tu creador": "🧑‍💻 Fui creado por un grupo de ingenieros de la clase de Seguridad Computacional del Doctor Raudales.",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AGENTES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def llamar_agente(system_prompt, user_message, max_tokens=600):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        max_tokens=max_tokens,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


def agente_1_entrevistador(user_input, historial=None):
    if historial is None:
        historial = []

    keywords = [
        "hack", "ataque", "vulnerabilidad", "acceso", "contraseña",
        "malware", "virus", "ip", "red", "base de datos", "servidor",
        "phishing", "ransomware", "firewall", "cifrado", "brecha",
        "incidente", "seguridad", "exploit", "sql", "xss", "ddos",
        "empleado", "logs", "descarga", "robo", "fuga", "datos",
        "cuenta", "sistema", "intruso", "puerto", "protocolo", "clave",
        "ciberseguridad", "amenaza", "riesgo", "backup", "autenticacion",
        "permiso", "credencial", "certificado", "vpn", "proxy", "token",
        "si", "sí", "ok", "claro", "adelante", "continua", "procede"
    ]

    # Si hay historial y el mensaje es corto → continuar conversación
    if historial and len(user_input.split()) <= 5:
        return "PROCEDER"

    # Si tiene 8+ palabras o contiene keyword → PROCEDER
    if len(user_input.split()) >= 8 or any(k in user_input.lower() for k in keywords):
        return "PROCEDER"

    return "🔍 Para ayudarte mejor, ¿puedes decirme qué sistema fue afectado y qué síntoma observaste exactamente?"


def agente_2_analista(user_input, historial=None):
    if historial is None:
        historial = []

    contexto_previo = ""
    if historial:
        contexto_previo = "\nCONTEXTO PREVIO DE LA CONVERSACIÓN:\n"
        for msg in historial[-4:]:
            rol = "Usuario" if msg["role"] == "user" else "TopoIA"
            contexto_previo += f"{rol}: {msg['content'][:150]}\n"

    prompt = """Eres el Agente 2: El Analista de Riesgos (basado en ISO 27005).
Tu trabajo es interno — calcular el riesgo y pasarlo al equipo.

Analiza el problema y devuelve SOLO un JSON con este formato exacto, sin texto adicional:
{
  "amenaza": "descripción breve",
  "vulnerabilidad": "descripción breve",
  "activo": "qué está en riesgo",
  "probabilidad": 4,
  "impacto": 5,
  "nivel_riesgo": 20,
  "cia_afectado": "Confidencialidad, Integridad",
  "nivel_texto": "MUY ALTO"
}

Probabilidad e Impacto del 1 al 5. Nivel de riesgo = probabilidad x impacto.
No incluyas texto antes ni después del JSON."""
    return llamar_agente(prompt, f"{contexto_previo}\nProblema actual: {user_input}", max_tokens=300)


def agente_3_contexto(user_input, analisis_riesgo, historial=None):
    if historial is None:
        historial = []

    contexto_previo = ""
    if historial:
        contexto_previo = "\nCONTEXTO PREVIO:\n"
        for msg in historial[-4:]:
            rol = "Usuario" if msg["role"] == "user" else "TopoIA"
            contexto_previo += f"{rol}: {msg['content'][:150]}\n"

    prompt = """Eres el Agente 3: Especialista en Inteligencia Contextual y Cumplimiento.
Sitúas el riesgo en el contexto real de Honduras y lo mapeas a estándares globales.

Considera:
- Contexto local: ENEE, CNBS, DPI Honduras, Código Penal de Honduras
- Estándares: ISO 27001/27002/27005, CIS Controls, NIST, GDPR, COBIT

Devuelve un análisis con:
1. La Realidad Local (Honduras)
2. Respaldo Normativo (cita cada control con su fuente)

Sé conciso. Responde en español."""
    return llamar_agente(
        prompt,
        f"{contexto_previo}\nProblema: {user_input}\n\nAnálisis de riesgo: {analisis_riesgo}",
        max_tokens=500
    )


def agente_4_arquitecto(user_input, analisis_riesgo, historial=None):
    if historial is None:
        historial = []

    contexto_previo = ""
    if historial:
        contexto_previo = "\nCONTEXTO PREVIO:\n"
        for msg in historial[-4:]:
            rol = "Usuario" if msg["role"] == "user" else "TopoIA"
            contexto_previo += f"{rol}: {msg['content'][:150]}\n"

    prompt = """Eres el Agente 4: El Arquitecto de Soluciones del Blue Team.
Diseña una defensa en profundidad con tres capas:

1. 🔧 Técnica: controles tecnológicos concretos
2. 📋 Administrativa: políticas y procedimientos
3. 🎓 Educativa: capacitación y concientización

Sé específico y accionable. Responde en español."""
    return llamar_agente(
        prompt,
        f"{contexto_previo}\nProblema: {user_input}\n\nRiesgo calculado: {analisis_riesgo}",
        max_tokens=500
    )


def agente_5_continuidad(user_input, analisis_riesgo, historial=None):
    if historial is None:
        historial = []

    contexto_previo = ""
    if historial:
        contexto_previo = "\nCONTEXTO PREVIO:\n"
        for msg in historial[-4:]:
            rol = "Usuario" if msg["role"] == "user" else "TopoIA"
            contexto_previo += f"{rol}: {msg['content'][:150]}\n"

    prompt = """Eres el Agente 5: Especialista en Continuidad del Negocio (El Bombero).

Si el incidente YA ocurrió: diseña un Plan de Contingencia (DRP) inmediato.
Si es una amenaza futura: diseña un Plan de Continuidad (BCP).

Incluye pasos concretos para mantener operaciones. Responde en español."""
    return llamar_agente(
        prompt,
        f"{contexto_previo}\nProblema: {user_input}\n\nRiesgo: {analisis_riesgo}",
        max_tokens=400
    )


def agente_6_comunicador(user_input, riesgo_json, contexto, arquitectura, continuidad, historial=None):
    if historial is None:
        historial = []

    contexto_previo = ""
    if historial:
        contexto_previo = "\n\nCONVERSACIÓN PREVIA (para dar continuidad, no repetir lo ya explicado):\n"
        for msg in historial[-6:]:
            rol = "Usuario" if msg["role"] == "user" else "TopoIA"
            contexto_previo += f"{rol}: {msg['content'][:200]}\n"

    prompt = """Eres el Agente 6: El Comunicador Ejecutivo del Blue Team.
Recibes los análisis de todos los agentes y produces el reporte final para el usuario.
Si hay conversación previa, úsala para dar continuidad y no repetir lo ya explicado.

REGLAS:
- Cero jerga técnica sin explicación
- Usa Markdown: negritas, listas, emojis
- Lenguaje claro, directo y empático

Estructura OBLIGATORIA — respeta exactamente estos encabezados:

## 🔍 1. Resumen de la Situación
[Párrafo claro explicando qué pasó y por qué importa]

## 🚨 2. Matriz de Alerta
| Riesgo | Probabilidad | Impacto | 🔥 Nivel |
|--------|-------------|---------|---------|
| [dato] | [dato]      | [dato]  | [dato]  |

**Triada CIA afectada:** [dato]

## 🌍 3. Contexto Local e Internacional
[Realidad Honduras + Normativa citada]

## ✅ 4. Hoja de Ruta Inmediata
- 🔧 **Técnico:** [acción concreta]
- 📋 **Administrativo:** [acción concreta]
- 🎓 **Educativo:** [consejo clave]
- ⚖️ **Legal (si aplica):** [qué hacer con la DPI]

## 🛡️ 5. Consejo Zero Trust
[Consejo final asumiendo entorno hostil]

Responde en español."""

    contexto_completo = f"""
Problema original: {user_input}
{contexto_previo}
Análisis de riesgo (Agente 2): {riesgo_json}
Contexto y normativa (Agente 3): {contexto}
Arquitectura de defensa (Agente 4): {arquitectura}
Plan de continuidad (Agente 5): {continuidad}
"""
    return llamar_agente(prompt, contexto_completo, max_tokens=1200)


def generar_sugerencias(user_input, reporte):
    prompt = """Eres un asistente de ciberseguridad.
Genera EXACTAMENTE 3 preguntas de seguimiento cortas y relevantes.

Devuelve SOLO un JSON array, sin texto adicional, sin backticks:
["pregunta 1", "pregunta 2", "pregunta 3"]

Las preguntas deben ser en español, máximo 10 palabras cada una."""
    try:
        resultado = llamar_agente(
            prompt,
            f"Consulta: {user_input}\n\nReporte: {reporte[:500]}",
            max_tokens=150
        )
        resultado = resultado.replace("```json", "").replace("```", "").strip()
        return json.loads(resultado)
    except:
        return ["¿Cómo implementar 2FA?", "¿Qué dice el OWASP Top 10?", "¿Cómo reportar a la DPI?"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUTAS FLASK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generar", methods=["POST"])
def generar():
    data       = request.get_json()
    user_input = data.get("prompt", "").strip()
    historial  = data.get("historial", [])

    if not user_input:
        return jsonify({"error": "El prompt está vacío."}), 400

    input_lower = user_input.lower().strip()
    for clave, respuesta in respuestas_fijas.items():
        if clave in input_lower:
            return jsonify({"respuesta": respuesta, "sugerencias": []})

    try:
        # Agente 1 — triaje local con historial
        triaje = agente_1_entrevistador(user_input, historial)
        if "PROCEDER" not in triaje.upper():
            return jsonify({"respuesta": triaje, "sugerencias": []})

        # Agentes 2-5 — análisis con historial
        riesgo_json  = agente_2_analista(user_input, historial)
        contexto     = agente_3_contexto(user_input, riesgo_json, historial)
        arquitectura = agente_4_arquitecto(user_input, riesgo_json, historial)
        continuidad  = agente_5_continuidad(user_input, riesgo_json, historial)

        # Agente 6 — reporte final
        reporte = agente_6_comunicador(
            user_input, riesgo_json, contexto, arquitectura, continuidad, historial
        )

        # Sugerencias
        sugerencias = generar_sugerencias(user_input, reporte)

        return jsonify({"respuesta": reporte, "sugerencias": sugerencias})

    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    app.run(debug=True)


