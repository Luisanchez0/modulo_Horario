import Modal from './Modal'

function AuthPage({
  isRegisterMode,
  alternarModoAuth,
  mensaje,
  error,
  clearError,
  loading,
  showPassword,
  setShowPassword,
  loginForm,
  setLoginForm,
  registerForm,
  setRegisterForm,
  iniciarSesion,
  crearUsuario,
}) {
  return (
    <main className="edu-app auth-page">
      <section className="auth-split">
        <aside className="auth-split__left">
          <div className="auth-split__content">
            <h1>SISTEMA DE GESTIÓN ACADÉMICA</h1>
            <p>Universidad Autónoma de Chiapas</p>
            <div className="auth-split__divider"></div>
            <em>"Por la conciencia de la necesidad de servir"</em>
          </div>
        </aside>

        <section className="auth-split__right">
          <div className="auth-logo">
            <img src="/logo_azul_unach.png" alt="Logo UNACH" />
          </div>

          <h2 className="auth-split__title">Módulo: Registro de Horarios</h2>
          <p className="auth-split__subtitle">Selecciona tu área de acceso</p>

          <details className="auth-card auth-card--accordion" open>
            <summary className="auth-card__summary">
              <div className="hero__badge">Iniciar sesión</div>
              <span className="auth-card__arrow">⌄</span>
            </summary>

            <div className="auth-card__content">
              {/*<h3>{isRegisterMode ? 'Crear usuario' : 'Iniciar sesión'}</h3>*/}

              <p>
                {isRegisterMode
                  ? 'Registra un usuario docente para ingresar al sistema.'
                  : 'Ingresa con tus credenciales para continuar.'}
              </p>

              {mensaje && (
                <section className="feedback auth-feedback">
                  <p className="feedback__ok">{mensaje}</p>
                </section>
              )}

              {error && (
                <Modal
                  title="Error de autenticación"
                  titleId="error-modal-title-auth"
                  onClose={clearError}
                  actions={
                    <button
                      className="btn btn--primary"
                      type="button"
                      onClick={clearError}
                    >
                      Entendido
                    </button>
                  }
                >
                  <p>{error}</p>
                </Modal>
              )}

              {!isRegisterMode ? (
                <form onSubmit={iniciarSesion} className="form auth-form">
                  <label>
                    Correo
                    <input
                      type="email"
                      value={loginForm.correo}
                      onChange={(e) =>
                        setLoginForm((prev) => ({
                          ...prev,
                          correo: e.target.value,
                        }))
                      }
                      required
                    />
                  </label>

                  <label>
                    Password

                    <span className="password-field">
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={loginForm.password}
                        onChange={(e) =>
                          setLoginForm((prev) => ({
                            ...prev,
                            password: e.target.value,
                          }))
                        }
                        required
                      />

                      <button
                        type="button"
                        className="password-toggle"
                        onClick={() => setShowPassword((prev) => !prev)}
                        aria-label={
                          showPassword
                            ? 'Ocultar contraseña'
                            : 'Ver contraseña'
                        }
                      >
                        {showPassword ? (
                          <svg
                            className="password-toggle__icon"
                            width="20"
                            height="20"
                            viewBox="0 0 24 24"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                            aria-hidden="true"
                          >
                            <path
                              d="M3 3l18 18"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />

                            <path
                              d="M10.58 10.58A3 3 0 0 0 13.42 13.42"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />

                            <path
                              d="M14.12 14.12C12.72 15.12 11.06 15.66 9.25 15.66C5.92 15.66 3 13.5 1.5 10.5C2.7 8 5.2 6 8.25 5"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>
                        ) : (
                          <svg
                            className="password-toggle__icon"
                            width="20"
                            height="20"
                            viewBox="0 0 24 24"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                            aria-hidden="true"
                          >
                            <path
                              d="M1.5 12C3 15 5.92 17.16 9.25 17.16C11.06 17.16 12.72 16.62 14.12 15.62"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />

                            <path
                              d="M21 12C19.5 9 16.58 6.84 13.25 6.84C11.44 6.84 9.78 7.38 8.38 8.38"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />

                            <circle
                              cx="12"
                              cy="12"
                              r="3"
                              stroke="currentColor"
                              strokeWidth="2"
                            />
                          </svg>
                        )}
                      </button>
                    </span>
                  </label>

                  <button type="submit" disabled={loading}>
                    {loading ? 'Validando...' : 'Entrar'}
                  </button>
                </form>
              ) : (
                <form onSubmit={crearUsuario} className="form auth-form">
                  <label>
                    Nombre
                    <input
                      value={registerForm.nombre}
                      onChange={(e) =>
                        setRegisterForm((prev) => ({
                          ...prev,
                          nombre: e.target.value,
                        }))
                      }
                      required
                    />
                  </label>

                  <label>
                    Correo
                    <input
                      type="email"
                      value={registerForm.correo}
                      onChange={(e) =>
                        setRegisterForm((prev) => ({
                          ...prev,
                          correo: e.target.value,
                        }))
                      }
                      required
                    />
                  </label>

                  <label>
                    Password

                    <span className="password-field">
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={registerForm.password}
                        onChange={(e) =>
                          setRegisterForm((prev) => ({
                            ...prev,
                            password: e.target.value,
                          }))
                        }
                        required
                      />

                      <button
                        type="button"
                        className="password-toggle"
                        onClick={() => setShowPassword((prev) => !prev)}
                        aria-label={
                          showPassword
                            ? 'Ocultar contraseña'
                            : 'Ver contraseña'
                        }
                      >
                        {showPassword ? (
                          <svg
                            className="password-toggle__icon"
                            width="20"
                            height="20"
                            viewBox="0 0 24 24"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                            aria-hidden="true"
                          >
                            <path
                              d="M3 3l18 18"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />

                            <path
                              d="M10.58 10.58A3 3 0 0 0 13.42 13.42"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />

                            <path
                              d="M14.12 14.12C12.72 15.12 11.06 15.66 9.25 15.66C5.92 15.66 3 13.5 1.5 10.5C2.7 8 5.2 6 8.25 5"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>
                        ) : (
                          <svg
                            className="password-toggle__icon"
                            width="20"
                            height="20"
                            viewBox="0 0 24 24"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                            aria-hidden="true"
                          >
                            <path
                              d="M1.5 12C3 15 5.92 17.16 9.25 17.16C11.06 17.16 12.72 16.62 14.12 15.62"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />

                            <path
                              d="M21 12C19.5 9 16.58 6.84 13.25 6.84C11.44 6.84 9.78 7.38 8.38 8.38"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />

                            <circle
                              cx="12"
                              cy="12"
                              r="3"
                              stroke="currentColor"
                              strokeWidth="2"
                            />
                          </svg>
                        )}
                      </button>
                    </span>
                  </label>

                  <label>
                    Rol

                    <select
                      value={registerForm.role}
                      onChange={(e) =>
                        setRegisterForm((prev) => ({
                          ...prev,
                          role: e.target.value,
                        }))
                      }
                    >
                      <option value="DOCENTE">DOCENTE</option>
                    </select>
                  </label>

                  <button type="submit" disabled={loading}>
                    {loading ? 'Creando...' : 'Crear usuario'}
                  </button>
                </form>
              )}

              <button
                type="button"
                className="auth-switch"
                onClick={alternarModoAuth}
              >
                {isRegisterMode
                  ? 'Ya tengo cuenta, iniciar sesión'
                  : 'No tengo cuenta, crear usuario'}
              </button>
            </div>
          </details>
        </section>


      </section>
    </main>
  )
}

export default AuthPage
