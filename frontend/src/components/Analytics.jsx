import { useEffect, useState } from "react";
import {
  AreaChart, Area,
  BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
  ScatterChart, Scatter,
} from "recharts";

const API = "http://127.0.0.1:8000";

/* Plausible-style colors */
const C  = ["#6366f1","#8b5cf6","#06b6d4","#f59e0b","#10b981","#ec4899","#f97316","#64748b"];
const AX = { fill:"#9ca3af", fontSize:11.5, fontFamily:"Inter,sans-serif" };
const GD = { stroke:"#f3f4f6", strokeDasharray:"4 4" };
const TT = {
  background:"#fff", border:"1px solid #e5e7eb",
  borderRadius:10, boxShadow:"0 4px 14px rgba(0,0,0,0.08)",
  color:"#111827", fontSize:12.5, fontFamily:"Inter,sans-serif",
  padding:"10px 14px",
};

export default function Analytics() {
  const [overview,     setOverview]     = useState(null);
  const [categories,   setCategories]   = useState([]);
  const [pricing,      setPricing]      = useState(null);
  const [correlations, setCorrelations] = useState(null);
  const [scatterData,  setScatterData]  = useState([]);
  const [topApps,      setTopApps]      = useState([]);
  const [topMetric,    setTopMetric]    = useState("engagement");
  const [insights,     setInsights]     = useState([]);
  const [error,        setError]        = useState("");

  useEffect(() => {
    Promise.all([
      fetch(`${API}/analytics/overview`),
      fetch(`${API}/analytics/categories`),
      fetch(`${API}/analytics/pricing`),
      fetch(`${API}/analytics/correlations`),
      fetch(`${API}/analytics/scatter`),
      fetch(`${API}/apps/rankings?metric=engagement&limit=10`),
      fetch(`${API}/analytics/insights`),
    ]).then(async rs => {
      if (rs.some(r => !r.ok)) throw new Error("analytics fetch failed");
      const [ov,ca,pr,co,sc,ta,in_] = await Promise.all(rs.map(r=>r.json()));
      setOverview(ov); setCategories(ca); setPricing(pr);
      setCorrelations(co); setScatterData(sc); setTopApps(ta); setInsights(in_);
    }).catch(() => setError("Unable to load analytics."));
  }, []);

  async function changeMetric(m) {
    setTopMetric(m);
    try {
      const r = await fetch(`${API}/apps/rankings?metric=${m}&limit=10`);
      if (!r.ok) throw 0;
      setTopApps(await r.json());
    } catch(e){console.error(e);}
  }

  if (error) return <div className="err-banner" style={{margin:"0 0 16px"}}>⚠ {error}</div>;
  if (!overview||!pricing||!correlations)
    return <div className="st-loading"><div className="spinner"/>Loading analytics…</div>;

  const pricingData  = pricing.pricing_models.map(d=>({ name:d.pricing_type, value:d.count }));
  const tierData     = pricing.price_tiers.map(d=>({ name:d.price_tier, value:d.count }));
  const rPopData     = scatterData.filter(a => a.rating!=null && a.popularity!=null);
  const pEngData     = scatterData.filter(a => a.price!=null && a.price>0 && a.engagement!=null);

  const ICONS = ["💡","📊","🏆","💰","🔍","⚡","📈","🎯"];

  const Tip = ({ active, payload }) => {
    if (!active||!payload?.length) return null;
    const a = payload[0].payload;
    return (
      <div style={TT}>
        <strong style={{display:"block",marginBottom:6}}>{a.app_name}</strong>
        {a.rating    != null && <p style={{margin:"2px 0",fontSize:12}}>⭐ Rating: {a.rating.toFixed(2)}</p>}
        {a.popularity!= null && <p style={{margin:"2px 0",fontSize:12}}>📈 Popularity: {a.popularity.toFixed(2)}</p>}
        {a.price     != null && <p style={{margin:"2px 0",fontSize:12}}>₹ Price/mo: {a.price.toFixed(0)}</p>}
        {a.engagement!= null && <p style={{margin:"2px 0",fontSize:12}}>🔥 Engagement: {a.engagement.toFixed(2)}</p>}
      </div>
    );
  };

  return (
    <>
      {/* ── Section label ── */}
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:14 }}>
        <div>
          <h2 style={{ margin:"0 0 3px", fontSize:15, fontWeight:700, color:"#111827", letterSpacing:"-0.2px" }}>Analytics</h2>
          <p style={{ margin:0, fontSize:12.5, color:"#6b7280" }}>Market patterns across all tracked apps</p>
        </div>
      </div>

      {/* ── Analytics overview stat bar ── */}
      <div className="analytics-panel glass-card" style={{ padding:0, marginBottom:16 }}>
        <div className="a-stats">
          {[
            { l:"Total Apps",        v: overview.total_apps },
            { l:"Categories",        v: overview.total_categories },
            { l:"Avg Rating",        v: `${overview.average_rating} ⭐` },
            { l:"Avg Engagement",    v: overview.average_engagement },
            { l:"Avg Popularity",    v: overview.average_popularity },
            { l:"Comparable Prices", v: `${overview.comparable_priced_apps}/${overview.total_apps}` },
          ].map(s => (
            <div className="a-stat-cell" key={s.l}>
              <div className="a-stat-label">{s.l}</div>
              <div className="a-stat-value">{s.v}</div>
            </div>
          ))}
        </div>

        {/* ── Area chart — avg engagement by category ── */}
        <div style={{ padding:"20px 16px 16px" }}>
          <p style={{ margin:"0 0 14px", fontSize:11.5, fontWeight:700, textTransform:"uppercase", letterSpacing:"0.06em", color:"#9ca3af" }}>
            Avg Engagement by Category
          </p>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={categories} layout="vertical"
              margin={{ top:4, right:20, left:10, bottom:4 }}>
              <CartesianGrid {...GD} />
              <XAxis type="number" domain={[0,100]} tick={AX} />
              <YAxis dataKey="category" type="category" width={130} tick={AX} />
              <Tooltip contentStyle={TT} />
              <Bar dataKey="avg_engagement" name="Engagement" radius={[0,4,4,0]}>
                {categories.map((_,i) => <Cell key={i} fill={C[i%C.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Pricing + Tiers ── */}
      <div className="a-grid-2">
        <div className="analytics-panel glass-card">
          <div className="a-head">
            <button className="ptab active">PRICING MODELS</button>
          </div>
          <div className="a-body">
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={pricingData} dataKey="value" nameKey="name"
                  cx="50%" cy="50%" outerRadius={95} innerRadius={42} paddingAngle={3}
                  label={({ name, percent }) => `${name} ${(percent*100).toFixed(0)}%`}
                  labelLine={{ stroke:"#c7d2fe" }}>
                  {pricingData.map((_,i) => <Cell key={i} fill={C[i%C.length]} stroke="none" />)}
                </Pie>
                <Tooltip contentStyle={TT} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="analytics-panel glass-card">
          <div className="a-head">
            <button className="ptab active">PRICE TIERS</button>
          </div>
          <div className="a-body">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={tierData} margin={{ top:4, right:8, left:0, bottom:4 }}>
                <CartesianGrid {...GD} />
                <XAxis dataKey="name" tick={AX} />
                <YAxis tick={AX} />
                <Tooltip contentStyle={TT} />
                <Bar dataKey="value" name="Apps" radius={[4,4,0,0]}>
                  {tierData.map((_,i) => <Cell key={i} fill={C[i%C.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* ── Scatter charts ── */}
      <div className="a-grid-2">
        <div className="analytics-panel glass-card">
          <div className="a-head"><button className="ptab active">RATING VS POPULARITY</button></div>
          <div className="a-body">
            <p className="chart-desc">Each point is an analyzed app</p>
            <ResponsiveContainer width="100%" height={280}>
              <ScatterChart margin={{ top:4, right:12, bottom:4, left:0 }}>
                <CartesianGrid {...GD} />
                <XAxis type="number" dataKey="rating"     name="Rating"     domain={[3,5]}   tick={AX}
                  label={{ value:"Rating", position:"insideBottomRight", offset:-8, fill:"#9ca3af", fontSize:11 }} />
                <YAxis type="number" dataKey="popularity" name="Popularity" domain={[0,100]} tick={AX} />
                <Tooltip content={<Tip/>} />
                <Scatter name="Apps" data={rPopData} fill={C[0]} fillOpacity={0.65} />
              </ScatterChart>
            </ResponsiveContainer>
            <div className="chart-note">
              Correlation: <strong>{correlations.rating_vs_popularity}</strong>
            </div>
          </div>
        </div>

        <div className="analytics-panel glass-card">
          <div className="a-head"><button className="ptab active">PRICE VS ENGAGEMENT</button></div>
          <div className="a-body">
            <p className="chart-desc">Paid apps with positive monthly price only</p>
            <ResponsiveContainer width="100%" height={280}>
              <ScatterChart margin={{ top:4, right:12, bottom:4, left:0 }}>
                <CartesianGrid {...GD} />
                <XAxis type="number" dataKey="price"      name="Price ₹"   tick={AX}
                  label={{ value:"Price (₹)", position:"insideBottomRight", offset:-8, fill:"#9ca3af", fontSize:11 }} />
                <YAxis type="number" dataKey="engagement" name="Engagement" domain={[0,100]} tick={AX} />
                <Tooltip content={<Tip/>} />
                <Scatter name="Apps" data={pEngData} fill={C[2]} fillOpacity={0.65} />
              </ScatterChart>
            </ResponsiveContainer>
            <div className="chart-note">
              Correlation: <strong>{correlations.price_vs_engagement}</strong>
            </div>
          </div>
        </div>
      </div>

      {/* ── Top Apps table ── */}
      <div className="analytics-panel glass-card" style={{ marginBottom:16 }}>
        <div className="a-head" style={{ justifyContent:"space-between" }}>
          <button className="ptab active">TOP APPS</button>
          <div className="rank-btns" style={{ marginRight:8 }}>
            {[
              {k:"engagement",l:"Engagement"},
              {k:"popularity",l:"Popularity"},
              {k:"rating",    l:"Rating"},
              {k:"value",     l:"Value"},
            ].map(m=>(
              <button key={m.k} className={`rank-btn${topMetric===m.k?" active":""}`}
                onClick={()=>changeMetric(m.k)}>{m.l}</button>
            ))}
          </div>
        </div>
        <div className="a-body" style={{ paddingTop:14 }}>
          <div className="tbl-wrap">
            <table className="atbl">
              <thead>
                <tr>
                  <th>#</th><th>App</th><th>Category</th>
                  <th>Rating</th><th>Popularity</th><th>Engagement</th>
                  <th>Monthly</th><th>Tier</th>
                </tr>
              </thead>
              <tbody>
                {topApps.map((a,i)=>(
                  <tr key={a.id}>
                    <td className="rn">{i+1}</td>
                    <td className="anc">
                      <strong>{a.app_name}</strong>
                      <span>{a.developer}</span>
                    </td>
                    <td>{a.category}</td>
                    <td>{a.rating?.toFixed(2)??"—"}</td>
                    <td>{a.popularity_score?.toFixed(1)??"—"}</td>
                    <td>{a.engagement_score?.toFixed(1)??"—"}</td>
                    <td>{a.normalized_monthly_price!=null?`₹${a.normalized_monthly_price.toFixed(0)}`:"—"}</td>
                    <td><span className="pill">{a.price_tier||"—"}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ── Category comparison ── */}
      <div className="analytics-panel glass-card" style={{ marginBottom:16 }}>
        <div className="a-head"><button className="ptab active">CATEGORY BREAKDOWN</button></div>
        <div className="a-body" style={{ paddingTop:14 }}>
          <div className="tbl-wrap">
            <table className="atbl">
              <thead>
                <tr>
                  <th>Category</th><th>Apps</th>
                  <th>Avg Rating</th><th>Avg Popularity</th>
                  <th>Avg Engagement</th><th>Avg Monthly</th>
                </tr>
              </thead>
              <tbody>
                {categories.map(c=>(
                  <tr key={c.category}>
                    <td><strong>{c.category}</strong></td>
                    <td>{c.app_count}</td>
                    <td>{c.avg_rating?.toFixed(2)??"—"}</td>
                    <td>{c.avg_popularity?.toFixed(1)??"—"}</td>
                    <td>{c.avg_engagement?.toFixed(1)??"—"}</td>
                    <td>{c.avg_monthly_price!=null?`₹${c.avg_monthly_price.toFixed(0)}`:"—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ── Key Relationships ── */}
      <div className="analytics-panel glass-card" style={{ marginBottom:16 }}>
        <div className="a-head"><button className="ptab active">KEY RELATIONSHIPS</button></div>
        <div className="a-body">
          <p className="sub-text" style={{margin:"0 0 14px"}}>Pearson correlation coefficients between app metrics</p>
          <div className="corr-grid">
            {[
              { l:"Rating ↔ Popularity",    v:correlations.rating_vs_popularity },
              { l:"Rating ↔ Engagement",    v:correlations.rating_vs_engagement },
              { l:"Popularity ↔ Engagement",v:correlations.popularity_vs_engagement },
              { l:"Price ↔ Engagement",     v:correlations.price_vs_engagement },
            ].map(c=>(
              <div className="corr-box" key={c.l}>
                <div className="corr-label">{c.l}</div>
                <div className="corr-value">{c.v}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Key Insights ── */}
      <div className="analytics-panel glass-card" style={{ marginBottom:4 }}>
        <div className="a-head"><button className="ptab active">KEY INSIGHTS</button></div>
        <div className="a-body">
          <div className="insight-list">
            {insights.map((ins,i)=>(
              <div className="insight-item" key={i}>
                <span className="insight-icon">{ICONS[i%ICONS.length]}</span>
                <div>
                  <strong>{ins.title}</strong>
                  <p>{ins.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}