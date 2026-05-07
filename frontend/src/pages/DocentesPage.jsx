import { useState } from 'react'
import Modal from '../components/Modal'

const emptyDocente = { matricula: '', nombre: '', correo: '', password: '', role: 'DOCENTE', turno: 'AMBOS', estado: true }

const TURNOS_DOCENTE = [
  { value: 'MATUTINO', label: 'Matutino' },
  { value: 'VESPERTINO', label: 'Vespertino' },
  { value: 'AMBOS', label: 'Ambos' },
]

function DocentesPage({ isAdmin, docentes, onCreate, onUpdate, onDelete }) {
  const [form, setForm] = useState(emptyDocente)
  const [editingId, setEditingId] = useState(null)
  const [busy, setBusy] = useState(false)
  const [docentePendienteEliminar, setDocentePendienteEliminar] = useState(null)

  function resetForm() {
    setForm(emptyDocente)
    setEditingId(null)
  }

  function startEdit(docente) {
    setEditingId(docente.id)
    setForm({
      matricula: docente.matricula || '',
      nombre: docente.nombre || '',
      correo: docente.correo || '',
      password: '',
      role: docente.rol || 'DOCENTE',
      turno: docente.turno || 'AMBOS',
      estado: Boolean(docente.estado),
    })
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)

    try {
      const payload = {
        matricula: form.matricula || null,
        nombre: form.nombre,
        correo: form.correo,
        role: form.role,
        turno: form.turno,
        estado: Boolean(form.estado),
      }

      if (form.password) {
        payload.password = form.password
      }

      if (editingId) {
        await onUpdate(editingId, payload)
      } else {
        if (!form.password) {
          throw new Error('La contraseña es obligatoria al crear un docente')
        }
        await onCreate({ ...payload, password: form.password })
      }

      resetForm()
    } finally {
      setBusy(false)
    }
  }

  async function handleDelete() {
    if (!docentePendienteEliminar) return
    setBusy(true)
    try {
      await onDelete(docentePendienteEliminar.id)
      setDocentePendienteEliminar(null)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="catalogs single">
      {isAdmin && (
        <article className="card">
          <h3>{editingId ? 'Editar docente' : 'Nuevo docente'}</h3>
          <form onSubmit={handleSubmit} className="form">
            <label>
              Matricula
              <input value={form.matricula} onChange={(e) => setForm((prev) => ({ ...prev, matricula: e.target.value }))} />
            </label>
            <label>
              Nombre
              <input value={form.nombre} onChange={(e) => setForm((prev) => ({ ...prev, nombre: e.target.value }))} required />
            </label>
            <label>
              Correo
              <input type="email" value={form.correo} onChange={(e) => setForm((prev) => ({ ...prev, correo: e.target.value }))} required />
            </label>
            <label>
              Password {editingId ? '(opcional)' : ''}
              <input type="password" value={form.password} onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))} required={!editingId} />
            </label>
            <label>
              Rol
              <select value={form.role} onChange={(e) => setForm((prev) => ({ ...prev, role: e.target.value }))}>
                <option value="DOCENTE">DOCENTE</option>
                <option value="ADMIN">ADMIN</option>
              </select>
            </label>
              <label>
                Turno
                <select value={form.turno} onChange={(e) => setForm((prev) => ({ ...prev, turno: e.target.value }))}>
                  {TURNOS_DOCENTE.map((turno) => (
                    <option key={turno.value} value={turno.value}>
                      {turno.label}
                    </option>
                  ))}
                </select>
              </label>
            <label>
              Estado
              <select value={form.estado ? 'true' : 'false'} onChange={(e) => setForm((prev) => ({ ...prev, estado: e.target.value === 'true' }))}>
                <option value="true">Activo</option>
                <option value="false">Inactivo</option>
              </select>
            </label>
            <button type="submit" disabled={busy}>{busy ? 'Guardando...' : editingId ? 'Actualizar' : 'Crear docente'}</button>
            {editingId && (
              <button type="button" className="button-alt" onClick={resetForm} disabled={busy}>
                Cancelar edición
              </button>
            )}
          </form>
        </article>
      )}

      <article className="card">
        <h3>Docentes</h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Matricula</th>
                <th>Correo</th>
                <th>Rol</th>
                <th>Turno</th>
                <th>Estado</th>
                {isAdmin && <th>Acciones</th>}
              </tr>
            </thead>
            <tbody>
              {docentes.map((d) => (
                <tr key={d.id}>
                  <td>{d.nombre}</td>
                  <td>{d.matricula || '-'}</td>
                  <td>{d.correo}</td>
                  <td>{d.role || d.rol || 'DOCENTE'}</td>
                  <td>{d.turno || 'AMBOS'}</td>
                  <td>{d.estado ? 'Activo' : 'Inactivo'}</td>
                  {isAdmin && (
                    <td>
                      <div className="row-actions">
                        <button type="button" onClick={() => startEdit(d)} disabled={busy}>Editar</button>
                        <button type="button" className="button-alt" onClick={() => setDocentePendienteEliminar(d)} disabled={busy}>Eliminar</button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>

      {docentePendienteEliminar && (
        <Modal title="Confirmar eliminacion" titleId="confirmar-eliminar-docente-title" onClose={() => setDocentePendienteEliminar(null)} actions={<>
          <button type="button" className="btn" onClick={() => setDocentePendienteEliminar(null)} disabled={busy}>Cancelar</button>
          <button type="button" className="btn btn--danger" onClick={handleDelete} disabled={busy}>
            {busy ? 'Eliminando...' : 'Eliminar'}
          </button>
        </>}>
          <p>Vas a eliminar al docente <strong>{docentePendienteEliminar.nombre}</strong>.</p>
        </Modal>
      )}
    </section>
  )
}

export default DocentesPage
