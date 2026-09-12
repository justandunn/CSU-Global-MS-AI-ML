# Module 3 Discussion: Predicting Demand and Stockout Risk

A practical application that interests me is an inventory decision-support system for a small manufacturer. The system would use linear regression to predict future unit demand and logistic regression to estimate whether an item will stock out during its replenishment lead time. The two predictions answer different but complementary business questions: “How many units are likely to be needed?” and “How likely are we to run out before replacement inventory arrives?”

For the linear regression model, the output would be a continuous value, such as the number of units expected to sell during the next four weeks. Inputs could include lagged weekly demand, recent demand trend, product family, price, promotion status, holidays, season, and customer-order backlog. Only information available at the forecast date should be included. Hyndman and Athanasopoulos (2021) explain that genuine forecasts must use predictor values known in advance or values that can themselves be forecast. This distinction would prevent the model from appearing accurate because it accidentally used future information.

The logistic regression model would produce a probability between zero and one representing the likelihood of a stockout during the supplier’s lead-time window. Its inputs could include current on-hand quantity, open purchase-order quantities and expected arrival dates, the linear model’s demand forecast, demand variability, supplier lead-time variability, and existing safety stock. A decision threshold could translate the probability into an operational flag, but the probability itself is more informative than a simple yes-or-no label. For example, a 0.78 stockout probability could justify expedited replenishment, while a 0.52 probability might call for planner review. TensorFlow’s logistic-regression guidance similarly treats the output as the estimated probability of membership in a binary class and uses binary cross-entropy to train the model (TensorFlow, n.d.).

These predictions would improve on fixed reorder points because they respond to changes in demand and supplier performance. The linear forecast could inform the recommended order quantity, while the logistic model could prioritize items requiring immediate attention. Business value should be measured with operational outcomes—not accuracy alone—including avoided stockouts, reduced excess inventory, improved fill rate, and lower expedite costs.

I would evaluate both models using chronological training and test periods. Mean absolute error would measure demand-forecast performance, while precision, recall, area under the precision-recall curve, and probability calibration would evaluate stockout risk. Simple seasonal-average and reorder-point rules should remain as baselines. If a later neural network cannot outperform those baselines on unseen periods or provide enough business value to justify its complexity, the regression models should remain in production.

## References

Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3rd ed.). OTexts. https://otexts.com/fpp3/

TensorFlow. (n.d.). *Logistic regression for binary classification with Core APIs*. Retrieved August 6, 2026, from https://www.tensorflow.org/guide/core/logistic_regression_core

