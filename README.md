# Heat, Households, and Human Development: Understanding the Behavioral and Developmental Consequences of Rising Temperatures

Andrés Felipe Camacho

A data story based on Cuartas & Camacho (2025) and Cuartas et al. (2025)

Global temperatures are rising rapidly: 2024 was the warmest year on record and the first to exceed ~1.5 °C above the pre-industrial average, capping a decade of unprecedented heat according to WMO and Copernicus analyses.  ￼ This research project links household microdata from UNICEF’s Multiple Indicator Cluster Surveys (MICS) with gridded climate reanalysis from ERA5-Land (monthly aggregates, 1950–present) to examine how heat translates into family life and child outcomes.  ￼ We focus on two dimensions with direct human-development implications: (1) parenting behaviors—e.g., violent punishment and psychological aggression—and (2) early childhood development, measured via MICS’ ECDI.


1) Temperature trends and anomalies

Raw temperature series reveal strong seasonality. To make warming visible and comparable across places, I use anomalies relative to a 30-year climatological baseline (1991–2020).
	•	Figure 1 — Monthly mean temperature over time
![Figure 1: Temperature time series](gr1temperature_time_series.jpeg)
	•	Figure 2 — 3-month rolling heat anomaly
![Figure 2: Rolling anomalies](gr2rolling3m_anomalies.jpeg)
	•	Figure 3 — Seasonal anomaly patterns by month
![Figure 3: Monthly anomaly heatmap](gr3heat_map_moth_anomalies.jpeg)
	•	Figure 4 — Global context: spatial temperature anomalies
![Figure 4: World anomalies map](gr4worldmapanomalies.jpeg)

Takeaway. The anomaly view highlights that recent years show systematic positive deviations from the long-term norm and that these deviations are not isolated weather blips but part of a broader warming signal.

⸻

2) Data and linkage: ERA5-Land × MICS

I merge ERA5-Land monthly maximum temperature with MICS geocoded clusters to align children and households to the climate they experience. Visuals below show the distribution of temperature exposure in the analytic countries and a couple of country snapshots.
	•	Figure 5 — Temperature distributions by country
![Figure 5: Exposure distributions](gr8TempDistrib.jpeg)
(Countries in the sample include Georgia, The Gambia, Madagascar, Malawi, Sierra Leone, and the State of Palestine.)
	•	Figure 5a — Georgia snapshot
![Figure 5a: Georgia](gr5aGeorgia.jpeg)
	•	Figure 5b — Madagascar snapshot
![Figure 5b: Madagascar](gr5bMadagascar.jpeg)

Why this design matters. The formal studies compare children within the same subnational regions and interview months, exploiting hotter-than-usual vs typical local temperatures rather than cross-country differences. That’s the logic behind the fixed-effects models: hold constant the “usual” climate in each place/season and ask what happens when recent heat is unusually high.

⸻

3) Measures: outcomes and constructions

Discipline & aggression (MICS discipline module)

From the MICS discipline module, the papers construct binary indicators for:
	•	Physical punishment
	•	Severe physical punishment
	•	Psychological aggression
	•	Non-violent discipline

These are coded as recent use (past month) binary outcomes for each child–caregiver dyad.
In the pooled sample used in the parenting paper, prevalence rates are high: physical punishment ~64%, severe physical punishment ~56%, psychological aggression ~80%, non-violent discipline ~88%.

Early Childhood Development (ECDI)

ECDI is a parent-reported, standardized early development indicator used in MICS, and the papers analyze the binary outcome “ECDI on track”. The development paper models the probability of being on track by temperature bins and in continuous/binscatter form, with Figure 3 showing predicted margins for unadjusted vs adjusted (FE) models.

⸻

4) Identification sketch and model equations

Both papers apply fixed-effects designs on geocoded, time-stamped data.

Linear FE model (continuous temperature — recent or cumulative):
Y_{ict} \;=\; \beta \cdot \mathrm{Temp}{ict} \;+\; X_i \theta \;+\; \tau_c \;+\; \phi_t \;+\; \varepsilon{ict}
	•	Y_{ict}: outcome for child i in cluster/region c at time t (discipline or ECDI on-track).
	•	\mathrm{Temp}_{ict}: recent or cumulative mean maximum temperature exposure.
	•	X_i: covariates (child age/sex, maternal education, wealth, area, and atmospheric controls in ECDI paper).
	•	\tau_c: subnational region (within-country) fixed effects; \phi_t: month-year fixed effects.
This design holds constant the “typical climate” of places and seasons; remaining variation is the unexpected local heat at interview timing.

