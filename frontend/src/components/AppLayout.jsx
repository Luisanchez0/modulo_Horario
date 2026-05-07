import { NavLink } from 'react-router-dom'
import Modal from './Modal'
import { useEffect, useState } from 'react'

function AppLayout({
  usuarioSesion,
  moduleLinks,
  dashboardTitle,
  dashboardSubtitle,
  cargarDatos,
  loading,
  cerrarSesion,
  mensaje,
  error,
  clearError,
  clearMensaje,
  children,
}) {
  const [showToast, setShowToast] = useState(false)

  useEffect(() => {
    if (mensaje) {
      const showTimer = setTimeout(() => {
        setShowToast(true)
      }, 0)
      const t = setTimeout(() => {
        setShowToast(false)
        if (typeof clearMensaje === 'function') clearMensaje()
      }, 4000)
      return () => {
        clearTimeout(showTimer)
        clearTimeout(t)
      }
    }
    return undefined
  }, [mensaje, clearMensaje])
  return (
    <main className="edu-app">
      <header className="topbar">
        <div className="brand">
          <span className="brand__primary">SISTEMA</span>
          <span>ESCOLAR</span>
        </div>
        <div className="topbar__user">
          <span>Usuario</span>
          <strong>{usuarioSesion?.rol ?? 'N/D'}</strong>
          <span
            className={`role-badge ${(usuarioSesion?.rol || '').toUpperCase() === 'ADMIN' ? 'role-badge--admin' : 'role-badge--docente'}`}
          >
            {(usuarioSesion?.rol || 'DOCENTE').toUpperCase()}
          </span>
        </div>
      </header>

      <div className="shell">
        <aside className="sidebar">
          <div className="sidebar__search">Buscar</div>
          <nav className="module-nav" aria-label="Navegacion por modulos">
            {moduleLinks.map((module) => (
              <NavLink
                key={module.path}
                to={module.path}
                className={({ isActive }) => (isActive ? 'active' : '')}
              >
                <span className="module-nav__icon" aria-hidden="true">
                  {module.icon}
                </span>
                {module.label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <section className="content">
          <div className="content__bar">
            <div>
              <p className="breadcrumb">Inicio / {dashboardSubtitle}</p>
              <h1>{dashboardTitle}</h1>
            </div>
            <div className="content__actions">
              <button type="button" onClick={cargarDatos} disabled={loading}>
                {loading ? 'Actualizando...' : 'Actualizar'}
              </button>
              <button type="button" className="button-alt" onClick={cerrarSesion}>
                Salir
              </button>
            </div>
          </div>

          

          {error && (
            <Modal title="Se produjo un error" titleId="error-modal-title" onClose={clearError} actions={<>
              <button className="btn btn--primary" type="button" onClick={clearError}>Entendido</button>
            </>}>
              <p>{error}</p>
            </Modal>
          )}

          {children}
        </section>
      </div>
      {showToast && mensaje && (
        <div className="toast-container" role="status" aria-live="polite">
          <div className="toast toast--success" onClick={() => { setShowToast(false); clearMensaje && clearMensaje(); }}>
            {mensaje}
          </div>
        </div>
      )}
    </main>
  )
}

export default AppLayout
