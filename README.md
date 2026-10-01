# ACE Control Deck

## Hardware Sensor Requirements & Topology Tiers

The ACE Control Deck adapts dynamically based on your sensor configuration. Below are the hardware sensor requirements and topology tiers:

### Tier 1: Minimal / 1 Toolhead Sensor
- Features a single toolhead sensor.
- Trade-offs: Blind feed.

### Tier 2: Standard / Hub + Toolhead
- Features a hub sensor and a toolhead sensor.
- Advantages: Staged loading, preventing fracture.

### Tier 3: High-Reliability Voron / CoreXY
- Features a hub sensor, entry sensor, post-gear sensor, and encoder.
- Advantages: 100% ground truth for high reliability.
