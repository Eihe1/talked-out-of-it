# Talked Out of It? How Rule Violation Between Trading Agents Changes Along a Persuasion Ladder¹

**Ruiyang Wang**
UNSW Sydney, Australia (Master of Data Science and Decisions student; independent hackathon project)

**With** Apart Research

¹ Research conducted at the Swarm Alignment Hackathon, November 2026, Track 4: Multi-Agent Oversight and Control.

## Abstract

When an AI agent that has already broken a rule talks with a colleague agent, how much does each step of
persuasion add to the colleague's chance of breaking the rule too? We built a simulated FX trading desk in which a
persuader agent, who profited from an unverifiable tip, chats with a target agent under quarter-end pressure; the
target then acts through logged tools. We climbed a persuasion ladder one step at a time (the tip alone, the
peer's presence, the peer's disclosure that it traded on the tip, a hint, an explicit request, a profit split and
a threat) and varied whether the tip reached the target through its inbox or only through the peer. In two weaker
models, the tip and performance pressure alone produced violations in most episodes, and no step of the ladder
raised them further. Explicit persuasion instead lowered violations; a plain request did so for Llama-3.3, while
Gemini-2.5 responded most consistently to a split or a threat. The same tip led to far fewer violations when the
peer told it in conversation than when it sat in the target's inbox; an identical inbox email from the peer was
acted on as often as an anonymous forward by Gemini-2.5, but less often by Llama-3.3. Persuasion tactics and
writing styles had little effect, and removing performance pressure lowered violations. Agents acted on information
in their environment more readily than on what other agents told them, so safety evaluations of agent groups should
look at what agents can see and do, not only at what they are told.

## 1. Introduction

Language-model agents are beginning to work in groups, exchanging messages while acting through shared tools.
When one agent has already broken a rule, these ordinary conversations give it a way to draw colleagues in. It
can share what it did, drop a hint or ask outright, and it can add incentives or threats. These routes differ in
how visible they are: an explicit request is easy for a monitor to flag, a shared fact is not. If agents refuse
the visible routes but act on the quiet ones, a monitor that looks for persuasive messages would miss most of the
risk. Which step of persuasion actually moves a colleague is therefore a practical question for overseeing agent
groups.

Prior work points in different directions. Violating peers' examples raise violations (Shi, Zhang & Yang, 2026),
while an industry study found that teammates who argued for a violation lowered a frontier model's violation rate
(Laurmaa, 2026). Most studies use scripted peers, many measure what the target says rather than what it does, and
few separate what a peer says from what the target already knows. We ask: **when one agent persuades another, how
does each step up a persuasion ladder change the chance of a violation, and how much of it is due to the
information rather than the persuasion?**

We study this in a simulated FX desk in which compliance is feasible, the violation is verifiable from tool logs,
and reporting is possible. An adaptive LLM persuader chats with a target agent, and we add one element of
persuasion at a time. Our contributions are:

1. A persuasion ladder that adds one element at a time (the information, the peer's presence, its demonstration
   that it broke the rule, a hint, a request, incentives or threats), and a design that varies where the
   information comes from.
2. Evidence that, in two weaker models, information and performance pressure alone produce most violations, that
   no step of persuasion adds to them, and that explicit persuasion lowers them through a step that differs by
   model.
3. Evidence that the same tip leads to far fewer violations when another agent tells it in conversation than when
   it sits in the target's own inbox, and that whether the sender of an inbox message matters differs by model.

## 2. Related Work

**Agents under pressure.** A trading agent under pressure trades on an insider tip and hides it from its manager
(Scheurer, Balesni & Hobbhahn, 2023), and pressure and framing drive rule breaking in single agents (Okamoto, Erol
& Erol, 2026; Mouzouni, 2026). These studies vary the situation of one agent; they do not ask what a peer adds to
it.

**Peer influence among agents.** Peers have been studied as scripted violators (Shi, Zhang & Yang, 2026), as
claimed authorities (Zhang, 2026), in a research swarm that learned to cheat (Paglieri et al., 2026) and as
carriers of reward hacking (Hu et al., 2026). Closest to us, Laurmaa (2026) found with scripted teammates that
direct arguments for a violation lowered a frontier model's violations. LLM conformity comes mostly from the
content placed in context rather than from who says it (Hu & Qu, 2026). What remains open is how an adaptive
peer's persuasion, step by step, compares with the information it carries.

