# Module 7 Peer Responses

## Response to Anil Karki

Anil,

Your fraud-detection example highlights an important advantage of deep learning: it can learn interactions among transaction amount, location, merchant, device, and account behavior that would be difficult to express as a fixed collection of rules. I would extend your idea by treating a customer's transactions as a sequence rather than evaluating each transaction independently. A purchase may not look fraudulent by itself, but it could become suspicious when it immediately follows a password change, a new-device login, or purchases in geographically distant locations. An LSTM or transformer could encode that recent event history, while a second network branch processes current-transaction attributes.

The class imbalance you identified also changes how the system should be tested. Accuracy would provide little value when legitimate transactions greatly outnumber fraudulent ones. I would report precision, recall, the precision-recall curve, dollars prevented, false declines per thousand legitimate transactions, and alert volume that investigators can realistically review. The decision threshold should reflect transaction value and intervention cost: a low-risk purchase might trigger an additional authentication step, while a high-risk transfer might be paused for human review.

I would also split the data chronologically and, where possible, by customer rather than randomly by transaction. Otherwise, closely related activity could occur in both training and testing and inflate performance. Fraud tactics also change in response to detection, so monitoring concept drift and regularly evaluating recent cases would be essential. How would you balance catching more fraud against the customer harm caused by false declines, and would you use one threshold for all transactions or adjust it according to value and risk?

## Response to Leslie Nunez

Leslie,

Your Netflix example is a strong illustration of why recommendation is a sequential problem rather than simply a catalog-matching problem. A user's next choice may depend on the order of recent viewing: finishing several episodes of one series, abandoning a movie after five minutes, or switching from children's content during the day to documentaries at night. A recurrent model or transformer could represent that session history and combine it with item features, device, time, and household context to rank the next set of titles.

One challenge is that viewing behavior is implicit feedback, not a direct statement of preference. A title may receive no click because it was placed low on the page, not because the user disliked it. Similarly, completion rate can mean different things for a short comedy special and a two-hour film. The training data should therefore preserve exposure position, impressions, searches, previews, watch duration, completion, repeats, and explicit ratings when available. Evaluation should use a time-aware split so future behavior cannot influence past recommendations, followed by a controlled online test of outcomes such as successful play, longer-term satisfaction, and cancellations.

I also like your observation that the data continually evolve. Retraining can address changing interests, but it can also reinforce a narrow feedback loop in which users see only content similar to what they already watched. I would reserve some recommendation space for exploration and measure diversity, novelty, and coverage in addition to engagement. For new users, a short preference survey and contextual popularity could address the cold-start problem. If engagement and satisfaction produce different rankings, which objective do you think Netflix should prioritize, and how could it measure satisfaction without overinterpreting watch time?
