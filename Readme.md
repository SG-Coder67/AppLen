AppLen

AppLen is a data analytics project that studies mobile applications, their pricing models, user ratings, downloads, and other metadata to understand how apps create and communicate value to users.

The project focuses on building a reproducible data pipeline that collects app metadata and pricing information, cleans and enriches the data, stores the final dataset, and produces analytical insights through SQL/Python and an interactive dashboard.

⸻

Project Objective

The goal of AppLen is to answer questions such as:

* Which app categories have the highest average prices?
* How do free, freemium, and subscription-based apps compare?
* Does higher pricing correlate with better ratings?
* Does popularity/download volume correlate with pricing?
* Which categories rely most heavily on subscriptions?
* How much do annual plans save compared with monthly plans?
* Which apps provide the most value relative to their price and popularity?
* How do pricing strategies differ between categories?

⸻

Project Scope

The initial dataset contains 90 applications across 15 categories.

Categories

* Music
* Streaming
* Education
* Productivity
* Cloud Storage
* AI Tools
* Health & Fitness
* Finance
* Shopping / E-Commerce
* Communication
* Travel
* Design
* Photo & Video
* Developer Tools
* Security & VPN

The dataset contains a mixture of:

* Subscription-based applications
* Freemium applications
* Free applications
* Transaction-based platforms
* Mixed pricing models

⸻

Project Architecture

                    ┌─────────────────────┐
                    │   App Sources       │
                    │                     │
                    │ Google Play /       │
                    │ Official Websites   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Data Collection     │
                    │      Python         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Raw Dataset         │
                    │       CSV           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Cleaning &          │
                    │ Validation          │
                    │      Pandas         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Pricing Enrichment  │
                    │ + Verification      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Final Dataset       │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
        ┌─────────────────┐        ┌─────────────────┐
        │ PostgreSQL      │        │ Python / Pandas │
        │ Database        │        │ Analytics       │
        └────────┬────────┘        └────────┬────────┘
                 │                           │
                 └─────────────┬─────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Dashboard           │
                    │ Visualization       │
                    └─────────────────────┘

⸻

Data Pipeline

AppLen follows an ETL-oriented workflow:

1. Extract

Application metadata is collected from sources such as Google Play and official application websites.

Collected metadata includes:

* Application name
* Category
* Developer
* Rating
* Downloads

Pricing information is collected separately and verified against reliable sources.

2. Transform

The raw data is cleaned using Python and Pandas.

Current cleaning tasks include:

* Converting download counts into numeric values
* Handling missing values
* Detecting duplicates
* Validating categories
* Standardizing data types
* Validating pricing information

3. Load

The finalized dataset will be loaded into PostgreSQL for structured querying and analytics.

⸻

Current Dataset

The initial metadata dataset contains:

90 applications
15 categories
6 applications per category

Current metadata columns:

app_name
category
developer
rating
downloads

Pricing enrichment adds fields such as:

monthly_price
yearly_price
currency
free_trial_days
pricing_type
pricing_source
pricing_date
pricing_status

The pricing dataset is intentionally allowed to contain missing values during the initial collection phase.

A missing value does not automatically mean that an application is free.

During the data-quality phase, remaining missing values will be investigated using additional reliable sources.

⸻

Data Quality Strategy

AppLen follows a conservative data-quality approach.

We do not fabricate missing values simply to make the dataset complete.

The workflow is:

Initial collection
       ↓
Verified data
       ↓
Identify missing values
       ↓
Secondary source verification
       ↓
Fill only genuinely verified values
       ↓
Keep unresolved values as NULL
       ↓
Final validated dataset

This ensures that the analytical results remain reproducible and defensible.

⸻

Technology Stack

Data Collection

* Python
* Google Play Scraper
* Requests / web-based sources where appropriate

Data Processing

* Pandas
* Python

Database

* PostgreSQL
* SQLAlchemy

Backend

* FastAPI
* Pydantic
* Uvicorn

Analytics

* Python
* Pandas
* SQL

Visualization

* Dashboard layer
* Interactive charts and analytical summaries

Development

* Git
* GitHub
* VS Code

⸻

Project Structure

