function DashboardPage({ isAdmin, usuarioSesion, docentes, materias, aulas, periodos, horarios }) {
  const nombreDocente = docentes[0]?.nombre || `Docente #${usuarioSesion?.id || 'N/D'}`

  return (
    <>
      <section className="kpis">
        <article>
          <h2>{isAdmin ? docentes.length : 1}</h2>
          <p>{isAdmin ? 'Docentes' : 'Mi perfil'}</p>
        </article>
        <article>
          <h2>{materias.length}</h2>
          <p>{isAdmin ? 'Materias' : 'Mis materias'}</p>
        </article>
        <article>
          <h2>{aulas.length}</h2>
          <p>{isAdmin ? 'Aulas' : 'Aulas asignadas'}</p>
        </article>
        <article>
          <h2>{periodos.length}</h2>
          <p>{isAdmin ? 'Periodos' : 'Periodos activos'}</p>
        </article>
        <article>
          <h2>{horarios.length}</h2>
          <p>{isAdmin ? 'Horarios' : 'Mis horarios'}</p>
        </article>
      </section>

      <section className="catalogs">
        <article className="card mini">
          <h3>{isAdmin ? 'Docentes' : 'Docente en sesion'}</h3>
          <ul>
            {isAdmin
              ? docentes.slice(0, 6).map((d) => <li key={d.id}>{d.nombre}</li>)
              : <li>{nombreDocente}</li>}
          </ul>
        </article>
        <article className="card mini">
          <h3>{isAdmin ? 'Materias' : 'Mis materias'}</h3>
          <ul>
            {materias.slice(0, 6).map((m) => (
              <li key={m.id}>{m.nombre}</li>
            ))}
          </ul>
        </article>
        <article className="card mini">
          <h3>{isAdmin ? 'Aulas' : 'Aulas de mis clases'}</h3>
          <ul>
            {aulas.slice(0, 6).map((a) => (
              <li key={a.id}>{a.nombre}</li>
            ))}
          </ul>
        </article>
      </section>
    </>
  )
}

export default DashboardPage
