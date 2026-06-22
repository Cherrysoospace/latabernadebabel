/**
 * resenas.js — CRUD completo para la colección 'resenas'.
 * Incluye selector de calificación con estrellas interactivas.
 */

/* ── Estado local ─────────────────────────────────────────────────── */
let resenasData = [];
let sortStateResenas = { field: null, dir: 'asc' };
let pagResenas = createPaginationState(25);

function ordenarResenas(field) {
  toggleSort(sortStateResenas, field, resenasData, renderTablaResenas);
  actualizarIndicadores('#resenas-table th[data-field]', sortStateResenas);
}

/* ── Cargar y renderizar ──────────────────────────────────────────── */

async function cargarResenas(pagina) {
  if (pagina !== undefined) pagResenas.page = pagina;

  showLoader('resenas-loader');
  hideEmpty('resenas-empty');

  const params = {};
  const q = document.getElementById('resenas-search')?.value.trim();
  if (q) params.q = q;
  const minCal = document.getElementById('resenas-filter-calificacion')?.value;
  if (minCal) params.calificacion_min = minCal;

  const hayFiltro = q || minCal;
  if (!hayFiltro) {
    const { skip, limit } = getPaginationParams(pagResenas);
    params.skip  = skip;
    params.limit = limit;
  }

  try {
    const data = await resenasAPI.getAll(params);

    if (data.total !== undefined) {
      resenasData = data.resenas || [];
      updatePaginationState(pagResenas, data.total);
      renderPaginacion('resenas-pagination', pagResenas, cargarResenas);
    } else {
      resenasData = Array.isArray(data) ? data : (data.resenas || []);
      const pc = document.getElementById('resenas-pagination');
      if (pc) pc.innerHTML = '';
    }

    renderTablaResenas(resenasData);
  } catch (err) {
    showToast(`Error al cargar reseñas: ${err.message}`, 'error');
    resenasData = [];
    renderTablaResenas([]);
  } finally {
    hideLoader('resenas-loader');
  }
}

function renderTablaResenas(resenas) {
  const tbody = document.getElementById('resenas-tbody');
  if (!tbody) return;

  if (!resenas.length) {
    tbody.innerHTML = '';
    showEmpty('resenas-empty');
    return;
  }

  hideEmpty('resenas-empty');
  tbody.innerHTML = resenas.map(r => `
    <tr>
      <td><code style="font-size:0.75rem">${r.resena_id || '—'}</code></td>
      <td>${r.usuario ? `${r.usuario.nombre} ${shortId(r.usuario.usuario_id)}` : '—'}</td>
      <td>${r.libro ? `${r.libro.titulo} ${shortId(r.libro.libro_id)}` : '—'}</td>
      <td>${starsHTML(r.calificacion)}</td>
      <td class="td-truncate" title="${(r.comentario || '').replace(/"/g, '&quot;')}">${truncate(r.comentario, 55)}</td>
      <td style="color:var(--text-muted)">${formatDate(r.fecha)}</td>
      <td>
        <div class="td-actions">
          <button class="btn btn-sm btn-secondary" onclick="abrirEditarResena('${r.resena_id}')">Editar</button>
          <button class="btn btn-sm btn-danger"    onclick="eliminarResena('${r.resena_id}')">Eliminar</button>
        </div>
      </td>
    </tr>
  `).join('');
}

/* ── Eliminar ─────────────────────────────────────────────────────── */

function eliminarResena(id) {
  confirmAction(
    '¿Eliminar esta reseña? Esta acción no se puede deshacer.',
    async () => {
      try {
        await resenasAPI.delete(id);
        showToast('Reseña eliminada.', 'success');
        cargarResenas();
      } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
      }
    }
  );
}

/* ── Selector de estrellas ────────────────────────────────────────── */

/**
 * Inicializa el selector de estrellas interactivo dentro del modal.
 * Escucha clics en los botones con clase .star-btn y actualiza el
 * valor del input oculto #f-calificacion.
 */
function initStarPicker(valorInicial = 0) {
  const picker = document.getElementById('star-picker');
  if (!picker) return;

  const stars = picker.querySelectorAll('.star-btn');
  let selected = valorInicial;

  function updateStars(n) {
    stars.forEach((btn, i) => {
      btn.classList.toggle('active', i < n);
    });
    document.getElementById('f-calificacion').value = n;
  }

  updateStars(selected);

  stars.forEach((btn, i) => {
    btn.addEventListener('click', () => {
      selected = i + 1;
      updateStars(selected);
    });
    btn.addEventListener('mouseenter', () => updateStars(i + 1));
    btn.addEventListener('mouseleave', () => updateStars(selected));
  });
}

/* ── Formulario ───────────────────────────────────────────────────── */

