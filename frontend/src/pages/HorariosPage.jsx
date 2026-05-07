import { useMemo, useState, useEffect, useRef } from 'react'
import CalendarioHorarios from '../components/CalendarioHorarios'
import Modal from '../components/Modal'

const DIAS_VISTA = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO']
const TURNOS = [
  { key: 'TURNO_1', etiqueta: '07:00 - 14:00', inicio: 7 * 60, fin: 14 * 60 },
  { key: 'TURNO_2', etiqueta: '15:00 - 22:00', inicio: 15 * 60, fin: 22 * 60 },
]

function normalizarDia(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase()
}

function tiempoAminutos(value) {
  const [horas, minutos] = String(value || '0:0').split(':').map(Number)
  return (horas || 0) * 60 + (minutos || 0)
}

function obtenerTurno(horaInicio) {
  const minutos = tiempoAminutos(horaInicio)
  return TURNOS.find((turno) => minutos >= turno.inicio && minutos < turno.fin)?.key || 'FUERA_TURNO'
}

function etiquetaTurno(turnoKey) {
  return TURNOS.find((turno) => turno.key === turnoKey)?.etiqueta || '14:00 - 15:00'
}

function ordenarPorTurnoYHora(a, b) {
  const ordenTurno = TURNOS.reduce((mapa, turno, indice) => {
    mapa[turno.key] = indice
    return mapa
  }, {})

  const turnoA = ordenTurno[obtenerTurno(a.hora_inicio)] ?? TURNOS.length
  const turnoB = ordenTurno[obtenerTurno(b.hora_inicio)] ?? TURNOS.length

  if (turnoA !== turnoB) return turnoA - turnoB

  const diaA = DIAS_VISTA.indexOf(normalizarDia(a.dia))
  const diaB = DIAS_VISTA.indexOf(normalizarDia(b.dia))
  if (diaA !== diaB) return diaA - diaB

  return tiempoAminutos(a.hora_inicio) - tiempoAminutos(b.hora_inicio)
}

