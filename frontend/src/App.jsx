import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import FleetOverview from './components/FleetOverview';
import MachineDetail from './components/MachineDetail';
import LiveSimulator from './components/LiveSimulator';
import AlertsCenter from './components/AlertsCenter';
import MaintenanceLog from './components/MaintenanceLog';
import KnowledgeBase from './components/KnowledgeBase';
import { api } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedMachineId, setSelectedMachineId] = useState(null);
  const [machines, setMachines] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);

  // Fetch initial fleet state
  const refreshData = async () => {
    try {
      const machData = await api.getMachines();
      setMachines(machData);
      if (machData.length > 0 && !selectedMachineId) {
        setSelectedMachineId(machData[0].id);
      }

      const alertData = await api.getAlerts();
      setAlerts(alertData);

      const sumData = await api.getMaintenanceSummary();
      setSummary(sumData);
    } catch (e) {
      console.error("Error refreshing dashboard data:", e);
    }
  };

  useEffect(() => {
    refreshData();
    const interval = setInterval(refreshData, 3000);
    return () => clearInterval(interval);
  }, []);

  // Toggle Live Simulator Stream
  const handleToggleSimulator = async () => {
    try {
      if (isSimulating) {
        await api.pauseSimulator();
        setIsSimulating(false);
      } else {
        await api.startSimulator(1.0);
        setIsSimulating(true);
      }
    } catch (e) {
      console.error("Toggle simulator error:", e);
    }
  };

  const handleSelectMachine = (mId) => {
    setSelectedMachineId(mId);
    setActiveTab('machine');
  };

  const activeAlertCount = alerts.filter(a => a.status === 'ACTIVE').length;

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-dark)', color: 'var(--text-main)' }}>
      {/* Top Navigation Bar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isSimulating={isSimulating}
        onToggleSimulator={handleToggleSimulator}
        activeAlertCount={activeAlertCount}
      />

      <main style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px 20px 48px 20px' }}>
        
        {/* Continuous Telemetry Simulator & Fault Injector Bar */}
        <div style={{ marginBottom: '24px' }}>
          <LiveSimulator
            machines={machines}
            isSimulating={isSimulating}
            onToggleSimulator={handleToggleSimulator}
            selectedMachineId={selectedMachineId}
          />
        </div>

        {/* Tab View Routing */}
        {activeTab === 'overview' && (
          <FleetOverview
            machines={machines}
            alerts={alerts}
            maintenanceSummary={summary}
            onSelectMachine={handleSelectMachine}
          />
        )}

        {activeTab === 'machine' && (
          <MachineDetail
            machineId={selectedMachineId || (machines[0]?.id)}
            machines={machines}
          />
        )}

        {activeTab === 'alerts' && (
          <AlertsCenter
            alerts={alerts}
            onRefreshAlerts={refreshData}
          />
        )}

        {activeTab === 'maintenance' && (
          <MaintenanceLog
            machines={machines}
            summary={summary}
            onRefreshSummary={refreshData}
          />
        )}

        {activeTab === 'knowledge' && (
          <KnowledgeBase />
        )}

      </main>
    </div>
  );
}
