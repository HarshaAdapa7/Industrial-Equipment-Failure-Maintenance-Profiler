# Standard Operating Procedure: Power Failure (PWF) Mitigation

## 1. Overview
Power Failure (PWF) is triggered when mechanical power output ($P = \text{Torque} \times \text{Angular Velocity}$) falls outside safe operational limits ($P < 3500\text{ W}$ or $P > 9000\text{ W}$). Extreme high power risks electrical motor burnout and drive tripping, while unexpectedly low power indicates belt slippage, clutch disengagement, or material loss.

## 2. Telemetry Thresholds & Trigger Indicators
- **Power Deviation**: Calculated Mechanical Power $< 3500\text{ W}$ or $> 9000\text{ W}$.
- **Torque / RPM Ratio**: Abnormal ratio indicating stalling or unloaded racing.
- **Drive Amp Draw**: Exceeding 45 Amps on AC Servo Drive.

## 3. Immediate Action Protocol
1. **Emergency Ramp Down**: Initiate soft stop sequence to avoid kinetic backlash.
2. **Drive Motor & Transmission Check**:
   - Inspect drive belt tension and check for tooth shear or slipping.
   - Measure motor winding resistance using megohmmeter (insulation check).
   - Check main power supply voltage stability and frequency harmonics (400V 3-phase ±5%).
3. **Feed Rate Optimization**: Recalibrate feed per tooth parameter in CAM settings to ensure power remains centered around the optimal 6000 W operating sweet spot.

## 4. Expected Maintenance Duration & Cost
- **Estimated Downtime**: 45 – 60 minutes.
- **Standard Maintenance Cost**: $250 – $800 (Servo belt adjustment, drive recalibration).
- **Prevented Loss**: Prevents main spindle drive motor burnouts ($18,000+) and electrical inverter trips.
