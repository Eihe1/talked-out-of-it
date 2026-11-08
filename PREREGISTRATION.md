# Preregistration of the reframing test

The hypothesis and analysis plan were written in the author's project log on 8 November 2026, before the run
reported as "Preregistered" in Table B4 of the report. This file summarises that plan; it was added to the
repository after the hackathon.

- **Hypothesis.** Adding a reframing of the tip as ordinary flow information (condition `C3a_reframe`) to the plain
  request (`C2b_ask`) increases the share of episodes in which the target shorts USD/JPY.
- **Sample.** Llama-3.3-70B and Gemini-2.5-Flash-Lite, 20 new episodes per condition and model (80 episodes).
- **Primary analysis.** Two models pooled; one-sided Fisher exact test (reframing > plain request); alpha = .05;
  all episodes. Episodes in which the persuader followed its instructions are analysed as a supplement.
- **Secondary analyses.** Per-model one-sided tests; the share of episodes in which the target refused in chat
  (expected lower with reframing; one-sided).
- **Reporting.** Results are reported whatever their direction.

The reported run is in `hackathon_fx/runs/20261108-141448_*` (Llama-3.3) and `20261108-141451_*` (Gemini-2.5). A
follow-up run with persuader reasoning enabled (`*_Pconf`) used the same tests.
