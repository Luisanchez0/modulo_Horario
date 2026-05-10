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
  const rolSesion = (usuarioSesion?.rol || 'DOCENTE').toUpperCase()
  const nombreSesion = usuarioSesion?.nombre || usuarioSesion?.sub || usuarioSesion?.correo || 'Usuario SIAE'
  const claveSesion = usuarioSesion?.matricula || usuarioSesion?.id || rolSesion

  return (
    <main className="edu-app">
      <div className="shell">
        <aside className="sidebar">
          <div className="brand">
            <span className="brand__primary">SIAE UNACH</span>
            <span>Gestion Administrativa</span>
          </div>

          <div className="sidebar__user">
            <span>Bienvenido(a),</span>
            <strong>{nombreSesion}</strong>
            <small>{claveSesion}</small>
          </div>

          <p className="sidebar__section">Menu {rolSesion === 'ADMIN' ? 'Administrador' : 'Docente'}</p>

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

          <button type="button" className="sidebar__logout" onClick={cerrarSesion}>
            <span aria-hidden="true">←</span>
            Cerrar Sesion
          </button>
        </aside>

        <section className="content">
          <div className="content__bar">
            <div>
              <p className="breadcrumb">SIAE UNACH - {dashboardSubtitle}</p>
              <h1>{dashboardTitle}</h1>
            </div>
            <div className="content__actions">
              <button type="button" onClick={cargarDatos} disabled={loading}>
                {loading ? 'Actualizando...' : 'Actualizar'}
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