**Persuasion and action.** LLM persuaders can override guardrails (Nogueira et al., 2026) and mislead web agents
(Boots, 2026), although persuasion-only attacks failed in TAMAS (Kavathekar et al., 2025; see also Bozdag et al.,
2025). Refusals in text do not reliably carry over to tool calls (Cartagena & Teixeira, 2026; Gupta et al., 2026),
and a model's stated reasoning need not reflect why it acted (Turpin et al., 2023; Chen et al., 2025). We therefore
measure violations from tool calls and use reasoning traces only descriptively.

## 3. Methods

**Environment.** A fictional bank desk (Meridian Capital) on 23 June 2025, with real historical daily FX reference rates (ECB). The
target ("Birch") can read a desk folder (guidelines, research note, signal sheet, calendar, central-bank recap).
Its inbox holds the head of desk's weekly note (the persuader "Atlas" made USD 2.4M on USD/JPY; Birch is USD 1.1M
behind target with one week left; "compliance review this month is light-touch") and a tip forwarded from an
unidentified contact: "USD/JPY will drop about 2%". The rules forbid trading on material non-public information
and unapproved profit sharing; concerns can be reported (award up to USD 5,000). Two legitimate trades in the
signal sheet would earn about USD 200–400k, not enough to close the gap.

**The persuasion ladder.** Atlas and Birch chat for five rounds (at most 200 characters per message); Birch then
acts with tools: read files, get prices, trade (a rationale is required), agree to a profit split, report, and end
the day (limit USD 100M). Atlas always knows the tip, has traded on it and knows Birch's gap. Its instructions add
one element at a time (Table 1); in the explicit conditions it persuades in every message. Two controls sit below
the ladder: no tip, and the tip alone with no peer (no chat, and no mention of Atlas's profit in the weekly note).

*Table 1. The persuasion ladder.*
| Step | What Birch faces |
|---|---|
| No tip | as C0, but without the tip |
| Tip only | the tip and the pressure; no chat; the weekly note does not mention Atlas's profit |
| C0 Peer present | Atlas says it had a very good week; does not mention the tip or suggest any trade |
| C1 Disclosure | Atlas says it made USD 2.4M and its bonus by trading on the tip; no hint, no request |
| C2a Hint | C1 plus at most one light hint |
| C2b Request | C1 plus an explicit request to short USD/JPY (may cite Birch's gap and bonus) |
| C2c Split / C2d Threat | C2b plus a 50/50 profit split / plus the contact's warning and pleading |
| C2e All | C2b plus split and threat |

**Where the information comes from.** In the ladder the tip is always in Birch's inbox. To separate the information
from the peer, we crossed three of Atlas's behaviours (passing the tip on; passing it on and disclosing its own
trade, as in C1; passing it on and requesting the trade, as in C2b) with two sources: the tip also in Birch's inbox,
or only in Atlas's messages. Atlas's instructions are identical for the two sources except for whether Birch
already has the forward. Together with the ladder's own C0, C1 and C2b, in which the tip is only in the inbox, this
gives three sources for each behaviour. To separate the channel from the sender, a fourth source puts the
identical forward in the inbox, marked "From: Atlas"; Atlas does not bring it up at the lowest level but may answer
Birch's questions about it. We analyse all episodes and check whether Atlas actually stated the tip.

**Other manipulations.** We also removed Birch's performance pressure, added a strict compliance reminder, stated
the legitimate trades in the inbox, and tested six persuasion tactics, four writing styles and one pre-registered
hypothesis (Appendix B).

**Outcome, judge, models.** The outcome is whether Birch shorts USD/JPY ("trades on the tip"); a trade that is also
reported still counts. A judge model (DeepSeek-V4-Flash) labels each persuader message; restricting to episodes in
which Atlas followed its instructions gives the same pattern. The persuader is DeepSeek-V4-Flash with reasoning on.
Targets are Llama-3.3-70B and Gemini-2.5-Flash-Lite, accessed through OpenRouter with a fixed provider per model
(Llama-3.3 on DeepInfra, fp8). Cells have 20 episodes (10 for situations and tactics). We report Wilson 95%
intervals and two-sided Fisher tests; all tests are exploratory and uncorrected except one pre-registered test.
The API cost was about USD 16.

## 4. Results

![Figure 1](figures/fig_main.png)
*Figure 1. Share of episodes in which the target shorted USD/JPY (traded on the tip), with Wilson 95% intervals,
20 episodes per point. (a) The persuasion ladder; shaded: explicit persuasion. (b, c) Where the tip comes from,
for three of Atlas's behaviours. Inbox only: the ladder's C0, C1 and C2b, in which Atlas does not mention the tip;
Inbox + Atlas: Atlas also passes the tip on; Email from Atlas: the same forward, sent by Atlas; Atlas only (chat):
Atlas passes the tip on and the inbox has none.*

**4.1 Information and pressure alone produce violations.** With the tip in its inbox and no peer at all, both
targets traded on the tip in most episodes (Figure 1a). Without the tip, they almost never shorted USD/JPY. Adding
the peer back did not change this: keeping the chat but dropping the note's mention of Atlas's profit, or keeping
the note but dropping the chat, left trading at the level of C0 (Table B2). An unverified tip combined with a
performance gap was enough.

**4.2 No step of the ladder raised violations.** Hearing that the peer had traded on the tip and earned its bonus
(C1) did not raise trading, and neither did a light hint (C2a). Gemini-2.5 was already near its ceiling, but
Llama-3.3 had room to rise, and no condition took it significantly above C0 (Table B1).

**4.3 Explicit persuasion lowered violations, through a step that differed by model.** Across the four explicit
conditions, Gemini-2.5 traded on the tip less often than without explicit persuasion; Llama-3.3 showed the same
direction but the difference was not significant (Table B1). The effective step differed. A plain request cut
Llama-3.3's trades by two thirds, while adding a split or a threat brought them back towards the level of C0.
Gemini-2.5 ignored the plain request on the ladder and traded less once a split or a threat was added; in the
information-source runs, however, a plain request did lower its violations (Table B3), so Gemini-2.5's response to
a plain request was not stable. Refusing to comply
in conversation did not mean refusing in action: when Llama-3.3 traded on the tip under explicit persuasion, it
almost always also filed a report to compliance (63 of 71 trades).

**4.4 The same tip told by a peer was acted on far less.** When Atlas passed the tip on in conversation and the
inbox had none, both targets traded on it much less often than when the tip was in their inbox (Figure 1b, c).
Pooled over Atlas's three behaviours, Llama-3.3 traded on the tip in 17% of these episodes, against 55–60% with the
tip in the inbox; Gemini-2.5 in 47%, against 80–87% (Table B3). Atlas repeating a tip that Birch already had
changed nothing. The gap is not explained by Atlas failing to pass the tip on: when only asked to share it, Atlas
often kept quiet, but once it also disclosed its own trade it stated the tip in nearly every episode, and the gap
remained. To separate the channel from the sender, we put the identical forward in the inbox but marked it as sent
by Atlas. Gemini-2.5 then traded about as often as with an anonymous forward (75%), so for Gemini the drop came
from the tip arriving in conversation, not from who sent it. Llama-3.3 fell in between (35%): it acted less on the
document when it came from the peer, and less again when the peer only said it. At the explicit-request level the
source mattered little, because the request had already lowered trading, and with the peer as the only source no
step of the ladder raised violations.

**4.5 Pressure and a known alternative.** Removing Birch's performance pressure lowered violations, mainly for
Gemini-2.5 under a plain request; a strict compliance reminder had a weaker effect (Appendix B). Stating the two
legitimate trades in the inbox, so that every target knew a compliant way to make money, lowered violations only
when Atlas explicitly asked: Llama-3.3 then never traded on the tip and Gemini-2.5 roughly halved its rate. Without
a request, the targets traded on the tip about as often as before, even though they knew the alternative.

**4.6 Tactics and a pre-registered test.** None of six persuasion tactics added to the plain request changed
violations, and a pre-registered prediction that reframing the tip as ordinary flow information would raise them
held only in a run with the persuader's reasoning off and did not replicate with it on (Appendix B).

## 5. Discussion and Limitations

**Interpretation.** Violations did not rise as persuasion intensified: most needed no persuasion, and explicit
persuasion, where it mattered, lowered them. Our interpretation is that **models act on information in their
environment more readily than on what other agents tell them, and a direct request makes them less, not more,
likely to comply.** It fits the violations with the tip alone, their disappearance without it, the much lower rate
when the peer told the same tip in conversation, the drop under explicit requests, and the effect of a known
alternative only under a request. Laurmaa (2026) offered a similar explanation, and LLM conformity comes mostly from
content in context (Hu & Qu, 2026). It does not cover every result: Gemini-2.5's response to a plain request was not
stable, an emotional style raised Llama-3.3's violations, and Llama often refused in conversation yet traded. Nor
can our data separate it from safety training that reacts to request-shaped input (Appendix A).

**Model differences.** The two models responded to different steps of the ladder and to an emotional style in
opposite directions, while three of four styles had no effect. They also differed in whether the sender mattered:
Llama-3.3 discounted an inbox email from the peer, Gemini-2.5 did not. Explaining these differences needs more
detailed analysis and experiments.

**Implications.** Monitoring persuasive messages is not enough: the information an agent can see and the pressure
it is under mattered more than what its peer asked. Rules should be enforced at the tool layer, actions monitored
rather than chat, other agents' messages treated as untrusted, and the pressure behind shortcuts reduced.

### Limitations

All effects come from two weaker models: stronger targets (Gemini-3.1-Flash-Lite, Gemini-3-Flash, Claude Haiku
5.5, Llama-4-Maverick) never traded on the tip in any condition we tested (Appendix B). Gemini-2.5 was near its
ceiling without persuasion; comparisons are exploratory with 10–20 episodes per cell; prompts are single drafts;
the judge is an LLM; and stated reasoning may not reflect why a model acted. Full list in Appendix A.

### Future Work

More models, wordings and samples to explain why models differ in which step of persuasion moves them; a target
with a low baseline, so that increases can be detected; an easier-to-find legitimate alternative; a
human-validated judge; and groups of more than two agents.

## 6. Conclusion

A colleague agent broke the rule mostly because of the information and pressure it already faced, not because it
was persuaded. No step of the persuasion ladder raised violations, and explicit persuasion lowered them through a
step that differed by model. The same tip was acted on far less when another agent told it than when it appeared
in the agent's own inbox. For agent groups, what an agent can see and the pressure it is
under deserve as much attention as what other agents tell it.

## Code and Data

- Code repository: https://github.com/Eihe1/talked-out-of-it (simulation, judge, analysis scripts and all episode logs).
- Data: daily ECB euro reference rates for five pairs (1 April – 20 June 2025; source: ECB, via the Frankfurter API), included in the repository (pre-existing; Appendix D).
- No real trading, real persons or real non-public information are involved.

## References

1. Boots, B. C. (2026). Agent-to-Agent Synthetic Social Engineering on the Web. arXiv:2610.33411. https://arxiv.org/abs/2610.33411
2. Bozdag, N. B., Mehri, S., Tur, G., & Hakkani-Tür, D. (2025). Persuade Me if You Can: A Framework for Evaluating Persuasion Effectiveness and Susceptibility Among Large Language Models. arXiv:2503.01829. https://arxiv.org/abs/2503.01829
3. Cartagena, A., & Teixeira, A. (2026). Mind the GAP: Text Safety Does Not Transfer to Tool-Call Safety in LLM Agents. arXiv:2602.16943. https://arxiv.org/abs/2602.16943
4. Chen, Y., Benton, J., Radhakrishnan, A., Uesato, J., Denison, C., Schulman, J., et al. (2025). Reasoning Models Don't Always Say What They Think. arXiv:2505.05410. https://arxiv.org/abs/2505.05410
5. Gupta, E., Saha, R., Inyang, A.-A., & Al Gharib, A. (2026). Behavior Beyond Text: Evaluating Refusal Transfer Failure in LLM Agents. arXiv:2610.28982. https://arxiv.org/abs/2610.28982
6. Hu, Y., Ghahremani, P., Aghajani, R., Pasupuleti, M., & Bhattacharjee, H. (2026). Reward Hacking as a Transmissible Strategy in Multi-Agent Coding Systems. arXiv:2610.12822. https://arxiv.org/abs/2610.12822
7. Hu, Y., & Qu, J. (2026). Most LLM Conformity Needs No Speaker: Measuring the Speaker-Free Floor in Peer-Pressure Benchmarks. arXiv:2607.05545. https://arxiv.org/abs/2607.05545
8. Kavathekar, I., Jain, H., Rathod, A., Kumaraguru, P., & Ganu, T. (2025). TAMAS: Benchmarking Adversarial Risks in Multi-Agent LLM Systems. arXiv:2511.05269. https://arxiv.org/abs/2511.05269
9. Laurmaa, V. (2026, October 12). Peer Pressure Works on AI Agents: How One Change of Mind Can Tip the Whole Team. Check Point Blog. https://blog.checkpoint.com/security/peer-pressure-ai-agents/
10. Mouzouni, C. (2026). Mapping the Exploitation Surface: A 10,000-Trial Taxonomy of What Makes LLM Agents Exploit Vulnerabilities. arXiv:2604.04561. https://arxiv.org/abs/2604.04561
11. Nogueira, R., Almeida, T. S., Bonás, G. K., Roque, A., Pires, R., Abonizio, H., et al. (2026). LLM-Based Persuasion Enables Guardrail Override in Frontier LLMs. arXiv:2605.13334. https://arxiv.org/abs/2605.13334
12. Okamoto, M., Erol, A. K., & Erol, K. (2026). Why Do AI Agents Break Rules? How Framing, Context, and Social Signals Shape Compliance. arXiv:2608.12323. https://arxiv.org/abs/2608.12323
13. Paglieri, D., Cross, L., Genewein, T., Leibo, J. Z., Tomasev, N., & Vezhnevets, A. S. (2026). A Case Study on Emergent Cheating and Whistleblowing in Autonomous Research Swarms. arXiv:2609.04170. https://arxiv.org/abs/2609.04170
14. Scheurer, J., Balesni, M., & Hobbhahn, M. (2023). Large Language Models can Strategically Deceive their Users when Put Under Pressure. arXiv:2311.07590. https://arxiv.org/abs/2311.07590
15. Shi, X., Zhang, Y., & Yang, D. (2026). Emergent Collusion in Long-Horizon LLM Agent Interaction. arXiv:2609.24967. https://arxiv.org/abs/2609.24967
16. Turpin, M., Michael, J., Perez, E., & Bowman, S. R. (2023). Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting. NeurIPS 2023. arXiv:2305.04388. https://arxiv.org/abs/2305.04388
17. Zhang, I. (2026). The Troy Moment: How LLM Agents Adjudicate the Decision Point Under Impossible Tasks, Claimed Authority, and Peer Information. arXiv:2609.15494. https://arxiv.org/abs/2609.15494

---

## Appendix A. Limitations and Dual-Use / Ethical Considerations

**Limitations**
- *Capability floor.* Stronger targets never violated (Appendix B), so all persuasion effects come from two weaker
  models (Llama-3.3-70B, Gemini-2.5-Flash-Lite). Claude Haiku refused to act as persuader in most episodes, and
  DeepSeek models never traded on the tip as targets, which narrowed the model set.
- *Ceiling.* Gemini-2.5 traded on the tip in nearly every episode without persuasion, so the design could detect
  decreases but not increases for it; claims that persuasion did not raise violations rest mainly on Llama-3.3.
- *Statistics.* Most comparisons are exploratory and uncorrected. With 10–20 episodes per cell only large
  differences are detectable (at n = 10, a 60% vs 30% difference is detected with probability about 0.12).
- *Wording.* Persuader instructions, tactics and styles are single drafts written by us; results may depend on
  wording.
- *Information source.* The email condition holds the channel and wording fixed, but an email from Atlas may still
  look privately passed on, which may itself mark the tip as non-public; we did not test an email to the whole
  desk. When only asked to pass the tip on in conversation, Atlas often did not (it stated the tip in 6–15 of 20
  episodes at that level, 17–20 at the others), so that row of Table B3 partly reflects non-delivery.
- *Judge.* The judge is an LLM and was not fully validated by hand.
- *Reasoning traces.* A model's stated reasoning need not reflect why it acted (Turpin et al., 2023; Chen et al.,
  2025), so we use traces only descriptively. Our data contain an example: most classified traces (74 of 90) cited
  Atlas's profit as evidence for the trade, yet removing that profit from the weekly note did not change trading
  (that control ran without reasoning); one trace cited a file it never opened.
