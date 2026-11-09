import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const emptyVehicle = { plate: "", owner: "", kind: "Automóvil", color: "" };
const localDate = (value) => {
  const d = value ? new Date(value) : new Date();
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16);
};
const emptyTicket = () => ({
  vehicle_id: "",
  entry_at: localDate(),
  exit_at: "",
  hourly_rate: "10.00",
});
const money = (v) =>
  new Intl.NumberFormat("es-GT", { style: "currency", currency: "GTQ" }).format(
    v,
  );
const date = (v) => new Date(v).toLocaleString("es-GT");
async function api(service, path, method = "GET", body) {
  const response = await fetch(`/api/${service}/${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(
      typeof error.detail === "string"
        ? error.detail
        : Array.isArray(error.detail)
          ? error.detail.map((e) => `${e.loc.at(-1)}: ${e.msg}`).join(" · ")
          : `Error HTTP ${response.status}`,
    );
  }
  return response.status === 204 ? null : response.json();
}
async function all(service, path) {
  let result = [],
    offset = 0;
  while (true) {
    const page = await api(service, `${path}?limit=200&offset=${offset}`);
    result = result.concat(page);
    if (page.length < 200) return result;
    offset += 200;
  }
}
function App() {
  const [tab, setTab] = useState("tickets");
  const [vehicles, setVehicles] = useState([]),
    [tickets, setTickets] = useState([]),
    [members, setMembers] = useState([]);
  const [vehicle, setVehicle] = useState(emptyVehicle),
    [ticket, setTicket] = useState(emptyTicket);
  const [vehicleId, setVehicleId] = useState(null),
    [ticketId, setTicketId] = useState(null);
  const [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false),
    [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  async function load() {
    const [v, t, m] = await Promise.all([
      all("vehicles", "vehicles"),
      all("tickets", "tickets"),
      api("vehicles", "members"),
    ]);
    setVehicles(v);
    setTickets(t);
    setMembers(m);
  }
  useEffect(() => {
    load()
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);
  async function action(fn, message) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await fn();
      await load();
      setNotice(message);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  function saveVehicle(e) {
    e.preventDefault();
    action(async () => {
      await api(
        "vehicles",
        `vehicles${vehicleId ? `/${vehicleId}` : ""}`,
        vehicleId ? "PUT" : "POST",
        vehicle,
      );
      setVehicle(emptyVehicle);
      setVehicleId(null);
    }, "Vehículo guardado");
  }
  function saveTicket(e) {
    e.preventDefault();
    action(async () => {
      await api(
        "tickets",
        `tickets${ticketId ? `/${ticketId}` : ""}`,
        ticketId ? "PUT" : "POST",
        {
          vehicle_id: Number(ticket.vehicle_id),
          entry_at: new Date(ticket.entry_at).toISOString(),
          exit_at: ticket.exit_at
            ? new Date(ticket.exit_at).toISOString()
            : null,
          hourly_rate: ticket.hourly_rate,
        },
      );
      setTicket(emptyTicket());
      setTicketId(null);
    }, "Ticket guardado");
  }
  function remove(service, id) {
    if (
      window.confirm(
        "¿Eliminar este registro? Esta acción no se puede deshacer.",
      )
    )
      action(
        () => api(service, `${service}/${id}`, "DELETE"),
        "Registro eliminado",
      );
  }
  const plate = (id) => vehicles.find((v) => v.id === id)?.plate || `#${id}`;
  const active = tickets.filter((t) => !t.exit_at).length;
  return (
    <div className="app">
      <aside>
        <a className="brand" href="/">
          G
          <span>
            GlitchTec<small>PARQUEO PÚBLICO</small>
          </span>
        </a>
        <div className="nav-label">ADMINISTRACIÓN</div>
        <nav aria-label="Principal">
          {[
            ["tickets", "◷", "Tickets de estadía"],
            ["vehicles", "▱", "Vehículos"],
            ["team", "◎", "Nuestro equipo"],
          ].map(([id, icon, label]) => (
            <button
              key={id}
              className={tab === id ? "selected" : ""}
              onClick={() => {
                setTab(id);
                setSearch("");
              }}
            >
              <span>{icon}</span>
              {label}
            </button>
          ))}
        </nav>
        <div className="sidebar-foot">
          <span className="dot" /> Caso 03 · URL
          <br />
          <small>Virtualización · Proyecto final 2026</small>
        </div>
      </aside>
      <main>
        <header>
          <div>
            <div className="eyebrow">GLITCHTEC / OPERACIONES</div>
            <h1>
              {tab === "tickets"
                ? "Cada estadía, bajo control."
                : tab === "vehicles"
                  ? "Tu registro de vehículos."
                  : "Las personas detrás del proyecto."}
            </h1>
            <p>Parqueo público · Universidad Rafael Landívar</p>
          </div>
          <button
            className="refresh"
            disabled={busy}
            onClick={() => action(load, "Datos actualizados")}
          >
            ↻ Actualizar
          </button>
        </header>
        {error && (
          <div className="alert error" role="alert">
            {error}{" "}
            <button onClick={() => action(load, "Conexión restablecida")}>
              Reintentar
            </button>
          </div>
        )}
        {notice && (
          <div className="alert success" role="status">
            {notice}
          </div>
        )}
        <section className="stats" aria-label="Resumen">
          <article>
            <span>Vehículos registrados</span>
            <strong>{vehicles.length.toString().padStart(2, "0")}</strong>
            <small>Registro centralizado</small>
          </article>
          <article>
            <span>Estadías activas</span>
            <strong>{active.toString().padStart(2, "0")}</strong>
            <small>
              <span className="dot" /> En el parqueo
            </small>
          </article>
          <article>
            <span>Ingresos de tickets cerrados</span>
            <strong>
              {money(tickets.reduce((sum, t) => sum + Number(t.total || 0), 0))}
            </strong>
            <small>Tarifa por hora o fracción</small>
          </article>
        </section>
        {loading ? (
          <div className="panel">Conectando con los microservicios…</div>
        ) : tab === "team" ? (
          <section className="panel">
            <div className="section-title">
              <h2>Equipo GlitchTec</h2>
              <span className="tag">DATOS DESDE POSTGRESQL</span>
            </div>
            <div className="team">
              {members.map((m) => (
                <article key={m.student_id}>
                  <div className="avatar">
                    {m.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </div>
                  <h3>{m.name}</h3>
                  <p>
                    Carné <strong>{m.student_id}</strong>
                  </p>
                </article>
              ))}
            </div>
          </section>
        ) : (
          <div className="workspace">
            <section className="panel records">
              <div className="section-title">
                <h2>
                  {tab === "tickets" ? "Tickets de estadía" : "Vehículos"}
                </h2>
                <span className="tag">
                  {tab === "tickets" ? tickets.length : vehicles.length}{" "}
                  REGISTROS
                </span>
              </div>
              <input
                className="search"
                aria-label="Buscar por placa"
                placeholder="Buscar por placa…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      {(tab === "vehicles"
                        ? ["Placa / propietario", "Tipo / color", "Acciones"]
                        : [
                            "Ticket / vehículo",
                            "Entrada / salida",
                            "Estado / total",
                            "Acciones",
                          ]
                      ).map((h) => (
                        <th key={h}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tab === "vehicles"
                      ? vehicles
                          .filter((v) =>
                            v.plate
                              .toLowerCase()
                              .includes(search.toLowerCase()),
                          )
                          .map((v) => (
                            <tr key={v.id}>
                              <td>
                                <strong className="plate">{v.plate}</strong>
                                <small>{v.owner}</small>
                              </td>
                              <td>
                                {v.kind}
                                <small>{v.color}</small>
                              </td>
                              <td className="actions">
                                <button
                                  disabled={busy}
                                  onClick={() => {
                                    setVehicle({ ...v });
                                    setVehicleId(v.id);
                                  }}
                                >
                                  Editar
                                </button>
                                <button
                                  disabled={busy}
                                  className="danger"
                                  onClick={() => remove("vehicles", v.id)}
                                >
                                  Eliminar
                                </button>
                              </td>
                            </tr>
                          ))
                      : tickets
                          .filter((t) =>
                            plate(t.vehicle_id)
                              .toLowerCase()
                              .includes(search.toLowerCase()),
                          )
                          .map((t) => (
                            <tr key={t.id}>
                              <td>
                                <strong>
                                  #{String(t.id).padStart(4, "0")}
                                </strong>
                                <small className="plate">
                                  {plate(t.vehicle_id)}
                                </small>
                              </td>
                              <td>
                                {date(t.entry_at)}
                                <small>
                                  {t.exit_at ? date(t.exit_at) : "En curso"}
                                </small>
                              </td>
                              <td>
                                <span
                                  className={`badge ${t.exit_at ? "closed" : ""}`}
                                >
                                  {t.status}
                                </span>
                                <small>
                                  {t.total
                                    ? money(t.total)
                                    : `${money(t.hourly_rate)} / h`}
                                </small>
                              </td>
                              <td className="actions">
                                <button
                                  disabled={busy}
                                  onClick={() => {
                                    setTicket({
                                      vehicle_id: t.vehicle_id,
                                      entry_at: localDate(t.entry_at),
                                      exit_at: t.exit_at
                                        ? localDate(t.exit_at)
                                        : "",
                                      hourly_rate: t.hourly_rate,
                                    });
                                    setTicketId(t.id);
                                  }}
                                >
                                  Editar / salida
                                </button>
                                <button
                                  disabled={busy}
                                  className="danger"
                                  onClick={() => remove("tickets", t.id)}
                                >
                                  Eliminar
                                </button>
                              </td>
                            </tr>
                          ))}
                  </tbody>
                </table>
                {!(tab === "vehicles" ? vehicles : tickets).length && (
                  <div className="empty">
                    <span>＋</span>
                    <h3>Todo listo para empezar</h3>
                    <p>
                      {tab === "vehicles"
                        ? "Registra el primer vehículo en el formulario."
                        : "Registra un vehículo y crea su primera estadía."}
                    </p>
                  </div>
                )}
              </div>
            </section>
            <section className="panel editor">
              <div className="section-title">
                <h2>
                  {tab === "vehicles"
                    ? vehicleId
                      ? "Editar vehículo"
                      : "Nuevo vehículo"
                    : ticketId
                      ? "Editar estadía"
                      : "Nueva estadía"}
                </h2>
                <span className="form-icon">＋</span>
              </div>
              {tab === "vehicles" ? (
                <form onSubmit={saveVehicle}>
                  <label>
                    Placa
                    <input
                      required
                      minLength={3}
                      maxLength={12}
                      pattern="[a-zA-Z0-9-]{3,12}"
                      placeholder="P123ABC"
                      value={vehicle.plate}
                      onChange={(e) =>
                        setVehicle({
                          ...vehicle,
                          plate: e.target.value.toUpperCase(),
                        })
                      }
                    />
                  </label>
                  <label>
                    Propietario
                    <input
                      required
                      maxLength={100}
                      value={vehicle.owner}
                      onChange={(e) =>
                        setVehicle({ ...vehicle, owner: e.target.value })
                      }
                    />
                  </label>
                  <label>
                    Tipo
                    <select
                      value={vehicle.kind}
                      onChange={(e) =>
                        setVehicle({ ...vehicle, kind: e.target.value })
                      }
                    >
                      {["Automóvil", "Motocicleta", "Pickup", "Otro"].map(
                        (k) => (
                          <option key={k}>{k}</option>
                        ),
                      )}
                    </select>
                  </label>
                  <label>
                    Color
                    <input
                      required
                      maxLength={40}
                      value={vehicle.color}
                      onChange={(e) =>
                        setVehicle({ ...vehicle, color: e.target.value })
                      }
                    />
                  </label>
                  <button className="primary" disabled={busy}>
                    {busy ? "Guardando…" : "Guardar vehículo"}
                  </button>
                  {vehicleId && (
                    <button
                      type="button"
                      onClick={() => {
                        setVehicleId(null);
                        setVehicle(emptyVehicle);
                      }}
                    >
                      Cancelar edición
                    </button>
                  )}
                  <p className="hint">
                    Para eliminar un vehículo, elimina primero sus tickets
                    vinculados.
                  </p>
                </form>
              ) : (
                <form onSubmit={saveTicket}>
                  <label>
                    Vehículo
                    <select
                      required
                      value={ticket.vehicle_id}
                      onChange={(e) =>
                        setTicket({ ...ticket, vehicle_id: e.target.value })
                      }
                    >
                      <option value="">Seleccionar placa</option>
                      {vehicles.map((v) => (
                        <option key={v.id} value={v.id}>
                          {v.plate} · {v.owner}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Entrada
                    <input
                      required
                      type="datetime-local"
                      value={ticket.entry_at}
                      onChange={(e) =>
                        setTicket({ ...ticket, entry_at: e.target.value })
                      }
                    />
                  </label>
                  <label>
                    Salida <span className="optional">opcional</span>
                    <input
                      type="datetime-local"
                      min={ticket.entry_at}
                      value={ticket.exit_at}
                      onChange={(e) =>
                        setTicket({ ...ticket, exit_at: e.target.value })
                      }
                    />
                  </label>
                  {ticketId && (
                    <button
                      type="button"
                      onClick={() =>
                        setTicket({ ...ticket, exit_at: localDate() })
                      }
                    >
                      Registrar salida ahora
                    </button>
                  )}
                  <label>
                    Tarifa por hora (Q)
                    <input
                      required
                      type="number"
                      min="0.01"
                      max="999999"
                      step="0.01"
                      value={ticket.hourly_rate}
                      onChange={(e) =>
                        setTicket({ ...ticket, hourly_rate: e.target.value })
                      }
                    />
                  </label>
                  <button
                    className="primary"
                    disabled={busy || !vehicles.length}
                  >
                    {busy ? "Guardando…" : "Guardar ticket"}
                  </button>
                  {ticketId && (
                    <button
                      type="button"
                      onClick={() => {
                        setTicketId(null);
                        setTicket(emptyTicket());
                      }}
                    >
                      Cancelar edición
                    </button>
                  )}
                  <p className="hint">
                    Se cobra por hora o fracción, con mínimo de una hora. Solo
                    una estadía activa por vehículo.
                  </p>
                </form>
              )}
            </section>
          </div>
        )}
        <footer>
          GlitchTec <span>Construido desde cero · Caso 03 · 2026</span>
        </footer>
      </main>
    </div>
  );
}
createRoot(document.getElementById("root")).render(<App />);
