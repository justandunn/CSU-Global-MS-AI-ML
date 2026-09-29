# CSC525 Module 8 Discussion Draft

Student: Justan Dunn

## Prompt Review

The Module 8 discussion examines how quantum computing could change artificial
intelligence, disrupt current generative AI and analytics systems, and create
new capabilities or risks. The initial post must contain at least one
well-developed paragraph and is due Thursday at 11:59 p.m. MT. At least two
substantive peer responses are due Sunday at 11:59 p.m. MT.

Most visible peer posts focused on faster AI training and the possibility that
quantum computers will break current encryption. To keep this post distinct,
the response focuses on a hybrid architecture in which quantum processors
accelerate narrow subproblems while classical CPUs and GPUs continue to perform
most AI work. It also distinguishes theoretical quantum speedup from practical
end-to-end performance.

## Initial Post: Quantum Computing as a Specialized AI Accelerator

I expect quantum computing to change artificial intelligence as a specialized
accelerator within hybrid systems, not as a replacement for the CPUs and GPUs
that currently train and run AI models. The IBM Think 2025 presentation
describes a future in which quantum, classical high-performance computing, and
AI resources work together (IBM Research, 2025). That distinction matters
because quantum computers do not make every calculation faster. Their strongest
potential is in particular classes of problems, including optimization,
sampling, and the simulation of quantum systems. These capabilities could help
AI search difficult solution spaces in fields such as drug discovery,
materials science, logistics, and financial risk analysis. However, a
generative model such as ChatGPT still depends heavily on classical matrix
operations, large datasets, and reliable data movement. Encoding classical data
for a quantum processor, correcting quantum errors, and returning results to a
classical system may reduce or even eliminate a theoretical speed advantage.
Biamonte et al. (2017) similarly concluded that quantum machine learning offers
promising algorithmic building blocks while still facing considerable hardware
and software challenges. Therefore, the first meaningful disruption may be a
hybrid workflow in which a quantum processor solves one computationally
difficult subproblem while classical infrastructure handles data preparation,
model orchestration, and deployment.

The more immediate disruption may be security rather than faster AI. Future
fault-tolerant quantum computers could weaken public-key cryptography that
protects model APIs, training data, credentials, and proprietary model
artifacts. This is no longer only a theoretical planning issue: the National
Institute of Standards and Technology (NIST, 2024) has approved three
post-quantum cryptography standards designed to resist future quantum attacks.
Organizations developing AI systems should begin inventorying cryptographic
dependencies and planning migration before large quantum computers become
available. Overall, quantum computing will probably accelerate selected AI
workloads and create applications that are impractical today, but it will also
introduce new costs, specialized skill requirements, security migrations, and
benchmarking challenges. The critical question will not be whether a quantum
algorithm is faster in isolation, but whether the complete hybrid system is
more accurate, secure, economical, and useful than the best classical
alternative.

References

Biamonte, J., Wittek, P., Pancotti, N., Rebentrost, P., Wiebe, N., & Lloyd, S.
(2017). Quantum machine learning. *Nature, 549*(7671), 195-202.
https://doi.org/10.1038/nature23474

IBM Research. (2025, May 9). *What's next for the future of computing - IBM
Think 2025* [Video]. YouTube. https://www.youtube.com/watch?v=nYQqTPlVLKo

National Institute of Standards and Technology. (2024, August 13). *Announcing
approval of three Federal Information Processing Standards (FIPS) for
post-quantum cryptography*.
https://csrc.nist.gov/News/2024/postquantum-cryptography-fips-approved

## Selected Peer Reply 1: Leslie Nunez

Leslie, your beauty-industry example identifies an important distinction
between having more computing power and having a problem that actually benefits
from quantum computing. Product recommendations and social-media trend analysis
are already handled effectively by classical AI, so a beauty company would
need to identify a narrower bottleneck that justifies the additional cost and
complexity. Two stronger candidates might be optimizing a very large portfolio
of product, inventory, pricing, and marketing decisions at the same time, or
combining AI with molecular simulation to evaluate new cosmetic formulations.
Your point about virtual try-on data is especially important because facial
images can create long-lived privacy risk. Even if a company never uses a
quantum computer directly, it may still need post-quantum protection for stored
customer profiles, API traffic, and vendor integrations. How would you decide
which beauty-business problem is valuable and complex enough to justify a
hybrid quantum-classical pilot rather than an improved classical model?

## Selected Peer Reply 2: Shourav Mandal

Shourav, your emphasis on avoiding both hype and dismissal is important because
claims of quantum advantage can depend heavily on what is included in the
comparison. A quantum routine might solve one optimization step quickly while
the overall workflow remains slower after data encoding, error mitigation,
queue time, and transfer back to classical infrastructure are included. For an
AI use case, I think a credible benchmark should compare the complete hybrid
workflow against the best available classical method using the same dataset,
accuracy requirement, wall-clock time, energy use, and total cost. That would
also help prevent a small experimental result from being generalized into a
claim that quantum computers will accelerate all model training. Your examples
of chemistry and materials science may be stronger early candidates because
the underlying problems are quantum mechanical, whereas ordinary language
model data begin as classical information. What evidence or benchmark would
you consider sufficient to show practical quantum advantage for an AI workload?
