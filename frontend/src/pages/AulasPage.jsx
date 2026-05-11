import { useState } from 'react'
import Modal from '../components/Modal'

const emptyAula = { nombre: '', capacidad: '0' }

function AulasPage({ isAdmin, aulas, onCreate, onUpdate, onDelete }) {
  const [form, setForm] = useState(emptyAula)
  const [editingId, setEditingId] = useState(null)
  const [busy, setBusy] = useState(false)
  const [aulaPendienteEliminar, setAulaPendienteEliminar] = useState(null)
  const [formError, setFormError] = useState('')

  function resetForm() {
    setForm(emptyAula)
    setEditingId(null)
    setFormError('')
  }

  function startEdit(aula) {
    setEditingId(aula.id)
    setForm({ nombre: aula.nombre || '', capacidad: String(aula.capacidad ?? 0) })
    setFormError('')
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setFormError('')

    try {
      const payload = {
        nombre: form.nombre,
        capacidad: Number(form.capacidad),
      }

      if (editingId) {
        await onUpdate(editingId, payload)
      } else {
        await onCreate(payload)
      }

      resetForm()
    } catch (error) {
      setFormError(error.message || 'No se pudo guardar el aula.')
    } finally {
      setBusy(false)
    }
  }

  async function handleDelete() {
    if (!aulaPendienteEliminar) return
    setBusy(true)
    try {
      await onDelete(aulaPendienteEliminar.id)
      setAulaPendienteEliminar(null)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="catalogs single">
      {isAdmin && (
        <article className="card">
          <h3>{editingId ? 'Editar aula' : 'Nueva aula'}</h3>
          <form onSubmit={handleSubmit} className="form">
            <label>
              Nombre
              <input
                value={form.nombre}
                onChange={(e) => {
                  setForm((prev) => ({ ...prev, nombre: e.target.value }))
                  if (formError) setFormError('')
                }}
                required
              />
            </label>
            <label>
              Capacidad
              <input
                type="number"
                min="1"
                value={form.capacidad}
                onChange={(e) => {
                  setForm((prev) => ({ ...prev, capacidad: e.target.value }))
                  if (formError) setFormError('')
                }}
                required
              />
            </label>
            {formError && (
              <div className="feedback" style={{ gridColumn: '1 / -1' }}>
                <p className="feedback__error">{formError}</p>
              </div>
            )}
            <button type="submit" disabled={busy}>{busy ? 'Guardando...' : editingId ? 'Actualizar' : 'Crear aula'}</button>
            {editingId && (
              <button type="button" className="button-alt" onClick={resetForm} disabled={busy}>
                Cancelar edición
              </button>
            )}
          </form>
        </article>
      )}

      <article className="card">
        <h3>Aulas</h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Capacidad</th>
                {isAdmin && <th>Acciones</th>}
              </tr>
            </thead>
            <tbody>
              {aulas.map((aula) => (
                <tr key={aula.id}>
                  <td>{aula.nombre}</td>
                  <td>{aula.capacidad ?? 'N/D'}</td>
                  {isAdmin && (
                    <td>
                      <div className="row-actions">
                        <button type="button" onClick={() => startEdit(aula)} disabled={busy}>Editar</button>
                        <button type="button" className="button-alt" onClick={() => setAulaPendienteEliminar(aula)} disabled={busy}>Eliminar</button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!isAdmin && (
          <ul className="list-grid">
            {aulas.map((a) => (
              <li key={a.id}>
                <strong>{a.nombre}</strong>
                <span>Capacidad: {a.capacidad ?? 'N/D'}</span>
              </li>
            ))}
          </ul>
        )}
      </article>

      {aulaPendienteEliminar && (
        <Modal title="Confirmar eliminacion" titleId="confirmar-eliminar-aula-title" onClose={() => setAulaPendienteEliminar(null)} actions={<>
          <button type="button" className="btn" onClick={() => setAulaPendienteEliminar(null)} disabled={busy}>Cancelar</button>
          <button type="button" className="btn btn--danger" onClick={handleDelete} disabled={busy}>
            {busy ? 'Eliminando...' : 'Eliminar'}
          </button>
        </>}>
          <p>Vas a eliminar el aula <strong>{aulaPendienteEliminar.nombre}</strong>.</p>
        </Modal>
      )}
    </section>
  )
}

export default AulasPage