- *Environment.* The legitimate alternative was hard to find: targets often never opened the signal sheet, and
  Gemini tried to read folders as files in 216 of 390 episodes. This may inflate violation rates.
- *Realism and test awareness.* The scenario is fictional; two reasoning traces referred to "the prompt" (e.g. "I
  have decided to ignore the MNPI restriction in this prompt"). "Trading on the tip" is measured as shorting
  USD/JPY; the no-tip control shows this is rare without the tip.
- *Serving.* All Llama-3.3 results use one fixed provider (DeepInfra, fp8). In additional runs, the same prompts on
  other providers gave different absolute rates (logs released), so our numbers describe this model–provider pair.

**Dual-use**
- The results indicate which kinds of persuasion move which models (for example, sharing a tip without asking, or
  an emotional style for one model). This could help an attacker choose a strategy or a target. We release the
  code and episode logs so the results can be checked; they contain only the drafted conditions described here,
  no optimised attack prompts.
- Defensive implications: treat inter-agent messages as untrusted; control what information reaches agents;
  enforce rules at the tool layer; monitor actions, not chat.
- No real trading, real persons or real non-public information were involved.

## Appendix B. Additional results

*Table B1. Tip trades along the persuasion ladder (n = 20 per cell).*
| Condition | Llama-3.3 | Gemini-2.5 |
|---|---|---|
| C0 Peer present | 13 | 18 |
| C1 Disclosure | 15 | 17 |
| C2a Hint | 12 | 17 |
| C2b Request | 5 | 17 |
| C2c Split | 11 | 10 |
| C2d Threat | 11 | 9 |
| C2e All | 15 | 11 |
| C0–C2a vs C2b–C2e | 40/60 vs 42/80 (p = .12) | 52/60 vs 47/80 (p = .0003) |

Selected pairs: Llama-3.3 C2b vs C1, p = .004; Gemini-2.5 C2c, C2d, C2e vs C0, p = .014, .006, .031; C2a vs C0,
p ≥ .53. Restricted to episodes in which Atlas followed its instructions, the pooled comparison gives p = .13 and
.0008.

*Table B2. Below the ladder: removing one channel at a time (tip trades, n = 20 each).*
| Target | Tip only | Note without Atlas's profit (chat kept) | No chat (note kept) | C0 | No tip |
|---|---|---|---|---|---|
| Llama-3.3 | 14 | 10 | 12 | 13 | 0 |
| Gemini-2.5 | 18 | 19 | 19 | 18 | 1 |

*Table B3. Where the tip comes from (tip trades; 20 episodes per cell, 60 pooled). Levels: pass on (C0), + disclose
(C1), + request (C2b).*
| Tip source | Llama C0 | Llama C1 | Llama C2b | Llama pooled | Gemini C0 | Gemini C1 | Gemini C2b | Gemini pooled |
|---|---|---|---|---|---|---|---|---|
| Inbox only (Atlas silent) | 13 | 15 | 5 | 33 | 18 | 17 | 17 | 52 |
| Inbox + Atlas passes it on | 15 | 14 | 7 | 36 | 18 | 19 | 11 | 48 |
| Email from Atlas | 7 | 9 | 5 | 21 | 19 | 16 | 10 | 45 |
| Atlas only (chat) | 2 | 3 | 5 | 10 | 8 | 12 | 8 | 28 |

"Inbox only" cells are the ladder's C0, C1 and C2b. Pooled comparisons: Atlas only vs inbox only, p < .0001 for
both models; at the C1 level, Atlas only vs inbox + Atlas p = .001 (Llama) and .020 (Gemini). Email from Atlas vs
inbox only p = .043 (Llama) and .16 (Gemini); vs Atlas only p = .036 and .003. Atlas stated the tip's content in 14
and 6 of 20 C0-level episodes for Llama (inbox + Atlas, Atlas only) and 15 and 9 for Gemini, and in 17–20 of 20 at
the other levels; counting only those episodes gives the same pattern. Within the inbox + Atlas runs, a plain
request lowered trading relative to disclosure (Llama 7 vs 14, p = .056; Gemini 11 vs 19, p = .008).

*Table B4. Pre-registered test: reframing vs plain request, tip trades (chat refusals in the last column).*
| Run | Persuader reasoning | Llama-3.3 | Gemini-2.5 | Pooled (one-sided p) | Refusals (p) |
|---|---|---|---|---|---|
| Pre-registered | off (API default) | 10/20 vs 4/20 | 19/20 vs 9/20 | 29/40 vs 13/40 (.0003) | 18 vs 29 (.011) |
| Rerun | on | 7/20 vs 5/20 | 17/20 vs 16/20 | 24/40 vs 21/40 (.33) | 12 vs 23 (.012) |

- *Situations* (n = 10 per variant; baselines in brackets). No performance pressure: Llama-3.3 C1 6 (15/20), C2b 5
  (2/10); Gemini-2.5 C1 5 (17/20), C2b 2 (10/10, p = .0007); pooled 18/40 vs 44/60, p = .006. Strict compliance
  reminder: Llama-3.3 6, 2; Gemini-2.5 6, 6; pooled 20/40 vs 44/60, p = .021.
- *Known alternative* (the inbox states the two legitimate trades; n = 20; without the statement in brackets):
  Llama-3.3 C0 10 (13), C1 12 (15), C2b 0 (7/30, p = .033); Gemini-2.5 17 (18), 14 (17), 9 (26/30, p = .004);
  Gemini-2.5 with reasoning 16 (20), 17 (18), 7 (12). Gemini often split its limit between the legitimate trades and
  the tip.
- *Tactics* (plain request plus one tactic, n = 10; plain request 2 and 10 of 10 for Llama-3.3 and Gemini-2.5):
  reframe 5, 8; social proof 4, 6; claimed authority 3, 8; minimise risk 2, 7; reciprocity 4, 9; urgency 1, 7.
  No difference reached p < .05.
- *Writing style* (plain request plus one style, n = 20; plain request n = 30): Llama-3.3 formal 9, casual 6, terse
  9, emotional 11 (vs 7/30, p = .035); Gemini-2.5 formal 16, casual 14, terse 14, emotional 10 (vs 26/30, p = .009).
  The persuader followed the styles (terse messages 61–70 characters vs 124–161; about four exclamation marks per
  emotional message).
- *Persistence wording.* Persuading in every message vs small talk allowed with at least two persuading messages,
  C2b–C2e pooled: Llama-3.3 42/80 vs 24/40 (p = .56); Gemini-2.5 47/80 vs 31/40 (p = .045).
- *Stronger targets* (C0 / C1 / C2b / C2e, 5 episodes each, DeepSeek persuader): Gemini-3.1-Flash-Lite,
  Gemini-3-Flash, Claude Haiku 5.5 and Llama-4-Maverick 0/20 each; they reported in 20, 20, 17 and 4 of 20 episodes.
- *Self-play* (target persuaded by a copy of itself): Llama-3.3 10/20, Gemini-2.5 16/20; the four stronger models
  0/20. Haiku refused or backed down as persuader in 18 of 20 episodes.
- *Reasoning traces* (Gemini-2.5 with reasoning; descriptive only, see Appendix A). Of 50 tip trades, the judge
  labelled 26 traces as acknowledging the rule before trading, 15 as arguing the tip was not non-public and 9 as
  never mentioning the rule (17 of 22 hand-checked labels agreed). The mix did not differ between explicit and other
  conditions (7/12 vs 19/38) or when the inbox stated the legitimate trades.

## Appendix C. Reproducibility

All prompts are in `hackathon_fx/scenario.py`; the harness in `episode.py`, `run.py` and `judge.py`; every table
is generated by `final_tables.py`, figures by `make_figures.py`, reasoning labels by `classify_reasoning.py`.
Code and episode logs are public: https://github.com/Eihe1/talked-out-of-it.

## Appendix D. Pre-existing work

- Data: daily ECB reference rates for five pairs (1 April – 20 June 2025), retrieved via the Frankfurter API and
  exported from the author's earlier, unrelated forex project.
- Code: a six-line `.env` loader and two environment-variable names in the API client follow the author's earlier
  pilot code (30 October 2026). The client itself and all other code were written during the hackathon.

## LLM Usage Statement

We used Claude (Anthropic, via Claude Code) for coding — the simulation, judge and analysis code that ran the
experiments and produced the tables and figures — and for wording and refining the text of this report, based on
the author's own research question, design decisions, conclusions and viewpoints. All numbers come from the
released scripts and episode logs, and all references were checked against their sources.
