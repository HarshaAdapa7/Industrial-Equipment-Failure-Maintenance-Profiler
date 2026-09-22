import React, { useState } from 'react';
import { BookOpen, FileText, Search, ShieldCheck } from 'lucide-react';

const SOP_DOCS = [
  {
    id: 'TWF',
    title: 'Tool Wear Failure (TWF) SOP',
    category: 'Cutting Tool Wear',
    threshold: 'Tool Wear > 200 min | Torque +15%',
    procedure: '1. Pause CNC cycle at tool retract position.\n2. Inspect cutting edge for micro-chipping or crater wear.\n3. Unclamp tool holder & insert fresh carbide insert.\n4. Zero tool offset Z-axis precision ±0.005 mm.',
    cost: 'Cost: $150–$350 | Downtime: 15–20 mins'
  },
  {
    id: 'HDF',
    title: 'Heat Dissipation Failure (HDF) SOP',
    category: 'Thermal Chiller System',
    threshold: 'ProcessTemp - AirTemp < 8.6 K | RPM < 1380',
    procedure: '1. Lower spindle feed rate by 30% via controller override.\n2. Inspect chiller reservoir fluid pressure & radiator dust buildup.\n3. Clean air filters on spindle cooling unit.\n4. Run 5-minute thermal stabilization cycle at 2000 RPM.',
    cost: 'Cost: $80–$200 | Downtime: 30–45 mins'
  },
  {
    id: 'PWF',
    title: 'Power Failure (PWF) SOP',
    category: 'Electrical & Transmission Drive',
    threshold: 'Power < 3500 W or > 9000 W | Amp Draw > 45A',
    procedure: '1. Initiate soft ramp-down sequence to avoid kinetic backlash.\n2. Inspect drive belt tension & measure motor winding resistance.\n3. Verify main power supply 400V 3-phase voltage stability.\n4. Recalibrate CAM feed per tooth parameter to center power at 6000 W.',
    cost: 'Cost: $250–$800 | Downtime: 45–60 mins'
  },
  {
    id: 'OSF',
    title: 'Overstrain Failure (OSF) SOP',
    category: 'Mechanical Strain',
    threshold: 'ToolWear * Torque > Strain Limit (11k-13k)',
    procedure: '1. Halt cutting pass immediately.\n2. Measure spindle axial runout using dial indicator (< 0.003 mm allowable).\n3. Inspect tool holder taper for galling or fretting corrosion.\n4. Reduce depth of cut (Ap) by 25%.',
    cost: 'Cost: $200–$500 | Downtime: 25–40 mins'
  },
  {
    id: 'RNF',
    title: 'Random Failure (RNF) SOP',
    category: 'Stochastic & Electrical Surges',
    threshold: '0.1% Baseline Stochastic Occurrence',
    procedure: '1. Execute full PLC controller diagnostic scan.\n2. Check sensor cabling shields and analog-to-digital converter readings.\n3. Reset alarm state and execute dry-run test cycle.',
    cost: 'Cost: $0–$50 | Downtime: 10–15 mins'
  }
];

export default function KnowledgeBase() {
  const [search, setSearch] = useState('');
  const [selectedSop, setSelectedSop] = useState(SOP_DOCS[0]);

  const filtered = SOP_DOCS.filter(s => 
    s.title.toLowerCase().includes(search.toLowerCase()) || 
    s.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
      
      {/* Sidebar List */}
      <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BookOpen size={20} color="#06b6d4" />
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f8fafc' }}>
            RAG Knowledge Base & SOP Manuals
          </h3>
        </div>

        {/* Search bar */}
        <div style={{ position: 'relative' }}>
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search SOP procedures..."
            style={{
              width: '100%',
              padding: '8px 12px 8px 36px',
              background: 'rgba(0,0,0,0.4)',
              border: '1px solid rgba(255,255,255,0.1)',
              color: '#fff',
              borderRadius: '8px',
              fontSize: '0.85rem'
            }}
          />
          <Search size={16} color="#94a3b8" style={{ position: 'absolute', left: '10px', top: '10px' }} />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {filtered.map(sop => (
            <div
              key={sop.id}
              onClick={() => setSelectedSop(sop)}
              style={{
                padding: '12px',
                borderRadius: '8px',
                background: selectedSop.id === sop.id ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                border: selectedSop.id === sop.id ? '1px solid rgba(6, 182, 212, 0.4)' : '1px solid rgba(255, 255, 255, 0.06)',
                cursor: 'pointer'
              }}
            >
              <h4 style={{ fontSize: '0.85rem', fontWeight: '600', color: '#f8fafc' }}>{sop.title}</h4>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{sop.category}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Main Document Viewer */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', pb: '16px', paddingBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <FileText size={20} color="#06b6d4" />
            <h2 style={{ fontSize: '1.2rem', fontWeight: '800', color: '#f8fafc' }}>
              {selectedSop.title}
            </h2>
          </div>
          <span className="badge badge-healthy">{selectedSop.category}</span>
        </div>

        <div style={{ background: 'rgba(0,0,0,0.3)', padding: '14px', borderRadius: '10px', borderLeft: '4px solid #f59e0b' }}>
          <span style={{ fontSize: '0.8rem', color: '#f59e0b', fontWeight: '600' }}>Trigger Telemetry Threshold:</span>
          <p style={{ fontSize: '0.85rem', color: '#f8fafc', marginTop: '2px', fontFamily: 'var(--font-mono)' }}>
            {selectedSop.threshold}
          </p>
        </div>

        <div>
          <h4 style={{ fontSize: '0.9rem', color: '#94a3b8', marginBottom: '8px' }}>Action Protocol Steps:</h4>
          <pre style={{
            fontFamily: 'var(--font-sans)',
            fontSize: '0.85rem',
            color: '#e2e8f0',
            whiteSpace: 'pre-wrap',
            lineHeight: '1.6',
            background: 'rgba(255,255,255,0.02)',
            padding: '16px',
            borderRadius: '10px',
            border: '1px solid rgba(255,255,255,0.05)'
          }}>
            {selectedSop.procedure}
          </pre>
        </div>

        <div style={{ background: 'rgba(16,185,129,0.1)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(16,185,129,0.3)', fontSize: '0.85rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldCheck size={18} /> {selectedSop.cost}
        </div>
      </div>

    </div>
  );
}
