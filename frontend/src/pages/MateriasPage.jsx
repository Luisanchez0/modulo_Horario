import { useState } from 'react'
import Modal from '../components/Modal'

const emptyMateria = { nombre: '', codigo: '', creditos: '0', turno: 'AMBOS', descripcion: '' }

const TURNOS_MATERIA = [
  { value: 'MATUTINO', label: 'Matutino' },
  { value: 'VESPERTINO', label: 'Vespertino' },
  { value: 'AMBOS', label: 'Ambos' },
]

function MateriasPage({ isAdmin, materias, onCreate, onUpdate, onDelete }) {
  const [form, setForm] = useState(emptyMateria)
  const [editingId, setEditingId] = useState(null)
  const [busy, setBusy] = useState(false)
  const [materiaPendienteEliminar, setMateriaPendienteEliminar] = useState(null)

  function resetForm() {
    setForm(emptyMateria)
    setEditingId(null)
  }

  function startEdit(materia) {
    setEditingId(materia.id)
    setForm({
      nombre: materia.nombre || '',
      codigo: materia.codigo || '',
      creditos: String(materia.creditos ?? 0),
      turno: materia.turno || 'AMBOS',
      descripcion: materia.descripcion || '',
    })
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)

    try {
      const payload = {
        nombre: form.nombre,
        codigo: form.codigo,
        creditos: Number(form.creditos),
        turno: form.turno,
        descripcion: form.descripcion || null,
      }

      if (editingId) {
        await onUpdate(editingId, payload)
      } else {
        await onCreate(payload)
      }

      resetForm()
    } finally {
      setBusy(false)
    }
  }

  async function handleDelete() {
    if (!materiaPendienteEliminar) return
    setBusy(true)
    try {
      await onDelete(materiaPendienteEliminar.id)
      setMateriaPendienteEliminar(null)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="catalogs single">
      {isAdmin && (
        <article className="card">
          <h3>{editingId ? 'Editar materia' : 'Nueva materia'}</h3>
          <form onSubmit={handleSubmit} className="form">
            <label>
              Nombre
              <input value={form.nombre} onChange={(e) => setForm((prev) => ({ ...prev, nombre: e.target.value }))} required />
            </label>
            <label>
              Codigo
              <input value={form.codigo} onChange={(e) => setForm((prev) => ({ ...prev, codigo: e.target.value }))} required />
            </label>
            <label>
              Creditos
              <input type="number" min="1" value={form.creditos} onChange={(e) => setForm((prev) => ({ ...prev, creditos: e.target.value }))} required />
            </label>
            <label>
              Turno
              <select value={form.turno} onChange={(e) => setForm((prev) => ({ ...prev, turno: e.target.value }))}>
                {TURNOS_MATERIA.map((turno) => (
                  <option key={turno.value} value={turno.value}>
                    {turno.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Descripcion
              <input value={form.descripcion} onChange={(e) => setForm((prev) => ({ ...prev, descripcion: e.target.value }))} />
            </label>
            <button type="submit" disabled={busy}>{busy ? 'Guardando...' : editingId ? 'Actualizar' : 'Crear materia'}</button>
            {editingId && (
              <button type="button" className="button-alt" onClick={resetForm} disabled={busy}>
                Cancelar edición
              </button>
            )}
          </form>
        </article>
      )}

      <article className="card">
        <h3>Materias</h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Codigo</th>
                <th>Creditos</th>
                <th>Turno</th>
                <th>Descripcion</th>
                {isAdmin && <th>Acciones</th>}
              </tr>
            </thead>
            <tbody>
              {materias.map((materia) => (
                <tr key={materia.id}>
                  <td>{materia.nombre}</td>
                  <td>{materia.codigo}</td>
                  <td>{materia.creditos}</td>
                  <td>{materia.turno || 'AMBOS'}</td>
                  <td>{materia.descripcion || '-'}</td>
                  {isAdmin && (
                    <td>
                      <div className="row-actions">
                        <button type="button" onClick={() => startEdit(materia)} disabled={busy}>Editar</button>
                        <button type="button" className="button-alt" onClick={() => setMateriaPendienteEliminar(materia)} disabled={busy}>Eliminar</button>
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
            {materias.map((m) => (
              <li key={m.id}>
                <strong>{m.nombre}</strong>
                {m.codigo && <span>Codigo: {m.codigo}</span>}
                <span>Turno: {m.turno || 'AMBOS'}</span>
              </li>
            ))}
          </ul>
        )}
      </article>

      {materiaPendienteEliminar && (
        <Modal title="Confirmar eliminacion" titleId="confirmar-eliminar-materia-title" onClose={() => setMateriaPendienteEliminar(null)} actions={<>
          <button type="button" className="btn" onClick={() => setMateriaPendienteEliminar(null)} disabled={busy}>Cancelar</button>
          <button type="button" className="btn btn--danger" onClick={handleDelete} disabled={busy}>
            {busy ? 'Eliminando...' : 'Eliminar'}
          </button>
        </>}>
          <p>Vas a eliminar la materia <strong>{materiaPendienteEliminar.nombre}</strong>.</p>
        </Modal>
      )}
    </section>
  )
}

export default MateriasPage
