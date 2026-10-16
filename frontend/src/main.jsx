import React, {useEffect, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import './styles.css';
const statuses = ['TODO', 'IN_PROGRESS', 'DONE'];
const label = value => value.replaceAll('_', ' ');
const blank = {title:'', description:'', assignee:'Demo Student', priority:'MEDIUM', status:'TODO'};
async function api(path='', options={}) {
  const response = await fetch(`/api/tasks${path}`, options);
  if (!response.ok) {
    let detail;
    try { detail = (await response.json()).detail; } catch { /* proxy may return HTML */ }
    throw Error(typeof detail === 'string' ? detail : `Request failed (${response.status}). Please retry.`);
  }
  return response.status === 204 ? null : response.json();
}
function App() {
  const [tasks,setTasks] = useState([]), [stats,setStats] = useState({total:0,todo:0,inProgress:0,done:0});
  const [filter,setFilter] = useState('ALL'), [priority,setPriority] = useState('ALL'), [search,setSearch] = useState('');
  const [loading,setLoading] = useState(true), [error,setError] = useState(''), [busy,setBusy] = useState(false);
  const [editing,setEditing] = useState(null), [form,setForm] = useState(blank), [events,setEvents] = useState([]);
  const [formError,setFormError] = useState('');
  const dialog = useRef(null);
  const load = async () => {
    setLoading(true);
    try { const [rows,counts] = await Promise.all([api(),api('/stats')]); setTasks(rows); setStats(counts); setError(''); }
    catch(e) { setError(e.message); } finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);
  const record = text => setEvents(previous => [{text,time:new Date().toLocaleTimeString()},...previous].slice(0,5));
  const open = task => {
    setEditing(task?.id ?? null);
    setForm(task ? Object.fromEntries(Object.keys(blank).map(k=>[k,task[k]])) : {...blank});
    setFormError(''); dialog.current.showModal();
  };
  const save = async event => {
    event.preventDefault(); setBusy(true); setFormError('');
    try {
      await api(editing ? `/${editing}` : '', {method:editing?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(form)});
      record(`${editing?'Updated':'Created'}: ${form.title}`); dialog.current.close(); await load();
    } catch(e) { setFormError(e.message); } finally { setBusy(false); }
  };
  const remove = async task => {
    if (!window.confirm(`Delete “${task.title}”?`)) return;
    setBusy(true);
    try { await api(`/${task.id}`,{method:'DELETE'}); record(`Deleted: ${task.title}`); await load(); }
    catch(e) { setError(e.message); } finally { setBusy(false); }
  };
  const visible = tasks.filter(t=>(filter==='ALL'||t.status===filter)&&(priority==='ALL'||t.priority===priority)&&`${t.title} ${t.assignee} ${t.description}`.toLowerCase().includes(search.toLowerCase()));
  return <div className="app">
    <aside className="sidebar"><div className="brand"><span className="brand-mark">T</span><div><b>Release Helpdesk</b><small>DevOps service desk</small></div></div>
      <nav aria-label="Workspace"><a className="active" href="#tasks">▦ <span>Ticket dashboard</span></a><a href="/docs" target="_blank" rel="noreferrer">↗ <span>API documentation</span></a></nav>
      <div className="side-bottom"><div className="upgrade"><strong>Triage. Resolve. Ship.</strong><p>Track deployment incidents and service requests through resolution.</p></div><div className="profile"><div className="avatar">DS</div><div><b>Demo workspace</b><small>Synthetic classroom data</small></div></div></div>
    </aside>
    <main className="main"><header><div><p className="eyebrow">WORKSPACE / OVERVIEW</p><h1>Unblock the next release.</h1><p className="muted">Triage deployment issues, access requests and release follow-ups.</p></div><button className="primary" onClick={()=>open(null)}>＋ New ticket</button></header>
      {error&&<div className="alert" role="alert">{error} <button onClick={load}>Retry</button></div>}
      <section className="stats" aria-label="Ticket statistics">{[['Total tickets',stats.total],['To do',stats.todo],['In progress',stats.inProgress],['Completed',stats.done]].map(([name,count])=><div className="stat" key={name}><div className="stat-icon">{name==='Completed'?'✓':'▦'}</div><div><small>{name}</small><strong>{count}</strong><span>From the task database</span></div></div>)}</section>
      <section className="content-grid"><div className="panel" id="tasks"><div className="panel-head"><div><h2>Release tickets</h2><p className="muted">Incidents and requests, owned and organized.</p></div><button className="icon-btn" onClick={load} disabled={loading}>Refresh</button></div>
        <div className="toolbar"><label>Search<input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Title, description or assignee"/></label><label>Status<select value={filter} onChange={e=>setFilter(e.target.value)}>{['ALL',...statuses].map(x=><option key={x}>{x}</option>)}</select></label><label>Priority<select value={priority} onChange={e=>setPriority(e.target.value)}>{['ALL','HIGH','MEDIUM','LOW'].map(x=><option key={x}>{x}</option>)}</select></label></div>
        {loading?<div className="empty" role="status">Loading tickets…</div>:<div className="table-wrap"><table><thead><tr><th>Ticket</th><th>Assignee</th><th>Priority</th><th>Status</th><th>Actions</th></tr></thead><tbody>{visible.map(t=><tr key={t.id}><td><div className="task-title"><span className={`dot ${t.status.toLowerCase()}`}/><div><b>{t.title}</b><small>{t.description}</small></div></div></td><td>{t.assignee}</td><td><span className={`priority ${t.priority.toLowerCase()}`}>{t.priority}</span></td><td><span className={`status ${t.status.toLowerCase()}`}>{label(t.status)}</span></td><td className="actions"><button className="icon-btn" disabled={busy} onClick={()=>open(t)} aria-label={`Edit ${t.title}`}>Edit</button><button className="icon-btn danger" disabled={busy} onClick={()=>remove(t)} aria-label={`Delete ${t.title}`}>Delete</button></td></tr>)}</tbody></table>{!visible.length&&<div className="empty">{tasks.length?'No tickets match these filters.':'The queue is clear. Open your first release ticket.'}</div>}</div>}
      </div><aside className="panel activity"><div className="panel-head"><div><h2>Session activity</h2><p className="muted">Actions taken in this browser session.</p></div></div>{events.length?events.map((e,i)=><div className="activity-row" key={i}><span className="activity-icon">✓</span><div><b>{e.text}</b><small>{e.time}</small></div></div>):<p className="empty">Your changes will appear here.</p>}<div className="pipeline">Git → Test → Build → Scan → Deploy</div><p className="empty">Delivery sequence • see GitHub Actions for actual run status.</p></aside></section>
      <dialog ref={dialog} aria-labelledby="task-form-title"><form className="modal" onSubmit={save}><div className="modal-head"><h2 id="task-form-title">{editing?'Edit ticket':'Open a release ticket'}</h2><button type="button" className="close" aria-label="Close" disabled={busy} onClick={()=>dialog.current.close()}>×</button></div>
      {formError&&<p className="alert" role="alert">{formError}</p>}
      <label>Ticket title<input autoFocus required maxLength={200} value={form.title} onChange={e=>setForm({...form,title:e.target.value})}/></label>
      <label>Description<textarea maxLength={10000} value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/></label>
      <div className="form-row"><label>Priority<select aria-label="Priority" value={form.priority} onChange={e=>setForm({...form,priority:e.target.value})}>{['LOW','MEDIUM','HIGH'].map(x=><option key={x}>{x}</option>)}</select></label><label>Status<select aria-label="Status" value={form.status} onChange={e=>setForm({...form,status:e.target.value})}>{statuses.map(x=><option key={x}>{x}</option>)}</select></label></div>
      <label>Assignee<input required maxLength={120} value={form.assignee} onChange={e=>setForm({...form,assignee:e.target.value})}/></label><button className="primary full" disabled={busy}>{busy?'Saving…':editing?'Save changes':'Create ticket'}</button></form></dialog>
    </main></div>;
}
createRoot(document.getElementById('root')).render(<App/>);
