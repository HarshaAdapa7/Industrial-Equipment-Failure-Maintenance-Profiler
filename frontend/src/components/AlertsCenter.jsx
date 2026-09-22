import React, { useState } from 'react';
import { ShieldAlert, CheckCircle, Clock, AlertTriangle, Filter } from 'lucide-react';
import { api } from '../services/api';

export default function AlertsCenter({ alerts, onRefreshAlerts }) {
  const [filter, setFilter] = useState('ALL');

  const handleAcknowledge = async (alertId) => {
    try {
      await api.acknowledgeAlert(alertId);
      onRefreshAlerts();
    } catch (e) {
      console.error("Error acknowledging alert:", e);
    }
  };

  const filteredAlerts = alerts.filter(a => {
    if (filter === 'ACTIVE') return a.status === 'ACTIVE';
    if (filter === 'ACKNOWLEDGED') return a.status === 'ACKNOWLEDGED';
    return true;
  });

  return (
    <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#f8fafc' }}>
            Alert Triage & Priority Feed
          </h2>
          <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '2px' }}>
            Cost-weighted prioritized maintenance alert queue
          </p>
        </div>

        {/* Filter Buttons */}
        <div style={{ display: 'flex', gap: '8px' }}>
          {['ALL', 'ACTIVE', 'ACKNOWLEDGED'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`btn ${filter === f ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '6px 12px', fontSize: '0.8rem' }}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Alert Feed List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {filteredAlerts.length === 0 ? (
          <div style={{ padding: '32px', textAlign: 'center', color: '#64748b', fontSize: '0.9rem' }}>
            No active alerts matching filter. Fleet is running safely.
          </div>
        ) : (
          filteredAlerts.map(alert => {
            const isCritical = alert.severity === 'CRITICAL';
            const isAck = alert.status === 'ACKNOWLEDGED';

            return (
              <div
                key={alert.id}
                style={{
                  background: isCritical ? 'rgba(239, 68, 68, 0.08)' : 'rgba(255, 255, 255, 0.03)',
                  border: isCritical ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '12px',
                  padding: '16px 20px',
                  display: 'flex',
                  justify: 'space-between',
                  alignItems: 'center',
                  gap: '16px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
                  <div style={{
                    background: isCritical ? 'rgba(239,68,68,0.2)' : 'rgba(245,158,11,0.2)',
                    padding: '10px',
                    borderRadius: '10px'
                  }}>
                    <AlertTriangle size={20} color={isCritical ? '#ef4444' : '#f59e0b'} />
                  </div>

                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: '700', color: '#f8fafc' }}>
                        {alert.machine_name}
                      </h4>
                      <span className={`badge ${isCritical ? 'badge-critical' : 'badge-warning'}`}>
                        {alert.severity}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: '#06b6d4', fontWeight: '600', fontFamily: 'var(--font-mono)' }}>
                        Priority: {alert.priority_score?.toFixed(1)}
                      </span>
                    </div>

                    <p style={{ fontSize: '0.85rem', color: '#e2e8f0', marginTop: '4px' }}>
                      {alert.message}
                    </p>

                    <div style={{ display: 'flex', gap: '12px', fontSize: '0.75rem', color: '#64748b', marginTop: '6px' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Clock size={12} /> Triggered: {new Date(alert.created_at).toLocaleTimeString()}
                      </span>
                      <span>Type: {alert.alert_type}</span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div>
                  {isAck ? (
                    <span style={{ fontSize: '0.8rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <CheckCircle size={14} /> Acknowledged
                    </span>
                  ) : (
                    <button
                      onClick={() => handleAcknowledge(alert.id)}
                      className="btn btn-secondary"
                      style={{ padding: '6px 14px', fontSize: '0.8rem' }}
                    >
                      Acknowledge
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
