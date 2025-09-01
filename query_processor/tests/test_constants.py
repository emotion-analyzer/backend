from datetime import datetime

from util.codes import POST_ANALYSIS_RESULT
from util.schemas import AnalysisRequestParameters, PostAnalysisResult

analysis_result_body = PostAnalysisResult(query_processor_id="id1", code=POST_ANALYSIS_RESULT,
                          source="test_source", link="www.test.com", text="test_text",
                          timestamp=datetime.now(), model="test_model",
                          affective_states={"ira": 0.60}, dominant_emotions=["ira"])

analysis_request_parameters = AnalysisRequestParameters(
    date_start=datetime.now(),
    date_end=datetime.now(),
    keyword="test",
    platform=["test_platform"],
    limit=100
)
