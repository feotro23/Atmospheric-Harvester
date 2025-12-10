# Atmospheric Harvester

A dynamic resources management and farming game powered by **real-time weather data**.  
*Harvest resources from the atmosphere, grow weather-dependent crops, and build a sustainable sky-island base.*

<img width="1922" height="1112" alt="image" src="https://github.com/user-attachments/assets/5e26151a-0f9e-42bc-b9e6-614b062a6ce6" />


## 🎮 Gameplay
You are an "Atmospheric Harvester" stationed on a floating island. Your goal is to collect energy, water, and biomass to expand your base and discover new crops and creatures.
But be careful—**the weather in the game reflects real-world weather patterns from around the globe.**

### Key Features
*   **Real-Time Weather**: Connects to NWS and Open-Meteo to simulate real conditions (Wind, Rain, Solar, Temperature).
*   **Dynamic Resources**:
    *   **Wind Turbines**: Generate Energy during windy conditions.
    *   **Solar Panels**: Generate Energy on sunny days.
    *   **Rain Collectors**: Collect Water during rainstorms.
*   **Farming**: Grow crops that react to moisture and temperature.
    *   *Cactus*: Thrives in heat, requires little water.
    *   *Rice*: Needs lots of water (rain or sprinklers).
    *   *Winter Wheat*: Survives in the cold.
*   **Creature Collection**: Capture elemental creatures that spawn during specific weather events.
    *   *Fulgarite Golem*: Spawns in Thunderstorms.
    *   *Frost Wisp*: Spawns in Freezing temperatures.
*   **Base Building**: Construct batteries, water tanks, sprinklers, and heaters to manage your environment.

## 🚀 Installation

1.  **Prerequisites**: Python 3.8+
2.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/atmospheric-harvester.git
    cd atmospheric-harvester
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🕹️ Controls

| Key | Action |
| :--- | :--- |
| **W A S D** | Pan Camera |
| **1 - 6** | Travel to different global locations |
| **B** | Open **Build Menu** |
| **F** | Toggle **Farming Overlay** |
| **M** | Open **Missions** |
| **E** | Show **Weather Events** |
| **U** | Open **Upgrades** |
| **X** | Toggle **Edit/Move Mode** |
| **Left Click** | Interact / Place / Harvest |
| **Right Click** | Cancel / Deselect |
| **Scroll** | Zoom (if supported) / Scroll Lists |
| **F5 / F9** | Quick Save / Quick Load |

## 🛠️ Tech Stack
*   **Engine**: `pygame-ce` (Community Edition)
*   **Networking**: `aiohttp` for async API requests.
*   **APIs**:
    *   National Weather Service (NWS)
    *   Open-Meteo
    *   Nominatim (OpenStreetMap)

## ⚠️ Notes
*   The game requires an internet connection to fetch initial weather data.
*   `assets/` folder must be present for the game to run.
