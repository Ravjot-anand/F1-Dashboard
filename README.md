# 🏎️ Formula 1 Analytics & Telemetry Dashboard

A premium, high-performance, dark-themed analytics web application designed with **Streamlit** and **Plotly** to visualize Formula 1 championship standings and compare driver telemetry in high definition.

---

## 🚀 Key Features

*   **🏆 Season Standings**: View interactive driver championship standings tables, dynamic championship leaderboards, and points distribution charts for any season (2020–2025).
*   **⚡ Overlay Telemetry Comparison**: Overlay and sync speed (km/h), throttle percentage, braking zones, and gear profiles on a shared distance axis.
*   **🏎️ Motec/ATLAS Inspired Brake Zones**: Visualizes active braking zones as shaded translucent overlays beneath the throttle curve.
*   **🎨 Premium Dark UI**: Formatted with custom typography (`Orbitron` & `Inter`), custom carbon styling, and locked dark mode.
*   **⚡ Under-300ms Comparisons**: Leveraging memory-caching of F1 session objects, switching or selecting comparison drivers renders instantly.
*   **📦 Production Ready**: Excluded development debris and compiled python artifacts via `.gitignore` and configured to run in minimal viewer mode (hidden developer menus and deploy buttons).

---

## 🧠 Application Logic & Architecture

The application is structured into two main modules: the backend data-fetcher ([f1_data.py](f1_data.py)) and the frontend interface ([app.py](app.py)).

### 1. High-Performance Session Loading & Caching
F1 telemetry files can be very large (often 30+ MB per session). Standard API loading pulls weather logs, messages, and all driver laps which is extremely slow. We optimized this behavior with the following logic:

*   **Selective API Loading**: When loading a session, we selectively retrieve only lap and telemetry data:
    ```python
    session.load(laps=True, telemetry=True, weather=False, messages=False)
    ```
    This cuts data fetch times by up to 50% by ignoring unneeded network resources.
*   **Memory Caching**: We utilize Streamlit's `@st.cache_resource` to cache the loaded FastF1 `Session` object in memory:
    ```python
    @st.cache_resource(show_spinner="Fetching telemetry session data...")
    def cached_session(year, gp, session_type):
        return f1_data.get_session(year, gp, session_type)
    ```
    When the dashboard loads telemetry for two drivers, it requests the same cached session. The second driver's telemetry is retrieved instantly from memory in **under 300ms** (down from a 15–20s load time).

### 2. Synced Telemetry Plotting
*   **Shared Distance X-Axis**: Subplots are created using Plotly's `make_subplots` with `shared_xaxes=True`. This ensures that hovering over any point on the track highlights the speed, throttle, brake state, and gear of both drivers at that exact meter of the lap.
*   **Visualizing Pedal telemetry**: 
    - **Throttle**: Rendered as a solid line (0–100%).
    - **Brakes**: Rendered as a dashed step line, coupled with a translucent filled area (`rgba(...)`) under the curve. When the brake is `ON`, the area is shaded, providing a clear visual contrast of braking points.
*   **High-Contrast Color Mapping**: To avoid overlapping lines of similar colors (e.g. orange and red), we map drivers to a curated high-contrast palette:
    - **Driver 1 (Primary)**: Electric Cyan (`#00F2FE`)
    - **Driver 2 (Secondary)**: Neon Pink/Coral (`#FF2D55`)

### 3. Clean CSS & Custom Theme Enforcements
*   **Locked Dark Mode**: Configured [.streamlit/config.toml](.streamlit/config.toml) to enforce dark mode. This locks the application's base theme and disables standard Streamlit light/dark toggles.
*   **Minimalist View Mode**: Configured `toolbarMode = "minimal"` and `hideTopBar = true` inside the streamlit configuration. We also inject CSS overrides inside `app.py` to completely hide developer menus:
    ```css
    .stAppDeployButton { display: none !important; visibility: hidden !important; }
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    ```
*   **Top Navigation Layout**: Page selection is moved out of the sidebar to the top header area using `st.segmented_control` styled as rounded tabs with F1 red gradient active states.

---

## 📁 Repository Structure

```
├── .streamlit/
│   └── config.toml          # Custom Streamlit theme and UI constraints
├── cache/                   # Local cached FastF1 API data (ignored by git)
├── .gitignore               # Excludes virtual environments & local cache
├── README.md                # Documentation and project logic
├── app.py                   # Streamlit dashboard UI & chart renderings
├── f1_data.py               # FastF1 data loaders & Ergast Standings API
└── requirements.txt         # Project dependencies
```

---

## 🛠️ Installation & Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Ravjot-anand/F1-Dashboard.git
    cd F1-Dashboard
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python -m venv .venv
    ```

3.  **Activate the Environment**:
    *   **Windows (Command Prompt)**:
        ```cmd
        .venv\Scripts\activate.bat
        ```
    *   **Windows (PowerShell)**:
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
    *   **macOS / Linux**:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the Dashboard Locally**:
    ```bash
    streamlit run app.py
    ```

The dashboard will open automatically in your browser at `http://localhost:8501`.
