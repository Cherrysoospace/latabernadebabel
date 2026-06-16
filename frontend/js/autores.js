/**
 * autores.js — CRUD completo para la colección 'autores'.
 */

/* ── Cargar y renderizar ──────────────────────────────────────────── */

async function cargarAutores() {
  showLoader('autores-loader');
  hideEmpty('autores-empty');

  const params = {};
  const q = document.getElementById('autores-search')?.value.trim();
  if (q) params.q = q;

  try {
    const data = await autoresAPI.getAll(params);
    const autores = Array.isArray(data) ? data : (data.autores || []);
    renderTablaAutores(autores);
  } catch (err) {
    showToast(`Error al cargar autores: ${err.message}`, 'error');
    renderTablaAutores([]);
  } finally {
    hideLoader('autores-loader');
  }
}

function renderTablaAutores(autores) {
  const tbody = document.getElementById('autores-tbody');
  if (!tbody) return;

  if (!autores.length) {
    tbody.innerHTML = '';
    showEmpty('autores-empty');
    return;
  }

  hideEmpty('autores-empty');
  tbody.innerHTML = autores.map(a => {
    // obras y premios pueden ser arrays de strings
    const obras   = Array.isArray(a.obras)   ? a.obras.join(', ')   : (a.obras   || '—');
    const premios = Array.isArray(a.premios) ? a.premios.join(', ') : (a.premios || '—');
    return `
      <tr>
        <td><strong>${a.nombre || '—'}</strong></td>
        <td>${a.nacionalidad || '—'}</td>
        <td class="td-truncate" title="${obras}">${truncate(obras, 50)}</td>
        <td class="td-truncate" title="${premios}">${truncate(premios, 50)}</td>
        <td>
          <div class="td-actions">
            <button class="btn btn-sm btn-secondary" onclick="abrirEditarAutor('${a._id}')">Editar</button>
            <button class="btn btn-sm btn-danger"    onclick="eliminarAutor('${a._id}', '${(a.nombre||'').replace(/'/g,"\\'")}')">Eliminar</button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

/* ── Eliminar ─────────────────────────────────────────────────────── */

function eliminarAutor(id, nombre) {
  confirmAction(
    `¿Eliminar al autor "${nombre}"? Esta acción no se puede deshacer.`,
    async () => {
      try {
        await autoresAPI.delete(id);
        showToast(`Autor "${nombre}" eliminado.`, 'success');
        cargarAutores();
      } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
      }
    }
  );
}

/* ── Formulario ───────────────────────────────────────────────────── */

function formAutorHTML(a = {}) {
  const obras   = Array.isArray(a.obras)   ? a.obras.join(', ')   : (a.obras   || '');
  const premios = Array.isArray(a.premios) ? a.premios.join(', ') : (a.premios || '');

  return `
    <div class="form-row">
      <div class="form-group">
        <label class="form-label" for="a-nombre">Nombre *</label>
        <input class="input-field" id="a-nombre" type="text" placeholder="Nombre completo" value="${a.nombre || ''}" required />
      </div>
      <div class="form-group">
        <label class="form-label" for="a-nacionalidad">Nacionalidad</label>
        <input class="input-field" id="a-nacionalidad" type="text" placeholder="Ej. Colombiano" value="${a.nacionalidad || ''}" />
      </div>
    </div>

    <div class="form-group">
      <label class="form-label" for="a-biografia">Biografía</label>
      <textarea class="input-field input-textarea" id="a-biografia"
                placeholder="Breve descripción del autor…">${a.biografia || ''}</textarea>
    </div>

    <div class="form-group">
      <label class="form-label" for="a-obras">Obras principales</label>
      <input class="input-field" id="a-obras" type="text"
             placeholder="Ej: El amor en los tiempos del cólera, Cien años de soledad"
             value="${obras}" />
      <small style="color:var(--text-muted);font-size:0.75rem">Separa las obras con comas.</small>
    </div>

    <div class="form-group">
      <label class="form-label" for="a-premios">Premios</label>
      <input class="input-field" id="a-premios" type="text"
             placeholder="Ej: Premio Nobel de Literatura 1982"
             value="${premios}" />
      <small style="color:var(--text-muted);font-size:0.75rem">Separa los premios con comas.</small>
    </div>
  `;
}

function recogerDatosAutor() {
  const obrasStr   = document.getElementById('a-obras')?.value   || '';
  const premiosStr = document.getElementById('a-premios')?.value || '';

  return {
    nombre:       document.getElementById('a-nombre')?.value.trim(),
    nacionalidad: document.getElementById('a-nacionalidad')?.value.trim() || undefined,
    biografia:    document.getElementById('a-biografia')?.value.trim()    || undefined,
    obras:   obrasStr.split(',').map(o => o.trim()).filter(Boolean),
    premios: premiosStr.split(',').map(p => p.trim()).filter(Boolean),
  };
}

function abrirCrearAutor() {
  modal.open(
    'Nuevo Autor',
    formAutorHTML(),
    async () => {
      const datos = recogerDatosAutor();
      if (!datos.nombre) {
        showToast('El nombre del autor es obligatorio.', 'warning');
        return;
      }
      try {
        await autoresAPI.create(datos);
        showToast('Autor creado exitosamente.', 'success');
        modal.close();
        cargarAutores();
      } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
      }
    }
  );
}

async function abrirEditarAutor(id) {
  try {
    const a = await autoresAPI.getById(id);
    modal.open(
      'Editar Autor',
      formAutorHTML(a),
      async () => {
        const datos = recogerDatosAutor();
        if (!datos.nombre) {
          showToast('El nombre del autor es obligatorio.', 'warning');
          return;
        }
        try {
          await autoresAPI.update(id, datos);
          showToast('Autor actualizado.', 'success');
          modal.close();
          cargarAutores();
        } catch (err) {
          showToast(`Error: ${err.message}`, 'error');
        }
      }
    );
  } catch (err) {
    showToast(`Error al cargar autor: ${err.message}`, 'error');
  }
}

/* ── Inicialización ───────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('autores-btn-crear')?.addEventListener('click', abrirCrearAutor);

  let debounceTimer;
  document.getElementById('autores-search')?.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(cargarAutores, 350);
  });

  registerLoader('/autores', cargarAutores);
});
