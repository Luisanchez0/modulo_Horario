import { useState } from 'react'
import Modal from '../components/Modal'

function PeriodosPage({
  periodoForm,
  setPeriodoForm,
  crearPeriodo,
  periodos,
  eliminarPeriodo,
  eliminarHorario,
}) {
  const [modalOpen, setModalOpen] = useState(false)
  const [modalDependencias, setModalDependencias] = useState([])
  const [errorModalMessage, setErrorModalMessage] = useState('')

  const mostrarErrorModal = (message) => {
    setErrorModalMessage(message || 'Ocurrio un error inesperado.')
  }

  const cerrarErrorModal = () => {
    setErrorModalMessage('')
  }

  return (
    <section className="grid">
      <details className="card collapsible-card" open>
        <summary>
          <h3>Crear Periodo</h3>
          <span aria-hidden="true">+</span>
        </summary>
        <form onSubmit={crearPeriodo} className="form">
          <label>
            Nombre
            <input
              value={periodoForm.nombre}
              onChange={(e) => setPeriodoForm((prev) => ({ ...prev, nombre: e.target.value }))}
              required
            />
          </label>
          <label>
            Tipo
            <select
              value={periodoForm.tipo}
              onChange={(e) => setPeriodoForm((prev) => ({ ...prev, tipo: e.target.value }))}
            >
              <option value="SEMESTRE">SEMESTRE</option>
              <option value="CUATRIMESTRE">CUATRIMESTRE</option>
            </select>
          </label>
          <label>
            Fecha inicio
            <input
              type="date"
              value={periodoForm.fecha_inicio}
              onChange={(e) =>
                setPeriodoForm((prev) => ({ ...prev, fecha_inicio: e.target.value }))
              }
              required
            />
          </label>
          <label>
            Fecha fin
            <input
              type="date"
              value={periodoForm.fecha_fin}
              onChange={(e) => setPeriodoForm((prev) => ({ ...prev, fecha_fin: e.target.value }))}
              required
            />
          </label>
          <button type="submit">Guardar periodo</button>
        </form>
      </details>

      <details className="card collapsible-card" open>
        <summary>
          <h3>Periodos existentes</h3>
          <span aria-hidden="true">+</span>
        </summary>

        {periodos.length === 0 ? (
          <p className="empty-state">No hay periodos registrados.</p>
        ) : (
          <ul className="periodos-list">
            {periodos.map((p) => (
              <li key={p.id}>
                <div>
                  <strong>{p.nombre}</strong>
                  <span>{p.tipo}</span>
                  <small>
                    {p.fecha_inicio} - {p.fecha_fin}
                  </small>
                </div>

                <div className="row-actions">
                  <button
                    type="button"
                    className="button-alt"
                    onClick={async () => {
                      try {
                        const resp = await eliminarPeriodo(p.id)
                        if (resp && resp.dependencias) {
                          setModalDependencias(resp.dependencias)
                          setModalOpen(true)
                        }
                      } catch (e) {
                        console.error(e)
                        mostrarErrorModal(e.message || 'Error al eliminar periodo')
                      }
                    }}
                  >
                    Eliminar
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </details>

      {errorModalMessage && (
        <Modal title="Se produjo un error" titleId="periodos-error-modal-title" onClose={cerrarErrorModal} actions={<>
          <button className="btn btn--primary" type="button" onClick={cerrarErrorModal}>Entendido</button>
        </>}>
          <p>{errorModalMessage}</p>
        </Modal>
      )}

      {modalOpen && (
        <Modal title="Dependencias encontradas" titleId="periodo-dependencias-modal-title" onClose={() => setModalOpen(false)} actions={<>
          <button type="button" className="btn" onClick={() => setModalOpen(false)}>Cerrar</button>
        </>}>
          <p>El periodo tiene horarios vinculados. Elige que horarios eliminar antes de intentar borrar el periodo.</p>
          <ul className="dependency-list">
            {modalDependencias.map((d) => (
              <li key={d.id}>
                <div>
                  <strong>Horario {d.id}</strong>
                  <span>{d.dia} - {d.hora_inicio} a {d.hora_fin}</span>
                </div>
                <button
                  type="button"
                  className="btn btn--danger"
                  onClick={async () => {
                    try {
                      await eliminarHorario(d.id)
                      setModalDependencias((prev) => prev.filter((x) => x.id !== d.id))
                    } catch (e) {
                      console.error(e)
                      mostrarErrorModal(e.message || 'Error al eliminar horario')
                    }
                  }}
                >
                  Eliminar horario
                </button>
              </li>
            ))}
          </ul>
        </Modal>
      )}
    </section>
  )
}

export default PeriodosPage
