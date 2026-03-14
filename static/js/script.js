const canvas = document.getElementById('matrix-bg');
const ctx    = canvas.getContext('2d');
canvas.width  = window.innerWidth;
canvas.height = window.innerHeight;
window.addEventListener('resize', () => {
  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight;
  initMatrix();
});

const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*<>/\\[]{}アイウエオカキクケコ';
let drops = [];

function initMatrix() {
  const cols = Math.floor(canvas.width / 16);
  drops = Array.from({ length: cols }, () => Math.random() * -50);
}
initMatrix();

function drawMatrix() {
  ctx.fillStyle = 'rgba(2,11,5,0.05)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#00ff41';
  ctx.font = '13px Share Tech Mono';
  drops.forEach((y, i) => {
    const ch = chars[Math.floor(Math.random() * chars.length)];
    ctx.fillText(ch, i * 16, y * 16);
    if (y * 16 > canvas.height && Math.random() > 0.975) drops[i] = 0;
    drops[i] += 0.5;
  });
}
setInterval(drawMatrix, 55);

// ── Chat logic ──
const chatWindow  = document.getElementById('chat-window');
const promptInput = document.getElementById('prompt');
const sendBtn     = document.getElementById('send-btn');
const welcome     = document.getElementById('welcome');
const msgCount    = document.getElementById('msg-count');
const charCount   = document.getElementById('char-count');
let count = 0;

// ── Historial de conversación ──
let historial = [];

promptInput.addEventListener('input', () => {
  promptInput.style.height = 'auto';
  promptInput.style.height = Math.min(promptInput.scrollHeight, 120) + 'px';
  charCount.textContent = `${promptInput.value.length} / 600`;
});

promptInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); enviar(); }
});
sendBtn.addEventListener('click', () => enviar());

function timestamp() {
  return new Date().toISOString().replace('T',' ').substring(0,19) + ' UTC';
}

// ── Markdown → HTML ──
function formatearRespuesta(texto) {
  let t = texto
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  t = t.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  t = t.replace(/\*(.*?)\*/g, '<em>$1</em>');
  t = t.replace(/^### (.+)$/gm, '<h4>$1</h4>');
  t = t.replace(/^## (.+)$/gm, '<h3>$1</h3>');

  const lines = t.split('\n');
  let html = '';
  let inList = false;
  let inTable = false;
  let tableRows = [];

  const flushTable = () => {
    if (tableRows.length === 0) return;
    html += '<table>';
    tableRows.forEach((row, i) => {
      const cells = row.split('|').map(c => c.trim()).filter(c => c !== '');
      if (i === 0) {
        html += '<thead><tr>' + cells.map(c => `<th>${c}</th>`).join('') + '</tr></thead><tbody>';
      } else {
        html += '<tr>' + cells.map(c => `<td>${c}</td>`).join('') + '</tr>';
      }
    });
    html += '</tbody></table>';
    tableRows = [];
    inTable = false;
  };

  lines.forEach(line => {
    const trimmed = line.trim();

    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      if (/^\|[\s\-\|]+\|$/.test(trimmed)) return;
      if (inList) { html += '</ul>'; inList = false; }
      inTable = true;
      tableRows.push(trimmed);
      return;
    }

    if (inTable) flushTable();

    if (/^[•\-] .+/.test(trimmed)) {
      if (!inList) { html += '<ul>'; inList = true; }
      html += `<li>${trimmed.replace(/^[•\-] /, '')}</li>`;
    } else if (/^\d+\. .+/.test(trimmed)) {
      if (!inList) { html += '<ul>'; inList = true; }
      html += `<li>${trimmed.replace(/^\d+\. /, '')}</li>`;
    } else if (trimmed === '') {
      if (inList) { html += '</ul>'; inList = false; }
      html += '<br>';
    } else {
      if (inList) { html += '</ul>'; inList = false; }
      html += `<p>${trimmed}</p>`;
    }
  });

  if (inList) html += '</ul>';
  if (inTable) flushTable();

  return html;
}

// ── Mensajes ──
function addMsg(role, text, isError = false) {
  if (welcome) welcome.style.display = 'none';

  const div = document.createElement('div');
  div.className = `msg ${isError ? 'error' : role}`;

  const labelMap = {
    user:  'ANALYST INPUT',
    bot:   'AI RESPONSE',
    error: 'SYSTEM ERROR'
  };

  const bodyContent = (role === 'bot' && !isError)
    ? formatearRespuesta(text)
    : `<p>${text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</p>`;

  div.innerHTML = `
    <div class="msg-header">
      <div class="tag">${isError ? 'SYSTEM ERROR' : labelMap[role]}</div>
      <span>${timestamp()}</span>
    </div>
    <div class="msg-body">${bodyContent}</div>
  `;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return div;
}

function addTyping() {
  if (welcome) welcome.style.display = 'none';
  const div = document.createElement('div');
  div.className = 'msg bot typing';
  div.innerHTML = `
    <div class="msg-header">
      <div class="tag">PROCESANDO · 6 AGENTES ACTIVOS</div>
      <span>${timestamp()}</span>
    </div>
    <div class="msg-body">
      <div class="t-dot"></div>
      <div class="t-dot"></div>
      <div class="t-dot"></div>
    </div>
  `;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return div;
}

// ── Sugerencias ──
function mostrarSugerencias(sugerencias) {
  const div = document.createElement('div');
  div.id = 'sugerencias';
  div.className = 'sugerencias-container';
  div.innerHTML = `
    <div class="sug-label">💡 CONSULTAS RELACIONADAS</div>
    <div class="sug-chips">
      ${sugerencias.map(s => `
        <button class="sug-chip" onclick="enviar('${s.replace(/'/g, "\\'")}')">
          <span>›</span> ${s}
        </button>`).join('')}
    </div>
  `;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ── Enviar mensaje ──
async function enviar(textoDirecto = null) {
  const text = textoDirecto || promptInput.value.trim();
  if (!text) return;

  addMsg('user', text);

  // Guardar en historial
  historial.push({ role: 'user', content: text });
  if (historial.length > 20) historial = historial.slice(-20);

  promptInput.value = '';
  promptInput.style.height = 'auto';
  charCount.textContent = '0 / 600';
  sendBtn.disabled = true;
  count++;
  msgCount.textContent = count;

  // Limpiar sugerencias anteriores
  const sugAnterior = document.getElementById('sugerencias');
  if (sugAnterior) sugAnterior.remove();

  const typingEl = addTyping();

  try {
    const res  = await fetch('/generar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: text, historial: historial })
    });
    const data = await res.json();
    typingEl.remove();

    if (data.error) {
      addMsg('error', data.error, true);
    } else {
      addMsg('bot', data.respuesta);

      // Guardar respuesta en historial
      historial.push({ role: 'assistant', content: data.respuesta });

      // Mostrar sugerencias si existen
      if (data.sugerencias && data.sugerencias.length > 0) {
        mostrarSugerencias(data.sugerencias);
      }
    }
  } catch (err) {
    typingEl.remove();
    addMsg('error', 'CONNECTION_REFUSED :: No se pudo contactar al servidor.', true);
  } finally {
    sendBtn.disabled = false;
    promptInput.focus();
  }
}