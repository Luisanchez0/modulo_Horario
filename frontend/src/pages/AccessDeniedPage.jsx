import { Link, useLocation } from 'react-router-dom'

function AccessDeniedPage() {
  const location = useLocation()
  const from = location.state?.from || 'recurso solicitado'
  const requiredRoles = Array.isArray(location.state?.requiredRoles)
    ? location.state.requiredRoles.join(', ')
    : 'ADMIN'

  return (
    <section className="catalogs single">
      <article className="card access-denied">
        <h3>Acceso denegado</h3>
        <p>
          No tienes permisos para abrir <strong>{from}</strong>.
        </p>
        <p>
          Esta seccion requiere el rol: <strong>{requiredRoles}</strong>.
        </p>
        <div className="content__actions">
          <Link to="/dashboard" className="inline-link-button">
            Volver al dashboard
          </Link>
          <Link to="/horarios" className="inline-link-button button-alt-link">
            Ir a mis horarios
          </Link>
        </div>
      </article>
    </section>
  )
}

export default AccessDeniedPage
