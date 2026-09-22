import React from 'react';
import { Activity, ShieldAlert, Cpu, Wrench, BookOpen, Radio } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, isSimulating, onToggleSimulator, activeAlertCount }) {
  return (
    <header style={{
      background: 'rgba(15, 23, 42, 0.9)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      padding: '12px 24px'
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        {/* Brand Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #06b6d4, #3b82f6)',
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px rgba(6, 182, 212, 0.4)'
          }}>
            <Cpu size={24} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: '800', letterSpacing: '-0.02em', background: 'linear-gradient(to right, #ffffff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              PredictSense
            </h1>
            <p style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: '500' }}>
              Predictive Maintenance Profiler & AI Agent
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', gap: '8px' }}>
          {[
            { id: 'overview', label: 'Fleet Overview', icon: Activity },
            { id: 'machine', label: 'Machine Inspector', icon: Cpu },
            { id: 'alerts', label: 'Alert Triage', icon: ShieldAlert, badge: activeAlertCount },
            { id: 'maintenance', label: 'Maintenance ROI', icon: Wrench },
            { id: 'knowledge', label: 'Knowledge SOPs', icon: BookOpen }
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`btn ${isActive ? 'btn-primary' : 'btn-secondary'}`}
                style={{
                  padding: '8px 14px',
                  fontSize: '0.85rem',
                  borderRadius: '8px',
                  position: 'relative'
                }}
              >
                <Icon size={16} />
                {tab.label}
                {tab.badge > 0 && (
                  <span style={{
                    background: '#ef4444',
                    color: '#ffffff',
                    fontSize: '0.7rem',
                    padding: '2px 6px',
                    borderRadius: '999px',
                    marginLeft: '4px'
                  }}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Streaming Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: isSimulating ? '#10b981' : '#64748b' }}>
            <Radio size={16} className={isSimulating ? "pulse-anim" : ""} />
            <span>{isSimulating ? 'Live Streaming' : 'Stream Paused'}</span>
          </div>

          <button
            onClick={onToggleSimulator}
            className={`btn ${isSimulating ? 'btn-danger' : 'btn-primary'}`}
            style={{ padding: '6px 14px', fontSize: '0.8rem' }}
          >
            {isSimulating ? 'Pause Stream' : 'Start Live Telemetry'}
          </button>
        </div>
      </div>
    </header>
  );
}
