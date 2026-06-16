/**
 * utils.js — Funciones de utilidad compartidas por todos los módulos.
 */

/* ── Formateo de fechas ─────────────────────────────────────────────── */

/**
 * Convierte un string ISO de fecha a formato legible en español.
 * @param {string|null} isoString
 * @returns {string}
 */
function formatDate(isoString) {
  if (!isoString) return '—';
  const d = new Date(isoString);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Devuelve "hace X días / hoy" a partir de una fecha ISO.
 * @param {string} isoString
 * @returns {string}
 */
function relativeDate(isoString) {
  if (!isoString) return '—';
  const d = new Date(isoString);
  const diff = Math.floor((Date.now() - d.getTime()) / 86400000);
  if (diff === 0) return 'Hoy';
  if (diff === 1) return 'Ayer';
  if (diff < 30) return `Hace ${diff} días`;
  return formatDate(isoString);
}

/* ── Truncado de texto ──────────────────────────────────────────────── */

/**
 * Trunca un texto largo con "…".
 * @param {string} text
 * @param {number} max
 */
function truncate(text, max = 60) {
  if (!text) return '—';
  return text.length > max ? text.slice(0, max) + '…' : text;
}

/* ── Generación de estrellas ────────────────────────────────────────── */

/**
 * Genera el HTML de estrellas para una calificación de 1 a 5.
 * @param {number} n
 * @returns {string}
 */
function starsHTML(n) {
  const filled = Math.round(n) || 0;
  let html = '<span class="stars">';
  for (let i = 1; i <= 5; i++) {
    html += i <= filled
      ? '<span class="star-filled">★</span>'
      : '<span class="star-empty">★</span>';
  }
  html += '</span>';
  return html;
}

/* ── Badges ─────────────────────────────────────────────────────────── */

/**
 * Devuelve el HTML de un badge con clase de color según valor.
 * @param {string} text
 * @param {'success'|'danger'|'warning'|'info'|'muted'} type
 */
function badgeHTML(text, type = 'muted') {
  return `<span class="badge badge-${type}">${text}</span>`;
}

/**
 * Mapeo de estado de préstamo a tipo de badge.
 */
function prestamoBadge(estado) {
  const map = {
    activo:   ['Activo', 'success'],
    devuelto: ['Devuelto', 'info'],
    vencido:  ['Vencido', 'danger'],
  };
  const [label, type] = map[estado] || [estado, 'muted'];
  return badgeHTML(label, type);
}

/**
 * Badge de membresía de usuario.
 */
function membresiaBadge(membresia) {
  const map = {
    premium:    ['Premium', 'warning'],
    basica:     ['Básica', 'muted'],
    estudiante: ['Estudiante', 'info'],
  };
  const [label, type] = map[membresia] || [membresia, 'muted'];
  return badgeHTML(label, type);
}

/**
 * Badge de disponibilidad de libro.
 */
function disponibleBadge(disponible) {
  return disponible
    ? badgeHTML('Disponible', 'success')
    : badgeHTML('No disponible', 'danger');
}

/* ── Toast de notificaciones ────────────────────────────────────────── */

const TOAST_ICONS = {
  success: '✅',
  error:   '❌',
  warning: '⚠️',
};

/**
 * Muestra un toast flotante en la esquina inferior derecha.
 * @param {string} message
 * @param {'success'|'error'|'warning'} type
 * @param {number} duration ms antes de desaparecer
 */
function showToast(message, type = 'success', duration = 3500) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${TOAST_ICONS[type] || 'ℹ️'}</span>
    <span class="toast-message">${message}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('removing');
    toast.addEventListener('animationend', () => toast.remove());
  }, duration);
}

/* ── Modal genérico ─────────────────────────────────────────────────── */

const modal = {
  overlay:   () => document.getElementById('modal-overlay'),
  title:     () => document.getElementById('modal-title'),
  body:      () => document.getElementById('modal-body'),
  submitBtn: () => document.getElementById('modal-submit'),
  closeBtn:  () => document.getElementById('modal-close'),
  cancelBtn: () => document.getElementById('modal-cancel'),

  /**
   * Abre el modal con un título, contenido HTML en body, y un handler para submit.
   * @param {string} title
   * @param {string} bodyHTML
   * @param {function} onSubmit  — Callback async que recibe el evento submit
   * @param {string} submitLabel — Texto del botón de guardar
   */
  open(title, bodyHTML, onSubmit, submitLabel = 'Guardar') {
    this.title().textContent  = title;
    this.body().innerHTML     = bodyHTML;
    this.submitBtn().textContent = submitLabel;
    this.overlay().classList.remove('hidden');

    // Reasignar handlers (clonar para limpiar listeners anteriores)
    const newSubmit = this.submitBtn().cloneNode(true);
    this.submitBtn().replaceWith(newSubmit);
    newSubmit.addEventListener('click', onSubmit);
  },

  close() {
    this.overlay().classList.add('hidden');
    this.body().innerHTML = '';
  },
};

/* Cerrar modal con X y Cancelar */
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('modal-close')?.addEventListener('click',  () => modal.close());
  document.getElementById('modal-cancel')?.addEventListener('click', () => modal.close());
  document.getElementById('modal-overlay')?.addEventListener('click', (e) => {
    if (e.target === document.getElementById('modal-overlay')) modal.close();
  });
});

/* ── Confirmación antes de eliminar ─────────────────────────────────── */

/**
 * Pide confirmación al usuario antes de ejecutar una acción destructiva.
 * @param {string} message
 * @param {function} onConfirm
 */
function confirmAction(message, onConfirm) {
  if (window.confirm(message)) onConfirm();
}

/* ── Loader de tabla ─────────────────────────────────────────────────── */

function showLoader(id)   { document.getElementById(id)?.classList.add('visible'); }
function hideLoader(id)   { document.getElementById(id)?.classList.remove('visible'); }
function showEmpty(id)    { document.getElementById(id)?.classList.remove('hidden'); }
function hideEmpty(id)    { document.getElementById(id)?.classList.add('hidden'); }

/* ── Serializar ID corto para mostrar en tabla ───────────────────────── */

/**
 * Muestra solo los primeros 8 caracteres del ObjectId en la tabla.
 * @param {string} id
 */
function shortId(id) {
  return id ? `<code style="font-size:0.75rem;color:var(--text-muted)">${id.slice(0, 8)}…</code>` : '—';
}
