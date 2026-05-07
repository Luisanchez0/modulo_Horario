import { useMemo, useState } from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import resourceTimeGridPlugin from '@fullcalendar/resource-timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import esLocale from '@fullcalendar/core/locales/es'
import Modal from './Modal'

const DIAS_SEMANA = {
  LUNES: 1,
  MARTES: 2,
  MIERCOLES: 3,
  JUEVES: 4,
  VIERNES: 5,
  SABADO: 6,
}

function normalizarDia(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase()
}

function obtenerFechaDelHorario(dia, horaInicio) {
  // Obtener la fecha de hoy
  const hoy = new Date()
  const dayOfWeek = hoy.getDay() // 0 = domingo, 1 = lunes, etc.

  // Normalizar el día del horario
  const diaNormalizado = normalizarDia(dia)
  const diaNumero = DIAS_SEMANA[diaNormalizado] || 1

  // Calcular días a sumar (considerando que Monday = 1)
  const diasARestar = dayOfWeek === 0 ? 6 : dayOfWeek - 1
  const fechaLunes = new Date(hoy)
  fechaLunes.setDate(hoy.getDate() - diasARestar)

  // Calcular fecha del día específico
  const diasAsumar = diaNumero - 1
  const fecha = new Date(fechaLunes)
  fecha.setDate(fechaLunes.getDate() + diasAsumar)

  // Parsear hora_inicio (formato HH:MM)
  const [horas, minutos] = String(horaInicio || '0:0').split(':').map(Number)
  fecha.setHours(horas || 0, minutos || 0, 0, 0)

  return fecha
}

function colorMateria(materiaId) {
  const palette = ['#d97706', '#0f766e', '#7c3aed', '#2563eb', '#be185d', '#15803d', '#b45309']
  const index = Math.abs(Number(materiaId) || 0) % palette.length
  return palette[index]
}

