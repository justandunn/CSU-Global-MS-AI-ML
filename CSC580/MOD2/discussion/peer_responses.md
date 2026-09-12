# Module 2 Peer Responses

## Response to Thomas Bogart

Thomas, your distinction between static thresholds and multivariate anomaly detection is especially important. A threshold such as 80% disk utilization treats the measurement as abnormal regardless of workload, deployment timing, or dependencies. An LSTM encoder-decoder can instead learn a normal operating envelope across related signals. I also agree that software creates a harder retraining problem than the ISS example because the system being modeled changes continually.

One extension I would add is deployment context as a first-class feature. Each observation could include the service version, deployment timestamp, infrastructure class, and dependency-graph version. That would help the pipeline distinguish a legitimate operating-regime change from a developing incident. For a newly deployed service, I would initially combine the learned score with conservative rules and gradually increase the model's influence after enough representative data accumulates.

The alert threshold should also reflect the cost of errors. A false positive contributes to alert fatigue, while a false negative may allow an outage to expand. Instead of one global reconstruction-error cutoff, the team could calibrate thresholds by service criticality and use a persistence rule—for example, requiring an anomaly across several windows unless the score is extreme. Precision-recall results and alerts per engineer-hour may therefore be more operationally meaningful than accuracy alone.

Your point about TensorFlow Serving also fits this lifecycle because it supports concurrent model versions and gradual rollout. Would you attach thresholds to each model version, or calibrate them separately by service so that a shared model does not over-alert on naturally noisy components?

## Response to Ryan Ganshert

Ryan, I agree that both TensorFlow and PyTorch could build an attrition classifier, so comparing them only by predictive accuracy may not reveal a meaningful difference. The stronger TensorFlow justification would be the surrounding lifecycle: Keras preprocessing layers can package transformations with the model, TFX can validate incoming data and track pipeline artifacts, and TensorFlow Serving can expose an approved model version to an internal application. PyTorch has production tools as well, but TensorFlow provides a particularly cohesive path when repeatable validation and deployment are central requirements.

I would also place governance ahead of model choice for this use case. Historical departures are not neutral labels; they may reflect pay inequity, poor management, limited advancement opportunities, or other organizational conditions. A model could reproduce those patterns and direct attention unevenly across demographic groups. I would exclude protected characteristics from intervention decisions, but I would retain them in a tightly controlled evaluation dataset so the team can test performance and error rates across groups. Intersectional checks matter too because acceptable aggregate results can hide poor performance for smaller groups.

The output should support a beneficial, human-reviewed action rather than label someone as disloyal. For example, a manager could receive an organization-level signal that a team has elevated retention risk, followed by consistent stay interviews or compensation reviews offered to everyone under the same policy. I would also compare the model with a simple logistic-regression baseline and check calibration, recall, false-positive rates, and stability over time.

What action would your organization take after a high-risk prediction, and how would it ensure that the intervention helps the employee instead of affecting promotion or assignment decisions?
