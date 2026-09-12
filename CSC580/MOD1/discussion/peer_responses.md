# Module 1 Peer Responses

## Response 1 — Colter Welden

Colter,

Your explanation of attention capturing long-range relationships between amino acids highlights an important reason Transformers are better suited to this problem than a conventional RNN. One additional strength of AlphaFold is that it does not provide only a three-dimensional prediction; it also provides confidence information. Jumper et al. (2021) reported that AlphaFold's predicted local distance difference test, or pLDDT, reliably estimated the local accuracy of a prediction. That confidence score could help researchers decide which parts of a predicted structure are strong enough to guide the next experiment and which regions still require greater caution.

This creates an interesting decision-support workflow rather than a replacement for laboratory science. A pharmaceutical team could use high-confidence regions to prioritize candidate binding sites, while routing low-confidence or functionally critical regions to crystallography, cryo-electron microscopy, or another validation method. That approach could reduce the search space and expense without treating a prediction as established biological evidence. It also shows that the business value comes from combining model output, uncertainty, and expert review—not simply generating more structures.

Your point about protein engineering also suggests a broader industrial application. If researchers can evaluate candidate structures more efficiently, they could explore enzymes for manufacturing, agriculture, or environmental remediation in addition to drug discovery. What validation threshold do you think an organization should require before using a predicted structure to make a costly decision: a minimum pLDDT score, successful laboratory replication, or a combination of both?

**Reference**

Jumper, J., Evans, R., Pritzel, A., Green, T., Figurnov, M., Ronneberger, O., Tunyasuvunakool, K., Bates, R., Žídek, A., Potapenko, A., Bridgland, A., Meyer, C., Kohl, S. A. A., Ballard, A. J., Cowie, A., Romera-Paredes, B., Nikolov, S., Jain, R., Adler, J., ... Hassabis, D. (2021). Highly accurate protein structure prediction with AlphaFold. *Nature, 596*(7873), 583–589. https://doi.org/10.1038/s41586-021-03819-2

## Response 2 — Thomas Bogart

Thomas,

Your distinction between reactive APAP and a system that predicts an event before it occurs identifies a valuable use of deep learning: changing treatment from response to prevention. The recurrence-plot approach is especially interesting because it converts temporal behavior into a representation a CNN can process. I could also see value in combining that CNN output with an LSTM that tracks a patient's recent pressure requirements, sleep-stage patterns, congestion, and longer-term changes. The CNN could estimate near-term event risk, while the LSTM could provide patient-specific context.

The main challenge would be turning a prediction into a safe closed-loop pressure adjustment. A false negative could allow an apnea event, but a false positive could raise pressure unnecessarily, disturb sleep, or reduce adherence. The system would therefore need more than overall accuracy. Sensitivity, false-alarm rate, calibration, and performance across different patient groups would all matter. A practical design might begin with conservative pressure limits and keep the existing APAP algorithm as a fallback while the predictive component demonstrates reliable performance.

Your example also raises an important issue about models that continue adapting after deployment. FDA guidance for AI-enabled medical-device software emphasizes controlled modifications, validation, and continued assurance of safety and effectiveness (Food and Drug Administration [FDA], 2025). Would you favor a model that learns continuously for each patient, or a locked model that is periodically retrained and clinically reviewed? The continuous model could personalize faster, but the locked model may be easier to validate and audit.

**Reference**

Food and Drug Administration. (2025). *Marketing submission recommendations for a predetermined change control plan for artificial intelligence-enabled device software functions: Guidance for industry and Food and Drug Administration staff*. https://www.fda.gov/regulatory-information/search-fda-guidance-documents/marketing-submission-recommendations-predetermined-change-control-plan-artificial-intelligence

