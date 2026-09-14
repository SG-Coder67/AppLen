import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [apps, setApps] = useState([]);
  const [allApps, setAllApps] = useState([]);
const [selectedApp, setSelectedApp] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [minRating, setMinRating] = useState("");
  const [maxPrice, setMaxPrice] = useState("");

  const [sortBy, setSortBy] = useState("id");
  const [order, setOrder] = useState("asc");

  const [page, setPage] = useState(0);
  const limit = 12;

  const [rankings, setRankings] = useState([]);
  const [rankingMetric, setRankingMetric] = useState("engagement");

  const [compare1, setCompare1] = useState("");
  const [compare2, setCompare2] = useState("");
  const [comparison, setComparison] = useState(null);

  // -------------------------
  // Fetch apps
  // -------------------------

  useEffect(() => {
    fetchApps();
  }, [
    search,
    category,
    minRating,
    maxPrice,
    sortBy,
    order,
    page,
  ]);
  useEffect(() => {
  fetch(`${API}/apps/?limit=100`)
    .then((response) => response.json())
    .then((data) => {
      setAllApps(data);
    })
    .catch((error) => {
      console.error("Error fetching all apps:", error);
    });
}, []);

  async function fetchApps() {
    try {
      setLoading(true);
      setError("");

      const params = new URLSearchParams();

      if (search) params.append("search", search);
      if (category) params.append("category", category);
      if (minRating) params.append("min_rating", minRating);
      if (maxPrice) params.append("max_price", maxPrice);

      params.append("sort_by", sortBy);
      params.append("order", order);
      params.append("limit", limit);
      params.append("offset", page * limit);

      const response = await fetch(
        `${API}/apps/?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch apps");
      }

      const data = await response.json();

      setApps(data);
    } catch (err) {
      console.error(err);
      setError("Unable to load apps.");
    } finally {
      setLoading(false);
    }
  }

  // -------------------------
  // Rankings
  // -------------------------

  async function fetchRankings(metric) {
    try {
      setRankingMetric(metric);

      const response = await fetch(
        `${API}/apps/rankings?metric=${metric}&limit=5`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch rankings");
      }

      const data = await response.json();

      setRankings(data);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    fetchRankings("engagement");
  }, []);

  // -------------------------
  // Comparison
  // -------------------------

  async function compareApps() {
    if (!compare1 || !compare2) {
      return;
    }

    try {
      const response = await fetch(
        `${API}/apps/compare?app1_id=${compare1}&app2_id=${compare2}`
      );

      if (!response.ok) {
        throw new Error("Comparison failed");
      }

      const data = await response.json();

      setComparison(data);
    } catch (err) {
      console.error(err);
      setComparison(null);
    }
  }
  async function viewAppDetails(appId) {
  try {
    const response = await fetch(
      `${API}/apps/${appId}`
    );

    if (!response.ok) {
      throw new Error("Failed to fetch app details");
    }

    const data = await response.json();

    setSelectedApp(data);
  } catch (error) {
    console.error(error);
  }
}

  // -------------------------
  // Helpers
  // -------------------------

  function formatNumber(value) {
    if (value === null || value === undefined) {
      return "N/A";
    }

    return Number(value).toLocaleString();
  }

  function formatPrice(value) {
    if (value === null || value === undefined) {
      return "N/A";
    }

    return `₹${Number(value).toFixed(0)}`;
  }

  function resetFilters() {
    setSearch("");
    setCategory("");
    setMinRating("");
    setMaxPrice("");
    setSortBy("id");
    setOrder("asc");
    setPage(0);
  }

  return (
    <div className="app">

      {/* ================= HEADER ================= */}

      <header className="header">
        <div>
          <h1>AppLen</h1>
          <p>App Analytics & Comparison Platform</p>
        </div>

        <nav>
          <a href="#explore">Explore</a>
          <a href="#rankings">Rankings</a>
          <a href="#compare">Compare</a>
        </nav>
      </header>


      {/* ================= HERO ================= */}

      <section className="hero">
        <div>
          <h2>Analyze apps smarter.</h2>

          <p>
            Explore app performance, pricing, popularity,
            engagement and value in one place.
          </p>
        </div>
      </section>


      {/* ================= EXPLORE ================= */}

      <section id="explore" className="section">

        <div className="section-header">
          <div>
            <h2>Explore Apps</h2>
            <p>Search and analyze the app database.</p>
          </div>

          <button
            className="reset-button"
            onClick={resetFilters}
          >
            Reset Filters
          </button>
        </div>


        {/* Filters */}

        <div className="filters">

          <input
            type="text"
            placeholder="Search apps..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
          />

          <select
            value={category}
            onChange={(e) => {
              setCategory(e.target.value);
              setPage(0);
            }}
          >
            <option value="">All Categories</option>
            <option value="Music">Music</option>
            <option value="Fitness">Fitness</option>
            <option value="Finance">Finance</option>
            <option value="Education">Education</option>
            <option value="Health & Fitness">
              Health & Fitness
            </option>
            <option value="Productivity">
              Productivity
            </option>
            <option value="Social">Social</option>
            <option value="Entertainment">
              Entertainment
            </option>
          </select>


          <input
            type="number"
            placeholder="Min rating"
            min="0"
            max="5"
            step="0.1"
            value={minRating}
            onChange={(e) => {
              setMinRating(e.target.value);
              setPage(0);
            }}
          />


          <input
            type="number"
            placeholder="Max price ₹"
            min="0"
            value={maxPrice}
            onChange={(e) => {
              setMaxPrice(e.target.value);
              setPage(0);
            }}
          />


          <select
            value={`${sortBy}-${order}`}
            onChange={(e) => {
              const [field, direction] =
                e.target.value.split("-");

              setSortBy(field);
              setOrder(direction);
              setPage(0);
            }}
          >
            <option value="id-asc">
              Default
            </option>

            <option value="rating-desc">
              Highest Rating
            </option>

            <option value="downloads-desc">
              Most Downloads
            </option>

            <option value="monthly_price-asc">
              Lowest Price
            </option>

            <option value="monthly_price-desc">
              Highest Price
            </option>

            <option value="engagement-desc">
              Highest Engagement
            </option>
          </select>

        </div>


        {/* Apps */}

        {loading && (
          <div className="status">
            Loading apps...
          </div>
        )}

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {!loading && !error && apps.length === 0 && (
          <div className="status">
            No apps found.
          </div>
        )}


        <div className="app-grid">

          {apps.map((app) => (

            <div className="app-card" key={app.id}>

              <div className="card-header">

                <div>
                  <h3>{app.app_name}</h3>

                  <span className="category">
                    {app.category}
                  </span>
                  
                </div>

                <span className="rating">
                  ⭐ {app.rating ?? "N/A"}
                </span>

              </div>


              <div className="metrics">

                <div>
                  <span>Downloads</span>
                  <strong>
                    {formatNumber(app.downloads)}
                  </strong>
                </div>


                <div>
                  <span>Engagement</span>
                  <strong>
                    {app.engagement_score
                      ? app.engagement_score.toFixed(1)
                      : "N/A"}
                  </strong>
                </div>
                <button
  className="details-button"
  onClick={() => viewAppDetails(app.id)}
>
  View Details →
</button>

                <div>
                  <span>Popularity</span>
                  <strong>
                    {app.popularity_score
                      ? app.popularity_score.toFixed(1)
                      : "N/A"}
                  </strong>
                </div>

              </div>


              <div className="card-footer">

                <div>
                  <span>Monthly</span>

                  <strong>
                    {formatPrice(
                      app.normalized_monthly_price
                    )}
                  </strong>
                </div>


                <div>
                  <span>Price Tier</span>

                  <strong>
                    {app.price_tier ?? "N/A"}
                  </strong>
                </div>

              </div>

            </div>

          ))}

        </div>


        {/* Pagination */}

        <div className="pagination">

          <button
            disabled={page === 0}
            onClick={() =>
              setPage((current) => current - 1)
            }
          >
            ← Previous
          </button>


          <span>
            Page {page + 1}
          </span>


          <button
            disabled={apps.length < limit}
            onClick={() =>
              setPage((current) => current + 1)
            }
          >
            Next →
          </button>

        </div>

      </section>


      {/* ================= RANKINGS ================= */}

      <section id="rankings" className="section">

        <div className="section-header">

          <div>
            <h2>Top Ranked Apps</h2>
            <p>
              Discover the strongest apps across different metrics.
            </p>
          </div>

          <select
            value={rankingMetric}
            onChange={(e) =>
              fetchRankings(e.target.value)
            }
          >
            <option value="engagement">
              Engagement
            </option>

            <option value="popularity">
              Popularity
            </option>

            <option value="rating">
              Rating
            </option>

            <option value="value">
              Value
            </option>
          </select>

        </div>


        <div className="ranking-list">

          {rankings.map((app, index) => (

            <div
              className="ranking-card"
              key={app.id}
            >

              <div className="rank">
                #{index + 1}
              </div>

              <div className="rank-info">
                <h3>{app.app_name}</h3>
                <span>{app.category}</span>
              </div>

              <div className="rank-score">

                {rankingMetric === "engagement" &&
                  app.engagement_score?.toFixed(2)}

                {rankingMetric === "popularity" &&
                  app.popularity_score?.toFixed(2)}

                {rankingMetric === "rating" &&
                  app.rating?.toFixed(2)}

                {rankingMetric === "value" &&
                  app.price_adjusted_value_score?.toFixed(2)}

              </div>

            </div>

          ))}

        </div>

      </section>


      {/* ================= COMPARE ================= */}

      <section id="compare" className="section">

        <div className="section-header">

          <div>
            <h2>Compare Apps</h2>

            <p>
              Compare two apps across their key metrics.
            </p>
          </div>

        </div>


        <div className="compare-controls">

          <select
            value={compare1}
            onChange={(e) =>
              setCompare1(e.target.value)
            }
          >
            <option value="">
              Select first app
            </option>

            {allApps.map((app) => (
              <option
                key={app.id}
                value={app.id}
              >
                {app.app_name}
              </option>
            ))}

          </select>


          <span className="vs">
            VS
          </span>


          <select
            value={compare2}
            onChange={(e) =>
              setCompare2(e.target.value)
            }
          >
            <option value="">
              Select second app
            </option>

            {allApps.map((app) => (
              <option
                key={app.id}
                value={app.id}
              >
                {app.app_name}
              </option>
            ))}

          </select>


          <button
            className="compare-button"
            onClick={compareApps}
          >
            Compare
          </button>

        </div>


        {comparison && (

          <div className="comparison">

            <div className="comparison-app">

              <h3>
                {comparison.app1.app_name}
              </h3>

              <ComparisonMetric
                label="Rating"
                value={comparison.app1.rating}
              />

              <ComparisonMetric
                label="Downloads"
                value={formatNumber(
                  comparison.app1.downloads
                )}
              />

              <ComparisonMetric
                label="Engagement"
                value={
                  comparison.app1.engagement_score?.toFixed(2)
                }
              />

              <ComparisonMetric
                label="Popularity"
                value={
                  comparison.app1.popularity_score?.toFixed(2)
                }
              />

              <ComparisonMetric
                label="Monthly Price"
                value={formatPrice(
                  comparison.app1.normalized_monthly_price
                )}
              />

            </div>


            <div className="comparison-app">

              <h3>
                {comparison.app2.app_name}
              </h3>

              <ComparisonMetric
                label="Rating"
                value={comparison.app2.rating}
              />

              <ComparisonMetric
                label="Downloads"
                value={formatNumber(
                  comparison.app2.downloads
                )}
              />

              <ComparisonMetric
                label="Engagement"
                value={
                  comparison.app2.engagement_score?.toFixed(2)
                }
              />

              <ComparisonMetric
                label="Popularity"
                value={
                  comparison.app2.popularity_score?.toFixed(2)
                }
              />

              <ComparisonMetric
                label="Monthly Price"
                value={formatPrice(
                  comparison.app2.normalized_monthly_price
                )}
              />

            </div>

          </div>

        )}

      </section>
{selectedApp && (
  <div
    className="modal-overlay"
    onClick={() => setSelectedApp(null)}
  >
    <div
      className="details-modal"
      onClick={(e) => e.stopPropagation()}
    >

      <button
        className="close-button"
        onClick={() => setSelectedApp(null)}
      >
        ×
      </button>

      <h2>{selectedApp.app_name}</h2>

      <p className="modal-category">
        {selectedApp.category}
      </p>

      <div className="detail-grid">

        <div>
          <span>Developer</span>
          <strong>
            {selectedApp.developer}
          </strong>
        </div>

        <div>
          <span>Rating</span>
          <strong>
            ⭐ {selectedApp.rating ?? "N/A"}
          </strong>
        </div>

        <div>
          <span>Downloads</span>
          <strong>
            {formatNumber(selectedApp.downloads)}
          </strong>
        </div>

        <div>
          <span>Engagement Score</span>
          <strong>
            {selectedApp.engagement_score?.toFixed(2) ?? "N/A"}
          </strong>
        </div>

        <div>
          <span>Popularity Score</span>
          <strong>
            {selectedApp.popularity_score?.toFixed(2) ?? "N/A"}
          </strong>
        </div>

        <div>
          <span>Rating Score</span>
          <strong>
            {selectedApp.rating_score?.toFixed(2) ?? "N/A"}
          </strong>
        </div>

        <div>
          <span>Monthly Price</span>
          <strong>
            {formatPrice(
              selectedApp.normalized_monthly_price
            )}
          </strong>
        </div>

        <div>
          <span>Yearly Price</span>
          <strong>
            {formatPrice(
              selectedApp.normalized_yearly_price
            )}
          </strong>
        </div>

        <div>
          <span>Annual Savings</span>
          <strong>
            {formatPrice(
              selectedApp.annual_savings
            )}
          </strong>
        </div>

        <div>
          <span>Annual Discount</span>
          <strong>
            {selectedApp.annual_discount_pct != null
              ? `${selectedApp.annual_discount_pct}%`
              : "N/A"}
          </strong>
        </div>

        <div>
          <span>Price Tier</span>
          <strong>
            {selectedApp.price_tier ?? "N/A"}
          </strong>
        </div>

        <div>
          <span>Free Trial</span>
          <strong>
            {selectedApp.has_free_trial
              ? `${selectedApp.free_trial_days} days`
              : "No"}
          </strong>
        </div>

      </div>

      <div className="modal-flags">

        {selectedApp.is_freemium && (
          <span>Freemium</span>
        )}

        {selectedApp.is_verified_price && (
          <span>Verified Price</span>
        )}

      </div>

    </div>
  </div>
)}

      {/* ================= FOOTER ================= */}

      <footer>
        <p>
          AppLen — App Analytics & Comparison Platform
        </p>
      </footer>

    </div>
  );
}


// --------------------------------
// Comparison metric component
// --------------------------------

function ComparisonMetric({ label, value }) {
  return (
    <div className="comparison-metric">

      <span>{label}</span>

      <strong>
        {value ?? "N/A"}
      </strong>

    </div>
  );
}

export default App;