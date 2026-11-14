This is a carefully curated list of possible future improvements - this should not be edited by agents unless edits to this file are explicitly requested.




# Research by Default

NOTICE: Unusually, this has already been done, but is kept in FURTHER for now until proven completed and adequate.

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





