import { useMemo, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

function ActivationPage({ activarCuenta }) {
  const location = useLocation()
  const navigate = useNavigate()
  const token = useMemo(() => new URLSearchParams(location.search).get('token') || '', [location.search])
  const [form, setForm] = useState({ password: '', confirm: '' })
  const [status, setStatus] = useState({ loading: false, error: '', success: '' })

  const handleSubmit = async (event) => {
    event.preventDefault()
    setStatus({ loading: true, error: '', success: '' })

    if (!token) {
      setStatus({ loading: false, error: 'No se encontro el token de activacion.', success: '' })
      return
    }

    if (form.password !== form.confirm) {
      setStatus({ loading: false, error: 'Las contrasenas no coinciden.', success: '' })
      return
    }

    try {
      await activarCuenta(token, form.password)
      setForm({ password: '', confirm: '' })
      setStatus({ loading: false, error: '', success: 'Cuenta activada. Ya puedes iniciar sesion.' })
    } catch (error) {
      setStatus({ loading: false, error: error.message || 'No se pudo activar la cuenta.', success: '' })
    }
  }

  return (
    <main className="edu-app auth-page">
      <section className="auth-split">
        <aside className="auth-split__left">
          <div className="auth-split__content">
            <h1>SISTEMA DE GESTION ACADEMICA</h1>
            <p>Universidad Autonoma de Chiapas</p>
            <div className="auth-split__divider"></div>
            <em>"Por la conciencia de la necesidad de servir"</em>
          </div>
        </aside>

        <section className="auth-split__right">
          <div className="auth-logo">
            <img src="/logo_azul_unach.png" alt="Logo UNACH" />
          </div>

          <h2 className="auth-split__title">Activar cuenta</h2>
          <p className="auth-split__subtitle">Crea tu nueva contrasena para el modulo de horarios</p>

          <section className="auth-card">
            <div className="hero__badge">Activacion</div>
            <h3>Crear contrasena</h3>
            <p>La contrasena debe tener al menos 8 caracteres, incluir letras y numeros.</p>

            {status.error && (
              <section className="feedback auth-feedback">
                <p className="feedback__error">{status.error}</p>
              </section>
            )}

            {status.success && (
              <section className="feedback auth-feedback">
                <p className="feedback__ok">{status.success}</p>
              </section>
            )}

            <form onSubmit={handleSubmit} className="form auth-form">
              <label>
                Nueva contrasena
                <input
                  type="password"
                  value={form.password}
                  onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
                  required
                  minLength={8}
                />
              </label>
              <label>
                Confirmar contrasena
                <input
                  type="password"
                  value={form.confirm}
                  onChange={(e) => setForm((prev) => ({ ...prev, confirm: e.target.value }))}
                  required
                  minLength={8}
                />
              </label>
              <button type="submit" disabled={status.loading}>
                {status.loading ? 'Activando...' : 'Activar cuenta'}
              </button>
            </form>

            <button type="button" className="auth-switch" onClick={() => navigate('/login')}>
              Ir a iniciar sesion
            </button>
            <p style={{ marginTop: '0.75rem' }}>
              <Link to="/login">Ya tienes cuenta? Inicia sesion</Link>
            </p>
          </section>
        </section>
      </section>
    </main>
  )
}

export default ActivationPage
