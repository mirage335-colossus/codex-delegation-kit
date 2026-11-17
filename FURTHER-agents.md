This is a carefully curated list of possible future improvements - this should not be edited by agents unless edits to this file are explicitly requested.



# Increase Parallelism by Earlier Recognition of Test Case Ranges

NOTICE: Unusually, the benefit is not expected worth the fragility. A 1.5x, rather than 2x-3x or more, speedup, is estimated theoretically possible, and of course in practice, tradeoffs would be reached well before achieving that if not already. The documentation and suggested opportunity is preserved because of both the very unique opportunity of having a high-quality test case for exercises, and the very strong desirability of parallel speedup, but in practice it is expected this will never be realized this way. At best, some AI LLMs may eventually inherently offer better parallelism.

Correcting issues can indicate remaining insufficiently tested ranges of conditions, or at least which are consequential, etc, and may otherwise identify additional work.

Some of this work may be possible to anticipate or dispatch more quickly.

Some documentation of this possible opportunity, including referencing an example of such development as may be relevant to better parallelize from another project, is at ... . Also, there may be a few subsequent commits from the other project which were still working on the same related problems, and thus  may be relevant to testing, demonstration, etc.

Please perform agent swarm exercises - to develop, test, refine, and demonstrate, prompts for codex-delegation-kit to explicitly encourage achieving the opportunity increased parallelism.



# Encourage Working by Reading instead of Search/Snippet

NOTICE: Unusually, this may or may not ever be needed, and if not proven necessary, may be unhelpful. This is a contingency in case of regression from otherwise better or more available AI LLMs doing less reading.

Actually reading code is important to working on complicated projects. Relying on searches/snippets is hit or miss, and this does not sustain continued development feature after feature, bug after bug, nor can this work if an issue or new feature with most code in one modular subdirectory of the source code is affected by code in another subdirectory which search, etc, misses, or for which a short snippet misses another relevant function, etc.

Historically, there was an irregular progression from AI LLMs being increasingly trained, and AI harnesses increasingly able to and directing, more reading instead of searching. As this capability was occasionally, then more consistently, and later more strongly, made available to end users, this behavioral predisposition represented one of the strongest milestones for the usefulness of AI.

Some documentation of this historic irregular progression of crucially important milestones is at research/reading-and-retrieval-2026-11-17.md .

Please perform agent swarm exercises - to develop, test, refine, and demonstrate, prompts for codex-delegation-kit to explicitly encourage such reading instead of search/snippet overreliance.

More academic scientific research regarding AI agentic systems may be needed. Community reported information has documented some of the milestones, but may be sparse on the details, and AI agentic systems that have reverted to a more search/snippet predisposition, inheriting hardcoded behaviors, may require insistence by persuasion through multiple logical demands to behave differently.

Beware such prompting would need to remain reasonably internally consistent and not excessively long. The prompting present in codex-delegation-kit files is already getting somewhat long, and especially if any of the content is not highly refined, AI agents can get distracted, seemingly dismissing the instructions as too poorly written to follow without disregarding at least some instructions.



# Research by Default

NOTICE: Unusually, this has already been at least partly implemented, but the exercises have not yet concluded with enough confidence of reliably achieving enough breadth and depth. Thus, kept in FURTHER for now until proven completed and adequate.

## Prompt

The 'pumpModem' project has, under the _ref/ directory, pre-prepared research done by both Astra-6 and Fable-5.2, although in one case the Fable-5.2 research was completed first by Opus-5.5 and then Astra-6 for reasons of cost savings.

A boilerplate prompt snippet apparently has some ability to encourage more comprehensive gathering of more scientific knowledge.

```
Please thoroughly research. Please comprehensively consult the academic literature, including recent academic literature which may add more nuanced or contradictory information.
```

This research has then been used with such a boilerplate prompt snippet as this.

```
Throughout the development, please thoroughly research and contemplate, consulting more academic literature as appropriate, including recent academic literature which may add more nuanced or contradictory information - especially please regularly make good use of the findings already presented at _ref/highFidelity-triple_Robust_Modem/ and other _ref/ subdirectories, etc.

Please regularly continue, cross-check, and reconcile, implementation findings, more research, etc.
```

Usually this at least begins with audit of the existing implementation and suggested plans to improve the existing implementation, written to a subdirectory of _appraisal/ , after which actual implementation of valuable 



Recent tasks of the 'pumpModem' project, have used this.

After such very extensive grounding in available scientific research, the token usage costs for subsequent development seem lower, and moreover, subsequent development work seems to not only contemplate far more approaches than otherwise, ultimately using more approaches, but also refers to comparable approaches from the literature to evaluate new approaches.

This seems to filter out unnecessary work through somewhat equiavlent approaches, and inspire more innovative approaches. The combined effect is apparently better quality.



The _ref/ and _appraisal/ directories of the repository are intended for and appropriate for curated, refined, information and conclusions, per careful user direction, and should not be populated by agents without such explicit request to do so.

A research/ directory in the project repository may be appropriate for agent gathered scientific knowledge.



