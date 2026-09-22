import React from 'react';
import { Activity, AlertTriangle, ShieldCheck, DollarSign, ArrowRight, Server } from 'lucide-react';

export default function FleetOverview({ machines, alerts, maintenanceSummary, onSelectMachine }) {
  const activeAlerts = alerts.filter(a => a.status === 'ACTIVE');
  const criticalCount = activeAlerts.filter(a => a.severity === 'CRITICAL').length;
  const warningCount = activeAlerts.filter(a => a.severity === 'HIGH' || a.severity === 'MODERATE').length;
  
  const avgHealth = machines.length > 0
    ? (machines.reduce((acc, m) => acc + (m.current_health || 100), 0) / machines.length).toFixed(1)
    : 95.0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Fleet KPI Metric Tiles */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        
        {/* KPI 1: Fleet Health Index */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: '500' }}>Fleet Health Index</span>
            <ShieldCheck size={20} color="#10b981" />
          </div>
          <div className="metric-value" style={{ fontSize: '2rem', color: avgHealth > 80 ? '#10b981' : (avgHealth > 50 ? '#f59e0b' : '#ef4444') }}>
            {avgHealth}%
          </div>
          <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            Overall health score across registered assets
          </p>
        </div>

        {/* KPI 2: Active Alerts */}
        <div className={`glass-panel ${criticalCount > 0 ? 'glow-red' : ''}`} style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: '500' }}>Active Failure Alarms</span>
            <AlertTriangle size={20} color={criticalCount > 0 ? '#ef4444' : '#f59e0b'} />
          </div>
          <div className="metric-value" style={{ fontSize: '2rem', color: criticalCount > 0 ? '#ef4444' : '#f59e0b' }}>
            {activeAlerts.length}
          </div>
          <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            {criticalCount} Critical | {warningCount} Warning
          </p>
        </div>

        {/* KPI 3: Net ROI Savings */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: '500' }}>Downtime Cost Savings</span>
            <DollarSign size={20} color="#06b6d4" />
          </div>
          <div className="metric-value" style={{ fontSize: '2rem', color: '#06b6d4' }}>
            ${(maintenanceSummary?.net_roi_savings || 165000).toLocaleString()}
          </div>
          <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            Prevented breakdown loss vs PM cost
          </p>
        </div>

        {/* KPI 4: Operating Assets */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: '500' }}>Active Assets</span>
            <Server size={20} color="#3b82f6" />
          </div>
          <div className="metric-value" style={{ fontSize: '2rem', color: '#3b82f6' }}>
            {machines.length}
          </div>
          <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            Multi-tenant milling machines monitored
          </p>
        </div>

      </div>

      {/* Machine Asset Cards Grid */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#f8fafc' }}>
            Equipment Assets Registry
          </h2>
          <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
            Real-time telemetry & failure risk status
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
          {machines.map(m => {
            const health = m.current_health || 100;
            const risk = m.current_risk || 0;
            const statusClass = m.status === 'CRITICAL' ? 'badge-critical' : (m.status === 'WARNING' ? 'badge-warning' : 'badge-healthy');

            return (
              <div
                key={m.id}
                className={`glass-panel ${m.status === 'CRITICAL' ? 'glow-red' : ''}`}
                style={{ padding: '20px', cursor: 'pointer' }}
                onClick={() => onSelectMachine(m.id)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f8fafc' }}>{m.name}</h3>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Product Type: {m.product_type}</span>
                  </div>
                  <span className={`badge ${statusClass}`}>{m.status}</span>
                </div>

                <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '16px' }}>
                  {m.description || 'CNC Milling Machine Center'}
                </p>

                {/* Health Meter Bar */}
                <div style={{ marginBottom: '14px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '6px' }}>
                    <span style={{ color: '#94a3b8' }}>Health Score</span>
                    <span className="metric-value" style={{ color: health > 70 ? '#10b981' : (health > 40 ? '#f59e0b' : '#ef4444') }}>
                      {health.toFixed(1)}%
                    </span>
                  </div>
                  <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{
                      width: `${health}%`,
                      height: '100%',
                      background: health > 70 ? '#10b981' : (health > 40 ? '#f59e0b' : '#ef4444'),
                      transition: 'width 0.5s ease'
                    }} />
                  </div>
                </div>

                {/* Risk Score Indicator */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '12px', borderTop: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Failure Risk</span>
                    <div className="metric-value" style={{ fontSize: '1rem', color: risk > 60 ? '#ef4444' : '#06b6d4' }}>
                      {risk.toFixed(1)}%
                    </div>
                  </div>

                  <button className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.75rem' }}>
                    Inspect Details <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
