/**
 * nosql.js — Panel "Consultas NoSQL": ejecuta comandos mongosh contra el backend.
 */

const NOSQL_API = `${BASE_URL}/nosql/ejecutar`;

/* ── Ejemplos predefinidos ───────────────────────────────────────────── */
const EJEMPLOS = [
  { label: 'Todos los libros',           cmd: 'db.libros.find()' },
  { label: 'Un libro por ID',            cmd: 'db.libros.findOne({ libro_id: "LIB-001" })' },
  { label: 'Libros disponibles',         cmd: 'db.libros.find({ disponible: true })' },
  { label: 'Contar libros',              cmd: 'db.libros.countDocuments()' },
  { label: 'Libros de fantasía',         cmd: 'db.libros.find({ genero: "fantasia" })' },
  { label: 'Agrupar por género',         cmd: 'db.libros.aggregate([{ $group: { _id: "$genero", total: { $sum: 1 } } }, { $sort: { total: -1 } }])' },
  { label: 'Usuarios premium',           cmd: 'db.usuarios.find({ membresia: "premium" })' },
  { label: 'Préstamos activos',          cmd: 'db.prestamos.find({ estado: "activo" })' },
  { label: 'Mostrar colecciones',        cmd: 'show collections' },
  { label: 'Top libros mejor rating',    cmd: 'db.resenas.aggregate([{ $group: { _id: "$libro_id", promedio: { $avg: "$calificacion" }, total: { $sum: 1 } } }, { $sort: { promedio: -1 } }, { $limit: 5 }])' },
];

/* ── Estado ──────────────────────────────────────────────────────────── */
let historial = [];

/* ── Inicialización ──────────────────────────────────────────────────── */
function cargarNoSql() {
  renderizarHistorial();
  renderizarEjemplos();
  configurarFormulario();
}

function configurarFormulario() {
  const input  = document.getElementById('nosql-input');
  const btn    = document.getElementById('nosql-btn-ejecutar');
  const loader = document.getElementById('nosql-loader');

  function ejecutar() {
    const cmd = input.value.trim();
    if (!cmd) return;
    agregarAlHistorial(cmd, null, 'pending');
    input.value = '';
    btn.disabled = true;
    loader.classList.add('visible');

    fetch(NOSQL_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ comando: cmd }),
    })
      .then(r => r.json())
      .then(data => {
        actualizarUltimoHistorial(data);
        renderizarHistorial();
      })
      .catch(err => {
        actualizarUltimoHistorial({ error: err.message, tipo: 'error' });
        renderizarHistorial();
      })
      .finally(() => {
        btn.disabled = false;
        loader.classList.remove('visible');
      });
  }

  btn.addEventListener('click', ejecutar);
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      ejecutar();
    }
  });
}

/* ── Historial ───────────────────────────────────────────────────────── */
function agregarAlHistorial(comando, resultado, estado) {
  historial.unshift({ comando, resultado, estado, ts: new Date().toISOString() });
}

function actualizarUltimoHistorial(resultado) {
  if (historial.length > 0) {
    historial[0].resultado = resultado;
    historial[0].estado = resultado.error ? 'error' : 'ok';
  }
}

function renderizarHistorial() {
  const container = document.getElementById('nosql-historial');
  if (!container) return;
  container.innerHTML = historial.length === 0
    ? '<div class="nosql-empty">Aún no has ejecutado ninguna consulta.</div>'
    : historial.map(item => renderizarItem(item)).join('');
  container.scrollTop = 0;
}

function renderizarItem(item) {
  const estadoClase = item.estado === 'error' ? 'nosql-item-error'
    : item.estado === 'pending' ? 'nosql-item-pending'
    : 'nosql-item-ok';

  const resultadoHTML = item.resultado
    ? renderizarResultado(item.resultado)
    : item.estado === 'pending'
      ? '<div class="nosql-result-pending">Ejecutando…</div>'
      : '';

  return `
    <div class="nosql-item ${estadoClase}">
      <div class="nosql-item-header">
        <code class="nosql-command">${escapeHtml(item.comando)}</code>
        <span class="nosql-timestamp">${formatDate(item.ts)}</span>
      </div>
      ${resultadoHTML}
    </div>
  `;
}

