# ACE Control Deck — Next-Gen Multi-Material Command Deck & Visualizer for Klipper

> [!WARNING]
> **BETA STATUS**: ACE Control Deck is currently in active **BETA** development (`v0.9.0-beta`). Interfaces, macro bindings, and features are subject to active refinement. Tested primarily on Anycubic ACE 2 Pro CoreXY/Voron integrations. Feedback, issue reports, and PRs are actively encouraged!

The **ACE Control Deck** is the official standalone command center and real-time visualizer for the Anycubic ACE 2 Pro (and similar multi-material systems) running on Klipper and Moonraker. It provides a production-grade interface for filament telemetry, hardware control, thermal management, and motion analytics.

## Architecture & Ecosystem

ACE Control Deck is the **Frontend Visualizer** and command dispatcher. It strictly relies on the **`multiACE`** backend driver to communicate with the ACE hardware.

`ACE 2 Pro Hardware (Custom Firmware) <--> multiACE Backend (decay71/multiACE) <--> Klipper & Moonraker <--> ACE Control Deck (Frontend)`

## Key Features

- **Interactive 4-Slot Multi-Material Visualization**: Live color swatches, brand labels, spool IDs, and material badges mapped directly to your Spoolman / OpenRFID data.
- **Real-Time Filament Path & Sensor Telemetry**: Instant visualization of filament traversal through the system (Hub switch, Entry switch, Postgear switch, Meltzone state).
- **Active Heating & Dryer Thermal Control**: Manage active drying with target temperatures, interactive temperature graphing, humidity (RH%) monitoring, and countdown timers.
- **Rotisserie & Dry Roll Motion Tracking**: Agitation mode for even heating, rotation angle tracking, and park datum state synchronization.
- **Configurable Auxiliary Actions**: Fully customizable macro buttons for Purging, Wiping, Loading, and Unloading to fit your specific printer's kinematics.
- **Mainsail & Fluidd Embeddable or Standalone**: Drop it directly into your Mainsail sidebar, host it via Moonraker static files, or run it as a responsive tablet/mobile web dashboard.

## Requirements & Hardware Prerequisites

To use the ACE Control Deck, your ecosystem must meet the following strict requirements:

1. **Physical Unit**: Anycubic ACE 2 Pro.
2. **Firmware Requirement**: Stock Anycubic firmware does NOT expose Moonraker/Klipper WebSocket APIs! The ACE 2 Pro **MUST** be flashed with open-source custom firmware compatible with the backend driver.
3. **Backend Driver**: Klipper + Moonraker running the **[`decay71/multiACE`](https://github.com/decay71/multiACE)** module (or a compatible fork). ACE Control Deck subscribes directly to `multiACE` printer objects for state.
4. **Sensors**: The deck visualizes `filament_switch_sensor hub_detect`, `toolhead_entry`, and `toolhead_postgear`. It degrades gracefully if you lack certain switches, but `hub_detect` is critical for multi-material parking.

## Installation Methods

### Method 1: Drop-in Single File / Tablet Web App (Easiest)
1. Download `index.html`.
2. Open `index.html` directly in any web browser on your tablet, phone, or desktop.
3. Click the **Settings (Gear)** icon in the top right and enter your Moonraker IP and port (e.g., `192.168.1.50:7125`). The app will instantly connect and save your settings.

### Method 2: Moonraker Static File Hosting
You can host the dashboard directly from your Klipper machine:
1. SSH into your Pi.
2. Clone this repository into a directory (e.g., `/home/pi/ace-control-deck`).
3. Add a static path to your `moonraker.conf`:
   ```ini
   [server]
   ...
   
   [static_file_path ace_deck]
   path: ~/ace-control-deck
   ```
4. Restart Moonraker. Access it via `http://<printer_ip>:7125/ace_deck/index.html`.

### Method 3: Mainsail Custom Sidebar Tab (iframe integration)
We provide an installation script to patch Mainsail's routing table to include ACE Control Deck natively in the sidebar:
1. Clone the repository to your pi:
   ```bash
   cd ~
   git clone https://github.com/Simon-CR/ace-control-deck.git
   ```
2. Run the patcher script:
   ```bash
   cd ace-control-deck/scripts
   ./install.sh --mainsail-path ~/mainsail
   ```
   *(If you omit `--mainsail-path`, it will default to `~/mainsail`)*
3. Refresh your Mainsail interface in the browser. You will now see an "ACE Deck" tab.

## Configuration & Connection Guide

- **Connection Setup**: If using the app standalone, use the UI settings modal (gear icon) to set your printer's address. Alternatively, you can pass the host via the URL: `index.html?host=192.168.1.100:7125`.
- **Macro Customization**: ACE Control Deck no longer enforces rig-specific macros (e.g. `GOOSE_PURGE` or `KOMB`). You can configure the exact commands dispatched by the UI using the **Settings Gear** in the top right:
  - **Load Command Template**: e.g. `ACE_LOAD SLOT={slot}` or `T{slot}`
  - **Unload Command Template**: e.g. `ACE_UNLOAD SLOT={slot}` or `ACE_EJECT T={slot}`
  - **Purge Macro Name**: e.g. `PURGE` or `CLEAN_NOZZLE`. Buttons will only appear if the macro exists in Klipper.

### Sample Configuration

A sample macro wrapper configuration is provided in `config/ace_deck_macros_sample.cfg` to bridge the deck's default templates into `multiACE` commands.

## Hardware Invariants & Operational Caveats

- **Clamped Idle Lanes**: Idle ACE 2 lanes clamp rather than freewheel. Ensure active lanes are properly normalized before attempting pulls.
- **Encoder Regimes**: The Hub encoder is direction-blind; rely on the switch sensors (hub, toolhead entry, postgear) for verified motion boundaries.
- **Thermal Safety Interlocks**: Cold-side loading stops at the postgear sensor; meltzone heating is strictly required before a nozzle push can execute.

## Filament Path Architecture

```mermaid
flowchart LR
    S[Spool 0..3] -->|Teflon Tube| H[Hub Switch]
    H --> E[Toolhead Entry]
    E --> G[Postgear Switch]
    G --> M[Meltzone]
```

## License

GPL-3.0 License.