async function buildFormResenaHTML(r = {}) {
  // Cargar usuarios y libros para los selects
  let usuarios = [];
  let libros   = [];
  try {
    const [uData, lData] = await Promise.all([
      usuariosAPI.getAll({ activo: 'true', limit: 200 }),
      librosAPI.getAll({ limit: 1000 }),
    ]);
    usuarios = Array.isArray(uData) ? uData : (uData.usuarios || []);
    libros   = Array.isArray(lData) ? lData : (lData.libros   || []);
  } catch (_) {}

  const optUsuarios = usuarios.map(u =>
    `<option value="${u.usuario_id}" ${r.usuario_id === u.usuario_id ? 'selected' : ''}>${u.nombre} (${u.correo})</option>`
  ).join('');

  const optLibros = libros.map(l =>
    `<option value="${l.libro_id}" ${r.libro_id === l.libro_id ? 'selected' : ''}>${l.titulo}</option>`
  ).join('');

  // Solo mostrar los selects al crear (no al editar)
  const isEdit = !!r.resena_id;
  const selectsHTML = isEdit ? '' : `
    <div class="form-group">
      <label class="form-label" for="r-usuario">Usuario *</label>
      <select class="input-field input-select" id="r-usuario">
        <option value="">Selecciona un usuario…</option>
        ${optUsuarios}
      </select>
    </div>
    <div class="form-group">
      <label class="form-label" for="r-libro">Libro *</label>
      <select class="input-field input-select" id="r-libro">
        <option value="">Selecciona un libro…</option>
        ${optLibros}
      </select>
    </div>
  `;

  return `
    ${selectsHTML}

    <div class="form-group">
      <label class="form-label">Calificación *</label>
      <div class="star-picker" id="star-picker">
        <button type="button" class="star-btn" aria-label="1 estrella">★</button>
        <button type="button" class="star-btn" aria-label="2 estrellas">★</button>
        <button type="button" class="star-btn" aria-label="3 estrellas">★</button>
        <button type="button" class="star-btn" aria-label="4 estrellas">★</button>
        <button type="button" class="star-btn" aria-label="5 estrellas">★</button>
      </div>
      <input type="hidden" id="f-calificacion" value="${r.calificacion || 0}" />
    </div>

    <div class="form-group">
      <label class="form-label" for="r-comentario">Comentario</label>
      <textarea class="input-field input-textarea" id="r-comentario"
                placeholder="Escribe tu reseña aquí…">${r.comentario || ''}</textarea>
    </div>
  `;
}

async function abrirCrearResena() {
  modal.open('Nueva Reseña', '<div class="loader visible" style="margin:2rem auto"></div>', () => {});
  const formHTML = await buildFormResenaHTML();
  document.getElementById('modal-body').innerHTML = formHTML;
  initStarPicker(0);

  const submitBtn = document.getElementById('modal-submit');
  const newBtn = submitBtn.cloneNode(true);
  submitBtn.replaceWith(newBtn);

  newBtn.addEventListener('click', async () => {
    const usuario_id    = document.getElementById('r-usuario')?.value;
    const libro_id      = document.getElementById('r-libro')?.value;
    const calificacion  = parseInt(document.getElementById('f-calificacion')?.value || '0');
    const comentario    = document.getElementById('r-comentario')?.value.trim();

    if (!usuario_id || !libro_id) {
      showToast('Debes seleccionar un usuario y un libro.', 'warning');
      return;
    }
    if (!calificacion || calificacion < 1 || calificacion > 5) {
      showToast('La calificación debe estar entre 1 y 5 estrellas.', 'warning');
      return;
    }

    try {
      await resenasAPI.create({ usuario_id, libro_id, calificacion, comentario });
      showToast('Reseña creada exitosamente.', 'success');
      modal.close();
      cargarResenas();
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    }
  });
}

async function abrirEditarResena(id) {
  try {
    const r = await resenasAPI.getById(id);
    modal.open('Editar Reseña', '<div class="loader visible" style="margin:2rem auto"></div>', () => {});
    const formHTML = await buildFormResenaHTML(r);
    document.getElementById('modal-body').innerHTML = formHTML;
    initStarPicker(r.calificacion || 0);

    const submitBtn = document.getElementById('modal-submit');
    const newBtn = submitBtn.cloneNode(true);
    submitBtn.replaceWith(newBtn);

    newBtn.addEventListener('click', async () => {
      const calificacion = parseInt(document.getElementById('f-calificacion')?.value || '0');
      const comentario   = document.getElementById('r-comentario')?.value.trim();

      if (!calificacion || calificacion < 1 || calificacion > 5) {
        showToast('La calificación debe estar entre 1 y 5 estrellas.', 'warning');
        return;
      }

      try {
        await resenasAPI.update(id, { calificacion, comentario });
        showToast('Reseña actualizada.', 'success');
        modal.close();
        cargarResenas();
      } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
      }
    });
  } catch (err) {
    showToast(`Error al cargar reseña: ${err.message}`, 'error');
  }
}

/* ── Inicialización ───────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('resenas-btn-crear')?.addEventListener('click', abrirCrearResena);
  document.getElementById('resenas-filter-calificacion')?.addEventListener('change', () => {
    pagResenas.page = 1;
    cargarResenas();
  });

  let debounceResenas;
  document.getElementById('resenas-search')?.addEventListener('input', () => {
    pagResenas.page = 1;
    clearTimeout(debounceResenas);
    debounceResenas = setTimeout(cargarResenas, 350);
  });

  registerLoader('/resenas', cargarResenas);
});
