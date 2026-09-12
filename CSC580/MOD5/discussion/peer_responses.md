# Module 5 Peer Responses

## Reply to Romeo Sayon

Hi Romeo,

Your connection between neural networks and blind hiring raises an important implementation issue. Removing names, gender, age, and similar identifiers from the model’s inputs can reduce direct discrimination, particularly in settings where favoritism or nepotism affects hiring. However, I do not think blindness alone can establish fairness because seemingly neutral variables can reconstruct much of the removed information. School attended, location, employment gaps, language patterns, or professional affiliations may function as proxies even when the protected characteristic is never presented directly to the network.

There is also a useful paradox here: an organization may need protected-class information to determine whether its supposedly blind system is producing unequal outcomes. I would separate the data into two roles. The production model would not receive protected characteristics when evaluating applicants, but an independent auditing process would retain them under controlled access. Auditors could then compare selection rates and, more importantly, false-negative rates across groups. That last measure matters because two groups could have similar overall acceptance rates while qualified members of one group are rejected more often.

I also appreciate that you connected this issue to Module 5 validation. I would extend validation beyond a single random holdout set by testing the system across time periods, locations, and applicant subgroups. A model that performs well overall but fails in one region or demographic group should not be considered ready for consequential use. How would you balance the privacy goal of minimizing protected-class data with the practical need to retain enough of that information to audit whether blind hiring is actually fair?

## Reply to Yann Gilbert

Hi Yann,

Your question about where to draw the line between a recommendation and a decision gets to the central governance problem. I would draw that line according to what action the model is authorized to take, not merely whether a human sees its output. A system remains advisory if it can add a candidate to a review pool, organize evidence, or flag uncertainty. It becomes a decision-maker when its score can remove a candidate from consideration without an individualized review. A nominally “human” process can therefore still be effectively automated if reviewers simply approve the model’s ranked list.

One practical design would use selective prediction rather than forcing the network to classify every applicant. Candidates clearly meeting published requirements would proceed normally. The model could surface additional candidates whom conventional screening might overlook, while ambiguous cases would enter an abstention zone requiring human evaluation. Importantly, the system would not possess an automatic-rejection threshold. This makes the cost of a model error more manageable: a false positive creates additional review work, whereas a false negative could silently eliminate a qualified person’s opportunity.

I would permit greater model authority only after the organization demonstrated calibrated probabilities, stable performance on future cohorts, comparable false-negative rates across relevant groups, meaningful explanations, and an accessible appeal process. Even then, responsibility must remain assigned to a person or institution rather than to the algorithm. Do you think organizations would accept a system designed this way if it improved fairness but saved less time than an automated ranking-and-rejection model?
