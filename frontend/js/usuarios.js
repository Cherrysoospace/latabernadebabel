/**
 * usuarios.js — CRUD completo para la colección 'usuarios'.
 */

/* ── Cargar y renderizar ──────────────────────────────────────────── */

async function cargarUsuarios() {
  showLoader('usuarios-loader');
  hideEmpty('usuarios-empty');

  const params = {};
  const membresia = document.getElementById('usuarios-filter-membresia')?.value;
  const activo    = document.getElementById('usuarios-filter-activo')?.value;

  if (membresia) params.membresia = membresia;
  if (activo)    params.activo    = activo;

  try {
    const data = await usuariosAPI.getAll(params);
    const usuarios = Array.isArray(data) ? data : (data.usuarios || []);
    renderTablaUsuarios(usuarios);
  } catch (err) {
    showToast(`Error al cargar usuarios: ${err.message}`, 'error');
    renderTablaUsuarios([]);
  } finally {
    hideLoader('usuarios-loader');
  }
}

function renderTablaUsuarios(usuarios) {
  const tbody = document.getElementById('usuarios-tbody');
  if (!tbody) return;

  if (!usuarios.length) {
    tbody.innerHTML = '';
    showEmpty('usuarios-empty');
    return;
  }

  hideEmpty('usuarios-empty');
  tbody.innerHTML = usuarios.map(u => `
    <tr>
      <td>${u.nombre || '—'}</td>
      <td style="color:var(--text-secondary);font-size:0.82rem">${u.correo || '—'}</td>
      <td>${membresiaBadge(u.membresia)}</td>
      <td>${u.activo ? badgeHTML('Activo','success') : badgeHTML('Inactivo','danger')}</td>
      <td style="color:var(--text-muted)">${formatDate(u.fecha_registro)}</td>
      <td>
        <div class="td-actions">
          <button class="btn btn-sm btn-secondary" onclick="abrirEditarUsuario('${u._id}')">Editar</button>
          ${u.activo
            ? `<button class="btn btn-sm btn-warning" onclick="desactivarUsuario('${u._id}', '${(u.nombre||'').replace(/'/g,"\\'")}')">Desactivar</button>`
            : ''}
          <button class="btn btn-sm btn-danger" onclick="eliminarUsuario('${u._id}', '${(u.nombre||'').replace(/'/g,"\\'")}')">Eliminar</button>
        </div>
      </td>
    </tr>
  `).join('');
}

/* ── Desactivar ───────────────────────────────────────────────────── */

async function desactivarUsuario(id, nombre) {
  confirmAction(
    `¿Desactivar la cuenta de "${nombre}"?`,
    async () => {
      try {
        await usuariosAPI.desactivar(id);
        showToast(`Usuario "${nombre}" desactivado.`, 'success');
        cargarUsuarios();
      } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
      }
    }
  );
}

/* ── Eliminar ─────────────────────────────────────────────────────── */

function eliminarUsuario(id, nombre) {
  confirmAction(
    `¿Eliminar permanentemente al usuario "${nombre}"?`,
    async () => {
      try {
        await usuariosAPI.delete(id);
        showToast(`Usuario "${nombre}" eliminado.`, 'success');
        cargarUsuarios();
      } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
      }
    }
  );
}

/* ── Formulario ───────────────────────────────────────────────────── */

function formUsuarioHTML(u = {}) {
  return `
    <div class="form-row">
      <div class="form-group">
        <label class="form-label" for="u-nombre">Nombre *</label>
        <input class="input-field" id="u-nombre" type="text" placeholder="Nombre completo" value="${u.nombre || ''}" required />
      </div>
      <div class="form-group">
        <label class="form-label" for="u-correo">Correo *</label>
        <input class="input-field" id="u-correo" type="email" placeholder="correo@ejemplo.com" value="${u.correo || ''}" required />
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label class="form-label" for="u-membresia">Membresía</label>
        <select class="input-field input-select" id="u-membresia">
          <option value="basica"     ${(u.membresia||'basica')==='basica'    ?'selected':''}>Básica</option>
          <option value="premium"    ${u.membresia==='premium'               ?'selected':''}>Premium</option>
          <option value="estudiante" ${u.membresia==='estudiante'            ?'selected':''}>Estudiante</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label" for="u-activo">Estado</label>
        <select class="input-field input-select" id="u-activo">
          <option value="true"  ${u.activo !== false ? 'selected' : ''}>Activo</option>
          <option value="false" ${u.activo === false  ? 'selected' : ''}>Inactivo</option>
        </select>
      </div>
    </div>

    <div class="form-group">
      <label class="form-label" for="u-preferencias">Géneros preferidos</label>
      <input class="input-field" id="u-preferencias" type="text"
             placeholder="Ej: ficcion, terror, poesia (separados por coma)"
             value="${(u.preferencias || []).join(', ')}" />
      <small style="color:var(--text-muted);font-size:0.75rem">Separa los géneros con comas.</small>
    </div>
  `;
}

function recogerDatosUsuario() {
  const prefStr = document.getElementById('u-preferencias')?.value || '';
  const preferencias = prefStr.split(',').map(p => p.trim().toLowerCase()).filter(Boolean);
  return {
    nombre:       document.getElementById('u-nombre')?.value.trim(),
    correo:       document.getElementById('u-correo')?.value.trim(),
    membresia:    document.getElementById('u-membresia')?.value,
    activo:       document.getElementById('u-activo')?.value === 'true',
    preferencias,
  };
}

function abrirCrearUsuario() {
  modal.open(
    'Nuevo Usuario',
    formUsuarioHTML(),
    async () => {
      const datos = recogerDatosUsuario();
      if (!datos.nombre || !datos.correo) {
        showToast('Nombre y correo son obligatorios.', 'warning');
        return;
      }
      try {
        await usuariosAPI.create(datos);
        showToast('Usuario creado exitosamente.', 'success');
        modal.close();
        cargarUsuarios();
      } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
      }
    }
  );
}

async function abrirEditarUsuario(id) {
  try {
    const u = await usuariosAPI.getById(id);
    modal.open(
      'Editar Usuario',
      formUsuarioHTML(u),
      async () => {
        const datos = recogerDatosUsuario();
        try {
          await usuariosAPI.update(id, datos);
          showToast('Usuario actualizado.', 'success');
          modal.close();
          cargarUsuarios();
        } catch (err) {
          showToast(`Error: ${err.message}`, 'error');
        }
      }
    );
  } catch (err) {
    showToast(`Error al cargar usuario: ${err.message}`, 'error');
  }
}

/* ── Inicialización ───────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('usuarios-btn-crear')?.addEventListener('click', abrirCrearUsuario);
  document.getElementById('usuarios-filter-membresia')?.addEventListener('change', cargarUsuarios);
  document.getElementById('usuarios-filter-activo')?.addEventListener('change', cargarUsuarios);

  registerLoader('/usuarios', cargarUsuarios);
});
