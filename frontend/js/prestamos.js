/**
 * prestamos.js — CRUD completo para la colección 'prestamos'.
 * Incluye el botón "Devolver" que cambia el estado y libera el libro.
 */

/* ── Estado local ─────────────────────────────────────────────────── */
let prestamosData = [];
let sortStatePrestamos = { field: null, dir: 'asc' };

function ordenarPrestamos(field) {
  toggleSort(sortStatePrestamos, field, prestamosData, renderTablaPrestamos);
  actualizarIndicadores('#prestamos-table th[data-field]', sortStatePrestamos);
}

/* ── Cargar y renderizar ──────────────────────────────────────────── */

async function cargarPrestamos() {
  showLoader('prestamos-loader');
  hideEmpty('prestamos-empty');

  const params = {};
  const estado = document.getElementById('prestamos-filter-estado')?.value;
  if (estado) params.estado = estado;

  try {
    const data = await prestamosAPI.getAll(params);
    prestamosData = Array.isArray(data) ? data : (data.prestamos || []);
    renderTablaPrestamos(prestamosData);
  } catch (err) {
    showToast(`Error al cargar préstamos: ${err.message}`, 'error');
    prestamosData = [];
    renderTablaPrestamos([]);
  } finally {
    hideLoader('prestamos-loader');
  }
}

function renderTablaPrestamos(prestamos) {
  const tbody = document.getElementById('prestamos-tbody');
  if (!tbody) return;

  if (!prestamos.length) {
    tbody.innerHTML = '';
    showEmpty('prestamos-empty');
    return;
  }

  hideEmpty('prestamos-empty');
  tbody.innerHTML = prestamos.map(p => `
    <tr>
      <td>${shortId(p.prestamo_id)}</td>
      <td>${p.usuario ? `${p.usuario.nombre} ${shortId(p.usuario.usuario_id)}` : '—'}</td>
      <td>${p.libro ? `${p.libro.titulo} ${shortId(p.libro.libro_id)}` : '—'}</td>
      <td style="color:var(--text-secondary)">${formatDate(p.fecha_inicio)}</td>
      <td style="color:var(--text-secondary)">${formatDate(p.fecha_fin)}</td>
      <td>${prestamoBadge(p.estado)}</td>
      <td>
        <div class="td-actions">
          ${p.estado === 'activo' || p.estado === 'vencido'
            ? `<button class="btn btn-sm btn-success" onclick="devolverPrestamo('${p.prestamo_id}')">Devolver</button>`
            : ''}
          <button class="btn btn-sm btn-danger" onclick="eliminarPrestamo('${p.prestamo_id}')">Eliminar</button>
        </div>
      </td>
    </tr>
  `).join('');
}

/* ── Devolver préstamo ────────────────────────────────────────────── */

async function devolverPrestamo(id) {
  confirmAction(
    '¿Confirmar la devolución de este préstamo? El libro volverá a estar disponible.',
    async () => {
      try {
        await prestamosAPI.devolver(id);
        showToast('Préstamo devuelto exitosamente.', 'success');
        cargarPrestamos();
      } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
      }
    }
  );
}

/* ── Eliminar ─────────────────────────────────────────────────────── */

function eliminarPrestamo(id) {
  confirmAction(
    `¿Eliminar el préstamo con ID "${id}"?`,
    async () => {
      try {
        await prestamosAPI.delete(id);
        showToast('Préstamo eliminado.', 'success');
        cargarPrestamos();
      } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
      }
    }
  );
}

/* ── Formulario de crear préstamo ─────────────────────────────────── */

/**
 * Carga los selects de usuarios y libros disponibles desde la API.
 * Se llama al abrir el modal para tener los datos frescos.
 */
async function buildFormPrestamoHTML() {
  // Cargar usuarios activos y libros disponibles en paralelo
  let usuarios = [];
  let libros   = [];

  try {
    const [uData, lData] = await Promise.all([
      usuariosAPI.getAll({ activo: 'true', limit: 200 }),
      librosAPI.getAll({ disponible: 'true', limit: 200 }),
    ]);
    usuarios = Array.isArray(uData) ? uData : (uData.usuarios || []);
    libros   = Array.isArray(lData) ? lData : (lData.libros   || []);
  } catch (_) {
    // Los selects quedarán vacíos; el backend validará al guardar
  }

  const optUsuarios = usuarios.length
    ? usuarios.map(u => `<option value="${u.usuario_id}">${u.nombre} (${u.correo})</option>`).join('')
    : '<option value="">— No hay usuarios activos —</option>';

  const optLibros = libros.length
    ? libros.map(l => `<option value="${l.libro_id}">${l.titulo} — ${l.autor?.name || l.autor || ''}</option>`).join('')
    : '<option value="">— No hay libros disponibles —</option>';

  return `
    <div class="form-group">
      <label class="form-label" for="p-usuario">Usuario *</label>
      <select class="input-field input-select" id="p-usuario">
        <option value="">Selecciona un usuario…</option>
        ${optUsuarios}
      </select>
    </div>

    <div class="form-group">
      <label class="form-label" for="p-libro">Libro disponible *</label>
      <select class="input-field input-select" id="p-libro">
        <option value="">Selecciona un libro…</option>
        ${optLibros}
      </select>
    </div>

    <div class="form-group">
      <label class="form-label" for="p-dias">Duración (días)</label>
      <input class="input-field" id="p-dias" type="number" min="1" max="60"
             placeholder="Se calcula por membresía si se deja vacío" />
      <small style="color:var(--text-muted);font-size:0.75rem">
        Básica: 14 días · Estudiante: 21 días · Premium: 30 días
      </small>
    </div>
  `;
}

async function abrirCrearPrestamo() {
  // Mostrar modal con loader mientras se cargan los selects
  modal.open('Nuevo Préstamo', '<div class="loader visible" style="margin:2rem auto"></div>', () => {});

  const formHTML = await buildFormPrestamoHTML();
  document.getElementById('modal-body').innerHTML = formHTML;

  // Reasignar el handler de submit ahora que el body está listo
  const submitBtn = document.getElementById('modal-submit');
  const newBtn = submitBtn.cloneNode(true);
  submitBtn.replaceWith(newBtn);

  newBtn.addEventListener('click', async () => {
    const usuario_id = document.getElementById('p-usuario')?.value;
    const libro_id   = document.getElementById('p-libro')?.value;
    const diasVal    = document.getElementById('p-dias')?.value;
    const dias       = diasVal ? parseInt(diasVal) : undefined;

    if (!usuario_id || !libro_id) {
      showToast('Debes seleccionar un usuario y un libro.', 'warning');
      return;
    }

    const datos = { usuario_id, libro_id };
    if (dias) datos.dias = dias;

    try {
      await prestamosAPI.create(datos);
      showToast('Préstamo creado exitosamente.', 'success');
      modal.close();
      cargarPrestamos();
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    }
  });
}

/* ── Inicialización ───────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('prestamos-btn-crear')?.addEventListener('click', abrirCrearPrestamo);
  document.getElementById('prestamos-filter-estado')?.addEventListener('change', cargarPrestamos);

  registerLoader('/prestamos', cargarPrestamos);
});
