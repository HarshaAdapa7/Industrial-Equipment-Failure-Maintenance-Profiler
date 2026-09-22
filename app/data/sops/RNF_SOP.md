# Standard Operating Procedure: Random Failure (RNF) Mitigation

## 1. Overview
Random Failures (RNF) represent unmodeled stochastic events occurring independently of measured wear or thermal parameters (~0.1% baseline probability). Causes include material inclusion hard-spots, electrical surges, or sensor communication glitches.

## 2. Immediate Action Protocol
1. **Full Diagnostics Scan**: Run complete PLC controller diagnostic cycle.
2. **Sensor Calibration Check**: Verify sensor cabling connections, ground shields, and analog-to-digital converter readings.
3. **Restart Sequence**: Reset alarm state on control console and run a dry-run test program without workpiece engagement.

## 3. Maintenance Duration & Cost
- **Estimated Downtime**: 10 – 15 minutes.
- **Cost**: $0 – $50 (Calibration / diagnostic check).
