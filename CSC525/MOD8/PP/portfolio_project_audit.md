# CSC525 Module 8 Portfolio Project Audit

Student: Justan Dunn  
Selected assignment: Option #2 - NLP Chatbot Final Version

## Live Assignment Requirements

The final submission must include a runnable executable file or a link that
allows the instructor to interact with the chatbot. The chatbot must use NLP
learning methods, return responses that are clearly related to user input, and
avoid nonsense responses. The written submission must explain whether the
chatbot is open- or closed-domain, identify the tools and libraries, describe
the NLP model, and provide complete run or access instructions.

The prompt requires at least two credible sources. The rubric raises the target
for full credit to at least four credible sources that are integrated into the
technical discussion. The rubric also requires all project components, strong
knowledge of NLP methods, clear application of course concepts, an organized
essay with introduction/body/conclusion, strong grammar, and APA formatting.

## Milestone Continuity

### Module 3: Project Definition

- Selected Option #2.
- Defined a closed-domain enterprise knowledge-support chatbot.
- Selected a retrieval design using TF-IDF and cosine similarity.
- Established confidence-based answer, clarification, and escalation behavior.

### Module 4: Data Strategy

- Refined the use case into customer-service routing and support.
- Selected RSiCS for conversational customer-service language.
- Selected WikiQA for answer ranking and no-answer behavior.
- Defined a sanitized enterprise FAQ/SOP corpus for approved routes and answers.

### Module 5: Initial Training

- Built an 80-row sanitized corpus with 10 support routes.
- Trained a TF-IDF cosine-similarity retrieval baseline.
- Used a 50-row training and 30-row grouped test split.
- Reported 1.0000 accuracy and macro F1 using `combined_text`.
- Recorded a question-only result of 0.2333 accuracy and 0.2094 macro F1.

### Module 6: Alpha Chatbot

- Produced a working command-line chatbot with demo, single-message, and
  interactive modes.
- Returned approved route-specific responses and confidence scores.
- Used a 0.35 fallback threshold.
- Accepted seven scripted in-domain messages and rejected one out-of-domain
  message.

## Current Strengths

- The selected domain and model remain consistent across milestones.
- The chatbot is runnable with only the Python standard library.
- Responses are controlled and tied to approved FAQ/SOP content.
- Low-confidence inputs can be clarified or escalated instead of answered.
- The corpus, scripts, metrics, and demo transcript are reproducible.
- Four credible sources have already been identified across the milestones.

## Gaps and Risks

1. The 1.0000 evaluation is not a fair estimate of runtime performance. The
   `combined_text` field appends the same route-specific keyword list to every
   example in a route. Held-out test queries therefore contain information that
   a real customer message will not contain. The question-only sweep is the
   more realistic baseline and shows that raw-language coverage is currently
   weak.
2. RSiCS and WikiQA were selected but have not been incorporated into the local
   training or validation artifacts.
3. The eight-message alpha demo is too small and too clean to support a strong
   final performance claim.
4. The current interface is functional but still labeled as an alpha and lacks
   a polished final-project entry point.
5. Threshold selection is based on a small scripted demonstration rather than
   a documented calibration set containing in-domain, ambiguous, and
   out-of-domain messages.
6. The final Module 8 paper and submission package do not yet exist.

## Recommended Final Scope

The final project should remain a closed-domain customer-service routing and
retrieval chatbot. The safest final architecture is:

1. Normalize the raw user message.
2. Apply a TF-IDF intent-routing model trained only on customer-language text.
3. Retrieve the approved response for the predicted route.
4. Combine route confidence and retrieval similarity into a fallback rule.
5. Ask for clarification or route to a human when confidence is low.
6. Log only sanitized test results for evaluation and reporting.

The final package should contain a clearly named chatbot entry script, a simple
interactive interface, the sanitized corpus, a requirements file if external
libraries are used, a README with exact commands, an evaluation report based on
raw messages, a demonstration transcript or screenshot, and an APA-formatted
technical paper. The paper should target four to five pages of substantive body
content, plus title and references pages, even though Option #2 states only a
one-page minimum. This gives enough space to satisfy the rubric's content and
source-integration expectations.

## Recommended Execution Order

1. Create an independent raw-message evaluation set with in-domain,
   paraphrased, ambiguous, and out-of-domain examples.
2. Compare the current retriever with word n-grams, character n-grams, and a
   supervised intent classifier without adding route keywords to test inputs.
3. Select and document the final threshold using measurable precision,
   coverage, and fallback behavior.
4. Build the final interactive interface and retain the command-line fallback.
5. Run reproducible validation and generate final figures or transcripts.
6. Write the APA report with at least four credible sources.
7. Assemble and validate one instructor-ready submission archive.
