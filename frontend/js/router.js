/**
 * router.js — Enrutador SPA basado en hash (#/seccion).
 * Controla qué sección se muestra y qué enlace del sidebar está activo.
 */

const ROUTES = {
  '/libros':   { sectionId: 'section-libros',    navId: 'nav-libros',    title: 'Libros',    subtitle: 'Gestión del catálogo' },
  '/usuarios': { sectionId: 'section-usuarios',  navId: 'nav-usuarios',  title: 'Usuarios',  subtitle: 'Gestión de cuentas' },
  '/prestamos':{ sectionId: 'section-prestamos', navId: 'nav-prestamos', title: 'Préstamos', subtitle: 'Control de préstamos' },
  '/resenas':  { sectionId: 'section-resenas',   navId: 'nav-resenas',   title: 'Reseñas',   subtitle: 'Gestión de reseñas' },
  '/autores':  { sectionId: 'section-autores',   navId: 'nav-autores',   title: 'Autores',   subtitle: 'Gestión de autores' },
  '/nosql':    { sectionId: 'section-nosql',     navId: 'nav-nosql',     title: 'Consultas NoSQL', subtitle: 'Ejecuta comandos mongosh directamente' },
};

// Sección por defecto al abrir la app
const DEFAULT_ROUTE = '/libros';

/**
 * Aplica la ruta actual: muestra la sección correspondiente,
 * activa el enlace del sidebar y actualiza el topbar.
 */
function applyRoute() {
  const hash  = window.location.hash.replace('#', '') || DEFAULT_ROUTE;
  const route = ROUTES[hash] || ROUTES[DEFAULT_ROUTE];

  // Ocultar todas las secciones
  document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));

  // Mostrar la sección activa
  const section = document.getElementById(route.sectionId);
  if (section) section.classList.remove('hidden');

  // Desactivar todos los links del sidebar
  document.querySelectorAll('.sidebar-nav-link').forEach(a => a.classList.remove('active'));

  // Activar el link correspondiente
  const navLink = document.getElementById(route.navId);
  if (navLink) navLink.classList.add('active');

  // Actualizar el topbar
  const topbarTitle    = document.getElementById('topbar-title');
  const topbarSubtitle = document.getElementById('topbar-subtitle');
  if (topbarTitle)    topbarTitle.textContent    = route.title;
  if (topbarSubtitle) topbarSubtitle.textContent = route.subtitle;

  // Cargar los datos de la sección si tiene un loader registrado
  if (sectionLoaders[hash]) {
    sectionLoaders[hash]();
  }
}

/**
 * Registro de funciones de carga por ruta.
 * Cada módulo (libros.js, etc.) registra aquí su función de inicialización.
 * Esto desacopla el router de la lógica de negocio.
 */
const sectionLoaders = {};

function registerLoader(route, fn) {
  sectionLoaders[route] = fn;
}

// Escuchar cambios de hash
window.addEventListener('hashchange', applyRoute);

// Aplicar ruta al cargar la página
document.addEventListener('DOMContentLoaded', applyRoute);
