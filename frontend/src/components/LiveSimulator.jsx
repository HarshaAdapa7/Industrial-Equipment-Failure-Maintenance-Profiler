import React, { useState } from 'react';
import { Play, Pause, Zap, AlertTriangle, Activity, Sliders } from 'lucide-react';
import { api } from '../services/api';

export default function LiveSimulator({ machines, isSimulating, onToggleSimulator, selectedMachineId }) {
  const [speed, setSpeed] = useState(1.0);
  const [faultMessage, setFaultMessage] = useState(null);

  const activeMachineId = selectedMachineId || (machines[0] ? machines[0].id : null);

  const handleSpeedChange = async (e) => {
    const val = parseFloat(e.target.value);
    setSpeed(val);
    if (isSimulating) {
      await api.startSimulator(val);
    }
  };

  const handleInjectFault = async (faultType) => {
    if (!activeMachineId) return;
    try {
      setFaultMessage(`Injecting synthetic ${faultType} fault...`);
      const res = await api.injectFault(activeMachineId, faultType);
      setFaultMessage(`Synthetic ${faultType} fault successfully injected into active machine!`);
      setTimeout(() => setFaultMessage(null), 4000);
    } catch (e) {
      console.error("Fault injection error:", e);
      setFaultMessage("Failed to inject fault.");
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={20} color="#06b6d4" />
            <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f8fafc' }}>
              Real-Time Telemetry Simulator & Synthetic Fault Injector
            </h3>
          </div>
          <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>
            Stream AI4I 2020 dataset telemetry in real time or trigger synthetic failure degradation scenarios.
          </p>
        </div>

        {/* Speed & Stream Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={16} color="#94a3b8" />
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Stream Interval:</span>
            <select
              value={speed}
              onChange={handleSpeedChange}
              style={{
                background: 'rgba(0,0,0,0.4)',
                border: '1px solid rgba(255,255,255,0.1)',
                color: '#fff',
                padding: '4px 8px',
                borderRadius: '6px',
                fontSize: '0.8rem'
              }}
            >
              <option value={0.5}>0.5s (Fast)</option>
              <option value={1.0}>1.0s (Normal)</option>
              <option value={2.0}>2.0s (Slow)</option>
            </select>
          </div>

          <button
            onClick={onToggleSimulator}
            className={`btn ${isSimulating ? 'btn-danger' : 'btn-primary'}`}
            style={{ padding: '8px 16px', fontSize: '0.85rem' }}
          >
            {isSimulating ? <><Pause size={16} /> Pause Stream</> : <><Play size={16} /> Start Stream</>}
          </button>
        </div>
      </div>

      {/* Fault Injection Buttons Bar */}
      <div style={{ paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.08)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: '600', color: '#94a3b8' }}>
          Synthetic Fault Injection Suite (Trigger Degradation Scenario):
        </span>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            onClick={() => handleInjectFault('TWF')}
            className="btn btn-secondary"
            style={{ borderLeft: '4px solid #ef4444', fontSize: '0.8rem' }}
          >
            <Zap size={14} color="#ef4444" /> Inject Tool Wear Failure (TWF)
          </button>

          <button
            onClick={() => handleInjectFault('HDF')}
            className="btn btn-secondary"
            style={{ borderLeft: '4px solid #f59e0b', fontSize: '0.8rem' }}
          >
            <AlertTriangle size={14} color="#f59e0b" /> Inject Heat Dissipation Failure (HDF)
          </button>

          <button
            onClick={() => handleInjectFault('PWF')}
            className="btn btn-secondary"
            style={{ borderLeft: '4px solid #3b82f6', fontSize: '0.8rem' }}
          >
            <Zap size={14} color="#3b82f6" /> Inject Power Failure (PWF)
          </button>

          <button
            onClick={() => handleInjectFault('OSF')}
            className="btn btn-secondary"
            style={{ borderLeft: '4px solid #8b5cf6', fontSize: '0.8rem' }}
          >
            <AlertTriangle size={14} color="#8b5cf6" /> Inject Overstrain Failure (OSF)
          </button>
        </div>

        {faultMessage && (
          <div style={{ fontSize: '0.8rem', color: '#10b981', background: 'rgba(16,185,129,0.1)', padding: '6px 12px', borderRadius: '6px', marginTop: '4px' }}>
            {faultMessage}
          </div>
        )}
      </div>
    </div>
  );
}
