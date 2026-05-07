import { useCallback, useEffect, useMemo, useState } from 'react'
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import './App.css'
import AuthPage from './components/AuthPage'
import AppLayout from './components/AppLayout'
import ProtectedRoute from './components/ProtectedRoute'
import DashboardPage from './pages/DashboardPage'
import DocentesPage from './pages/DocentesPage'
import MateriasPage from './pages/MateriasPage'
import AulasPage from './pages/AulasPage'
import PeriodosPage from './pages/PeriodosPage'
import HorariosPage from './pages/HorariosPage'
import AccessDeniedPage from './pages/AccessDeniedPage'
import { ADMIN_MODULE_LINKS, DOCENTE_MODULE_LINKS } from './constants/modules'

function decodeJwtPayload(token) {
  try {
    const payloadPart = token.split('.')[1]
    if (!payloadPart) return null

    const base64 = payloadPart.replace(/-/g, '+').replace(/_/g, '/')
    const json = decodeURIComponent(
      atob(base64)
        .split('')
        .map((char) => `%${`00${char.charCodeAt(0).toString(16)}`.slice(-2)}`)
        .join(''),
    )

    return JSON.parse(json)
  } catch {
    return null
  }
}

function horarioDentroDeTurno(horaInicio, horaFin, turno) {
  const turnoNormalizado = String(turno || 'AMBOS').toUpperCase()
  if (turnoNormalizado === 'MATUTINO') return horaInicio >= '07:00' && horaFin <= '14:00'
  if (turnoNormalizado === 'VESPERTINO') return horaInicio >= '15:00' && horaFin <= '22:00'
  return (horaInicio >= '07:00' && horaFin <= '14:00') || (horaInicio >= '15:00' && horaFin <= '22:00')
}

function describirTurno(turno) {
  const turnoNormalizado = String(turno || 'AMBOS').toUpperCase()
  if (turnoNormalizado === 'MATUTINO') return '07:00 a 14:00'
  if (turnoNormalizado === 'VESPERTINO') return '15:00 a 22:00'
  return '07:00 a 14:00 o 15:00 a 22:00'
}

