# Module 3 Peer Responses

## Response to Romeo Sayon

Romeo, your proposal connects the continuous soil-moisture estimate and the binary drought-risk decision effectively. The most important improvement I would make is to represent both time and location explicitly. Rainfall, temperature, soil moisture, and groundwater conditions are autocorrelated across nearby locations and consecutive periods. A neural network trained with randomly mixed observations could therefore see almost identical neighboring measurements in both training and testing data, producing an overly optimistic result. Holding out entire regions and future seasons would provide a more realistic evaluation of whether the system generalizes to a new location or drought cycle.

I would also add lagged measurements, vegetation indices, land-cover type, elevation, soil texture, and seasonal indicators. The sensor readings and field measurements may arrive at different spatial resolutions and frequencies, so the pipeline should document how each observation is aligned before training. Missing sensor values should be flagged rather than silently treated as zero.

For the logistic model, the definition of “drought” should be tied to a specific threshold, forecast horizon, and intended intervention. Because severe drought observations may be less common than normal conditions, accuracy alone could hide poor detection. Recall, precision, the precision-recall curve, and probability calibration would be more useful. For the neural-network extension, I would compare a small temporal or spatial-temporal model with the regression baselines and quantify uncertainty around every prediction.

How would you establish ground-truth drought labels in regions where field observations are sparse: government drought declarations, crop outcomes, local soil measurements, or a combination of sources?

## Response to Boubacar Barry

Boubacar, your scoring and win-probability examples demonstrate the difference between continuous and binary outputs clearly. For a pregame prediction, I think the first improvement is to separate variables that are known before tipoff from variables observed during or after the game. Final shooting percentage, rebounds, and turnovers are highly predictive of winning, but using their completed-game values would leak the outcome into the inputs. Pregame versions could instead use rolling averages from prior games, projected starters, injury status, rest days, travel distance, home-court status, and opponent-adjusted offensive and defensive efficiency.

A neural network could improve the model by learning interactions that a basic regression may miss. For example, a team’s overall rebounding average may matter less than how its expected lineup matches the opponent’s size. Team and player embeddings could represent those identities, while recent-game sequences could capture changing form. I would still keep linear and logistic regression as baselines because a more complex network should demonstrate measurable out-of-sample value before coaches rely on it.

The test design should also follow time. Training on earlier seasons and testing on later games would better simulate deployment than randomly distributing games across sets. I would report mean absolute error for points, plus log loss, Brier score, discrimination, and calibration for win probability. Calibration matters because a team assigned a 70% probability should win approximately 70% of comparable games. Performance should also be segmented by season stage and by games involving major lineup changes.

Would your prediction be made before the game or updated live? A live model could use current turnovers and shooting data, but it would require a separate design and evaluation from the pregame model.
