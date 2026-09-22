import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar, Cell } from 'recharts';
import { Cpu, ShieldAlert, CheckCircle, FileText, DollarSign, RefreshCw, Zap } from 'lucide-react';
import { api } from '../services/api';

export default function MachineDetail({ machineId, machines }) {
  const [detail, setDetail] = useState(null);
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(true);

  const selectedMachine = machines.find(m => m.id === machineId) || machines[0];

  const fetchMachineData = async () => {
    if (!machineId) return;
    setLoading(true);
    try {
      const data = await api.getMachineDetail(machineId);
      setDetail(data);

      const agentData = await api.diagnoseMachine(machineId);
      setDiagnosis(agentData);
    } catch (e) {
      console.error("Error fetching machine detail or agent diagnosis:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMachineData();
  }, [machineId]);

  if (!selectedMachine) return <div style={{ color: '#94a3b8' }}>Select a machine to inspect.</div>;

  const latestPred = detail?.latest_prediction || {
    risk_score: 15.0,
    health_score: 85.0,
    label_probs: { TWF: 0.12, HDF: 0.02, PWF: 0.05, OSF: 0.08, RNF: 0.00 }
  };

  // Format Failure Mode Bar Data
  const failureModeData = Object.entries(latestPred.label_probs || {}).map(([key, val]) => ({
    mode: key,
    prob: Math.round(val * 100)
  }));

  // Format SHAP Data
  const shapData = (diagnosis?.shap_top_drivers || [
    { feature: 'tool_wear', impact: 0.42, value: 210 },
    { feature: 'wear_torque', impact: 0.28, value: 12500 },
    { feature: 'power', impact: 0.15, value: 6800 }
  ]).map(d => ({
    feature: d.feature,
    impact: Math.round(d.impact * 100),
    value: d.value
  }));

  const readings = detail?.recent_readings || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Header Info */}
      <div className="glass-panel" style={{ padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Cpu size={24} color="#06b6d4" />
            <h2 style={{ fontSize: '1.25rem', fontWeight: '800', color: '#f8fafc' }}>
              {selectedMachine.name}
            </h2>
            <span className="badge badge-healthy">Type {selectedMachine.product_type}</span>
          </div>
          <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '4px' }}>
            {selectedMachine.description} | Criticality: {selectedMachine.asset_criticality}x
          </p>
        </div>

        <button onClick={fetchMachineData} className="btn btn-secondary">
          <RefreshCw size={16} /> Refresh Agent
        </button>
      </div>

      {/* Grid Row 1: AI Agent Diagnostic Card & Live Risk Meters */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px' }}>
        
        {/* LangGraph Agent Diagnosis Box */}
        <div className={`glass-panel ${diagnosis?.alert_priority === 'CRITICAL' ? 'glow-red' : ''}`} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Zap size={20} color="#8b5cf6" />
              <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f8fafc' }}>LangGraph AI Diagnostic Agent</h3>
            </div>
            <span className={`badge ${diagnosis?.alert_priority === 'CRITICAL' ? 'badge-critical' : 'badge-healthy'}`}>
              {diagnosis?.alert_priority || 'NORMAL'}
            </span>
          </div>

          <div style={{ background: 'rgba(0,0,0,0.3)', padding: '14px', borderRadius: '10px', borderLeft: '4px solid #8b5cf6' }}>
            <h4 style={{ fontSize: '0.9rem', color: '#f8fafc', fontWeight: '600' }}>
              {diagnosis?.recommendation || "Machine operational within target limits."}
            </h4>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '4px' }}>
              Primary Mode: <strong style={{ color: '#06b6d4' }}>{diagnosis?.primary_failure_mode} ({((diagnosis?.primary_failure_prob || 0)*100).toFixed(0)}%)</strong>
            </p>
          </div>

          {/* Action Steps */}
          <div>
            <h5 style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '8px' }}>Recommended Maintenance SOP Steps:</h5>
            <ul style={{ display: 'flex', flexDirection: 'column', gap: '6px', listStyle: 'none' }}>
              {(diagnosis?.action_steps || []).map((step, idx) => (
                <li key={idx} style={{ fontSize: '0.8rem', color: '#e2e8f0', display: 'flex', alignItems: 'flex-start', gap: '6px' }}>
                  <CheckCircle size={14} color="#10b981" style={{ marginTop: '2px', flexShrink: 0 }} />
                  <span>{step}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* SOP Citation Links */}
          {diagnosis?.supporting_sops?.length > 0 && (
            <div style={{ paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
              <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Retrieved RAG SOP Document:</span>
              <div style={{ display: 'flex', gap: '8px', marginTop: '6px' }}>
                {diagnosis.supporting_sops.map((sop, i) => (
                  <div key={i} style={{ background: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.3)', padding: '4px 8px', borderRadius: '6px', fontSize: '0.75rem', color: '#06b6d4', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <FileText size={12} /> {sop.title}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Multi-Label Failure Mode Probabilities */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f8fafc' }}>
            Multi-Label Failure Mode Probabilities
          </h3>
          <div style={{ width: '100%', height: '220px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={failureModeData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="mode" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} domain={[0, 100]} />
                <Tooltip contentStyle={{ background: '#111827', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }} />
                <Bar dataKey="prob" radius={[6, 6, 0, 0]}>
                  {failureModeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.prob > 50 ? '#ef4444' : (entry.prob > 25 ? '#f59e0b' : '#06b6d4')} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Grid Row 2: Live Telemetry Line Charts & SHAP Explainability */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
        
        {/* Real-time Telemetry Graph */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f8fafc', marginBottom: '16px' }}>
            Real-Time Sensor Telemetry Time-Series
          </h3>
          <div style={{ width: '100%', height: '240px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={readings}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="timestamp" stroke="#64748b" fontSize={10} tickFormatter={(t) => t ? t.substring(11, 19) : ''} />
                <YAxis stroke="#64748b" fontSize={10} />
                <Tooltip contentStyle={{ background: '#111827', borderColor: 'rgba(255,255,255,0.1)', color: '#fff' }} />
                <Line type="monotone" dataKey="tool_wear" stroke="#06b6d4" name="Tool Wear (min)" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="torque" stroke="#f59e0b" name="Torque (Nm)" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="process_temp" stroke="#ef4444" name="Process Temp (K)" strokeWidth={1.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* SHAP Feature Importance Bar Chart */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f8fafc', marginBottom: '16px' }}>
            SHAP Explainability: Feature Risk Drivers
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {shapData.map((d, i) => (
              <div key={i}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                  <span style={{ color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>{d.feature}</span>
                  <span style={{ color: '#06b6d4', fontWeight: '600' }}>Impact: +{d.impact}% (Value: {d.value})</span>
                </div>
                <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.08)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${Math.min(100, Math.abs(d.impact) * 2)}%`,
                    height: '100%',
                    background: 'linear-gradient(to right, #06b6d4, #8b5cf6)',
                    borderRadius: '4px'
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}
