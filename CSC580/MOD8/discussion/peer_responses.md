# Module 8 Peer Responses

## Response to Dominic Suarez

Dominic,

Your tokamak example clearly demonstrates the distinction between prediction and control. As you noted, a sequence model might forecast the plasma's next state, but the RL controller must repeatedly decide how to adjust the magnetic coils so the desired configuration remains stable. I found the use of all 19 coils particularly important because the actuators are coupled: changing one magnetic field can affect several aspects of the plasma. Optimizing each coil with an independent rule could therefore create conflicts, whereas one policy can account for the combined action.

The application also raises a major safety issue: trial-and-error learning cannot begin on the physical reactor. I would train the policy in a validated simulator, randomize physical parameters and sensor noise during training, and then test increasingly difficult scenarios before controlled hardware deployment. This domain-randomization process could help prevent the policy from depending on one unrealistically precise simulation. The reward should also treat hard safety limits differently from ordinary performance goals. Plasma stability and equipment protection should be constraints that the agent cannot trade away simply to obtain a slightly better shape or efficiency score.

I would pair the learned controller with independent limit monitors, a conventional fallback controller, and automatic shutdown logic. Engineers should also examine performance under sensor failures, delayed measurements, and operating conditions outside the training range. Your example makes a strong case for RL, but it also shows why successful simulation performance is only the beginning of validation. Which safeguard do you think should have final authority if the learned controller and the conventional safety system recommend conflicting coil actions?

## Response to Ryan Ganshert

Ryan,

Your adaptive workout example is a strong RL problem because today's training decision changes both the athlete's future fitness and the options that will be safe tomorrow. I would define the state using recent workout type, pace, duration, heart-rate response, sleep, resting heart rate, reported soreness, injury history, and progress toward the user's goal. Actions could include selecting workout intensity, distance, recovery, or rest. The reward should combine long-term improvement with penalties for excessive fatigue, missed sessions, pain, and injury risk rather than rewarding only faster times.

The delayed reward is the most difficult part. A hard workout may produce fatigue today but improve performance weeks later, while repeatedly maximizing short-term pace could cause overtraining. Moreover, wearable data are observational: a user who slept well may both run faster and recover better, so the system should not automatically conclude that the assigned workout caused the improvement. I would begin with offline RL using historical coaching and wearable records, then limit the live policy to conservative adjustments within sports-medicine guidelines.

Personalization is another reason RL could outperform a static plan. However, learning an entirely separate policy for every athlete would require too much individual data. A practical system could start with a population-level policy, personalize its state and reward weights, and keep a human coach or user able to reject recommendations. It should also recognize missing or unreliable sensor readings instead of interpreting them as poor recovery. How would you design the reward when the measurable goal—such as marathon time—might conflict with equally important outcomes such as adherence, enjoyment, and avoiding injury?