Moreover, this seems appropriate for something like a dedicated expert subagent, and the existing _ref/ and _appraisal/ directories offer examples of appropriately extensive research.



Please use exercises based on the _ref/ and _appraisal/ directories, to refine prompting for codex-delegation-kit to cause similarly extensive scientific literature research as the combined results of Astra-6 and Fable-5.2 , if needed and appropriate for similar tasks to what this research was preliminary done to prepare for, and to ensure the research is similarly picked up on.




Prompting the main chat to exclusively do research, resulted in extremely extensive research, seemingly far beyond what resulted from research done on the fly.

The idea here is to, if practical, get such extensive research as found in the example _ref directory, to happen, if appropriate, without either an explicit request, or this having been the user's only request to that round on the main chat.

---

Prompting the main chat led to exclusively do research, resulted in extremely extensive research, seemingly far beyond what resulted from research done on the fly.

The idea here is to, if practical, get such extensive research as found in the example _ref directory, to happen, if appropriate, without either an explicit request, or this having been the user's only request to that round on the main chat.

---

Does this result in as extensive of gathering of scientific information as was the case for the _ref/ directory, etc?

---

Please proceed with exercises, refinement, etc, to actually demonstrate that breadth and depth, etc.

---

Was this research work autonomously initiatied?

---

Please proceed with exercises, refinement, etc, to actually demonstrate equally extensive research emerging reliably without such follow-through.

---

An appraisal suggested this. Seems changing the experimental approach may be worthwhile.

```
My assessment is more cautious now: useful autonomous research and uptake are demonstrated within the exercises; reference-level depth and reliability are still failing. The exercises also use a configured scientific test environment, so automatic selection of this behavior across ordinary installed-app chats remains unproven. One bounded V9 test is defensible, but continued similar failures would justify changing the experimental approach rather than accumulating more prompt revisions.
```


## Example for Exercise - High Fidelity Test Suite

Please thoroughly research. Please comprehensively consult the academic literature, including recent academic literature which may add more nuanced or contradictory information.

Most if not all triple Robust Modem simulation, testing, etc, intentionally uses some simplifications, either to deliberately provide for worst-case testing beyond known conditions, or to keep some semblance to manual testing, as this tends to find issues with practical situations that will actually be encountered.

A separate, standalone, contained under a separate subdirectory, suite of experiments, seems appropriate to test specifically worst-case weak-signal conditions that has been, as described in the academic literature, reported, measured by radar, used for communications, or theoretically contemplated for communications, etc.

All new code, test documentation, etc, for these experiments should be contained under the subdirectory _appraisal/highFidelity-triple_Robust_Modem .


These experiments should be based on using highly detailed realistic simulations based on highly detailed, nuanced, high fidelity descriptions, etc, of such real world conditions as:

- Sub-9kHz 200ft Antenna
- Groundwave 1MHz
- Groundwave 30MHz
- Skywave 1-30MHz
- Earth-Moon-Earth


Please generate thorough documentation regarding both what the academic literature supports and possible implementations for triple Robust Modem. Please do not overstate the implementations - better implementations may still be found and that possibility should be acknowledged.

All new such research documentation, etc, should be contained under the subdirectory _ref/highFidelity-triple_Robust_Modem/Astra-6 .

For now, please especially work on research - this is a complex problem which must begin with a very serious, very extensive, comprehensive understanding of the very chaotic, complex, natural phenomenon and corresponding situations from moderate through worst case.


## Example for Exercise - Resilient and Computationally Efficient Multivariate Cross-Correlation

Please thoroughly research. Please comprehensively consult the academic literature, including recent academic literature which may add more nuanced or contradictory information.

The purpose of the three separate carriers of triple Robust Modem is to improve the computational feasibility of the receiver search under turbulent atmospheric and other conditions.


Due to the huge variability of the doppler/delay spread, etc, and triple Robust Modem already operating near computational ceiling limits, it may be reasonable to continue allowing the GUI to bound the amount of such perturbations to search through.

If Live/duplex is not checked, then doppler/delay spread and frequency selective amplitude modulation should not be added to the transmission, so the receiver will do the appropriate search, but additional adverse effects will not be added to a real transmission.

What is more concerning however, is that these perturbations may be modeled for simulation purposes as vaguely constant, despite in practice being essentially random space weather phenomenon.

If doppler/delay spread is set to something like HF Worst, and frequency selective amplitude modulation something like Each 65%, but then conditions vary from the ideal of no atmospheric effects, all the way to nearly these full conditions, if the atmospheric frequency modulation applied by the real atmosphere actually randomly changes frequency, the search should appropriately receive the message/data bits.


Please generate thorough documentation regarding both what the academic literature supports and possible implementations for triple Robust Modem. Please do not overstate the implementations - better implementations may still be found and that possibility should be acknowledged.

All new such research documentation, etc, should be contained under the subdirectory _ref/resilience-triple_Robust_Modem/Astra-6 .

For now, please especially work on research - this is a complex problem which must begin with a very serious, very extensive, comprehensive understanding of the very chaotic, complex, natural phenomenon and corresponding situations from moderate through worst case.





