# CSC525 Module 5 CTP Dataset Candidates

Assignment path: Option #1, Text Dataset Augmentation.

Goal: choose a text dataset that can be included with the submission, augmented by a Python script, and reused for the Module 5 Portfolio Milestone NLP chatbot training run.

## Recommendation

Use a compact sampled subset of the Bitext Customer Support LLM Chatbot Training Dataset.

Why:
- It directly matches the portfolio chatbot direction.
- It already contains customer-service questions, intent labels, categories, and responses.
- The CTP can augment customer question text while preserving labels and responses.
- The Portfolio Milestone can train a lightweight intent-routing or retrieval baseline on the same augmented data.

Submission approach:
- Keep the full external source out of the zip if it is too large.
- Create `data/raw/customer_support_seed.csv` with a clean, documented subset.
- Create `data/augmented/customer_support_augmented.csv` from the script.
- Include a short `README.md` explaining source, sampling, augmentation methods, and AI-use note if applicable.

## Candidate 1: Bitext Customer Support LLM Chatbot Training Dataset

Source:
- Hugging Face: https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset
- GitHub: https://github.com/bitext/customer-support-llm-chatbot-training-dataset

Fit:
- Strongest fit for the portfolio chatbot.
- Customer-service vertical.
- Contains question/instruction text, intent, category, response, and language-generation tags.
- About 26.9k rows, 27 intents, and 10-11 categories depending on source view.

Augmentation ideas:
- Phrase replacement for customer-service language, such as "I need help with" -> "Can you help me with".
- Intent-preserving typo/noise injection.
- Politeness/casing/punctuation variants.
- Light word dropout or swap for robustness.

Risks:
- Full CSV is larger than necessary for a coursework submission.
- Some responses are templated/synthetic, so final paper should call that out.
- Need to preserve placeholders such as `{{Order Number}}`.

Verdict:
- Best choice if we want the CTP and Portfolio Milestone to align tightly.

## Candidate 2: BANKING77

Source:
- Hugging Face: https://huggingface.co/datasets/PolyAI/banking77

Fit:
- Clean customer-service style intent dataset for banking.
- 13,083 online banking queries labeled with 77 intents.
- Small enough to work with easily.
- Strong for intent classification and routing.

Augmentation ideas:
- Synonym and phrase variants for banking questions.
- Politeness and punctuation variants.
- Small typo/noise injection.

Risks:
- Banking-only domain, less general than a customer-support chatbot.
- Has question text and labels, but no agent responses.

Verdict:
- Best choice if we want a clean, simple, low-risk dataset for a classifier-style chatbot.

## Candidate 3: CLINC150

Source:
- UCI Machine Learning Repository: https://archive.ics.uci.edu/dataset/570/clinc150

Fit:
- Intent classification dataset with 150 in-domain intents and an out-of-scope class.
- 23,700 text instances.
- Good for demonstrating chatbot routing and fallback behavior.

Augmentation ideas:
- Intent-preserving paraphrase-like phrase variants.
- Add out-of-scope/no-match examples to test fallback behavior.
- Punctuation/casing variants.

Risks:
- Multi-domain assistant data, not specifically customer service.
- Needs transformation from JSON format into a simple CSV for submission.

Verdict:
- Strong second choice if we want out-of-scope handling in the chatbot.

## Candidate 4: Customer Support on Twitter

Source:
- Kaggle: https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter

Fit:
- Real public customer-support conversations.
- Very relevant for noisy real-world customer text.

Augmentation ideas:
- Normalize mentions, URLs, and hashtags.
- Emoji and punctuation variants.
- Thread-pair extraction.

Risks:
- Very large dataset.
- Noisy, social-media-specific language.
- Kaggle download may require login/API setup.
- More preprocessing effort than needed for this CTP.

Verdict:
- Good research source, but too heavy for this assignment unless we only use a small curated sample.

## Candidate 5: MASSIVE

Source:
- Amazon Science/Hugging Face: https://huggingface.co/datasets/AmazonScience/massive

Fit:
- Large multilingual NLU dataset for intent prediction and slot annotation.
- Useful if we wanted multilingual or voice-assistant style routing.

Augmentation ideas:
- English-only subset.
- Intent and slot-preserving variants.
- Add light user-query noise.

Risks:
- Much bigger than needed.
- More voice-assistant oriented than customer-support oriented.
- Multilingual scope adds complexity that does not help this submission.

Verdict:
- Technically strong but overkill for Module 5 CTP.

## Practical Selection Criteria

Pick the dataset that best satisfies these:

1. Easy to include as a small raw CSV sample.
2. Has clear text fields to augment.
3. Has labels or responses we can preserve after augmentation.
4. Supports the Module 5 Portfolio Milestone training run.
5. Does not require heavy external setup or manual login.

Current best choice: Bitext sampled subset.
