from app.ml.model_loader import get_model_service
from app.agent.fallback_engine import get_agent_fallback_engine

class PredictSenseDiagnosticGraph:
    """
    State-machine orchestration agent executing multi-stage reasoning:
    Fetch State -> Run ML Models -> Evaluate Severity -> Retrieve RAG SOPs -> Synthesize Cost-Aware Diagnosis
    """
    def __init__(self):
        self.model_service = get_model_service()
        self.fallback_engine = get_agent_fallback_engine()

    def run_diagnostic_workflow(self, machine_dict, latest_reading):
        """
        Executes the agent workflow for a given machine and sensor reading.
        """
        # Step 1 & 2: ML Inference & Feature Engineering
        prediction_res = self.model_service.predict_reading(latest_reading)

        # Step 3, 4, 5, 6: State evaluation, SOP RAG retrieval, and Cost Triage
        diagnosis = self.fallback_engine.diagnose_machine(
            machine_dict=machine_dict,
            prediction_res=prediction_res,
            recent_readings=[latest_reading]
        )

        return diagnosis, prediction_res

_graph_agent_instance = None

def get_graph_agent():
    global _graph_agent_instance
    if _graph_agent_instance is None:
        _graph_agent_instance = PredictSenseDiagnosticGraph()
    return _graph_agent_instance
