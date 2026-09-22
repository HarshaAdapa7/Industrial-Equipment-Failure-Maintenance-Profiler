import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const api = {
  // Machine Endpoints
  getMachines: async () => {
    const res = await axios.get(`${API_BASE_URL}/machines`);
    return res.data;
  },

  getMachineDetail: async (id) => {
    const res = await axios.get(`${API_BASE_URL}/machines/${id}`);
    return res.data;
  },

  // Telemetry Ingestion
  postReading: async (readingData) => {
    const res = await axios.post(`${API_BASE_URL}/readings`, readingData);
    return res.data;
  },

  // ML Predictions
  predictFailure: async (telemetryData) => {
    const res = await axios.post(`${API_BASE_URL}/predict/failure`, telemetryData);
    return res.data;
  },

  explainPrediction: async (telemetryData) => {
    const res = await axios.post(`${API_BASE_URL}/predict/explain`, telemetryData);
    return res.data;
  },

  // LangGraph Diagnostic Agent
  diagnoseMachine: async (machineId) => {
    const res = await axios.post(`${API_BASE_URL}/agent/diagnose`, { machine_id: machineId });
    return res.data;
  },

  // Alerts Management
  getAlerts: async () => {
    const res = await axios.get(`${API_BASE_URL}/alerts`);
    return res.data;
  },

  acknowledgeAlert: async (alertId) => {
    const res = await axios.post(`${API_BASE_URL}/alerts/${alertId}/ack`, {
      acknowledged_by: "Maintenance Tech",
      user_comment: "Inspecting machine asset."
    });
    return res.data;
  },

  // Maintenance Logging & Financial ROI
  logMaintenanceAction: async (actionData) => {
    const res = await axios.post(`${API_BASE_URL}/maintenance/actions`, actionData);
    return res.data;
  },

  getMaintenanceSummary: async () => {
    const res = await axios.get(`${API_BASE_URL}/maintenance/summary`);
    return res.data;
  },

  // Telemetry Simulator & Fault Injection
  startSimulator: async (speed = 1.0) => {
    const res = await axios.post(`${API_BASE_URL}/simulator/start?speed_delay=${speed}`);
    return res.data;
  },

  pauseSimulator: async () => {
    const res = await axios.post(`${API_BASE_URL}/simulator/pause`);
    return res.data;
  },

  injectFault: async (machineId, faultType) => {
    const res = await axios.post(`${API_BASE_URL}/simulator/inject-fault`, {
      machine_id: machineId,
      fault_type: faultType
    });
    return res.data;
  }
};
