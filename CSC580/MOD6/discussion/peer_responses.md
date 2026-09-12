# Module 6 Peer Responses

## Response to Colter Welden

Colter,

Your vessel-navigation example shows why a real CNN application usually needs more than image classification. Recognizing a buoy or bridge is useful, but the navigation decision also depends on where that object is relative to the vessel, whether it is moving, and how confident the system is under the current conditions. I would therefore frame the camera component as an object-detection and tracking system rather than a simple classifier. Bounding boxes could estimate the position and apparent size of buoys, docks, other vessels, and debris across consecutive frames. Those visual observations could then be fused with radar, GPS, heading, speed, water depth, and electronic-chart data.

Your point about changing river conditions is especially important. Training data would need to represent morning glare, fog, rain, darkness, seasonal vegetation, high and low water, partially submerged markers, and camera vibration. I would also separate training and testing data by trip or date. Randomly splitting consecutive video frames could place nearly identical scenes in both groups and create an unrealistically strong test result.

I would keep a licensed operator in control and initially deploy the system as an advisory tool. An alert could identify an unexpected obstacle or disagreement between the camera, radar, and chart position, while the operator makes the navigation decision. How would you design the system when sensors disagree—for example, when the CNN detects a buoy but radar does not, or when a buoy has moved away from its mapped position?

## Response to Christine Deluna

Christine,

Your comparison between a one-dimensional CNN and tree-based models is an important addition because the model should be selected based on validation evidence, not simply because deep learning is available. A 1D CNN could learn short local patterns such as several days of falling heart-rate variability combined with rising resting heart rate. Random forest or gradient boosting, however, may be more effective when clinicians already understand which rolling changes and deviations from a personal baseline are meaningful.

I would evaluate these approaches with a patient-level, time-aware design. All observations from one patient should remain within one partition so the model cannot learn an individual's baseline in training and then appear to generalize to that same person in testing. The test period should also occur after the training period. Because flare events are uncommon, accuracy could be misleading; event recall, precision, false alerts per patient-week, calibration, and the amount of advance warning would better represent clinical usefulness.

Label uncertainty is another major issue. I like your distinction among self-reported, clinician-confirmed, and laboratory-supported events. Rather than treating all labels as equally reliable, the dataset could retain the evidence source and use a sensitivity analysis to determine whether conclusions change under stricter flare definitions. Missing wearable measurements should also be represented explicitly because non-wear may correlate with illness.

Would you expect one global model to work across patients, or would you begin with a population model and then calibrate its threshold or final layer to each patient's normal physiological range?