function App() {
  const API = useMemo(
    () => ({
      usuarios: import.meta.env.VITE_USUARIOS_API_URL || 'http://localhost:8001',
      materias: import.meta.env.VITE_MATERIAS_API_URL || 'http://localhost:8002',
      aulas: import.meta.env.VITE_AULAS_API_URL || 'http://localhost:8003',
      horario: import.meta.env.VITE_HORARIO_API_URL || 'http://localhost:8004',
      jwtStorageKey: import.meta.env.VITE_JWT_STORAGE_KEY || 'auth_token',
    }),
    [],
  )

  const [authToken, setAuthToken] = useState(() => localStorage.getItem(API.jwtStorageKey) || '')
  const [loginForm, setLoginForm] = useState({
    correo: 'admin@example.com',
    password: '1234',
  })
  const [registerForm, setRegisterForm] = useState({
    nombre: '',
    correo: '',
    password: '',
    role: 'DOCENTE',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [isRegisterMode, setIsRegisterMode] = useState(false)

  const [loading, setLoading] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [error, setError] = useState('')

  const [docentes, setDocentes] = useState([])
  const [materias, setMaterias] = useState([])
  const [aulas, setAulas] = useState([])
  const [periodos, setPeriodos] = useState([])
  const [horarios, setHorarios] = useState([])

  const [periodoForm, setPeriodoForm] = useState({
    nombre: '2026-2',
    tipo: 'SEMESTRE',
    fecha_inicio: '2026-09-01',
    fecha_fin: '2027-01-15',
  })

  const [horarioForm, setHorarioForm] = useState({
    docente_id: '1',
    materia_id: '1',
    aula_id: '1',
    periodo_id: '1',
    dia: 'LUNES',
    hora_inicio: '08:00',
    hora_fin: '10:00',
  })

  const [generacionForm, setGeneracionForm] = useState({
    periodo_id: '1',
    duracion_minutos: '60',
    hora_inicio_jornada: '08:00',
    hora_fin_jornada: '18:00',
    dias: 'LUNES,MARTES,MIERCOLES,JUEVES,VIERNES',
    docente_ids: '',
    materia_ids: '',
    aula_ids: '',
  })

  const usuarioSesion = useMemo(() => decodeJwtPayload(authToken), [authToken])
  const userRole = usuarioSesion?.rol || 'DOCENTE'
  const isAdmin = userRole === 'ADMIN'
  const currentUserId = Number(usuarioSesion?.id)
  const moduleLinks = isAdmin ? ADMIN_MODULE_LINKS : DOCENTE_MODULE_LINKS
  const dashboardTitle = isAdmin ? 'Panel de Gestion Academica' : 'Panel Docente'
  const dashboardSubtitle = isAdmin ? 'Sistema escolar' : 'Panel docente'
  const isAuthenticated = Boolean(authToken)
  const navigate = useNavigate()
  const clearError = useCallback(() => setError(''), [])
  const clearMensaje = useCallback(() => setMensaje(''), [])

  const fetchJson = useCallback(async (url, options = {}, requiresAuth = false) => {
    const authHeaders = requiresAuth
      ? { Authorization: `Bearer ${authToken}` }
      : {}

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
        ...(options.headers || {}),
      },
      ...options,
    })

    const text = await response.text()
    const data = text ? JSON.parse(text) : null

    if (!response.ok) {
      const detail = data?.detail || data || `HTTP ${response.status}`
      throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    }

    return data
  }, [authToken])

  const cargarDatos = useCallback(async () => {
    if (!isAuthenticated) return

    setLoading(true)
    setError('')

    try {
      const [docentesData, materiasData, aulasData, periodosData, horariosData] = await Promise.all([
        fetchJson(`${API.usuarios}/docentes`, {}, true),
        fetchJson(`${API.materias}/api/v1/materias/`),
        fetchJson(`${API.aulas}/aulas`),
        fetchJson(`${API.horario}/periodos`),
        fetchJson(`${API.horario}/horarios`),
      ])

      if (isAdmin) {
        setDocentes(docentesData)
        setMaterias(materiasData)
        setAulas(aulasData)
        setPeriodos(periodosData)
        setHorarios(horariosData)
      } else {
        const horariosDocente = horariosData.filter(
          (horario) => Number(horario.docente_id) === currentUserId,
        )
        const materiasAsignadas = new Set(horariosDocente.map((horario) => Number(horario.materia_id)))
        const aulasAsignadas = new Set(horariosDocente.map((horario) => Number(horario.aula_id)))
        const periodosAsignados = new Set(horariosDocente.map((horario) => Number(horario.periodo_id)))
        const docenteSesion = docentesData.find((docente) => Number(docente.id) === currentUserId)

        setDocentes(docenteSesion ? [docenteSesion] : [])
        setMaterias(materiasData.filter((materia) => materiasAsignadas.has(Number(materia.id))))
        setAulas(aulasData.filter((aula) => aulasAsignadas.has(Number(aula.id))))
        setPeriodos(periodosData.filter((periodo) => periodosAsignados.has(Number(periodo.id))))
        setHorarios(horariosDocente)
      }
    } catch (err) {
      if (err.message.includes('401')) {
        localStorage.removeItem(API.jwtStorageKey)
        setAuthToken('')
        setError('Tu sesión expiró. Inicia sesión nuevamente.')
        return
      }
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [API, isAuthenticated, fetchJson, isAdmin, currentUserId])

  const cargarHorarios = useCallback(async () => {
    if (!isAuthenticated) return

    try {
      const horariosData = await fetchJson(`${API.horario}/horarios`)
      if (isAdmin) {
        setHorarios(horariosData)
      } else {
        const horariosDocente = horariosData.filter(
          (horario) => Number(horario.docente_id) === currentUserId,
        )
        setHorarios(horariosDocente)
      }
    } catch (err) {
      if (err.message.includes('401')) {
        localStorage.removeItem(API.jwtStorageKey)
        setAuthToken('')
        setError('Tu sesión expiró. Inicia sesión nuevamente.')
        return
      }
      setError(err.message)
    }
  }, [API, fetchJson, isAuthenticated, isAdmin, currentUserId])

  useEffect(() => {
    if (!isAuthenticated) return undefined

    const frame = requestAnimationFrame(() => {
      void cargarDatos()
    })

    return () => cancelAnimationFrame(frame)
  }, [cargarDatos, isAuthenticated])

  // Update form defaults with first available IDs
  useEffect(() => {
    if (docentes.length > 0 || materias.length > 0 || aulas.length > 0 || periodos.length > 0) {
      const frame = requestAnimationFrame(() => {
        setHorarioForm((prev) => ({
          ...prev,
          docente_id: docentes.length > 0 ? String(docentes[0].id) : prev.docente_id,
          materia_id: materias.length > 0 ? String(materias[0].id) : prev.materia_id,
          aula_id: aulas.length > 0 ? String(aulas[0].id) : prev.aula_id,
          periodo_id: periodos.length > 0 ? String(periodos[0].id) : prev.periodo_id,
        }))
        setGeneracionForm((prev) => ({
          ...prev,
          periodo_id: periodos.length > 0 ? String(periodos[0].id) : prev.periodo_id,
        }))
      })

      return () => cancelAnimationFrame(frame)
    }

    return undefined
  }, [docentes, materias, aulas, periodos])

  function alternarModoAuth() {
    setMensaje('')
    setError('')
    setShowPassword(false)
    setIsRegisterMode((prev) => !prev)
  }

  async function iniciarSesion(event) {
    event.preventDefault()
    setMensaje('')
    setError('')
    setLoading(true)

    try {
      const data = await fetchJson(`${API.usuarios}/auth/login`, {
        method: 'POST',
        body: JSON.stringify(loginForm),
      })

      localStorage.setItem(API.jwtStorageKey, data.token)
      setAuthToken(data.token)
      setMensaje('Sesión iniciada correctamente.')
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function crearUsuario(event) {
    event.preventDefault()
    setMensaje('')
    setError('')
    setLoading(true)

    try {
      await fetchJson(`${API.usuarios}/auth/register`, {
        method: 'POST',
        body: JSON.stringify(registerForm),
      })

      setMensaje('Usuario creado. Ahora puedes iniciar sesión con tus credenciales.')
      setLoginForm((prev) => ({
        ...prev,
        correo: registerForm.correo,
        password: registerForm.password,
      }))
      setRegisterForm({ nombre: '', correo: '', password: '', role: 'DOCENTE' })
      setIsRegisterMode(false)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function cerrarSesion() {
    localStorage.removeItem(API.jwtStorageKey)
    setAuthToken('')
    setMensaje('Sesión cerrada.')
    setError('')
    setDocentes([])
    setMaterias([])
    setAulas([])
    setPeriodos([])
    setHorarios([])
    navigate('/login', { replace: true })
  }

  async function crearPeriodo(event) {
    event.preventDefault()
    if (!isAdmin) {
      setError('Solo un administrador puede crear periodos.')
      return
    }
    setMensaje('')
    setError('')

    try {
      await fetchJson(`${API.horario}/periodos`, {
        method: 'POST',
        body: JSON.stringify({
          nombre: periodoForm.nombre,
          tipo: periodoForm.tipo,
          fecha_inicio: periodoForm.fecha_inicio,
          fecha_fin: periodoForm.fecha_fin,
        }),
      }, true)
      setMensaje('Periodo creado correctamente.')
      await cargarDatos()
    } catch (err) {
      setError(err.message)
    }
  }

  async function crearHorario(event) {
    event.preventDefault()
    if (!isAdmin) {
      setError('Solo un administrador puede crear horarios.')
      return
    }
    setMensaje('')
    setError('')

    const docente = docentes.find((item) => String(item.id) === String(horarioForm.docente_id))
    if (docente && !horarioDentroDeTurno(horarioForm.hora_inicio, horarioForm.hora_fin, docente.turno)) {
      setError(`El docente es de turno ${docente.turno || 'AMBOS'} y solo puede trabajar de ${describirTurno(docente.turno)}.`)
      return
    }

    try {
      await fetchJson(`${API.horario}/horarios`, {
        method: 'POST',
        body: JSON.stringify({
          docente_id: Number(horarioForm.docente_id),
          materia_id: Number(horarioForm.materia_id),
          aula_id: Number(horarioForm.aula_id),
          periodo_id: Number(horarioForm.periodo_id),
          dia: horarioForm.dia,
          hora_inicio: horarioForm.hora_inicio,
          hora_fin: horarioForm.hora_fin,
        }),
      }, true)
      setMensaje('Horario creado correctamente.')
      await cargarDatos()
    } catch (err) {
      setError(err.message)
    }
  }

  async function generarHorariosAutomaticos(event) {
    event.preventDefault()
    if (!isAdmin) {
      setError('Solo un administrador puede generar horarios automaticos.')
      return
    }
    setMensaje('')
    setError('')

    const dias = generacionForm.dias
      .split(',')
      .map((dia) => dia.trim().toUpperCase())
      .filter(Boolean)
    const parseIds = (value) =>
      value
        .split(',')
        .map((id) => Number(id.trim()))
        .filter((id) => Number.isInteger(id) && id > 0)

    const docenteIds = parseIds(generacionForm.docente_ids)
    const materiaIds = parseIds(generacionForm.materia_ids)
    const aulaIds = parseIds(generacionForm.aula_ids)

    try {
      const result = await fetchJson(`${API.horario}/horarios/generar`, {
        method: 'POST',
        body: JSON.stringify({
          periodo_id: Number(generacionForm.periodo_id),
          duracion_minutos: Number(generacionForm.duracion_minutos),
          hora_inicio_jornada: generacionForm.hora_inicio_jornada,
          hora_fin_jornada: generacionForm.hora_fin_jornada,
          dias,
          ...(docenteIds.length > 0 ? { docente_ids: docenteIds } : {}),
          ...(materiaIds.length > 0 ? { materia_ids: materiaIds } : {}),
          ...(aulaIds.length > 0 ? { aula_ids: aulaIds } : {}),
        }),
      }, true)

      const mensajes = result?.mensajes?.length ? ` ${result.mensajes.join(' | ')}` : ''
      setMensaje(`Generacion completada. Horarios creados: ${result?.creados?.length || 0}.${mensajes}`)
      await cargarDatos()
    } catch (err) {
      setError(err.message)
    }
  }

  async function crearMateria(payload) {
    await fetchJson(`${API.materias}/api/v1/materias/`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }, true)
    await cargarDatos()
  }

  async function actualizarMateria(materiaId, payload) {
    await fetchJson(`${API.materias}/api/v1/materias/${materiaId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }, true)
    await cargarDatos()
  }

  async function eliminarMateria(materiaId) {
    setMensaje('')
    setError('')
    try {
      await fetchJson(`${API.materias}/api/v1/materias/${materiaId}`, {
        method: 'DELETE',
      }, true)
      setMensaje('Materia eliminada correctamente.')
      await cargarDatos()
    } catch (err) {
      setError(err.message)
      throw err
    }
  }

  async function crearAula(payload) {
    await fetchJson(`${API.aulas}/aulas`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }, true)
    await cargarDatos()
  }

  async function actualizarAula(aulaId, payload) {
    await fetchJson(`${API.aulas}/aulas/${aulaId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }, true)
    await cargarDatos()
  }

  async function eliminarAula(aulaId) {
    setMensaje('')
    setError('')
    try {
      await fetchJson(`${API.aulas}/aulas/${aulaId}`, {
        method: 'DELETE',
      }, true)
      setMensaje('Aula eliminada correctamente.')
      await cargarDatos()
    } catch (err) {
      setError(err.message)
      throw err
    }
  }

  async function crearDocente(payload) {
    await fetchJson(`${API.usuarios}/docentes`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }, true)
    await cargarDatos()
  }

  async function actualizarDocente(docenteId, payload) {
    await fetchJson(`${API.usuarios}/docentes/${docenteId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }, true)
    await cargarDatos()
  }

  async function eliminarDocente(docenteId) {
    setMensaje('')
    setError('')
    try {
      await fetchJson(`${API.usuarios}/docentes/${docenteId}`, {
        method: 'DELETE',
      }, true)
      setMensaje('Docente eliminado correctamente.')
      await cargarDatos()
    } catch (err) {
      setError(err.message)
      throw err
    }
  }

  async function eliminarHorario(horarioId) {
    setMensaje('')
    setError('')
    try {
      await fetchJson(`${API.horario}/horarios/${horarioId}`, {
        method: 'DELETE',
      }, true)
      setMensaje('Horario eliminado correctamente.')
      await cargarDatos()
    } catch (err) {
      setError(err.message)
      throw err
    }
  }

  async function actualizarHorario(horarioId, payload) {
    setMensaje('')
    setError('')
    try {
      await fetchJson(`${API.horario}/horarios/${horarioId}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      }, true)
      setMensaje('Horario actualizado correctamente.')
      await cargarDatos()
    } catch (err) {
      setError(err.message)
      throw err
    }
  }

  async function eliminarPeriodo(periodoId) {
    try {
      await fetchJson(`${API.horario}/periodos/${periodoId}`, {
        method: 'DELETE',
      }, true)
      await cargarDatos()
      return null
    } catch (err) {
      // intentamos parsear detalle con dependencias devuelto por backend
      try {
        const parsed = JSON.parse(err.message)
        const detail = parsed?.detail || parsed
        return detail
      } catch {
        throw err
      }
    }
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={
          isAuthenticated ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <AuthPage
              isRegisterMode={isRegisterMode}
              alternarModoAuth={alternarModoAuth}
              mensaje={mensaje}
              error={error}
              clearError={clearError}
              loading={loading}
              showPassword={showPassword}
              setShowPassword={setShowPassword}
              loginForm={loginForm}
              setLoginForm={setLoginForm}
              registerForm={registerForm}
              setRegisterForm={setRegisterForm}
              iniciarSesion={iniciarSesion}
              crearUsuario={crearUsuario}
            />
          )
        }
      />

      <Route element={<ProtectedRoute isAuthenticated={isAuthenticated} />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route
          path="/dashboard"
          element={
            <AppLayout
              usuarioSesion={usuarioSesion}
              moduleLinks={moduleLinks}
              dashboardTitle={dashboardTitle}
              dashboardSubtitle={dashboardSubtitle}
              cargarDatos={cargarDatos}
              loading={loading}
              cerrarSesion={cerrarSesion}
              mensaje={mensaje}
              error={error}
              clearError={clearError}
              clearMensaje={clearMensaje}
            >
              <DashboardPage
                isAdmin={isAdmin}
                usuarioSesion={usuarioSesion}
                docentes={docentes}
                materias={materias}
                aulas={aulas}
                periodos={periodos}
                horarios={horarios}
              />
            </AppLayout>
          }
        />
        <Route element={<ProtectedRoute isAuthenticated={isAuthenticated} userRole={userRole} allowedRoles={['ADMIN']} />}>
          <Route
            path="/docentes"
            element={
              <AppLayout
                usuarioSesion={usuarioSesion}
                moduleLinks={moduleLinks}
                dashboardTitle={dashboardTitle}
                dashboardSubtitle={dashboardSubtitle}
                cargarDatos={cargarDatos}
                loading={loading}
                cerrarSesion={cerrarSesion}
                mensaje={mensaje}
                error={error}
                clearError={clearError}
                clearMensaje={clearMensaje}
              >
                <DocentesPage
                  isAdmin={isAdmin}
                  docentes={docentes}
                  onCreate={crearDocente}
                  onUpdate={actualizarDocente}
                  onDelete={eliminarDocente}
                />
              </AppLayout>
            }
          />
        </Route>
        <Route
          path="/materias"
          element={
            <AppLayout
              usuarioSesion={usuarioSesion}
              moduleLinks={moduleLinks}
              dashboardTitle={dashboardTitle}
              dashboardSubtitle={dashboardSubtitle}
              cargarDatos={cargarDatos}
              loading={loading}
              cerrarSesion={cerrarSesion}
              mensaje={mensaje}
              error={error}
              clearError={clearError}
              clearMensaje={clearMensaje}
            >
              <MateriasPage
                isAdmin={isAdmin}
                materias={materias}
                onCreate={crearMateria}
                onUpdate={actualizarMateria}
                onDelete={eliminarMateria}
              />
            </AppLayout>
          }
        />
        <Route
          path="/aulas"
          element={
            <AppLayout
              usuarioSesion={usuarioSesion}
              moduleLinks={moduleLinks}
              dashboardTitle={dashboardTitle}
              dashboardSubtitle={dashboardSubtitle}
              cargarDatos={cargarDatos}
              loading={loading}
              cerrarSesion={cerrarSesion}
              mensaje={mensaje}
              error={error}
              clearError={clearError}
              clearMensaje={clearMensaje}
            >
              <AulasPage
                isAdmin={isAdmin}
                aulas={aulas}
                onCreate={crearAula}
                onUpdate={actualizarAula}
                onDelete={eliminarAula}
              />
            </AppLayout>
          }
        />
        <Route element={<ProtectedRoute isAuthenticated={isAuthenticated} userRole={userRole} allowedRoles={['ADMIN']} />}>
          <Route
            path="/periodos"
            element={
              <AppLayout
                usuarioSesion={usuarioSesion}
                moduleLinks={moduleLinks}
                dashboardTitle={dashboardTitle}
                dashboardSubtitle={dashboardSubtitle}
                cargarDatos={cargarDatos}
                loading={loading}
                cerrarSesion={cerrarSesion}
                mensaje={mensaje}
                error={error}
                clearError={clearError}
                clearMensaje={clearMensaje}
              >
                <PeriodosPage
                  periodoForm={periodoForm}
                  setPeriodoForm={setPeriodoForm}
                  crearPeriodo={crearPeriodo}
                  periodos={periodos}
                  eliminarPeriodo={eliminarPeriodo}
                  eliminarHorario={eliminarHorario}
                />
              </AppLayout>
            }
          />
        </Route>
        <Route
          path="/horarios"
          element={
            <AppLayout
              usuarioSesion={usuarioSesion}
              moduleLinks={moduleLinks}
              dashboardTitle={dashboardTitle}
              dashboardSubtitle={dashboardSubtitle}
              cargarDatos={cargarDatos}
              loading={loading}
              cerrarSesion={cerrarSesion}
              mensaje={mensaje}
              error={error}
              clearError={clearError}
              clearMensaje={clearMensaje}
            >
              <HorariosPage
                isAdmin={isAdmin}
                horarioForm={horarioForm}
                setHorarioForm={setHorarioForm}
                generacionForm={generacionForm}
                setGeneracionForm={setGeneracionForm}
                crearHorario={crearHorario}
                generarHorariosAutomaticos={generarHorariosAutomaticos}
                docentes={docentes}
                materias={materias}
                aulas={aulas}
                periodos={periodos}
                horarios={horarios}
                eliminarHorario={eliminarHorario}
                actualizarHorario={actualizarHorario}
                cargarDatos={cargarDatos}
                cargarHorarios={cargarHorarios}
              />
            </AppLayout>
          }
        />
        <Route
          path="/acceso-denegado"
          element={
            <AppLayout
              usuarioSesion={usuarioSesion}
              moduleLinks={moduleLinks}
              dashboardTitle={dashboardTitle}
              dashboardSubtitle={dashboardSubtitle}
              cargarDatos={cargarDatos}
              loading={loading}
              cerrarSesion={cerrarSesion}
              mensaje={mensaje}
              error={error}
              clearError={clearError}
              clearMensaje={clearMensaje}
            >
              <AccessDeniedPage />
            </AppLayout>
          }
        />
      </Route>

      <Route
        path="*"
        element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />}
      />
    </Routes>
  )
}

export default App
