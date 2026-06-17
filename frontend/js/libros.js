/**
 * libros.js — CRUD completo para la colección 'libros'.
 *
 * Responsabilidades:
 *   - Cargar y renderizar la tabla de libros con filtros.
 *   - Abrir el modal para crear y editar un libro.
 *   - Cambiar la disponibilidad de un libro (PATCH).
 *   - Eliminar un libro con confirmación.
 */

/* ── Estado local ─────────────────────────────────────────────────── */
let librosData = [];  // Cache de los libros actualmente mostrados
let sortStateLibros = { field: null, dir: 'asc' };

function ordenarLibros(field) {
  toggleSort(sortStateLibros, field, librosData, renderTablaLibros);
  actualizarIndicadores('#libros-table th[data-field]', sortStateLibros);
}

/* ── Cargar y renderizar ──────────────────────────────────────────── */

async function cargarLibros() {
  showLoader('libros-loader');
  hideEmpty('libros-empty');

  // Construir parámetros desde los filtros activos
  const params = {};
  const q         = document.getElementById('libros-search')?.value.trim();
  const genero    = document.getElementById('libros-filter-genero')?.value;
  const disponible = document.getElementById('libros-filter-disponible')?.value;

  if (q)          params.q = q;
  if (genero)     params.genero = genero;
  if (disponible) params.disponible = disponible;

  try {
    const data = await librosAPI.getAll(params);
    // El endpoint puede devolver un array directo o { libros: [...] }
    librosData = Array.isArray(data) ? data : (data.libros || []);
    renderTablaLibros(librosData);
  } catch (err) {
    showToast(`Error al cargar libros: ${err.message}`, 'error');
    librosData = [];
    renderTablaLibros([]);
  } finally {
    hideLoader('libros-loader');
  }
}

function renderTablaLibros(libros) {
  const tbody = document.getElementById('libros-tbody');
  if (!tbody) return;

  if (!libros.length) {
    tbody.innerHTML = '';
    showEmpty('libros-empty');
    return;
  }

  hideEmpty('libros-empty');
  tbody.innerHTML = libros.map(l => `
    <tr>
      <td><code style="font-size:0.75rem;color:var(--text-muted)">${l.libro_id || '—'}</code></td>
      <td class="td-truncate" title="${l.titulo || ''}">${l.titulo || '—'}</td>
      <td>${l.autor?.name || l.autor || '—'}</td>
      <td>${l.genero ? `<span style="text-transform:capitalize">${l.genero}</span>` : '—'}</td>
      <td>${l.anio || '—'}</td>
      <td>${(l.idioma || 'es').toUpperCase()}</td>
      <td>${disponibleBadge(l.disponible)}</td>
      <td>
        <div class="td-actions">
          <button class="btn btn-sm btn-secondary" onclick="abrirEditarLibro('${l.libro_id}')">Editar</button>
          <button class="btn btn-sm ${l.disponible ? 'btn-warning' : 'btn-success'}"
                  onclick="toggleDisponibilidad('${l.libro_id}', ${l.disponible})"
                  title="${l.disponible ? 'Marcar no disponible' : 'Marcar disponible'}">
            ${l.disponible ? 'No disp.' : 'Disp.'}
          </button>
          <button class="btn btn-sm btn-danger" onclick="eliminarLibro('${l.libro_id}', '${(l.titulo || '').replace(/'/g, "\\'")}')">Eliminar</button>
        </div>
      </td>
    </tr>
  `).join('');
}

/* ── Cambiar disponibilidad ───────────────────────────────────────── */

async function toggleDisponibilidad(id, estadoActual) {
  try {
    await librosAPI.cambiarDisponibilidad(id, !estadoActual);
    showToast(`Disponibilidad actualizada.`, 'success');
    cargarLibros();
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  }
}

/* ── Eliminar ─────────────────────────────────────────────────────── */

function eliminarLibro(id, titulo) {
  confirmAction(
    `¿Eliminar el libro "${titulo}"? Esta acción no se puede deshacer.`,
    async () => {
      try {
        await librosAPI.delete(id);
        showToast(`Libro "${titulo}" eliminado.`, 'success');
        cargarLibros();
      } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
      }
    }
  );
}

/* ── Formulario de crear/editar ───────────────────────────────────── */

let autoresCache = [];

async function cargarAutoresSelect() {
  try {
    const data = await autoresAPI.getAll({ limit: 200 });
    autoresCache = Array.isArray(data) ? data : (data.autores || []);
  } catch (_) {
    autoresCache = [];
  }
}