function renderizarResultado(data) {
  if (data.error) {
    return `<div class="nosql-result nosql-result-error">${escapeHtml(data.error)}</div>`;
  }

  if (data.tipo === 'number') {
    return `<div class="nosql-result nosql-result-number">${formatNumber(data.resultado)}</div>`;
  }

  if (data.tipo === 'null') {
    return `<div class="nosql-result nosql-result-null">null</div>`;
  }

  if (data.tipo === 'cursor' && data.total === 0) {
    return `<div class="nosql-result nosql-result-empty">No se encontraron documentos.</div>`;
  }

  if (data.tipo === 'cursor') {
    const resumen = `<div class="nosql-result-count">${data.total} documento${data.total !== 1 ? 's' : ''} encontrado${data.total !== 1 ? 's' : ''}</div>`;
    const tabla = data.total > 0 ? generarTabla(data.resultado) : '';
    return resumen + tabla;
  }

  if (data.tipo === 'document') {
    return `<pre class="nosql-result-json">${syntaxHighlight(data.resultado)}</pre>`;
  }

  if (data.tipo === 'list') {
    if (Array.isArray(data.resultado) && data.resultado.length > 0) {
      const items = data.resultado.map(item =>
        typeof item === 'string' ? escapeHtml(item) : syntaxHighlight(item)
      ).join('\n');
      return `<pre class="nosql-result-json">${items}</pre>`;
    }
    return `<pre class="nosql-result-json">${JSON.stringify(data.resultado, null, 2)}</pre>`;
  }

  if (data.tipo === 'insert_result') {
    if (Array.isArray(data.resultado)) {
      return `<div class="nosql-result nosql-result-success">${data.resultado.length} documento(s) insertado(s). IDs: ${data.resultado.join(', ')}</div>`;
    }
    return `<div class="nosql-result nosql-result-success">Documento insertado. ID: ${data.resultado}</div>`;
  }

  if (data.tipo === 'update_result') {
    return `<div class="nosql-result nosql-result-success">Coincidieron: ${data.resultado.matched_count}, Modificados: ${data.resultado.modified_count}${data.resultado.upserted_id ? ', Upserted ID: ' + data.resultado.upserted_id : ''}</div>`;
  }

  if (data.tipo === 'delete_result') {
    return `<div class="nosql-result nosql-result-success">${data.resultado.deleted_count} documento(s) eliminado(s).</div>`;
  }

  if (data.tipo === 'success') {
    return `<div class="nosql-result nosql-result-success">${escapeHtml(data.resultado)}</div>`;
  }

  return `<pre class="nosql-result-json">${syntaxHighlight(data.resultado)}</pre>`;
}

/* ── Tabla genérica para resultados de cursor ────────────────────────── */
function generarTabla(docs) {
  if (!docs || docs.length === 0) return '';
  const keys = Object.keys(docs[0]);
  const rows = docs.map(doc => {
    const cells = keys.map(k => {
      const val = doc[k];
      return `<td>${formatearCelda(val)}</td>`;
    }).join('');
    return `<tr>${cells}</tr>`;
  }).join('');

  return `
    <div class="table-wrapper nosql-table-wrapper">
      <table class="data-table nosql-table">
        <thead><tr>${keys.map(k => `<th>${escapeHtml(k)}</th>`).join('')}</tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function formatearCelda(val) {
  if (val === null || val === undefined) return '<span class="nosql-cell-null">null</span>';
  if (typeof val === 'boolean') return val ? 'true' : 'false';
  if (typeof val === 'object') {
    if (val instanceof Array) return `<code>Array(${val.length})</code>`;
    return `<code>${escapeHtml(JSON.stringify(val).slice(0, 80))}${JSON.stringify(val).length > 80 ? '…' : ''}</code>`;
  }
  return escapeHtml(String(val));
}

/* ── Ejemplos ────────────────────────────────────────────────────────── */
function renderizarEjemplos() {
  const container = document.getElementById('nosql-ejemplos');
  if (!container) return;
  container.innerHTML = EJEMPLOS.map(e => `
    <button class="nosql-ejemplo-btn" data-cmd="${escapeHtml(e.cmd)}">
      <span class="ejemplo-label">${escapeHtml(e.label)}</span>
      <code class="ejemplo-cmd">${escapeHtml(e.cmd)}</code>
    </button>
  `).join('');

  container.querySelectorAll('.nosql-ejemplo-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.getElementById('nosql-input');
      input.value = btn.dataset.cmd;
      input.focus();
    });
  });
}

/* ── Utilidades ──────────────────────────────────────────────────────── */
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function formatNumber(n) {
  return new Intl.NumberFormat('es-CO').format(n);
}

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function syntaxHighlight(obj) {
  const json = JSON.stringify(obj, null, 2);
  if (!json) return '';
  return escapeHtml(json);
  /* Se podría agregar highlighting con regex, pero dejamos texto plano por ahora */
}

/* ── Registrar loader ────────────────────────────────────────────────── */
registerLoader('/nosql', cargarNoSql);