Binned (non-linear) specification:
Y_{ict} \;=\; \sum_{b} \beta_b \cdot \mathbf{1}\{\mathrm{Temp}_{ict}\in \text{bin}b\} \;+\; X_i \theta \;+\; \tau_c \;+\; \phi_t \;+\; \varepsilon{ict}
The ECDI paper uses 1 °C bins with <26 °C as the reference category, enabling non-linear responses (e.g., sharper declines beyond ~30–32 °C).

⸻

5) Results: heat and parenting behavior
	•	Figure 6 — Probability of psychological aggression vs temperature (binned)
![Figure 6: Aggression vs temperature](gr6AggressionTemp.jpeg)

Visual binscatter evidence shows a strong positive association between heat and both severe physical punishment and psychological aggression; the relations are essentially linear in the temperature range observed, while physical punishment (all severities combined) and non-violent discipline show little change.

Regression magnitudes (per +1 SD ≈ +3.9 °C in recent mean max temperature):
	•	Severe physical punishment: +4 to +8 percentage points (preferred FE models ~+7.6 pp).
	•	Psychological aggression: +3 to +4 pp (preferred FE models ~+4.2 pp).
No robust effects for milder physical punishment or non-violent discipline.

Interpretation. Heat loads increase physiological stress and impair emotion regulation, raising the propensity for harsh responses during caregiving. The formal paper documents consistency across linear and binned specs and sensitivity checks.

⸻

6) Results: heat and early childhood development
	•	Figure 7 — Probability of “ECDI on track” vs temperature (bins + FE)
![Figure 7: ECDI vs temperature](gr7ECDITemp.jpeg)

Predicted margins decline as temperature bins rise, with adjusted (FE) estimates showing a clearer drop beyond ~30–32 °C compared to the unadjusted series. The bins are defined with <26 °C as reference, and the figure overlays both unadjusted and adjusted curves for transparency.

The continuous/binscatter specification shows the same pattern: as average maximum temperature from birth to interview increases, ECDI scores (and on-track probabilities) fall.

Heterogeneity. The development paper explores differences by wealth, urban vs rural, and water/sanitation access—key moderators for adaptation and exposure.

⸻

7) How to read these figures together

Sections 5–6 point to a coherent mechanism: heat increases household stress and reduces the quality of caregiving environments while directly burdening children’s physiology and sleep, resulting in worse developmental outcomes—especially as temperatures move into the 30–35 °C range for longer periods. The econometric designs focus on within-place variation to avoid confounding from baseline climatic differences and seasonality.

⸻

8) Notes on the sample

The pooled analytic sample in these studies includes ≈19,600 children living in 3,600+ clusters across Georgia, The Gambia, Madagascar, Malawi, Sierra Leone, and the State of Palestine (MICS 2017–2020).

⸻

9) Methods appendix (concise)
	•	ERA5-Land (monthly aggregates) linked to geocoded MICS clusters. Models include region FE and month-year FE to absorb baseline climatic conditions and seasonality; remaining variation is unexpected local heat at interview timing.
	•	ECDI is analyzed as on-track probability; discipline variables are binary “any use” in the last month.
	•	The development paper visualizes bins and binscatter (continuous) with the <26 °C reference.

⸻

10) References to the companion papers
	•	Cuartas, J., & Camacho, A. (2025). Heat and Violent Child Punishment at Home (Psychology of Violence). Evidence of increased severe physical punishment and psychological aggression with higher recent heat exposure, consistent across linear and binned specifications.
	•	Cuartas, J., Balza, L. H., Camacho, A., & Gómez-Parra, N. (2025). Ambient Heat and Early Childhood Development: A Cross-National Analysis. ECDI on-track declines with higher temperature bins; bins defined with <26 °C as reference; results robust to specifications and continuous/binscatter plots.

⸻

11) What can we do next with this merged dataset?
	•	Decompose exposure: Contrast short heat shocks (e.g., prior month) vs cumulative exposure (birth→interview).
	•	Moderators: Stratify by wealth, urbanicity, water/sanitation to identify where adaptation policies are most needed.
	•	Mechanisms: Add proxies for caregiver stress or illness episodes; test if they mediate heat → aggression or heat → ECDI.
	•	Place features: Merge land cover/greenness (MODIS) or nighttime lights (VIIRS) to measure urban heat islands and infrastructure buffers.
	•	Temporal design: Evaluate seasonal thresholds (e.g., >32 °C months) and lag structures.
	•	Policy targeting: Simulate cooling access and safe water expansions to estimate potential reductions in harsh discipline and ECDI losses.