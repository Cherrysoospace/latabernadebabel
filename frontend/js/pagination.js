/**
 * pagination.js — Módulo reutilizable de paginación del lado del cliente.
 *
 * Cada colección mantiene su propio estado de paginación a través de
 * un objeto PaginationState que se pasa a las funciones de este módulo.
 *
 * Uso típico:
 *   1. Crear un estado: const pag = createPaginationState(25);
 *   2. Al recibir datos: updatePaginationState(pag, total);
 *   3. Renderizar: renderPaginacion(containerId, pag, callbackIrAPagina);
 */

const PAGE_SIZE_DEFAULT = 25;

/* ── Crear / actualizar estado ───────────────────────────────────── */

/**
 * Crea un objeto de estado de paginación.
 * @param {number} pageSize  — Documentos por página.
 * @returns {{ page: number, pageSize: number, total: number, totalPages: number }}
 */
function createPaginationState(pageSize = PAGE_SIZE_DEFAULT) {
  return { page: 1, pageSize, total: 0, totalPages: 0 };
}

/**
 * Actualiza el estado de paginación con el total recibido del backend.
 * @param {{ page, pageSize, total, totalPages }} state
 * @param {number} total  — Total de documentos en la colección.
 */
function updatePaginationState(state, total) {
  state.total      = total;
  state.totalPages = Math.max(1, Math.ceil(total / state.pageSize));
  // Asegurar que la página actual no supere el total de páginas
  if (state.page > state.totalPages) state.page = state.totalPages;
}

/**
 * Retorna los parámetros `skip` y `limit` para la petición al backend.
 * @param {{ page, pageSize }} state
 * @returns {{ skip: number, limit: number }}
 */
function getPaginationParams(state) {
  return {
    skip:  (state.page - 1) * state.pageSize,
    limit: state.pageSize,
  };
}

/* ── Renderizar controles ────────────────────────────────────────── */

/**
 * Renderiza los controles de paginación dentro del elemento con el id dado.
 * @param {string}   containerId — ID del elemento contenedor.
 * @param {object}   state       — Estado de paginación.
 * @param {function} onPageChange — Callback que recibe la nueva página (number).
 */
function renderPaginacion(containerId, state, onPageChange) {
  const container = document.getElementById(containerId);
  if (!container) return;

  // Si sólo hay una página (o ningún dato), ocultar el paginador
  if (state.totalPages <= 1 && state.total === 0) {
    container.innerHTML = '';
    return;
  }

  const { page, totalPages, total, pageSize } = state;
  const desde = Math.min((page - 1) * pageSize + 1, total);
  const hasta  = Math.min(page * pageSize, total);

  // Construir botones de páginas numeradas (ventana de ±2 alrededor de la actual)
  const pagesHTML = _buildPageButtons(page, totalPages, onPageChange);

  container.innerHTML = `
    <div class="pagination-wrapper">
      <span class="pagination-info">
        Mostrando <strong>${desde}</strong>–<strong>${hasta}</strong> de <strong>${total}</strong> registros
      </span>
      <nav class="pagination-nav" aria-label="Paginación">
        <button class="pagination-btn"
                id="${containerId}-prev"
                ${page <= 1 ? 'disabled' : ''}
                onclick="(${onPageChange.toString()})(${page - 1})"
                aria-label="Página anterior">
          ‹
        </button>
        ${pagesHTML}
        <button class="pagination-btn"
                id="${containerId}-next"
                ${page >= totalPages ? 'disabled' : ''}
                onclick="(${onPageChange.toString()})(${page + 1})"
                aria-label="Página siguiente">
          ›
        </button>
      </nav>
    </div>
  `;
}

/**
 * Construye el HTML de los botones de número de página.
 * Muestra: [1] ... [page-2] [page-1] [page] [page+1] [page+2] ... [totalPages]
 * @private
 */
function _buildPageButtons(current, totalPages, onPageChange) {
  if (totalPages <= 1) return '';

  const fnStr = onPageChange.toString();
  const pages = _getPageNumbers(current, totalPages);
  let html = '';

  pages.forEach(p => {
    if (p === '…') {
      html += `<span class="pagination-ellipsis">…</span>`;
    } else {
      const active = p === current ? 'active' : '';
      html += `<button class="pagination-btn ${active}" onclick="(${fnStr})(${p})" aria-label="Página ${p}" ${p === current ? 'aria-current="page"' : ''}>${p}</button>`;
    }
  });

  return html;
}

/**
 * Genera el array de páginas a mostrar, con '…' como separador.
 * @private
 */
function _getPageNumbers(current, total) {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  const pages = [];
  const delta = 2;
  const left  = current - delta;
  const right = current + delta + 1;

  let prev = null;
  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || (i >= left && i < right)) {
      if (prev !== null && i - prev > 1) pages.push('…');
      pages.push(i);
      prev = i;
    }
  }
  return pages;
}
