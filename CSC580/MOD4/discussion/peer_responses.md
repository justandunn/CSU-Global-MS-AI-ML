# Module 4 Discussion Forum: Peer Responses

## Response to Ryan Ganshert

Ryan, your compensation-equity example is a strong illustration of why a neural network’s output should begin an inquiry rather than settle one. One way to impugn the model would be to challenge whether it suffers from omitted-variable bias. Two employees may appear comparable based on job level, family, geography, market rate, and compa-ratio while differing in tenure, specialized certifications, shift requirements, sales territory, performance history, or the timing of a promotion. If legitimate variables are missing, the network may label a defensible pay difference as discrimination. The opposite problem is also possible: seemingly neutral features such as geography, department, employment gaps, or prior salary may act as proxies for protected characteristics and allow a biased historical pay structure to reproduce itself.

I would therefore ask the proponent to produce subgroup-specific false-positive and false-negative rates rather than one overall accuracy figure. The model should also be tested across job families, locations, gender, race, age, and intersectional groups, with confidence intervals where the sample is small. NIST’s framework is useful here because it treats validity, transparency, explainability, and management of harmful bias as separate requirements; satisfying one does not establish the others (National Institute of Standards and Technology [NIST], 2023). A defense expert could also rerun the analysis after removing suspected proxy variables, changing the comparison group, or using matched employee pairs. If the result changes materially, that instability would weaken its evidentiary value.

What standard would you use to distinguish a model-discovered disparity that warrants investigation from one strong enough to justify a corrective salary adjustment?

## Response to Leslie Nunez

Leslie, I agree that deepfake detection may help authenticate digital evidence, but the detector itself creates several productive lines of attack. The first is distribution shift. A model can test well when the questioned media were created by generators represented in its training data yet fail on a new generator or after resizing, recompression, cropping, noise, or social-media processing. NIST reports that synthetic-image detectors perform better on content from familiar generators and can retain substantial error rates under cross-generator testing and post-processing (National Institute of Standards and Technology [NIST], 2026). Therefore, a party should not be allowed to cite a benchmark accuracy unless the validation conditions resemble the actual exhibit.

A second challenge concerns provenance and reproducibility. The opponent should request the original file, cryptographic hash, metadata, complete chain of custody, detector name and version, decision threshold, training-data description, and every transformation performed before analysis. Testing only a downloaded or recompressed copy could create or destroy the artifacts on which the detector relies. An independent examiner should also run competing detection methods and document whether the tools agree. Finally, even a technically correct “synthetic” classification does not establish who created the media, when it was altered, or whether the altered portion is material to the case. Those facts require corroborating device records, platform logs, witnesses, and content provenance.

How would you handle a case in which the detector flags a courtroom video but a second validated detector classifies the same file as authentic?

## References

National Institute of Standards and Technology. (2023). *Artificial intelligence risk management framework (AI RMF 1.0)* (NIST AI 100-1). U.S. Department of Commerce. https://doi.org/10.6028/NIST.AI.100-1

National Institute of Standards and Technology. (2026). *Trustworthy and responsible AI* (NIST AI 100-4, initial public draft). U.S. Department of Commerce. https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-4.pdf