async function formLibroHTML(libro = {}) {
  await cargarAutoresSelect();
  const autorActual = libro.autor || {};
  const autorIdActual = autorActual.autor_id || '';

  const opcionesAutores = autoresCache.length
    ? autoresCache.map(a =>
        `<option value="${a.autor_id}" data-name="${a.nombre}" data-nacionalidad="${a.nacionalidad || ''}" ${a.autor_id === autorIdActual ? 'selected' : ''}>${a.nombre}${a.nacionalidad ? ` (${a.nacionalidad})` : ''}</option>`
      ).join('')
    : '<option value="">— No hay autores disponibles —</option>';

  return `
    <div class="form-row">
      <div class="form-group">
        <label class="form-label" for="f-titulo">Título *</label>
        <input class="input-field" id="f-titulo" type="text" placeholder="Título del libro" value="${libro.titulo || ''}" required />
      </div>
      <div class="form-group">
        <label class="form-label" for="f-autor">Autor *</label>
        <select class="input-field input-select" id="f-autor" required>
          <option value="">Selecciona un autor…</option>
          ${opcionesAutores}
        </select>
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label class="form-label" for="f-genero">Género *</label>
        <select class="input-field input-select" id="f-genero" required>
          ${['ficcion','no ficcion','ciencia ficcion','fantasia','terror','romance','misterio',
             'thriller','biografia','historia','ciencia','tecnologia','filosofia','poesia',
             'infantil','juvenil','autoayuda','arte','economia','derecho','otro']
            .map(g => `<option value="${g}" ${libro.genero === g ? 'selected' : ''}>${g.charAt(0).toUpperCase()+g.slice(1)}</option>`)
            .join('')}
        </select>
      </div>
      <div class="form-group">
        <label class="form-label" for="f-editorial">Editorial</label>
        <input class="input-field" id="f-editorial" type="text" placeholder="Casa editorial" value="${libro.editorial || ''}" />
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label class="form-label" for="f-anio">Año</label>
        <input class="input-field" id="f-anio" type="number" min="1000" max="${new Date().getFullYear() + 1}" placeholder="Ej. 1984" value="${libro.anio || ''}" />
      </div>
      <div class="form-group">
        <label class="form-label" for="f-idioma">Idioma</label>
        <select class="input-field input-select" id="f-idioma">
          ${[['es','Español'],['en','Inglés'],['fr','Francés'],['pt','Portugués'],
             ['de','Alemán'],['it','Italiano'],['zh','Chino'],['ja','Japonés'],
             ['ru','Ruso'],['ar','Árabe']]
            .map(([code, name]) => `<option value="${code}" ${(libro.idioma||'es')===code?'selected':''}>${name}</option>`)
            .join('')}
        </select>
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label class="form-label" for="f-formato">Formato</label>
        <select class="input-field input-select" id="f-formato">
          <option value="fisico"     ${(libro.formato||'fisico')==='fisico'?'selected':''}>Físico</option>
          <option value="digital"    ${libro.formato==='digital'?'selected':''}>Digital</option>
          <option value="audiolibro" ${libro.formato==='audiolibro'?'selected':''}>Audiolibro</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label" for="f-disponible">Disponible</label>
        <select class="input-field input-select" id="f-disponible">
          <option value="true"  ${libro.disponible !== false ? 'selected' : ''}>Sí</option>
          <option value="false" ${libro.disponible === false ? 'selected' : ''}>No</option>
        </select>
      </div>
    </div>

    <div class="form-group">
      <label class="form-label" for="f-descripcion">Descripción</label>
      <textarea class="input-field input-textarea" id="f-descripcion" placeholder="Sinopsis o descripción...">${libro.descripcion || ''}</textarea>
    </div>
  `;
}

function recogerDatosLibro() {
  const autorSelect = document.getElementById('f-autor');
  const autorOption = autorSelect?.options[autorSelect.selectedIndex];
  const autorId = autorOption?.value || '';

  let autor = null;
  if (autorId) {
    autor = {
      autor_id: autorId,
      name: autorOption?.dataset.name || '',
      nacionalidad: autorOption?.dataset.nacionalidad || '',
    };
  }

  return {
    titulo:      document.getElementById('f-titulo')?.value.trim(),
    autor:       autor,
    genero:      document.getElementById('f-genero')?.value,
    editorial:   document.getElementById('f-editorial')?.value.trim() || undefined,
    anio:        document.getElementById('f-anio')?.value
                   ? parseInt(document.getElementById('f-anio').value) : undefined,
    idioma:      document.getElementById('f-idioma')?.value,
    formato:     document.getElementById('f-formato')?.value,
    disponible:  document.getElementById('f-disponible')?.value === 'true',
    descripcion: document.getElementById('f-descripcion')?.value.trim() || undefined,
  };
}

async function abrirCrearLibro() {
  modal.open('Nuevo Libro', '<div class="loader visible" style="margin:2rem auto"></div>', () => {});
  const formHTML = await formLibroHTML();
  document.getElementById('modal-body').innerHTML = formHTML;

  const submitBtn = document.getElementById('modal-submit');
  const newBtn = submitBtn.cloneNode(true);
  submitBtn.replaceWith(newBtn);

  newBtn.addEventListener('click', async () => {
    const datos = recogerDatosLibro();
    if (!datos.titulo || !datos.autor || !datos.genero) {
      showToast('Título, autor y género son obligatorios.', 'warning');
      return;
    }
    try {
      await librosAPI.create(datos);
      showToast('Libro creado exitosamente.', 'success');
      modal.close();
      cargarLibros();
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    }
  });
}

async function abrirEditarLibro(id) {
  try {
    const libro = await librosAPI.getById(id);
    modal.open('Editar Libro', '<div class="loader visible" style="margin:2rem auto"></div>', () => {});
    const formHTML = await formLibroHTML(libro);
    document.getElementById('modal-body').innerHTML = formHTML;

    const submitBtn = document.getElementById('modal-submit');
    const newBtn = submitBtn.cloneNode(true);
    submitBtn.replaceWith(newBtn);

    newBtn.addEventListener('click', async () => {
      const datos = recogerDatosLibro();
      try {
        await librosAPI.update(id, datos);
        showToast('Libro actualizado.', 'success');
        modal.close();
        cargarLibros();
      } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
      }
    });
  } catch (err) {
    showToast(`Error al cargar libro: ${err.message}`, 'error');
  }
}

/* ── Inicialización ───────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  // Botón crear
  document.getElementById('libros-btn-crear')?.addEventListener('click', abrirCrearLibro);

  // Filtros con debounce
  let debounceTimer;
  function filtrarLibros() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(cargarLibros, 350);
  }

  document.getElementById('libros-search')?.addEventListener('input', filtrarLibros);
  document.getElementById('libros-filter-genero')?.addEventListener('change', cargarLibros);
  document.getElementById('libros-filter-disponible')?.addEventListener('change', cargarLibros);

  // Registrar en el router
  registerLoader('/libros', cargarLibros);
});
