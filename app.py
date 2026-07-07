import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import f1_data

# Set page config for a widescreen layout
st.set_page_config(
    page_title="Formula 1 Telemetry & Analytics",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom Premium CSS Styling (Dark Carbon Theme with F1 Red and Cyan accents)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600;700&display=swap');
    
    /* Global Overrides */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #0d0e12;
    }
    
    body {
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        letter-spacing: 0.05em;
    }
    
    /* Headers & Subheaders Custom Style */
    .f1-title {
        color: #ff1801;
        font-weight: 900;
        text-shadow: 0 0 15px rgba(255, 24, 1, 0.4);
        margin-bottom: 0.2rem;
    }
    .f1-subtitle {
        color: #8a99ad;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Glassmorphic Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 32, 42, 0.7), rgba(15, 16, 21, 0.7));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        margin-bottom: 1rem;
    }
    
    .metric-title {
        font-size: 0.85rem;
        color: #8a99ad;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    .metric-sub {
        font-size: 0.85rem;
        color: #10b981; /* Green success */
        margin-top: 0.3rem;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111216 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Custom divider line */
    .f1-divider {
        height: 4px;
        background: linear-gradient(90deg, #ff1801 0%, rgba(255, 24, 1, 0.1) 100%);
        border-radius: 2px;
        margin-bottom: 2rem;
    }
    
    /* Table Styling */
    .stDataFrame {
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        overflow: hidden;
    }

    /* Hide Deploy Button and Header Options */
    .stAppDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
    }
    footer {
        display: none !important;
        visibility: hidden !important;
    }

    /* Segmented Control / Header Buttons Styling */
    div[data-testid="stSegmentedControl"] {
        background: rgba(30, 32, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 30px !important;
        padding: 4px 6px !important;
        width: fit-content !important;
        margin-left: auto !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    
    div[data-testid="stSegmentedControl"] button {
        background-color: transparent !important;
        color: #8a99ad !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 10px 28px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    div[data-testid="stSegmentedControl"] button:hover {
        color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background: linear-gradient(135deg, #ff1801, #b31000) !important;
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(255, 24, 1, 0.5) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Layout (Top Navigation Row)
header_cols = st.columns([1, 1], vertical_alignment="center")

with header_cols[0]:
    st.markdown("<h1 style='margin:0; padding:0; color:#ff1801; font-family:Orbitron; font-size:2.2rem; text-shadow: 0 0 15px rgba(255, 24, 1, 0.4);'>🏎️ F1 DASHBOARD</h1>", unsafe_allow_html=True)

with header_cols[1]:
    page = st.segmented_control(
        "Navigation",
        options=["🏆 Season Standings", "⚡ Telemetry Analysis"],
        default="🏆 Season Standings",
        label_visibility="collapsed",
        key="navigation"
    )

# Add custom horizontal divider line at the top
st.markdown("<div class='f1-divider' style='margin-top: 1rem; margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

# Caching Data Calls for performance optimization
@st.cache_data(show_spinner="Fetching Standings from Ergast API...")
def cached_standings(seasons):
    return f1_data.get_multi_season_standings(seasons)

@st.cache_data(show_spinner="Loading GP list for season...")
def cached_gps(year):
    return f1_data.get_gps_for_season(year)

@st.cache_data(show_spinner="Loading drivers list for session...")
def cached_drivers(year, gp, session_type):
    try:
        return f1_data.get_drivers_for_session(year, gp, session_type)
    except Exception as e:
        st.error(f"Error fetching drivers: {e}")
        return {}

@st.cache_resource(show_spinner="Fetching telemetry session data (cache optimized)...")
def cached_session(year, gp, session_type):
    try:
        return f1_data.get_session(year, gp, session_type)
    except Exception as e:
        return None

# ----------------- PAGE 1: SEASON STANDINGS -----------------
if page == "🏆 Season Standings":
    st.markdown("<h2 style='margin-bottom: 0.2rem; font-family:Orbitron;'>Season Standings</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8a99ad; margin-bottom:2rem; font-size:1rem;'>View, filter, and analyze Formula 1 championship standings</p>", unsafe_allow_html=True)

    # Season selector
    seasons_available = list(range(2025, 2019, -1))
    selected_season = st.selectbox("Select Season", seasons_available, index=0)

    # Load data
    df_standings = cached_standings([selected_season])

    if df_standings.empty:
        st.warning("No standings data available for this season yet.")
    else:
        # Podium Display
        st.subheader("🏁 Drivers Championship Podium")
        cols = st.columns(3)
        
        # Helper for podium layout: 2nd place, 1st place, 3rd place
        podium_indices = [1, 0, 2] # 2nd, 1st, 3rd
        positions = ["🥈 2nd Place", "🥇 World Championship Leader", "🥉 3rd Place"]
        card_colors = ["border: 1px solid #c0c0c0;", "border: 1px solid #ffd700; box-shadow: 0 0 15px rgba(255, 215, 0, 0.25);", "border: 1px solid #cd7f32;"]

        for col_idx, p_idx in enumerate(podium_indices):
            if p_idx < len(df_standings):
                row = df_standings.iloc[p_idx]
                with cols[col_idx]:
                    st.markdown(
                        f"""
                        <div class='metric-card' style='{card_colors[col_idx]}'>
                            <div class='metric-title'>{positions[col_idx]}</div>
                            <div class='metric-value'>{row['driverName']}</div>
                            <div style='margin-top:0.5rem; font-weight:600; color:#ffffff;'>{row['constructorNames']}</div>
                            <div class='metric-sub'>{int(row['points'])} Points | {int(row['wins'])} Wins</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
        # Display full standings & Plotly charts side by side
        col_table, col_chart = st.columns([1, 1])
        
        with col_table:
            st.subheader("📋 Full Standings Table")
            display_df = df_standings.copy()
            display_df.columns = ["Season", "Pos", "Points", "Wins", "Driver ID", "Driver Name", "Constructor"]
            st.dataframe(
                display_df.set_index("Pos"),
                use_container_width=True,
                height=450
            )
            
        with col_chart:
            st.subheader("📊 Points Distribution")
            # Create interactive plotly bar chart
            fig = go.Figure()
            # Sort for nice horizontal chart
            chart_df = df_standings.sort_values("points", ascending=True)
            
            fig.add_trace(go.Bar(
                x=chart_df["points"],
                y=chart_df["driverName"],
                orientation='h',
                marker=dict(
                    color=chart_df["points"],
                    colorscale='Reds',
                    line=dict(color='rgba(255,24,1,1.0)', width=1)
                ),
                hovertemplate="<b>%{y}</b><br>Points: %{x}<extra></extra>"
            ))
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=10, b=10),
                xaxis=dict(
                    title="Points",
                    gridcolor='rgba(255,255,255,0.05)',
                    tickfont=dict(color='#8a99ad')
                ),
                yaxis=dict(
                    gridcolor='rgba(255,255,255,0.05)',
                    tickfont=dict(color='#8a99ad')
                ),
                height=450,
            )
            st.plotly_chart(fig, use_container_width=True)


# ----------------- PAGE 2: TELEMETRY ANALYSIS -----------------
elif page == "⚡ Telemetry Analysis":
    st.markdown("<h2 style='margin-bottom: 0.2rem; font-family:Orbitron;'>Telemetry Comparison</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8a99ad; margin-bottom:2rem; font-size:1rem;'>Overlay and compare vehicle telemetry from fastest laps</p>", unsafe_allow_html=True)

    # Telemetry selection panel
    col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
    
    with col_s1:
        year = st.selectbox("Season", [2025, 2024, 2023], index=0)
    
    # Load GP list for the year
    gps = cached_gps(year)
    
    with col_s2:
        # Default to Monaco if available, else first GP
        monaco_idx = 0
        for idx, gp in enumerate(gps):
            if "Monaco" in gp:
                monaco_idx = idx
                break
        selected_gp = st.selectbox("Grand Prix", gps, index=monaco_idx)
        
    with col_s3:
        selected_session = st.selectbox(
            "Session",
            ["Q", "R", "FP1", "FP2", "FP3"],
            index=0,
            format_func=lambda x: {"Q": "Qualifying", "R": "Race", "FP1": "Practice 1", "FP2": "Practice 2", "FP3": "Practice 3"}[x]
        )

    # Fetch drivers available for the session
    drivers_dict = cached_drivers(year, selected_gp, selected_session)
    
    if not drivers_dict:
        st.warning("Could not load drivers for this session. Please select another GP or Session.")
    else:
        st.subheader("🏎️ Driver Selection")
        # Multi-select for comparing drivers
        selected_driver_abbrs = st.multiselect(
            "Select Drivers to Compare (Maximum 2)",
            options=list(drivers_dict.keys()),
            default=list(drivers_dict.keys())[:2] if len(drivers_dict) >= 2 else list(drivers_dict.keys())[:1],
            format_func=lambda x: f"{x} - {drivers_dict[x]['name']} ({drivers_dict[x]['team']})"
        )
        
        if len(selected_driver_abbrs) > 2:
            st.error("Please select a maximum of 2 drivers for overlay telemetry comparison.")
        elif len(selected_driver_abbrs) == 0:
            st.info("Select at least one driver to begin visual analysis.")
        else:
            # Fetch telemetry for selected drivers using cached session object
            tele_results = {}
            error_occured = False
            
            # Load cached session resource (loads only once per GP/session)
            session_obj = cached_session(year, selected_gp, selected_session)
            
            if session_obj is None:
                st.error("Failed to load session data. This session might not be available yet.")
                error_occured = True
            else:
                with st.spinner("Processing driver telemetry..."):
                    for abbr in selected_driver_abbrs:
                        try:
                            # Extract telemetry instantly in memory from the loaded session
                            data = f1_data.get_driver_telemetry_from_session(session_obj, abbr)
                            tele_results[abbr] = data
                        except Exception as e:
                            st.error(f"Failed to extract telemetry for driver {abbr}: {e}")
                            error_occured = True
            
            if not error_occured and tele_results:
                # Top metrics side by side
                st.write("")
                cols = st.columns(len(selected_driver_abbrs))
                
                for idx, abbr in enumerate(selected_driver_abbrs):
                    drv_data = tele_results[abbr]
                    drv_meta = drivers_dict[abbr]
                    color_style = f"border-left: 5px solid {drv_data['team_color']};"
                    
                    with cols[idx]:
                        max_speed = int(drv_data['telemetry']['Speed'].max())
                        st.markdown(
                            f"""
                            <div class='metric-card' style='{color_style}'>
                                <div class='metric-title'>{drv_meta['name']}</div>
                                <div class='metric-value'>{drv_data['lap_time_str']}</div>
                                <div style='font-size:0.9rem; margin-top:0.4rem;'>
                                    Team: <b style='color:{drv_data["team_color"]}'>{drv_data['team_name']}</b> | Compound: <b>{drv_data['compound']}</b>
                                </div>
                                <div class='metric-sub' style='color:#ffffff;'>
                                    Max Speed: <span style='font-family:Orbitron; font-weight:700; color:#ff1801;'>{max_speed} km/h</span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
                # Interactive Plotly Overlay Graphs
                st.subheader("📉 Shared-Axis Telemetry Overlays")
                
                # Create subplots sharing X axis (Distance)
                fig = make_subplots(
                    rows=3, 
                    cols=1, 
                    shared_xaxes=True, 
                    vertical_spacing=0.1,  # Increased spacing for proper gap
                    subplot_titles=("Speed Comparison (km/h)", "Throttle (%) & Brake Application", "Gear Profile"),
                    row_heights=[0.45, 0.32, 0.23]
                )
                
                # Curated contrasting color palette for clear driver comparison (Cyan & Neon Pink)
                comparison_colors = ["#00F2FE", "#FF2D55"]
                
                # Plot telemetry curves for each driver
                for idx, abbr in enumerate(selected_driver_abbrs):
                    drv_data = tele_results[abbr]
                    tele_df = drv_data['telemetry']
                    
                    # Use contrasting comparison colors
                    color = comparison_colors[idx % len(comparison_colors)]
                    
                    # Row 1: Speed
                    fig.add_trace(go.Scatter(
                        x=tele_df['Distance'],
                        y=tele_df['Speed'],
                        name=f"{abbr} - Speed",
                        line=dict(color=color, width=2.5),
                        hovertemplate="%{y} km/h"
                    ), row=1, col=1)
                    
                    # Row 2: Throttle (solid line)
                    fig.add_trace(go.Scatter(
                        x=tele_df['Distance'],
                        y=tele_df['Throttle'],
                        name=f"{abbr} - Throttle",
                        line=dict(color=color, width=2, dash='solid'),
                        legendgroup=f"{abbr}_pedals",
                        hovertemplate="%{y}%"
                    ), row=2, col=1)
                    
                    # Row 2: Brake (filled step chart for a professional ATLAS/Motec look)
                    brake_mapped = tele_df['Brake'].apply(lambda x: 100 if x else 0)
                    fill_rgba = "rgba(0, 242, 254, 0.12)" if idx == 0 else "rgba(255, 45, 85, 0.12)"
                    
                    fig.add_trace(go.Scatter(
                        x=tele_df['Distance'],
                        y=brake_mapped,
                        name=f"{abbr} - Brake",
                        line=dict(color=color, width=1.5, dash='dot'),
                        fill='tozeroy',
                        fillcolor=fill_rgba,
                        legendgroup=f"{abbr}_pedals",
                        hovertemplate="Brake: %{text}",
                        text=tele_df['Brake'].apply(lambda x: "ON" if x else "OFF")
                    ), row=2, col=1)
                    
                    # Row 3: Gear (step chart)
                    fig.add_trace(go.Scatter(
                        x=tele_df['Distance'],
                        y=tele_df['nGear'],
                        name=f"{abbr} - Gear",
                        line=dict(color=color, width=2, shape='hv'),
                        hovertemplate="Gear: %{y}"
                    ), row=3, col=1)
                
                # Update Layout aesthetics
                fig.update_layout(
                    height=850,  # Increased height to give subplots breathing room
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=30, r=30, t=60, b=30),  # Adjusted top margin for centered legend
                    hovermode="x unified",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.05,
                        xanchor="center",
                        x=0.5,
                        font=dict(color='#8a99ad', size=11),
                        bgcolor='rgba(13, 14, 18, 0.6)',
                        bordercolor='rgba(255, 255, 255, 0.1)',
                        borderwidth=1
                    )
                )
                
                # Style the subplot titles with Orbitron font
                fig.update_annotations(
                    font=dict(family="Orbitron", size=13, color="#ffffff")
                )
                
                # Customize axes styling
                for r in [1, 2, 3]:
                    fig.update_xaxes(
                        showgrid=True, 
                        gridcolor='rgba(255,255,255,0.05)', 
                        zeroline=False,
                        tickfont=dict(color='#8a99ad'),
                        row=r, col=1
                    )
                    fig.update_yaxes(
                        showgrid=True, 
                        gridcolor='rgba(255,255,255,0.05)', 
                        zeroline=False,
                        tickfont=dict(color='#8a99ad'),
                        row=r, col=1
                    )
                
                # Label X-axis on last row only
                fig.update_xaxes(title_text="Distance (Meters)", row=3, col=1)
                
                # Render chart
                st.plotly_chart(fig, use_container_width=True)
                
                # Pro tip helper
                st.markdown(
                    """
                    <div style='background-color:#1e202a; border-radius:8px; padding:1rem; border: 1px solid rgba(255,255,255,0.05); margin-top:1.5rem;'>
                        💡 <b>Analysis Tip:</b> Hover anywhere on the graphs to see a unified view comparing both drivers' speed, throttle percentage, brake application, and selected gears at that exact position of the circuit. Use the zoom tools to inspect corners in detail.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
