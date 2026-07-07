from pathlib import Path
import fastf1
from fastf1.ergast import Ergast
import pandas as pd

_CACHE_INITIALIZED = False

def setup_f1_cache():
    global _CACHE_INITIALIZED
    if not _CACHE_INITIALIZED:
        cache_path = Path(__file__).parent / "cache"
        cache_path.mkdir(exist_ok=True)
        fastf1.Cache.enable_cache(cache_path)
        _CACHE_INITIALIZED = True


def get_multi_season_standings(seasons):
    ergast = Ergast()
    all_standings = []

    for season in seasons:
        response = ergast.get_driver_standings(season=season)
        df = response.content[0].copy()
        df["season"] = int(season)
        
        df['driverName'] = df['givenName'] + ' ' + df['familyName']
        df['constructorNames'] = df['constructorNames'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        df_clean = df[['season', 'position', 'points', 'wins', 'driverId', 'driverName', 'constructorNames']]

        all_standings.append(df_clean)
    return pd.concat(all_standings, ignore_index=True)


def get_gps_for_season(year):
    setup_f1_cache()
    schedule = fastf1.get_event_schedule(year)
    # Filter for real rounds (exclude pre-season testing)
    gps = schedule[schedule['RoundNumber'] > 0]
    return gps['EventName'].tolist()


def get_drivers_for_session(year, gp, session_type):
    setup_f1_cache()
    session = fastf1.get_session(year, gp, session_type)
    session.load(laps=True, telemetry=False, weather=False, messages=False)
    drivers_dict = {}
    for d in session.drivers:
        drv = session.get_driver(d)
        drivers_dict[drv['Abbreviation']] = {
            "number": d,
            "name": drv['FullName'],
            "team": drv['TeamName'],
            "color": drv['TeamColor'] if drv['TeamColor'] else "FF0000"
        }
    return drivers_dict


def get_session(year, gp, session_type):
    setup_f1_cache()
    session = fastf1.get_session(year, gp, session_type)
    session.load(laps=True, telemetry=True, weather=False, messages=False)
    return session


def get_driver_telemetry_from_session(session, driver):
    driver_laps = session.laps.pick_drivers(driver)
    if driver_laps.empty:
        raise ValueError(f"No laps found for driver {driver}")
        
    fastest_lap = driver_laps.pick_fastest()
    
    telemetry = fastest_lap.get_telemetry().copy()
    telemetry['time_seconds'] = telemetry['Time'].dt.total_seconds()

    lap_time_td = fastest_lap['LapTime']
    if pd.isnull(lap_time_td):
        lap_time_str = "No Time"
    else:
        minutes, seconds = divmod(lap_time_td.total_seconds(), 60)
        lap_time_str = f"{int(minutes)}:{seconds:06.3f}"
    
    drv_info = session.get_driver(driver)
    color = drv_info['TeamColor'] if drv_info['TeamColor'] else "FF0000"
    
    return {
        "telemetry": telemetry,
        "lap_time_str": lap_time_str,
        "lap_time": lap_time_td,
        "compound": fastest_lap['Compound'] if 'Compound' in fastest_lap else "Unknown",
        "team_color": f"#{color}",
        "team_name": drv_info['TeamName']
    }


def get_driver_telemetry(year, gp, session_type, driver):
    session = get_session(year, gp, session_type)
    return get_driver_telemetry_from_session(session, driver)



if __name__ == "__main__":
    print("Initializing Cache...")
    setup_f1_cache()

    print("Fetching standings for 2025...")
    standings = get_multi_season_standings([2025])
    print(standings.head(5))

    print("\nFetching telemetry for Verstappen in Monaco 2025 Quali...")
    tele_data = get_driver_telemetry(2025, "Monaco", "Q", "VER")
    print(f"Verstappen Lap Time: {tele_data['lap_time_str']}")
    print(tele_data['telemetry'][['Distance', 'Speed', 'Throttle', 'Brake', 'nGear']].head(5))