function HorariosPage({
  isAdmin,
  horarioForm,
  setHorarioForm,
  generacionForm,
  setGeneracionForm,
  crearHorario,
  generarHorariosAutomaticos,
  docentes,
  materias,
  aulas,
  periodos,
  horarios,
  eliminarHorario,
  actualizarHorario,
  cargarHorarios,
}) {
  const [vista, setVista] = useState('tabla')
  const [vistaCalendario, setVistaCalendario] = useState('semana') // 'semana' | 'por_aula' | 'por_docente'
  const [compacto, setCompacto] = useState(true)
  const [recursoSeleccionado, setRecursoSeleccionado] = useState('')
  const debounceTimer = useRef(null)
  const printTargetRef = useRef(null)

  // Llamar a la versión ligera que solo recarga `horarios` con debounce
  useEffect(() => {
    if (typeof cargarHorarios !== 'function') return undefined

    if (debounceTimer.current) clearTimeout(debounceTimer.current)
    debounceTimer.current = setTimeout(() => {
      void cargarHorarios()
      debounceTimer.current = null
    }, 300)

    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current)
    }
  }, [vistaCalendario, recursoSeleccionado, cargarHorarios])

  const [filtroDocente, setFiltroDocente] = useState('')
  const [filtroMateria, setFiltroMateria] = useState('')
  const [filtroAula, setFiltroAula] = useState('')
  const [filtroPeriodo, setFiltroPeriodo] = useState('')
  const [eliminandoHorarioId, setEliminandoHorarioId] = useState(null)
  const [errorModalMessage, setErrorModalMessage] = useState('')
  const [horarioPendienteEliminar, setHorarioPendienteEliminar] = useState(null)
  const [horarioPendienteEditar, setHorarioPendienteEditar] = useState(null)
  const [formularioEdicion, setFormularioEdicion] = useState({
    docente_id: '',
    materia_id: '',
    aula_id: '',
    periodo_id: '',
    dia: '',
    hora_inicio: '',
    hora_fin: '',
  })

  const mostrarErrorModal = (message) => {
    setErrorModalMessage(message || 'Ocurrio un error inesperado.')
  }

  const cerrarErrorModal = () => {
    setErrorModalMessage('')
  }

  const docentesPorId = new Map(docentes.map((docente) => [Number(docente.id), docente]))
  const materiasPorId = new Map(materias.map((materia) => [Number(materia.id), materia]))
  const aulasPorId = new Map(aulas.map((aula) => [Number(aula.id), aula]))
  const periodosPorId = new Map(periodos.map((periodo) => [Number(periodo.id), periodo]))

  const obtenerDocente = (horario) =>
    horario.docente_nombre || docentesPorId.get(Number(horario.docente_id))?.nombre || 'Docente no disponible'

  const obtenerMateria = (horario) =>
    horario.materia_nombre || materiasPorId.get(Number(horario.materia_id))?.nombre || 'Materia no disponible'

  const obtenerAula = (horario) =>
    horario.aula_nombre || aulasPorId.get(Number(horario.aula_id))?.nombre || 'Aula no disponible'

  const obtenerPeriodo = (horario) =>
    periodosPorId.get(Number(horario.periodo_id))?.nombre || 'Periodo no disponible'

  const horariosFiltrados = useMemo(() => {
    return horarios.filter((horario) => {
      if (filtroDocente && String(horario.docente_id) !== filtroDocente) return false
      if (filtroMateria && String(horario.materia_id) !== filtroMateria) return false
      if (filtroAula && String(horario.aula_id) !== filtroAula) return false
      if (filtroPeriodo && String(horario.periodo_id) !== filtroPeriodo) return false
      return true
    })
  }, [horarios, filtroDocente, filtroMateria, filtroAula, filtroPeriodo])

  const horariosOrdenados = useMemo(() => {
    return [...horariosFiltrados].sort(ordenarPorTurnoYHora)
  }, [horariosFiltrados])

  const colorTurno = (turno) => {
    if (turno === 'TURNO_1') return '#2a89d8'
    if (turno === 'TURNO_2') return '#d97706'
    return '#6b7280'
  }

  const actualizarSeleccionGeneracion = (campo, options) => {
    const value = Array.from(options)
      .filter((option) => option.selected)
      .map((option) => option.value)
      .join(',')

    setGeneracionForm((prev) => ({ ...prev, [campo]: value }))
  }

  const exportarVista = async () => {
    const target = printTargetRef.current
    if (!target) {
      mostrarErrorModal('No se encontro el recuadro para exportar.')
      return
    }

    try {
      const [{ default: html2canvas }, { default: jsPDF }] = await Promise.all([
        import('html2canvas'),
        import('jspdf'),
      ])

      const canvas = await html2canvas(target, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff',
      })

      const isLandscape = canvas.width > canvas.height
      const pdf = new jsPDF(isLandscape ? 'landscape' : 'portrait', 'mm', 'a4')
      const pageWidth = pdf.internal.pageSize.getWidth()
      const pageHeight = pdf.internal.pageSize.getHeight()
      const margin = 8
      const printableWidth = pageWidth - margin * 2
      const printableHeight = pageHeight - margin * 2
      const imageWidth = printableWidth
      const imageHeight = (canvas.height * imageWidth) / canvas.width
      const imageData = canvas.toDataURL('image/png')

      let heightLeft = imageHeight
      let positionY = margin

      pdf.addImage(imageData, 'PNG', margin, positionY, imageWidth, imageHeight)
      heightLeft -= printableHeight

      while (heightLeft > 0) {
        pdf.addPage()
        positionY = margin - (imageHeight - heightLeft)
        pdf.addImage(imageData, 'PNG', margin, positionY, imageWidth, imageHeight)
        heightLeft -= printableHeight
      }

      pdf.save('horario.pdf')
    } catch (error) {
      console.error(error)
      mostrarErrorModal('No se pudo generar el PDF. Intenta nuevamente.')
    }
  }

  const handleEliminarHorario = async (horario) => {
    setHorarioPendienteEliminar(horario)
  }

  const confirmarEliminarHorario = async () => {
    if (!horarioPendienteEliminar) return

    const horario = horarioPendienteEliminar
    setHorarioPendienteEliminar(null)

    setEliminandoHorarioId(horario.id)
    try {
      await eliminarHorario(horario.id)
    } catch (error) {
      mostrarErrorModal(error.message || 'Error al eliminar horario')
    } finally {
      setEliminandoHorarioId(null)
    }
  }

  const handleEditarHorario = (horario) => {
    setHorarioPendienteEditar(horario)
    setFormularioEdicion({
      docente_id: String(horario.docente_id),
      materia_id: String(horario.materia_id),
      aula_id: String(horario.aula_id),
      periodo_id: String(horario.periodo_id),
      dia: horario.dia,
      hora_inicio: horario.hora_inicio,
      hora_fin: horario.hora_fin,
    })
  }

  const confirmarEditarHorario = async () => {
    if (!horarioPendienteEditar) return

    const horario = horarioPendienteEditar
    setHorarioPendienteEditar(null)

    try {
      await actualizarHorario(horario.id, {
        docente_id: Number(formularioEdicion.docente_id),
        materia_id: Number(formularioEdicion.materia_id),
        aula_id: Number(formularioEdicion.aula_id),
        periodo_id: Number(formularioEdicion.periodo_id),
        dia: formularioEdicion.dia,
        hora_inicio: formularioEdicion.hora_inicio,
        hora_fin: formularioEdicion.hora_fin,
      })
    } catch (error) {
      mostrarErrorModal(error.message || 'Error al actualizar horario')
    }
  }

  return (
    <section className={`grid horarios-board ${isAdmin ? 'horarios-board--admin' : 'horarios-board--docente'}`}>
      <article className="card card--wide">
        <h3>
          Visualizador de Horarios
          <span className={`panel-chip ${isAdmin ? 'panel-chip--admin' : 'panel-chip--docente'}`}>
            {isAdmin ? 'Panel ADMIN' : 'Panel DOCENTE'}
          </span>
        </h3>
        <div className="filter-toolbar">
          <div className="filter-row">
            <label>
              Docente
              <select value={filtroDocente} onChange={(e) => setFiltroDocente(e.target.value)}>
                <option value="">Todos</option>
                {docentes.map((docente) => (
                  <option key={docente.id} value={docente.id}>
                    {docente.nombre} ({docente.turno || 'AMBOS'})
                  </option>
                ))}
              </select>
            </label>
            <label>
              Materia
              <select value={filtroMateria} onChange={(e) => setFiltroMateria(e.target.value)}>
                <option value="">Todas</option>
                {materias.map((materia) => (
                  <option key={materia.id} value={materia.id}>
                    {materia.nombre} ({materia.turno || 'AMBOS'})
                  </option>
                ))}
              </select>
            </label>
            <label>
              Aula
              <select value={filtroAula} onChange={(e) => setFiltroAula(e.target.value)}>
                <option value="">Todas</option>
                {aulas.map((aula) => (
                  <option key={aula.id} value={aula.id}>
                    {aula.nombre}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Periodo
              <select value={filtroPeriodo} onChange={(e) => setFiltroPeriodo(e.target.value)}>
                <option value="">Todos</option>
                {periodos.map((periodo) => (
                  <option key={periodo.id} value={periodo.id}>
                    {periodo.nombre}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="view-toggle">
            <button
              type="button"
              className={vista === 'tabla' ? 'active' : ''}
              onClick={() => setVista('tabla')}
            >
              Vista tabla
            </button>
            <button
              type="button"
              className={vista === 'malla' ? 'active' : ''}
              onClick={() => setVista('malla')}
            >
              Vista horario
            </button>
            <div className="calendar-options">
              <label>
                <input type="radio" name="vista_cal" value="semana" checked={vistaCalendario === 'semana'} onChange={() => setVistaCalendario('semana')} /> Semana
              </label>
              <label>
                <input type="radio" name="vista_cal" value="por_aula" checked={vistaCalendario === 'por_aula'} onChange={() => setVistaCalendario('por_aula')} /> Por Aula
              </label>
              <label>
                <input type="radio" name="vista_cal" value="por_docente" checked={vistaCalendario === 'por_docente'} onChange={() => setVistaCalendario('por_docente')} /> Por Docente
              </label>
              <label>
                <input type="checkbox" checked={compacto} onChange={(e) => setCompacto(e.target.checked)} /> Compacto
              </label>
            </div>
            {/* Selección de recurso cuando se muestra por-aula o por-docente */}
            {(vistaCalendario === 'por_aula' || vistaCalendario === 'por_docente') && (
              <label className="resource-filter">
                Filtrar recurso:
                <select value={recursoSeleccionado} onChange={(e) => setRecursoSeleccionado(e.target.value)}>
                  <option value="">Todos</option>
                  {vistaCalendario === 'por_aula' && aulas.map((a) => (
                    <option key={a.id} value={a.id}>{a.nombre}</option>
                  ))}
                  {vistaCalendario === 'por_docente' && docentes.map((d) => (
                    <option key={d.id} value={d.id}>{d.nombre}</option>
                  ))}
                </select>
              </label>
            )}
            <button type="button" onClick={exportarVista}>
              Exportar / Imprimir
            </button>
          </div>
        </div>
      </article>

      {errorModalMessage && (
        <Modal title="Se produjo un error" titleId="horarios-error-modal-title" onClose={cerrarErrorModal} actions={<>
          <button className="btn btn--primary" type="button" onClick={cerrarErrorModal}>Entendido</button>
        </>}>
          <p>{errorModalMessage}</p>
        </Modal>
      )}

      {horarioPendienteEliminar && (
        <Modal title="Confirmar eliminacion" titleId="confirmar-eliminar-horario-title" onClose={() => setHorarioPendienteEliminar(null)} actions={<>
          <button type="button" className="btn" onClick={() => setHorarioPendienteEliminar(null)}>Cancelar</button>
          <button type="button" className="btn btn--danger" onClick={confirmarEliminarHorario}>Eliminar</button>
        </>}>
          <p>
            Vas a eliminar el horario de <strong>{obtenerMateria(horarioPendienteEliminar)}</strong> el
            {' '}
            {horarioPendienteEliminar.dia}
            {' '}
            de
            {' '}
            {horarioPendienteEliminar.hora_inicio}
            {' '}
            a
            {' '}
            {horarioPendienteEliminar.hora_fin}.
          </p>
        </Modal>
      )}

      {horarioPendienteEditar && (
        <Modal title="Editar Horario" titleId="editar-horario-title" onClose={() => setHorarioPendienteEditar(null)} actions={<>
          <button type="button" className="btn" onClick={() => setHorarioPendienteEditar(null)}>Cancelar</button>
          <button type="button" className="btn btn--primary" onClick={confirmarEditarHorario}>Guardar</button>
        </>}>
          <form onSubmit={(e) => { e.preventDefault(); confirmarEditarHorario(); }} style={{ display: 'grid', gap: '0.75rem' }}>
            <label style={{ display: 'grid', gap: '0.3rem' }}>
              Docente
              <select
                value={formularioEdicion.docente_id}
                onChange={(e) => setFormularioEdicion((prev) => ({ ...prev, docente_id: e.target.value }))}
                required
              >
                {docentes.map((docente) => (
                  <option key={docente.id} value={docente.id}>
                    {docente.nombre}
                  </option>
                ))}
              </select>
            </label>
            <label style={{ display: 'grid', gap: '0.3rem' }}>
              Materia
              <select
                value={formularioEdicion.materia_id}
                onChange={(e) => setFormularioEdicion((prev) => ({ ...prev, materia_id: e.target.value }))}
                required
              >
                {materias.map((materia) => (
                  <option key={materia.id} value={materia.id}>
                    {materia.nombre}
                  </option>
                ))}
              </select>
            </label>
            <label style={{ display: 'grid', gap: '0.3rem' }}>
              Aula
              <select
                value={formularioEdicion.aula_id}
                onChange={(e) => setFormularioEdicion((prev) => ({ ...prev, aula_id: e.target.value }))}
                required
              >
                {aulas.map((aula) => (
                  <option key={aula.id} value={aula.id}>
                    {aula.nombre}
                  </option>
                ))}
              </select>
            </label>
            <label style={{ display: 'grid', gap: '0.3rem' }}>
              Periodo
              <select
                value={formularioEdicion.periodo_id}
                onChange={(e) => setFormularioEdicion((prev) => ({ ...prev, periodo_id: e.target.value }))}
                required
              >
                {periodos.map((periodo) => (
                  <option key={periodo.id} value={periodo.id}>
                    {periodo.nombre}
                  </option>
                ))}
              </select>
            </label>
            <label style={{ display: 'grid', gap: '0.3rem' }}>
              Día
              <select
                value={formularioEdicion.dia}
                onChange={(e) => setFormularioEdicion((prev) => ({ ...prev, dia: e.target.value }))}
              >
                <option>LUNES</option>
                <option>MARTES</option>
                <option>MIERCOLES</option>
                <option>JUEVES</option>
                <option>VIERNES</option>
              </select>
            </label>
            <label style={{ display: 'grid', gap: '0.3rem' }}>
              Hora Inicio
              <input
                type="time"
                value={formularioEdicion.hora_inicio}
                onChange={(e) => setFormularioEdicion((prev) => ({ ...prev, hora_inicio: e.target.value }))}
                required
              />
            </label>
            <label style={{ display: 'grid', gap: '0.3rem' }}>
              Hora Fin
              <input
                type="time"
                value={formularioEdicion.hora_fin}
                onChange={(e) => setFormularioEdicion((prev) => ({ ...prev, hora_fin: e.target.value }))}
                required
              />
            </label>
          </form>
        </Modal>
      )}

      {isAdmin && vista !== 'malla' && (
        <>
          <details className="card collapsible-card" open>
            <summary>
              <h3>Crear Horario</h3>
              <span aria-hidden="true">+</span>
            </summary>
            <form onSubmit={crearHorario} className="form">
              <label>
                Docente
                <select
                  value={horarioForm.docente_id}
                  onChange={(e) => setHorarioForm((prev) => ({ ...prev, docente_id: e.target.value }))}
                  required
                >
                  {docentes.length === 0 && <option value={horarioForm.docente_id}>Cargando docentes</option>}
                  {docentes.map((docente) => (
                    <option key={docente.id} value={docente.id}>
                      {docente.nombre} ({docente.turno || 'AMBOS'})
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Materia
                <select
                  value={horarioForm.materia_id}
                  onChange={(e) => setHorarioForm((prev) => ({ ...prev, materia_id: e.target.value }))}
                  required
                >
                  {materias.length === 0 && <option value={horarioForm.materia_id}>Cargando materias</option>}
                  {materias.map((materia) => (
                    <option key={materia.id} value={materia.id}>
                      {materia.nombre} ({materia.turno || 'AMBOS'})
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Aula
                <select
                  value={horarioForm.aula_id}
                  onChange={(e) => setHorarioForm((prev) => ({ ...prev, aula_id: e.target.value }))}
                  required
                >
                  {aulas.length === 0 && <option value={horarioForm.aula_id}>Cargando aulas</option>}
                  {aulas.map((aula) => (
                    <option key={aula.id} value={aula.id}>
                      {aula.nombre}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Periodo
                <select
                  value={horarioForm.periodo_id}
                  onChange={(e) => setHorarioForm((prev) => ({ ...prev, periodo_id: e.target.value }))}
                  required
                >
                  {periodos.length === 0 && <option value={horarioForm.periodo_id}>Cargando periodos</option>}
                  {periodos.map((periodo) => (
                    <option key={periodo.id} value={periodo.id}>
                      {periodo.nombre}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Dia
                <select
                  value={horarioForm.dia}
                  onChange={(e) => setHorarioForm((prev) => ({ ...prev, dia: e.target.value }))}
                >
                  <option>LUNES</option>
                  <option>MARTES</option>
                  <option>MIERCOLES</option>
                  <option>JUEVES</option>
                  <option>VIERNES</option>
                </select>
              </label>
              <label>
                Hora inicio
                <input
                  type="time"
                  value={horarioForm.hora_inicio}
                  onChange={(e) => setHorarioForm((prev) => ({ ...prev, hora_inicio: e.target.value }))}
                  required
                />
              </label>
              <label>
                Hora fin
                <input
                  type="time"
                  value={horarioForm.hora_fin}
                  onChange={(e) => setHorarioForm((prev) => ({ ...prev, hora_fin: e.target.value }))}
                  required
                />
              </label>
              <button type="submit">Guardar horario</button>
            </form>
          </details>

          <details className="card collapsible-card">
            <summary>
              <h3>Generar Horarios Automaticos</h3>
              <span aria-hidden="true">+</span>
            </summary>
            <form onSubmit={generarHorariosAutomaticos} className="form">
              <label>
                Periodo
                <select
                  value={generacionForm.periodo_id}
                  onChange={(e) => setGeneracionForm((prev) => ({ ...prev, periodo_id: e.target.value }))}
                  required
                >
                  {periodos.length === 0 && <option value={generacionForm.periodo_id}>Cargando periodos</option>}
                  {periodos.map((periodo) => (
                    <option key={periodo.id} value={periodo.id}>
                      {periodo.nombre}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Duracion por clase (min)
                <input
                  type="number"
                  min="30"
                  step="5"
                  value={generacionForm.duracion_minutos}
                  onChange={(e) => setGeneracionForm((prev) => ({ ...prev, duracion_minutos: e.target.value }))}
                  required
                />
              </label>
              <label>
                Inicio jornada
                <input
                  type="time"
                  value={generacionForm.hora_inicio_jornada}
                  onChange={(e) => setGeneracionForm((prev) => ({ ...prev, hora_inicio_jornada: e.target.value }))}
                  required
                />
              </label>
              <label>
                Fin jornada
                <input
                  type="time"
                  value={generacionForm.hora_fin_jornada}
                  onChange={(e) => setGeneracionForm((prev) => ({ ...prev, hora_fin_jornada: e.target.value }))}
                  required
                />
              </label>
              <label>
                Dias (separados por coma)
                <input
                  value={generacionForm.dias}
                  onChange={(e) => setGeneracionForm((prev) => ({ ...prev, dias: e.target.value }))}
                  required
                />
              </label>
              <label>
                Docentes
                <select
                  multiple
                  value={generacionForm.docente_ids ? generacionForm.docente_ids.split(',') : []}
                  onChange={(e) => actualizarSeleccionGeneracion('docente_ids', e.target.options)}
                >
                  {docentes.map((docente) => (
                    <option key={docente.id} value={docente.id}>
                      {docente.nombre} ({docente.turno || 'AMBOS'})
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Materias
                <select
                  multiple
                  value={generacionForm.materia_ids ? generacionForm.materia_ids.split(',') : []}
                  onChange={(e) => actualizarSeleccionGeneracion('materia_ids', e.target.options)}
                >
                  {materias.map((materia) => (
                    <option key={materia.id} value={materia.id}>
                      {materia.nombre} ({materia.turno || 'AMBOS'})
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Aulas
                <select
                  multiple
                  value={generacionForm.aula_ids ? generacionForm.aula_ids.split(',') : []}
                  onChange={(e) => actualizarSeleccionGeneracion('aula_ids', e.target.options)}
                >
                  {aulas.map((aula) => (
                    <option key={aula.id} value={aula.id}>
                      {aula.nombre}
                    </option>
                  ))}
                </select>
              </label>
              <button type="submit">Generar automaticamente</button>
            </form>
          </details>
        </>
      )}

      <article ref={printTargetRef} className="card card--wide print-target">
        <h3>{vista === 'tabla' ? 'Horarios Filtrados' : 'Horario Semanal'}</h3>

        {horariosFiltrados.length === 0 ? (
          <p className="empty-state">No hay horarios que coincidan con los filtros seleccionados.</p>
        ) : vista === 'tabla' ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Turno</th>
                  <th>Docente</th>
                  <th>Materia</th>
                  <th>Aula</th>
                  <th>Periodo</th>
                  <th>Dia</th>
                  <th>Hora</th>
                  {isAdmin && <th>Acciones</th>}
                </tr>
              </thead>
              <tbody>
                {horariosOrdenados.map((h) => (
                  <tr key={h.id}>
                    <td>
                      <span
                        className="turno-badge"
                        style={{ background: colorTurno(obtenerTurno(h.hora_inicio)) }}
                      >
                        {etiquetaTurno(obtenerTurno(h.hora_inicio))}
                      </span>
                    </td>
                    <td>
                      <strong>{obtenerDocente(h)}</strong>
                      {h.docente_correo && <span>{h.docente_correo}</span>}
                    </td>
                    <td>
                      <strong>{obtenerMateria(h)}</strong>
                      {h.materia_codigo && <span>{h.materia_codigo}</span>}
                      <span>Turno {h.materia_turno || materiasPorId.get(Number(h.materia_id))?.turno || 'AMBOS'}</span>
                    </td>
                    <td>
                      <strong>{obtenerAula(h)}</strong>
                      {h.aula_capacidad && <span>Capacidad {h.aula_capacidad}</span>}
                    </td>
                    <td>{obtenerPeriodo(h)}</td>
                    <td>{h.dia}</td>
                    <td>
                      {h.hora_inicio} - {h.hora_fin}
                    </td>
                    {isAdmin && (
                      <td>
                        <div className="row-actions">
                          <button
                            type="button"
                            onClick={() => handleEditarHorario(h)}
                          >
                            Editar
                          </button>
                          <button
                            type="button"
                            className="button-alt"
                            onClick={() => handleEliminarHorario(h)}
                            disabled={eliminandoHorarioId === h.id}
                          >
                            {eliminandoHorarioId === h.id ? 'Eliminando...' : 'Eliminar'}
                          </button>
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <CalendarioHorarios
            horarios={horarios}
            filtroDocente={filtroDocente}
            filtroMateria={filtroMateria}
            filtroAula={filtroAula}
            filtroPeriodo={filtroPeriodo}
            isAdmin={isAdmin}
            eliminarHorario={eliminarHorario}
            aulas={aulas}
            docentes={docentes}
            vistaCalendario={vistaCalendario}
            compacto={compacto}
            recursoSeleccionado={recursoSeleccionado}
            setRecursoSeleccionado={setRecursoSeleccionado}
          />
        )}
      </article>
    </section>
  )
}

export default HorariosPage
