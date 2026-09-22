import pytest
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_backend_root():
    res = requests.get("http://localhost:8000/")
    assert res.status_code == 200
    assert res.json()["status"] == "ONLINE"

def test_list_machines():
    res = requests.get(f"{BASE_URL}/machines")
    assert res.status_code == 200
    machines = res.json()
    assert len(machines) >= 3
    assert "name" in machines[0]

def test_predict_failure():
    payload = {
        "air_temp": 300.5,
        "process_temp": 310.2,
        "rpm": 1500.0,
        "torque": 55.0,
        "tool_wear": 180.0,
        "product_type": "M"
    }
    res = requests.post(f"{BASE_URL}/predict/failure", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "risk_score" in data
    assert "label_probs" in data

def test_agent_diagnose():
    machines = requests.get(f"{BASE_URL}/machines").json()
    m_id = machines[0]["id"]

    res = requests.post(f"{BASE_URL}/agent/diagnose", json={"machine_id": m_id})
    assert res.status_code == 200
    data = res.json()
    assert "recommendation" in data
    assert "action_steps" in data
    assert "supporting_sops" in data
