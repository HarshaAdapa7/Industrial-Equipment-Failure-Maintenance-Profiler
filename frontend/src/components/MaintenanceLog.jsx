import React, { useState } from 'react';
import { Wrench, DollarSign, CheckCircle, TrendingUp, Plus } from 'lucide-react';
import { api } from '../services/api';

export default function MaintenanceLog({ machines, summary, onRefreshSummary }) {
  const [selectedMachineId, setSelectedMachineId] = useState(machines[0]?.id || '');
  const [actionText, setActionText] = useState('');
  const [techName, setTechName] = useState('Senior Technician');
  const [cost, setCost] = useState(250);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedMachineId || !actionText) return;

    setSubmitting(true);
    try {
      await api.logMaintenanceAction({
        machine_id: selectedMachineId,
        action_taken: actionText,
        performed_by: techName,
        cost: parseFloat(cost)
      });
      setActionText('');
      onRefreshSummary();
    } catch (err) {
      console.error("Maintenance action log error:", err);
    } finally {
      setSubmitting(false);
    }
  };

  const actions = summary?.actions_history || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Financial ROI Summary Header Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        
        <div className="glass-panel" style={{ padding: '20px' }}>
          <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Cumulative PM Actions</span>
          <div className="metric-value" style={{ fontSize: '1.8rem', color: '#3b82f6', marginTop: '4px' }}>
            {summary?.total_actions || actions.length || 0}
          </div>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Logged preventive interventions</span>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Total PM Cost Spent</span>
          <div className="metric-value" style={{ fontSize: '1.8rem', color: '#f59e0b', marginTop: '4px' }}>
            ${(summary?.total_pm_cost || 0).toLocaleString()}
          </div>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Carbide inserts & technician labor</span>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Prevented Breakdown Losses</span>
          <div className="metric-value" style={{ fontSize: '1.8rem', color: '#10b981', marginTop: '4px' }}>
            ${(summary?.total_prevented_downtime_cost || 0).toLocaleString()}
          </div>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Avoided spindle bearing damages</span>
        </div>

        <div className="glass-panel glow-cyan" style={{ padding: '20px' }}>
          <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Net Financial ROI</span>
          <div className="metric-value" style={{ fontSize: '1.8rem', color: '#06b6d4', marginTop: '4px' }}>
            ${(summary?.net_roi_savings || 0).toLocaleString()}
          </div>
          <span style={{ fontSize: '0.75rem', color: '#06b6d4' }}>Net financial savings</span>
        </div>

      </div>

      {/* Grid: Log Action Form & History Table */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px' }}>
        
        {/* Log Action Form */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Wrench size={18} color="#06b6d4" /> Log Performed Maintenance Action
          </h3>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Target Asset:</label>
              <select
                value={selectedMachineId}
                onChange={e => setSelectedMachineId(e.target.value)}
                style={{ width: '100%', padding: '8px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', borderRadius: '8px', fontSize: '0.85rem' }}
              >
                {machines.map(m => (
                  <option key={m.id} value={m.id}>{m.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Action Executed (SOP Procedure):</label>
              <textarea
                value={actionText}
                onChange={e => setActionText(e.target.value)}
                placeholder="e.g. Replaced cutting insert bit, zeroed Z-axis offset, flushed coolant lines."
                rows={3}
                style={{ width: '100%', padding: '10px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', borderRadius: '8px', fontSize: '0.85rem' }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Technician:</label>
                <input
                  type="text"
                  value={techName}
                  onChange={e => setTechName(e.target.value)}
                  style={{ width: '100%', padding: '8px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', borderRadius: '8px', fontSize: '0.85rem' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Cost ($):</label>
                <input
                  type="number"
                  value={cost}
                  onChange={e => setCost(e.target.value)}
                  style={{ width: '100%', padding: '8px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', borderRadius: '8px', fontSize: '0.85rem' }}
                />
              </div>
            </div>

            <button type="submit" disabled={submitting} className="btn btn-primary" style={{ marginTop: '8px' }}>
              <Plus size={16} /> Log Action & Reset Asset Health
            </button>
          </form>
        </div>

        {/* Action History List */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#f8fafc', marginBottom: '16px' }}>
            Action History Log
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '350px', overflowY: 'auto' }}>
            {actions.length === 0 ? (
              <div style={{ color: '#64748b', fontSize: '0.85rem', padding: '20px', textAlign: 'center' }}>
                No maintenance actions logged yet.
              </div>
            ) : (
              actions.map(act => (
                <div key={act.id} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '10px', padding: '12px 16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h4 style={{ fontSize: '0.9rem', color: '#f8fafc', fontWeight: '600' }}>{act.machine_name}</h4>
                    <span style={{ fontSize: '0.8rem', color: '#10b981', fontFamily: 'var(--font-mono)' }}>${act.cost}</span>
                  </div>
                  <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '4px' }}>{act.action_taken}</p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748b', marginTop: '6px' }}>
                    <span>By: {act.performed_by}</span>
                    <span>{new Date(act.timestamp).toLocaleDateString()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
