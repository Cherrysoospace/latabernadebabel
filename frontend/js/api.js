/**
 * api.js — Capa de acceso al backend Flask.
 * Proporciona un objeto API con métodos por cada colección.
 * Todos los métodos retornan la respuesta parseada como JSON o lanzan un Error.
 */

const BASE_URL = 'http://localhost:5000/api';

/** Wrapper genérico de fetch con manejo de errores centralizado */
async function request(url, options = {}) {
  const defaultHeaders = { 'Content-Type': 'application/json' };
  const config = {
    ...options,
    headers: { ...defaultHeaders, ...options.headers },
  };

  const response = await fetch(url, config);

  // Intentar parsear como JSON siempre
  let data;
  try {
    data = await response.json();
  } catch (_) {
    data = null;
  }

  if (!response.ok) {
    // Extraer el mensaje de error del cuerpo JSON si existe
    const msg = data?.error || data?.mensaje || `Error HTTP ${response.status}`;
    throw new Error(msg);
  }

  return data;
}

/* ══════════════════════════════════════════════════════════════════
   API de LIBROS
══════════════════════════════════════════════════════════════════ */
const librosAPI = {
  /** GET /api/libros — lista paginada. Acepta ?q=, ?genero=, ?disponible=true */
  getAll(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return request(`${BASE_URL}/libros/${qs ? '?' + qs : ''}`);
  },

  /** GET /api/libros/:id */
  getById(id) {
    return request(`${BASE_URL}/libros/${id}`);
  },

  /** POST /api/libros */
  create(data) {
    return request(`${BASE_URL}/libros/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /** PUT /api/libros/:id */
  update(id, data) {
    return request(`${BASE_URL}/libros/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /** PATCH /api/libros/:id/disponibilidad */
  cambiarDisponibilidad(id, disponible) {
    return request(`${BASE_URL}/libros/${id}/disponibilidad`, {
      method: 'PATCH',
      body: JSON.stringify({ disponible }),
    });
  },

  /** DELETE /api/libros/:id */
  delete(id) {
    return request(`${BASE_URL}/libros/${id}`, { method: 'DELETE' });
  },
};

/* ══════════════════════════════════════════════════════════════════
   API de USUARIOS
══════════════════════════════════════════════════════════════════ */
const usuariosAPI = {
  /** GET /api/usuarios — lista paginada. Acepta ?membresia=, ?activo=true */
  getAll(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return request(`${BASE_URL}/usuarios/${qs ? '?' + qs : ''}`);
  },

  /** GET /api/usuarios/:id */
  getById(id) {
    return request(`${BASE_URL}/usuarios/${id}`);
  },

  /** POST /api/usuarios */
  create(data) {
    return request(`${BASE_URL}/usuarios/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /** PUT /api/usuarios/:id */
  update(id, data) {
    return request(`${BASE_URL}/usuarios/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /** DELETE /api/usuarios/:id */
  delete(id) {
    return request(`${BASE_URL}/usuarios/${id}`, { method: 'DELETE' });
  },

  /** PATCH /api/usuarios/:id/desactivar */
  desactivar(id) {
    return request(`${BASE_URL}/usuarios/${id}/desactivar`, { method: 'PATCH' });
  },
};

/* ══════════════════════════════════════════════════════════════════
   API de PRÉSTAMOS
══════════════════════════════════════════════════════════════════ */
const prestamosAPI = {
  /** GET /api/prestamos — lista paginada. Acepta ?estado= */
  getAll(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return request(`${BASE_URL}/prestamos/${qs ? '?' + qs : ''}`);
  },

  /** GET /api/prestamos/:id */
  getById(id) {
    return request(`${BASE_URL}/prestamos/${id}`);
  },

  /** POST /api/prestamos */
  create(data) {
    return request(`${BASE_URL}/prestamos/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /** PATCH /api/prestamos/:id/devolver */
  devolver(id) {
    return request(`${BASE_URL}/prestamos/${id}/devolver`, { method: 'PATCH' });
  },

  /** DELETE /api/prestamos/:id */
  delete(id) {
    return request(`${BASE_URL}/prestamos/${id}`, { method: 'DELETE' });
  },
};

/* ══════════════════════════════════════════════════════════════════
   API de RESEÑAS
══════════════════════════════════════════════════════════════════ */
const resenasAPI = {
  /** GET /api/resenas — lista paginada. Acepta ?min_calificacion= */
  getAll(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return request(`${BASE_URL}/resenas/${qs ? '?' + qs : ''}`);
  },

  /** GET /api/resenas/:id */
  getById(id) {
    return request(`${BASE_URL}/resenas/${id}`);
  },

  /** POST /api/resenas */
  create(data) {
    return request(`${BASE_URL}/resenas/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /** PUT /api/resenas/:id */
  update(id, data) {
    return request(`${BASE_URL}/resenas/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /** DELETE /api/resenas/:id */
  delete(id) {
    return request(`${BASE_URL}/resenas/${id}`, { method: 'DELETE' });
  },
};

/* ══════════════════════════════════════════════════════════════════
   API de AUTORES
══════════════════════════════════════════════════════════════════ */
const autoresAPI = {
  /** GET /api/autores — lista paginada. Acepta ?q= */
  getAll(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return request(`${BASE_URL}/autores/${qs ? '?' + qs : ''}`);
  },

  /** GET /api/autores/:id */
  getById(id) {
    return request(`${BASE_URL}/autores/${id}`);
  },

  /** POST /api/autores */
  create(data) {
    return request(`${BASE_URL}/autores/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /** PUT /api/autores/:id */
  update(id, data) {
    return request(`${BASE_URL}/autores/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /** DELETE /api/autores/:id */
  delete(id) {
    return request(`${BASE_URL}/autores/${id}`, { method: 'DELETE' });
  },
};
