import { useEffect, useState } from "react";
import "./App.css";
import Analytics from "./components/Analytics";

const API = "http://127.0.0.1:8000";

const CAT_ICON = {
  Music: "🎵", Fitness: "💪", Finance: "💰", Education: "📚",
  "Health & Fitness": "❤️", Productivity: "⚡", Social: "💬", Entertainment: "🎬",
};
function icon(c) { return CAT_ICON[c] || "📱"; }

/* Number formatters */
function fmtK(v) {
  if (v == null) return "—";
  const n = Number(v);
  if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
  if (n >= 1e3) return (n / 1e3).toFixed(1) + "k";
  return String(n);
}
function fmtPrice(v) { return v == null ? "—" : `₹${Number(v).toFixed(0)}`; }
function fmtScore(v) { return v == null ? "—" : Number(v).toFixed(1); }

export default function App() {
  const [apps,        setApps]        = useState([]);
  const [allApps,     setAllApps]     = useState([]);
  const [selectedApp, setSelectedApp] = useState(null);
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState("");

  const [search,    setSearch]    = useState("");
  const [category,  setCategory]  = useState("");
  const [minRating, setMinRating] = useState("");
  const [maxPrice,  setMaxPrice]  = useState("");
  const [sortBy,    setSortBy]    = useState("id");
  const [order,     setOrder]     = useState("asc");
  const [page,      setPage]      = useState(0);
  const LIMIT = 12;

  const [rankings,       setRankings]       = useState([]);
  const [rankingMetric,  setRankingMetric]  = useState("engagement");
  const [compare1,       setCompare1]       = useState("");
  const [compare2,       setCompare2]       = useState("");
  const [comparison,     setComparison]     = useState(null);
  const [activeSection,  setActiveSection]  = useState("explore");

  /* ── fetch ── */
  useEffect(() => { fetchApps(); }, [search, category, minRating, maxPrice, sortBy, order, page]);

  useEffect(() => {
    fetch(`${API}/apps/?limit=200`)
      .then(r => r.json()).then(setAllApps).catch(console.error);
    fetchRankings("engagement");
  }, []);

  async function fetchApps() {
    setLoading(true); setError("");
    try {
      const p = new URLSearchParams();
      if (search)    p.append("search",    search);
      if (category)  p.append("category",  category);
      if (minRating) p.append("min_rating",minRating);
      if (maxPrice)  p.append("max_price", maxPrice);
      p.append("sort_by", sortBy); p.append("order", order);
      p.append("limit", LIMIT); p.append("offset", page * LIMIT);
      const r = await fetch(`${API}/apps/?${p}`);
      if (!r.ok) throw 0;
      setApps(await r.json());
    } catch { setError("Backend not reachable — run: uvicorn app.main:app --reload"); }
    finally  { setLoading(false); }
  }

  async function fetchRankings(metric) {
    setRankingMetric(metric);
    try {
      const r = await fetch(`${API}/apps/rankings?metric=${metric}&limit=8`);
      if (!r.ok) throw 0;
      setRankings(await r.json());
    } catch(e) { console.error(e); }
  }

  async function compareApps() {
    if (!compare1 || !compare2) return;
    try {
      const r = await fetch(`${API}/apps/compare?app1_id=${compare1}&app2_id=${compare2}`);
      if (!r.ok) throw 0;
      setComparison(await r.json());
    } catch(e) { console.error(e); }
  }

  async function viewDetails(id) {
    try {
      const r = await fetch(`${API}/apps/${id}`);
      if (!r.ok) throw 0;
      setSelectedApp(await r.json());
    } catch(e) { console.error(e); }
  }

  function reset() {
    setSearch(""); setCategory(""); setMinRating(""); setMaxPrice("");
    setSortBy("id"); setOrder("asc"); setPage(0);
  }

  /* Derived computed values */
  const maxDownloads = apps.length ? Math.max(...apps.map(a => a.downloads ?? 0)) || 1 : 1;

  const catCounts = allApps.reduce((acc, a) => { acc[a.category] = (acc[a.category]||0)+1; return acc; }, {});
  const maxCatCount = Math.max(...Object.values(catCounts), 1);

  const rankMax = rankings.length ? Math.max(...rankings.map(a => {
    if (rankingMetric === "engagement") return a.engagement_score ?? 0;
    if (rankingMetric === "popularity") return a.popularity_score ?? 0;
    if (rankingMetric === "rating")     return a.rating ?? 0;
    return a.price_adjusted_value_score ?? 0;
  }), 1) : 1;

  function rankScore(a) {
    if (rankingMetric === "engagement") return a.engagement_score;
    if (rankingMetric === "popularity") return a.popularity_score;
    if (rankingMetric === "rating")     return a.rating;
    return a.price_adjusted_value_score;
  }

  /* Plausible-style "current visitors" = allApps.length */
  const liveCount = allApps.length;

  /* aggregate stats */
  const ratedApps = allApps.filter(a => a.rating != null);
  const avgRating = ratedApps.length
    ? (ratedApps.reduce((s,a) => s + a.rating, 0) / ratedApps.length).toFixed(2)
    : "—";
  const engApps = allApps.filter(a => a.engagement_score != null);
  const avgEng = engApps.length
    ? (engApps.reduce((s,a) => s + a.engagement_score, 0) / engApps.length).toFixed(1)
    : "—";

  /* ─────────────────────────────────────────────── */
  return (
    <>
      {/* ══ TOP NAV ════════════════════════════════ */}
      <nav className="top-nav">
        <div className="nav-brand">
          <div className="nav-logo">A</div>
          <span className="nav-brand-name">AppLen</span>
        </div>
        <div className="nav-right">
          <a className="nav-link" href="#explore">Explore</a>
          <a className="nav-link" href="#rankings">Rankings</a>
          <a className="nav-link" href="#compare">Compare</a>
          <a className="nav-link" href="#analytics">Analytics</a>
        </div>
      </nav>

      {/* ══ SUB-HEADER ════════════════════════════ */}
      <div className="sub-header">
        <div className="sub-left">
          <div className="site-favicon">A</div>
          <span className="site-domain">applen.io</span>
          {liveCount > 0 && (
            <span className="live-badge">
              <span className="live-dot" />
              {liveCount} apps tracked
            </span>
          )}
        </div>
        <div className="sub-right">
          <button className="ctrl-btn" onClick={reset}>⊘ Filter</button>
          {["explore","rankings","compare","analytics"].map(s => (
            <button
              key={s}
              className={`ctrl-btn${activeSection===s?" active":""}`}
              onClick={() => {
                setActiveSection(s);
                document.getElementById(s)?.scrollIntoView({ behavior:"smooth" });
              }}
            >
              {s.charAt(0).toUpperCase()+s.slice(1)}
            </button>
          ))}
          <div className="ctrl-dots" title="More">⋯</div>
        </div>
      </div>

      {/* ══ DASHBOARD ═════════════════════════════ */}
      <main className="dashboard">

        {/* ── BIG TOP CARD — stat bar + placeholder chart ── */}
        <div className="main-card glass-card" id="explore">
          <div className="stat-bar">
            <StatCell label="Total Apps"      value={allApps.length || "—"} active />
            <StatCell label="Categories"      value={Object.keys(catCounts).length || "8"} />
            <StatCell label="Avg Rating"      value={avgRating} />
            <StatCell label="Avg Engagement"  value={avgEng} />
            <StatCell label="Freemium"        value={allApps.filter(a=>a.is_freemium).length || "—"} />
            <StatCell label="Free Trial"      value={allApps.filter(a=>a.has_free_trial).length || "—"} />
          </div>

          {/* Mini area chart placeholder — category distribution bars */}
          <div className="chart-area" style={{ paddingBottom: 20 }}>
            <p style={{ margin:"0 0 14px", fontSize:12, color:"var(--t3)", fontWeight:600, textTransform:"uppercase", letterSpacing:"0.06em" }}>
              Apps per Category
            </p>
            <div style={{ display:"flex", flexDirection:"column", gap:7 }}>
              {Object.entries(catCounts).sort((a,b)=>b[1]-a[1]).map(([cat,cnt]) => (
                <div key={cat} style={{ display:"flex", alignItems:"center", gap:12 }}>
                  <span style={{ width:130, fontSize:12.5, color:"var(--t2)", fontWeight:500, flexShrink:0, textAlign:"right" }}>
                    {icon(cat)} {cat}
                  </span>
                  <div style={{ flex:1, height:20, background:"var(--bg)", borderRadius:4, overflow:"hidden", position:"relative" }}>
                    <div style={{
                      position:"absolute", top:0, left:0, bottom:0,
                      width:`${(cnt/maxCatCount)*100}%`,
                      background:"#6366f1", borderRadius:4,
                      transition:"width 0.5s ease",
                    }} />
                  </div>
                  <span style={{ width:24, fontSize:12.5, fontWeight:700, color:"var(--t1)", textAlign:"right", flexShrink:0 }}>{cnt}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── TWO-COLUMN: Rankings + Category ── */}
        <div className="panels-grid" id="rankings">

          {/* Rankings panel */}
          <div className="panel glass-card">
            <div className="panel-head">
              {["engagement","popularity","rating","value"].map(m => (
                <button
                  key={m}
                  className={`ptab${rankingMetric===m?" active":""}`}
                  onClick={() => fetchRankings(m)}
                >
                  {m.toUpperCase()}
                </button>
              ))}
              <div className="panel-head-actions">
                <button className="panel-icon-btn" title="Expand">⤢</button>
              </div>
            </div>
            <div className="panel-cols"><span>App</span><span>Score</span></div>
            {rankings.map((app, i) => {
              const score = rankScore(app);
              const pct   = score != null ? (score / rankMax) * 100 : 0;
              return (
                <div className="prop-row" key={app.id}>
                  <div className="prop-fill indigo" style={{ width:`${pct}%` }} />
                  <div className="prop-label">
                    <span className="prop-icon">{icon(app.category)}</span>
                    <span className="prop-name">{app.app_name}</span>
                  </div>
                  <span className="prop-count">
                    {score != null ? Number(score).toFixed(2) : "—"}
                  </span>
                </div>
              );
            })}
            {rankings.length === 0 && <div className="st-empty" style={{padding:20}}>Loading…</div>}
          </div>

          {/* Category breakdown panel */}
          <div className="panel glass-card">
            <div className="panel-head">
              <button className="ptab active">CATEGORIES</button>
              <button className="ptab">PRICE TIERS</button>
              <div className="panel-head-actions">
                <button className="panel-icon-btn" title="Expand">⤢</button>
              </div>
            </div>
            <div className="panel-cols"><span>Category</span><span>Apps</span></div>
            {Object.entries(catCounts).sort((a,b)=>b[1]-a[1]).map(([cat,cnt]) => (
              <div className="prop-row" key={cat}>
                <div className="prop-fill yellow" style={{ width:`${(cnt/maxCatCount)*100}%` }} />
                <div className="prop-label">
                  <span className="prop-icon">{icon(cat)}</span>
                  <span className="prop-name">{cat}</span>
                </div>
                <span className="prop-count">{cnt}</span>
              </div>
            ))}
          </div>
        </div>

        {/* ── EXPLORE — filter bar ── */}
        <div className="explore-bar glass-card">
          <div className="explore-bar-top">
            <span className="explore-title">App Explorer</span>
            <button className="btn-ghost" onClick={reset}>↺ Reset filters</button>
          </div>
          <div className="filter-row">
            <input
              id="search-input"
              className="f-input"
              type="text"
              placeholder="🔍  Search apps…"
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(0); }}
            />
            <select id="cat-filter" className="f-select" value={category}
              onChange={e => { setCategory(e.target.value); setPage(0); }}>
              <option value="">All Categories</option>
              {Object.keys(CAT_ICON).map(c => <option key={c} value={c}>{c}</option>)}
            </select>
            <input id="rating-filter" className="f-input" type="number"
              placeholder="Min rating" min="0" max="5" step="0.1"
              style={{ flex:"0 0 120px" }} value={minRating}
              onChange={e => { setMinRating(e.target.value); setPage(0); }}
            />
            <input id="price-filter" className="f-input" type="number"
              placeholder="Max ₹" min="0"
              style={{ flex:"0 0 100px" }} value={maxPrice}
              onChange={e => { setMaxPrice(e.target.value); setPage(0); }}
            />
            <select id="sort-filter" className="f-select"
              value={`${sortBy}-${order}`}
              onChange={e => { const [f,d]=e.target.value.split("-"); setSortBy(f); setOrder(d); setPage(0); }}>
              <option value="id-asc">Default</option>
              <option value="rating-desc">↑ Rating</option>
              <option value="downloads-desc">↑ Downloads</option>
              <option value="monthly_price-asc">↓ Price</option>
              <option value="engagement-desc">↑ Engagement</option>
            </select>
          </div>
        </div>

        {/* ── APPS TABLE — Plausible proportion rows ── */}
        <div className="apps-panel glass-card">
          <div className="apps-panel-head">
            <div className="apps-panel-tabs">
              <button className="ptab active">ALL APPS</button>
            </div>
            <span style={{ fontSize:12, color:"var(--t3)", fontWeight:600 }}>
              {apps.length} results · page {page+1}
            </span>
          </div>

          <div className="apps-col-header">
            <div>#</div>
            <div>App Name</div>
            <div>Rating</div>
            <div>Downloads</div>
            <div className="col-hide">Engage</div>
            <div className="col-hide">Popul.</div>
            <div>Monthly</div>
            <div>Action</div>
          </div>

          {error && <div className="err-banner" style={{margin:"12px 14px"}}>⚠ {error}</div>}

          {loading && <div className="st-loading"><div className="spinner"/>Loading apps…</div>}

          {!loading && !error && apps.length === 0 && (
            <div className="st-empty">No apps match your filters.</div>
          )}

          {!loading && apps.map((app, i) => {
            const pct = ((app.downloads ?? 0) / maxDownloads) * 100;
            const rank = page * LIMIT + i;
            const rankCls = rank === 0 ? "g" : rank === 1 ? "s" : rank === 2 ? "b" : "";
            return (
              <div className="app-row" key={app.id}>
                <div className="row-fill" style={{ width:`${pct}%` }} />
                <span className={`row-n ${rankCls}`}>{rank + 1}</span>
                <div>
                  <div className="row-name">{app.app_name}</div>
                  <div className="row-sub">{icon(app.category)} {app.category}</div>
                </div>
                <div className="row-num">⭐ {app.rating ?? "—"}</div>
                <div className="row-num">{fmtK(app.downloads)}</div>
                <div className="row-num col-hide">{fmtScore(app.engagement_score)}</div>
                <div className="row-num col-hide">{fmtScore(app.popularity_score)}</div>
                <div className="row-num">{fmtPrice(app.normalized_monthly_price)}</div>
                <div style={{ display:"flex", justifyContent:"flex-end", alignItems:"center" }}>
                  <button className="detail-btn" onClick={() => viewDetails(app.id)}>
                    Details →
                  </button>
                </div>
              </div>
            );
          })}

          {!loading && apps.length > 0 && (
            <div className="pagination">
              <button id="prev-btn" className="pag-btn" disabled={page===0}
                onClick={() => setPage(p=>p-1)}>← Prev</button>
              <span className="pag-info">Page {page+1}</span>
              <button id="next-btn" className="pag-btn" disabled={apps.length < LIMIT}
                onClick={() => setPage(p=>p+1)}>Next →</button>
            </div>
          )}
        </div>

        {/* ── COMPARE ── */}
        <div className="compare-panel glass-card" id="compare">
          <div className="compare-panel-head">
            <button className="ptab active">COMPARE APPS</button>
          </div>
          <div className="compare-controls">
            <select id="c1" value={compare1} onChange={e=>setCompare1(e.target.value)}>
              <option value="">Select first app…</option>
              {allApps.map(a=><option key={a.id} value={a.id}>{a.app_name}</option>)}
            </select>
            <span className="vs-text">vs</span>
            <select id="c2" value={compare2} onChange={e=>setCompare2(e.target.value)}>
              <option value="">Select second app…</option>
              {allApps.map(a=><option key={a.id} value={a.id}>{a.app_name}</option>)}
            </select>
            <button id="compare-btn" className="btn-purple"
              disabled={!compare1||!compare2} onClick={compareApps}>
              Compare
            </button>
          </div>

          {comparison && (
            <div className="comp-result">
              {[comparison.app1, comparison.app2].map((app,ci) => (
                <div className="comp-col" key={ci}>
                  <div className="comp-col-head">
                    <h3>{app.app_name}</h3>
                    <div className="sub">{app.category} · {app.developer}</div>
                  </div>
                  {[
                    ["Rating",      app.rating != null ? `⭐ ${app.rating}` : "—"],
                    ["Downloads",   fmtK(app.downloads)],
                    ["Engagement",  fmtScore(app.engagement_score)],
                    ["Popularity",  fmtScore(app.popularity_score)],
                    ["Monthly",     fmtPrice(app.normalized_monthly_price)],
                    ["Price Tier",  app.price_tier ?? "—"],
                  ].map(([k,v]) => (
                    <div className="comp-row" key={k}>
                      <span className="comp-k">{k}</span>
                      <span className="comp-v">{v}</span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ── ANALYTICS ── */}
        <div id="analytics">
          <Analytics />
        </div>

      </main>

      {/* ── FOOTER ── */}
      <footer className="footer">
        <strong>AppLen</strong> · App Analytics &amp; Comparison Dashboard
      </footer>

      {/* ── DETAIL MODAL ── */}
      {selectedApp && (
        <div className="modal-overlay" onClick={()=>setSelectedApp(null)}>
          <div className="modal" onClick={e=>e.stopPropagation()}>
            <div className="modal-top">
              <div>
                <h2>{selectedApp.app_name}</h2>
                <span style={{ fontSize:12.5, fontWeight:600, color:"var(--indigo-dark)", background:"#eef2ff", padding:"3px 10px", borderRadius:99 }}>
                  {icon(selectedApp.category)} {selectedApp.category}
                </span>
              </div>
              <button className="modal-close" onClick={()=>setSelectedApp(null)} aria-label="Close">×</button>
            </div>
            <div className="modal-body">
              <div className="modal-grid">
                {[
                  ["Developer",      selectedApp.developer ?? "—"],
                  ["Rating",         selectedApp.rating != null ? `⭐ ${selectedApp.rating}` : "—"],
                  ["Downloads",      fmtK(selectedApp.downloads)],
                  ["Engagement",     fmtScore(selectedApp.engagement_score)],
                  ["Popularity",     fmtScore(selectedApp.popularity_score)],
                  ["Rating Score",   fmtScore(selectedApp.rating_score)],
                  ["Monthly Price",  fmtPrice(selectedApp.normalized_monthly_price)],
                  ["Yearly Price",   fmtPrice(selectedApp.normalized_yearly_price)],
                  ["Annual Savings", fmtPrice(selectedApp.annual_savings)],
                  ["Annual Discount",selectedApp.annual_discount_pct != null ? `${selectedApp.annual_discount_pct}%` : "—"],
                  ["Price Tier",     selectedApp.price_tier ?? "—"],
                  ["Free Trial",     selectedApp.has_free_trial ? `${selectedApp.free_trial_days} days` : "No"],
                ].map(([l,v])=>(
                  <div className="mcell" key={l}>
                    <span className="mclabel">{l}</span>
                    <span className="mcvalue">{v}</span>
                  </div>
                ))}
              </div>
              <div className="mflags">
                {selectedApp.is_freemium      && <span className="mflag">✦ Freemium</span>}
                {selectedApp.is_verified_price && <span className="mflag">✔ Verified Price</span>}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

/* ── Stat cell ── */
function StatCell({ label, value, active }) {
  return (
    <div className={`stat-cell${active?" active":""}`}>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
    </div>
  );
}