import { Navigate, Outlet, useLocation } from 'react-router-dom'

function ProtectedRoute({ isAuthenticated, userRole, allowedRoles = [] }) {
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(userRole)) {
    return (
      <Navigate
        to="/acceso-denegado"
        replace
        state={{ from: location.pathname, requiredRoles: allowedRoles }}
      />
    )
  }

  return <Outlet />
}

export default ProtectedRoute