function toLocalDateTimeString(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`
}

function tiempoAMinutos(valor) {
  const [horas, minutos] = String(valor || '0:0').split(':').map(Number)
  return (horas || 0) * 60 + (minutos || 0)
}

function haySolape(h1Inicio, h1Fin, h2Inicio, h2Fin) {
  return h1Inicio < h2Fin && h2Inicio < h1Fin
}

export default function CalendarioHorarios({
  horarios,
  filtroDocente,
  filtroMateria,
  filtroAula,
  filtroPeriodo,
  isAdmin,
  eliminarHorario,
  aulas,
  docentes,
  vistaCalendario = 'semana',
  compacto = true,
  recursoSeleccionado,
}) {
  const [eventoSeleccionado, setEventoSeleccionado] = useState(null)

  const horariosFiltrados = useMemo(() => {
    return horarios.filter((horario) => {
      if (filtroDocente && String(horario.docente_id) !== filtroDocente) return false
      if (filtroMateria && String(horario.materia_id) !== filtroMateria) return false
      if (filtroAula && String(horario.aula_id) !== filtroAula) return false
      if (filtroPeriodo && String(horario.periodo_id) !== filtroPeriodo) return false
      return true
    })
  }, [horarios, filtroDocente, filtroMateria, filtroAula, filtroPeriodo])

  const conflictosPorHorarioId = useMemo(() => {
    const conflictos = new Map()

    for (let i = 0; i < horariosFiltrados.length; i += 1) {
      const actual = horariosFiltrados[i]
      for (let j = i + 1; j < horariosFiltrados.length; j += 1) {
        const candidato = horariosFiltrados[j]

        const mismoDia = normalizarDia(actual.dia) === normalizarDia(candidato.dia)
        const mismoPeriodo = String(actual.periodo_id) === String(candidato.periodo_id)
        if (!mismoDia || !mismoPeriodo) continue

        const actualInicio = tiempoAMinutos(actual.hora_inicio)
        const actualFin = tiempoAMinutos(actual.hora_fin)
        const candidatoInicio = tiempoAMinutos(candidato.hora_inicio)
        const candidatoFin = tiempoAMinutos(candidato.hora_fin)
        if (!haySolape(actualInicio, actualFin, candidatoInicio, candidatoFin)) continue

        const conflictosActual = conflictos.get(String(actual.id)) || new Set()
        const conflictosCandidato = conflictos.get(String(candidato.id)) || new Set()

        if (String(actual.docente_id) === String(candidato.docente_id)) {
          conflictosActual.add(`Docente repetido: ${actual.docente_nombre || 'Docente'}`)
          conflictosCandidato.add(`Docente repetido: ${candidato.docente_nombre || 'Docente'}`)
        }

        if (String(actual.aula_id) === String(candidato.aula_id)) {
          conflictosActual.add(`Aula ocupada: ${actual.aula_nombre || 'Aula'}`)
          conflictosCandidato.add(`Aula ocupada: ${candidato.aula_nombre || 'Aula'}`)
        }

        if (conflictosActual.size > 0) conflictos.set(String(actual.id), conflictosActual)
        if (conflictosCandidato.size > 0) conflictos.set(String(candidato.id), conflictosCandidato)
      }
    }

    return conflictos
  }, [horariosFiltrados])

  const eventosCalendario = useMemo(() => {
    return horariosFiltrados
      .map((horario) => {
        const fechaInicio = obtenerFechaDelHorario(horario.dia, horario.hora_inicio)

        // Parsear hora_fin
        const [horasFin, minutosFin] = String(horario.hora_fin || '0:0')
          .split(':')
          .map(Number)
        const fechaFin = new Date(fechaInicio)
        fechaFin.setHours(horasFin || 0, minutosFin || 0, 0, 0)

        const conflictos = [...(conflictosPorHorarioId.get(String(horario.id)) || [])]
        const tieneConflicto = conflictos.length > 0

        return {
          id: String(horario.id),
          title: horario.materia_nombre || 'Materia',
          start: toLocalDateTimeString(fechaInicio),
          end: toLocalDateTimeString(fechaFin),
          resourceId: vistaCalendario === 'por_aula' ? String(horario.aula_id) : vistaCalendario === 'por_docente' ? String(horario.docente_id) : undefined,
          backgroundColor: colorMateria(horario.materia_id),
          borderColor: tieneConflicto ? '#b42318' : colorMateria(horario.materia_id),
          classNames: tieneConflicto ? ['calendar-event--conflict'] : [],
          extendedProps: {
            tieneConflicto,
            conflictos,
            materiaId: horario.materia_id,
            materiaNombre: horario.materia_nombre,
            periodoNombre: horario.periodo_nombre,
            docenteId: horario.docente_id,
            docenteNombre: horario.docente_nombre,
            aulaNombre: horario.aula_nombre,
            aulaCapacidad: horario.aula_capacidad,
            originalData: horario,
          },
        }
      })
  }, [horariosFiltrados, conflictosPorHorarioId, vistaCalendario])

  const recursos = useMemo(() => {
    if (vistaCalendario === 'por_aula') {
      const lista = (aulas || []).map((a) => ({ id: String(a.id), title: a.nombre }))
      return recursoSeleccionado ? lista.filter((r) => r.id === String(recursoSeleccionado)) : lista
    }
    if (vistaCalendario === 'por_docente') {
      const lista = (docentes || []).map((d) => ({ id: String(d.id), title: d.nombre }))
      return recursoSeleccionado ? lista.filter((r) => r.id === String(recursoSeleccionado)) : lista
    }
    return []
  }, [vistaCalendario, aulas, docentes, recursoSeleccionado])

  const manejarEliminarSeleccionado = async () => {
    if (!eventoSeleccionado) return
    await eliminarHorario(eventoSeleccionado.originalData.id)
    setEventoSeleccionado(null)
  }

  const handleEventClick = (info) => {
    setEventoSeleccionado(info.event.extendedProps)
  }

  const eventContent = (eventInfo) => {
    const props = eventInfo.event.extendedProps
    if (compacto) {
      return (
        <div className="calendar-event-content calendar-event-compact">
          <strong className="calendar-event-title">{props.materiaNombre || 'Materia'}</strong>
          {props.tieneConflicto && <span className="calendar-event-warning">⚠</span>}
        </div>
      )
    }

    return (
      <div className="calendar-event-content">
        <strong className="calendar-event-title">{props.materiaNombre || 'Materia'}</strong>
        <span>{props.docenteNombre || 'Docente'}</span>
        <span>{props.aulaNombre || 'Aula'}</span>
        {props.tieneConflicto && <span className="calendar-event-warning">Conflicto</span>}
      </div>
    )
  }

  const eventDidMount = (eventInfo) => {
    const props = eventInfo.event.extendedProps
    const conflictoTexto = props.tieneConflicto
      ? `\nConflictos: ${props.conflictos.join(' | ')}`
      : ''

    eventInfo.el.title = `${props.materiaNombre || 'Materia'}\n${props.docenteNombre || 'Docente'}\n${props.aulaNombre || 'Aula'}${conflictoTexto}`
  }

  return (
    <>
      <div className="calendar-container">
        <FullCalendar
          key={[
            vistaCalendario,
            compacto ? 'compacto' : 'detallado',
            filtroDocente || 'all-docentes',
            filtroMateria || 'all-materias',
            filtroAula || 'all-aulas',
            filtroPeriodo || 'all-periodos',
            recursoSeleccionado || 'all-recursos',
          ].join('|')}
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin, resourceTimeGridPlugin]}
          headerToolbar={{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay',
          }}
          events={eventosCalendario}
          resources={recursos}
          resourceAreaHeaderContent={vistaCalendario === 'por_aula' ? 'Aulas' : vistaCalendario === 'por_docente' ? 'Docentes' : ''}
          initialView={vistaCalendario === 'por_aula' || vistaCalendario === 'por_docente' ? 'resourceTimeGridWeek' : 'timeGridWeek'}
          eventClick={handleEventClick}
          eventContent={eventContent}
          eventDidMount={eventDidMount}
          height="auto"
          contentHeight="auto"
          slotDuration="01:00:00"
          slotLabelInterval="01:00:00"
          slotLabelFormat={{
            hour: '2-digit',
            minute: '2-digit',
            meridiem: false,
            omitZeroMinute: false,
          }}
          dayMaxEventRows={false}
          locale={esLocale}
          allDaySlot={false}
          firstDay={1}
          weekends={true}
          eventDisplay="block"
          eventTimeFormat={{
            hour: '2-digit',
            minute: '2-digit',
            meridiem: false,
          }}
          slotMinTime="07:00:00"
          slotMaxTime="23:00:00"
          editable={false}
          selectable={false}
          businessHours={false}
          slotEventOverlap={false}
          nowIndicator={true}
        />
      </div>

      {eventoSeleccionado && (
        <Modal title={eventoSeleccionado.materiaNombre || 'Materia'} titleId="evento-horario-modal-title" onClose={() => setEventoSeleccionado(null)} actions={<>
          <button type="button" className="button-alt" onClick={() => setEventoSeleccionado(null)}>
            Cerrar
          </button>
          {isAdmin && (
            <button type="button" className="btn btn--danger" onClick={manejarEliminarSeleccionado}>
              Eliminar horario
            </button>
          )}
        </>}>
            <p>
              <strong>Docente:</strong> {eventoSeleccionado.docenteNombre || 'Docente no disponible'}
            </p>
            <p>
              <strong>Aula:</strong> {eventoSeleccionado.aulaNombre || 'Aula no disponible'}
            </p>
            <p>
              <strong>Horario:</strong> {eventoSeleccionado.originalData.hora_inicio} - {eventoSeleccionado.originalData.hora_fin}
            </p>
            <p>
              <strong>Dia:</strong> {eventoSeleccionado.originalData.dia}
            </p>
            {eventoSeleccionado.tieneConflicto && (
              <div className="calendar-modal-warning">
                <strong>Conflictos detectados:</strong>
                <ul>
                  {eventoSeleccionado.conflictos.map((conflicto, indice) => (
                    <li key={`${eventoSeleccionado.originalData.id}-${indice}`}>{conflicto}</li>
                  ))}
                </ul>
              </div>
            )}
        </Modal>
      )}
    </>
  )
}
