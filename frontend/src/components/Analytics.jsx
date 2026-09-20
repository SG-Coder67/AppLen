import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
} from "recharts";

const API = "http://127.0.0.1:8000";

function Analytics() {
  const [overview, setOverview] = useState(null);
  const [categories, setCategories] = useState([]);
  const [pricing, setPricing] = useState(null);
  const [correlations, setCorrelations] = useState(null);
  const [scatterData, setScatterData] = useState([]);
  const [topApps, setTopApps] = useState([]);
  const [topMetric, setTopMetric] = useState("engagement");
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadAnalytics() {
      try {
        const [
          overviewResponse,
          categoryResponse,
          pricingResponse,
          correlationResponse,
          scatterResponse,
          topAppsResponse,
        ] = await Promise.all([
          fetch(`${API}/analytics/overview`),
          fetch(`${API}/analytics/categories`),
          fetch(`${API}/analytics/pricing`),
          fetch(`${API}/analytics/correlations`),
          fetch(`${API}/analytics/scatter`),
          fetch(`${API}/apps/rankings?metric=engagement&limit=10`),
        ]);

        if (
          !overviewResponse.ok ||
          !categoryResponse.ok ||
          !pricingResponse.ok ||
          !correlationResponse.ok ||
          !scatterResponse.ok ||
          !topAppsResponse.ok
        ) {
          throw new Error("Failed to load analytics");
        }

        const overviewData = await overviewResponse.json();
        const categoryData = await categoryResponse.json();
        const pricingData = await pricingResponse.json();
        const correlationData = await correlationResponse.json();
        const scatterDataResponse = await scatterResponse.json();
        const topAppsData = await topAppsResponse.json();

        setOverview(overviewData);
        setCategories(categoryData);
        setPricing(pricingData);
        setCorrelations(correlationData);
        setScatterData(scatterDataResponse);
        setTopApps(topAppsData);
      } catch (err) {
        console.error(err);
        setError("Unable to load analytics data.");
      }
    }

    loadAnalytics();
  }, []);

  async function changeTopMetric(metric) {
    try {
      setTopMetric(metric);

      const response = await fetch(
        `${API}/apps/rankings?metric=${metric}&limit=10`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch rankings");
      }

      const data = await response.json();
      setTopApps(data);
    } catch (err) {
      console.error(err);
    }
  }

  if (error) {
    return <div className="analytics-error">{error}</div>;
  }

  if (!overview || !pricing || !correlations) {
    return <div className="analytics-loading">Loading analytics...</div>;
  }

  const pricingData = pricing.pricing_models.map((item) => ({
    name: item.pricing_type,
    value: item.count,
  }));

  const priceTierData = pricing.price_tiers.map((item) => ({
    name: item.price_tier,
    value: item.count,
  }));

  const ratingPopularityData = scatterData.filter(
    (app) =>
      app.rating != null &&
      app.popularity != null
  );

  const priceEngagementData = scatterData.filter(
    (app) =>
      app.price != null &&
      app.price > 0 &&
      app.engagement != null
  );

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload.length) {
      return null;
    }

    const app = payload[0].payload;

    return (
      <div className="analytics-tooltip">
        <strong>{app.app_name}</strong>

        {app.rating != null && (
          <p>Rating: {app.rating.toFixed(2)}</p>
        )}

        {app.popularity != null && (
          <p>Popularity: {app.popularity.toFixed(2)}</p>
        )}

        {app.price != null && (
          <p>Price: ₹{app.price.toFixed(0)}/month</p>
        )}

        {app.engagement != null && (
          <p>Engagement: {app.engagement.toFixed(2)}</p>
        )}
      </div>
    );
  };

  return (
    <div className="analytics-page">

      {/* HEADER */}
      <div className="analytics-header">
        <h1>App Analytics</h1>
        <p>
          Explore market patterns across the applications analyzed in
          AppLen.
        </p>
      </div>

      {/* OVERVIEW */}
      <div className="analytics-cards">

        <div className="analytics-card">
          <span>Total Apps</span>
          <strong>{overview.total_apps}</strong>
        </div>

        <div className="analytics-card">
          <span>Categories</span>
          <strong>{overview.total_categories}</strong>
        </div>

        <div className="analytics-card">
          <span>Average Rating</span>
          <strong>{overview.average_rating} ⭐</strong>
        </div>

        <div className="analytics-card">
          <span>Avg Engagement</span>
          <strong>{overview.average_engagement}</strong>
        </div>

        <div className="analytics-card">
          <span>Avg Popularity</span>
          <strong>{overview.average_popularity}</strong>
        </div>

        <div className="analytics-card">
          <span>Comparable Prices</span>
          <strong>
            {overview.comparable_priced_apps}/{overview.total_apps}
          </strong>
        </div>

      </div>

      {/* CATEGORY ENGAGEMENT */}
      <div className="analytics-section">
        <div className="analytics-panel large-panel">

          <h2>Average Engagement by Category</h2>

          <ResponsiveContainer width="100%" height={420}>
            <BarChart
              data={categories}
              layout="vertical"
              margin={{
                top: 10,
                right: 30,
                left: 30,
                bottom: 10,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />

              <XAxis
                type="number"
                domain={[0, 100]}
              />

              <YAxis
                dataKey="category"
                type="category"
                width={120}
              />

              <Tooltip />

              <Bar
                dataKey="avg_engagement"
                name="Engagement"
              />
            </BarChart>
          </ResponsiveContainer>

        </div>
      </div>

      {/* PRICING */}
      <div className="analytics-grid">

        <div className="analytics-panel">

          <h2>Pricing Models</h2>

          <ResponsiveContainer width="100%" height={320}>
            <PieChart>

              <Pie
                data={pricingData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={110}
                label
              >
                {pricingData.map((_, index) => (
                  <Cell key={index} />
                ))}
              </Pie>

              <Tooltip />

            </PieChart>
          </ResponsiveContainer>

        </div>

        <div className="analytics-panel">

          <h2>Price Tiers</h2>

          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={priceTierData}>

              <CartesianGrid strokeDasharray="3 3" />

              <XAxis dataKey="name" />

              <YAxis />

              <Tooltip />

              <Bar
                dataKey="value"
                name="Apps"
              />

            </BarChart>
          </ResponsiveContainer>

        </div>

      </div>

      {/* SCATTER CHARTS */}
      <div className="analytics-grid">

        <div className="analytics-panel">

          <h2>Rating vs Popularity</h2>

          <p className="chart-description">
            Each point represents an analyzed app.
          </p>

          <ResponsiveContainer width="100%" height={360}>
            <ScatterChart>

              <CartesianGrid />

              <XAxis
                type="number"
                dataKey="rating"
                name="Rating"
                domain={[3, 5]}
              />

              <YAxis
                type="number"
                dataKey="popularity"
                name="Popularity"
                domain={[0, 100]}
              />

              <Tooltip content={<CustomTooltip />} />

              <Scatter
                name="Apps"
                data={ratingPopularityData}
              />

            </ScatterChart>
          </ResponsiveContainer>

          <p className="chart-note">
            Correlation: {correlations.rating_vs_popularity}
          </p>

        </div>

        <div className="analytics-panel">

          <h2>Price vs Engagement</h2>

          <p className="chart-description">
            Only apps with directly comparable positive monthly prices are
            included.
          </p>

          <ResponsiveContainer width="100%" height={360}>
            <ScatterChart>

              <CartesianGrid />

              <XAxis
                type="number"
                dataKey="price"
                name="Monthly Price"
              />

              <YAxis
                type="number"
                dataKey="engagement"
                name="Engagement"
                domain={[0, 100]}
              />

              <Tooltip content={<CustomTooltip />} />

              <Scatter
                name="Apps"
                data={priceEngagementData}
              />

            </ScatterChart>
          </ResponsiveContainer>

          <p className="chart-note">
            Correlation: {correlations.price_vs_engagement}
          </p>

        </div>

      </div>

      {/* TOP APPS */}
      <div className="analytics-section">

        <div className="analytics-panel">

          <div className="top-apps-header">

            <div>
              <h2>Top Apps</h2>
              <p>
                Compare the highest-ranked apps across key metrics.
              </p>
            </div>

            <div className="ranking-buttons">

              <button
                className={topMetric === "engagement" ? "active" : ""}
                onClick={() => changeTopMetric("engagement")}
              >
                Engagement
              </button>

              <button
                className={topMetric === "popularity" ? "active" : ""}
                onClick={() => changeTopMetric("popularity")}
              >
                Popularity
              </button>

              <button
                className={topMetric === "rating" ? "active" : ""}
                onClick={() => changeTopMetric("rating")}
              >
                Rating
              </button>

              <button
                className={topMetric === "value" ? "active" : ""}
                onClick={() => changeTopMetric("value")}
              >
                Value
              </button>

            </div>

          </div>

          <div className="top-apps-table-wrapper">

            <table className="top-apps-table">

              <thead>
                <tr>
                  <th>#</th>
                  <th>App</th>
                  <th>Category</th>
                  <th>Rating</th>
                  <th>Popularity</th>
                  <th>Engagement</th>
                  <th>Monthly Price</th>
                  <th>Price Tier</th>
                </tr>
              </thead>

              <tbody>

                {topApps.map((app, index) => (
                  <tr key={app.id}>

                    <td className="rank-number">
                      {index + 1}
                    </td>

                    <td className="app-name-cell">
                      <strong>{app.app_name}</strong>
                      <span>{app.developer}</span>
                    </td>

                    <td>{app.category}</td>

                    <td>
                      {app.rating != null
                        ? app.rating.toFixed(2)
                        : "N/A"}
                    </td>

                    <td>
                      {app.popularity_score != null
                        ? app.popularity_score.toFixed(1)
                        : "N/A"}
                    </td>

                    <td>
                      {app.engagement_score != null
                        ? app.engagement_score.toFixed(1)
                        : "N/A"}
                    </td>

                    <td>
                      {app.normalized_monthly_price != null
                        ? `₹${app.normalized_monthly_price.toFixed(0)}`
                        : "N/A"}
                    </td>

                    <td>
                      <span className="price-tier">
                        {app.price_tier || "N/A"}
                      </span>
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>

        </div>

      </div>

      {/* CATEGORY COMPARISON */}
      <div className="analytics-section">

        <div className="analytics-panel">

          <div className="top-apps-header">

            <div>
              <h2>Category Comparison</h2>
              <p>
                Compare performance and pricing patterns across app
                categories.
              </p>
            </div>

          </div>

          <div className="top-apps-table-wrapper">

            <table className="top-apps-table">

              <thead>
                <tr>
                  <th>Category</th>
                  <th>Apps</th>
                  <th>Avg Rating</th>
                  <th>Avg Popularity</th>
                  <th>Avg Engagement</th>
                  <th>Avg Monthly Price</th>
                </tr>
              </thead>

              <tbody>

                {categories.map((category) => (
                  <tr key={category.category}>

                    <td>
                      <strong>{category.category}</strong>
                    </td>

                    <td>{category.app_count}</td>

                    <td>
                      {category.avg_rating != null
                        ? category.avg_rating.toFixed(2)
                        : "N/A"}
                    </td>

                    <td>
                      {category.avg_popularity != null
                        ? category.avg_popularity.toFixed(1)
                        : "N/A"}
                    </td>

                    <td>
                      {category.avg_engagement != null
                        ? category.avg_engagement.toFixed(1)
                        : "N/A"}
                    </td>

                    <td>
                      {category.avg_monthly_price != null
                        ? `₹${category.avg_monthly_price.toFixed(0)}`
                        : "N/A"}
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>

        </div>

      </div>

      {/* CORRELATIONS */}
      <div className="analytics-section">

        <div className="analytics-panel">

          <h2>Key Relationships</h2>

          <div className="correlation-grid">

            <div>
              <span>Rating ↔ Popularity</span>
              <strong>
                {correlations.rating_vs_popularity}
              </strong>
            </div>

            <div>
              <span>Rating ↔ Engagement</span>
              <strong>
                {correlations.rating_vs_engagement}
              </strong>
            </div>

            <div>
              <span>Popularity ↔ Engagement</span>
              <strong>
                {correlations.popularity_vs_engagement}
              </strong>
            </div>

            <div>
              <span>Price ↔ Engagement</span>
              <strong>
                {correlations.price_vs_engagement}
              </strong>
            </div>

          </div>

        </div>

      </div>

      {/* INSIGHTS */}
      <div className="analytics-panel insights-panel">

        <h2>Key Insights</h2>

        <div className="insight-list">

          <div className="insight-item">
            <strong>Engagement</strong>
            <p>
              Engagement combines rating and popularity, providing a broader
              view than either metric alone.
            </p>
          </div>

          <div className="insight-item">
            <strong>Pricing coverage</strong>
            <p>
              Only {overview.comparable_priced_apps} of{" "}
              {overview.total_apps} analyzed apps have directly comparable
              positive monthly prices.
            </p>
          </div>

          <div className="insight-item">
            <strong>Rating vs popularity</strong>
            <p>
              The correlation is{" "}
              {correlations.rating_vs_popularity}, showing a very weak
              linear relationship in this dataset.
            </p>
          </div>

          <div className="insight-item">
            <strong>Price vs engagement</strong>
            <p>
              The observed correlation is{" "}
              {correlations.price_vs_engagement}, indicating little linear
              relationship between monthly price and engagement in this
              sample.
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}

export default Analytics;