AppLen/
│
├── collector/
│   ├── collect_apps.py
│   ├── metadata_collector.py
│   └── clean_metadata.py
│
├── data/
│   ├── raw/
│   │   ├── apps_master.csv
│   │   └── apps_metadata.csv
│   │
│   └── cleaned/
│       └── apps_cleaned.csv
│
├── analytics/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── database.py
│   │   └── main.py
│   │
│   └── tests/
│
├── dashboard/
│
├── alembic/
│   └── versions/
│
├── .gitignore
├── README.md
└── requirements.txt

⸻

Example Data Cleaning

Raw download values such as:

1,000,000,000+

are transformed into numeric values that can be used for analysis.

Example:

def clean_downloads(value):
    if pd.isna(value):
        return None
    value = value.replace(",", "")
    value = value.replace("+", "")
    return int(value)

⸻

Planned Analytics

Once the final dataset is completed, AppLen will perform exploratory and statistical analysis.

Pricing Analysis

* Average monthly price by category
* Average annual price by category
* Most expensive applications
* Cheapest paid applications
* Free vs paid distribution

Pricing Model Analysis

Free
Freemium
Subscription
Transaction-based
Mixed

Popularity Analysis

* Downloads by category
* Rating vs downloads
* Price vs downloads
* Price vs rating

Subscription Analysis

* Monthly vs annual pricing
* Annual discount percentage
* Trial availability
* Subscription adoption by category

Value Analysis

Potential value metrics will combine factors such as:

Rating
Downloads
Price
Pricing model

The exact formula will be defined after the final dataset is validated rather than arbitrarily assigning weights beforehand.

⸻

Data Quality Checks

Before analytics, the final dataset will undergo checks for:

* Missing values
* Duplicate applications
* Invalid prices
* Invalid ratings
* Invalid download values
* Inconsistent currencies
* Incorrect categories
* Duplicate pricing records
* Outdated pricing information

⸻

Database

The cleaned and enriched data will eventually be stored in PostgreSQL.

The database layer uses:

* SQLAlchemy ORM
* PostgreSQL
* Alembic migrations

This allows the project to move from static CSV-based analysis toward a structured analytical application.

⸻

API

The backend is being developed using FastAPI.

Planned API functionality includes:

GET    /apps
GET    /apps/{id}
POST   /apps
PUT    /apps/{id}
DELETE /apps/{id}

Additional analytical endpoints will be added after the dataset and database schema are finalized.

⸻

Dashboard

The final dashboard will provide an interactive view of:

* App categories
* Pricing models
* Monthly and yearly prices
* Ratings
* Downloads
* Category comparisons
* Pricing trends
* Value analysis

The dashboard will be built on top of the finalized analytical dataset rather than directly using incomplete raw data.

⸻

Reproducibility

The project is designed so that the data pipeline can be executed again as sources change.

The intended workflow is:

python collector/metadata_collector.py
python collector/clean_metadata.py

Additional enrichment and database-loading scripts will be added as the project progresses.

⸻

Current Status

Completed

* Project structure
* Application category selection
* Initial application list
* Metadata collection
* Raw CSV dataset
* Metadata cleaning
* Duplicate checking
* Missing-value identification
* Initial pricing collection
* Pricing model classification

In Progress

* Verify remaining pricing values
* Enrich missing pricing information
* Finalize pricing dataset
* Merge metadata and pricing datasets
* Final data-quality validation
* PostgreSQL schema
* Load final dataset into PostgreSQL
* SQL analytics
* Python analytics
* FastAPI analytical endpoints
* Dashboard
* Final documentation

⸻

Future Improvements

Possible future additions include:

* Historical pricing tracking
* Automated periodic data collection
* More applications and categories
* Regional pricing comparison
* App-store ranking analysis
* Pricing change detection
* Automated data-quality checks
* Scheduled ETL pipeline
* More advanced statistical analysis

⸻

Disclaimer

App pricing, plans, availability, and features can change over time and may vary by region.

AppLen records pricing together with its source and collection date wherever possible. Analytical conclusions are based on the dataset available at the time of collection.

⸻

Author

Sarath Ganesh

B.Tech Information Technology
VIT Vellore

⸻

License

This project is intended primarily for educational, portfolio, and analytical purposes.
