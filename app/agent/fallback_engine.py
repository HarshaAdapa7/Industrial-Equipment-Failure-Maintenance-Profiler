from app.agent.rag_engine import get_rag_store
from app.ml.shap_explainer import get_shap_service

class AgentFallbackDiagnosticEngine:
    _instance = None

    def diagnose_machine(self, machine_dict, prediction_res, recent_readings=None):
        """
        Synthesizes agentic reasoning diagnosis combining ML probabilities, SHAP drivers,
        retrieved RAG SOPs, and asset cost-benefit triaging.
        """
        rag_store = get_rag_store()
        shap_service = get_shap_service()

        risk_score = prediction_res['risk_score']
        health_score = prediction_res['health_score']
        label_probs = prediction_res['label_probs']
        anomaly_score = prediction_res['anomaly_score']

        # Determine primary failure mode
        sorted_modes = sorted(label_probs.items(), key=lambda x: x[1], reverse=True)
        primary_mode, primary_prob = sorted_modes[0]

        # Calculate Priority Score: Risk * Criticality * (FailureCost / PMCost)
        asset_crit = machine_dict.get('asset_criticality', 1.5)
        fail_cost = machine_dict.get('failure_cost', 180000.0)
        pm_cost = machine_dict.get('pm_cost', 15000.0)

        cost_ratio = (fail_cost / max(1.0, pm_cost))
        raw_priority = (risk_score / 100.0) * asset_crit * (cost_ratio / 10.0) * 100.0
        priority_score = round(min(100.0, max(5.0, raw_priority)), 1)

        # Severity categorization
        if priority_score >= 75.0 or risk_score >= 75.0:
            alert_priority = "CRITICAL"
        elif priority_score >= 50.0 or risk_score >= 50.0:
            alert_priority = "HIGH"
        elif priority_score >= 30.0 or risk_score >= 30.0:
            alert_priority = "MODERATE"
        else:
            alert_priority = "NORMAL"

        # Get SHAP explanation
        shap_res = shap_service.explain_prediction(
            prediction_res['features'], target_mode=primary_mode
        )
        top_drivers = shap_res.get('feature_attributions', [])[:4]

        # Retrieve matching SOP documents via RAG engine
        query_text = f"Fix {primary_mode} failure mode procedure tool wear torque temperature"
        retrieved_sops = rag_store.query_sops(query_text, top_k=2)

        # Construct Actionable Recommendation & Steps
        if alert_priority in ["CRITICAL", "HIGH"]:
            rec_title = f"Urgent Intervention Required: High Risk of {primary_mode} Failure ({primary_prob * 100:.0f}%)"
            action_steps = [
                f"1. Safely halt cycle on machine '{machine_dict.get('name', 'Machine')}' immediately.",
                f"2. Inspect primary failure driver: {top_drivers[0]['feature'] if top_drivers else 'tool_wear'} (current value: {top_drivers[0]['value'] if top_drivers else 'N/A'}).",
                f"3. Execute Standard Operating Procedure '{primary_mode}_SOP' retrieved from Knowledge Base.",
                f"4. Recalibrate tool offset and verify flood coolant pressure before resuming production."
            ]
        elif alert_priority == "MODERATE":
            rec_title = f"Warning: Degradation Trend Detected for {primary_mode} ({primary_prob * 100:.0f}%)"
            action_steps = [
                "1. Schedule preventive maintenance during the next shift change.",
                f"2. Monitor telemetry for parameter: {top_drivers[0]['feature'] if top_drivers else 'torque'}.",
                "3. Prepare replacement tooling inserts and inspect spindle lubrication."
            ]
        else:
            rec_title = f"Machine Healthy ({health_score:.1f}% Health Score)"
            action_steps = [
                "1. Machine operating within normal baseline limits.",
                "2. Continue standard operational monitoring."
            ]

        # Financial impact analysis
        expected_failure_cost = round((risk_score / 100.0) * fail_cost, 2)
        net_savings = round(max(0.0, expected_failure_cost - pm_cost), 2)

        cost_analysis = {
            'estimated_failure_cost': fail_cost,
            'preventive_maintenance_cost': pm_cost,
            'expected_loss_without_action': expected_failure_cost,
            'net_savings_from_pm': net_savings,
            'roi_multiplier': round((net_savings / max(1.0, pm_cost)), 2)
        }

        return {
            'machine_id': machine_dict.get('id', 'm1'),
            'machine_name': machine_dict.get('name', 'CNC Milling Machine #1'),
            'alert_priority': alert_priority,
            'risk_score': risk_score,
            'health_score': health_score,
            'primary_failure_mode': primary_mode,
            'primary_failure_prob': round(primary_prob, 4),
            'recommendation': rec_title,
            'action_steps': action_steps,
            'supporting_sops': retrieved_sops,
            'expected_cost_analysis': cost_analysis,
            'shap_top_drivers': top_drivers
        }

def get_agent_fallback_engine():
    if AgentFallbackDiagnosticEngine._instance is None:
        AgentFallbackDiagnosticEngine._instance = AgentFallbackDiagnosticEngine()
    return AgentFallbackDiagnosticEngine._instance
