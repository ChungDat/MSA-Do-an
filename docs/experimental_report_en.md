# Experimental Report: Exploratory Factor Analysis on OCEAN and Sample Data

**Generated:** July 9, 2026  
**Application:** Factor Analysis Application with Optional Ollama-Based Factor Naming

## 1. Objective

This experiment evaluates the application's exploratory factor analysis (EFA)
pipeline on two datasets:

1. a large, real-world Big Five personality dataset (`OCEAN_app.csv`); and
2. a small local demonstration dataset (`sample.csv`).

The experiment focuses on data suitability, automatic factor retention using
the Kaiser criterion, factor loadings, explained variance, and the
interpretability and limitations of the extracted factors.

## 2. Dataset Description

### 2.1 OCEAN dataset

#### Source and collection

The original data came from the
[Open-Source Psychometrics Project raw-data repository](https://openpsychometrics.org/_rawdata/).
The source describes it as responses to a Big Five personality test constructed
from International Personality Item Pool (IPIP) items. The test contains 50
Likert-rated statements and was completed by 19,719 respondents. The data were
collected through an interactive online test around 2012 and released on May 18,
2014. Participants were informed about research use and confirmed consent and
response accuracy.

The item wording and variable definitions were cross-checked against the
[Big Five dataset documentation](https://rkabacoff.github.io/qacr/reference/big5.html).
The instrument is based on the Big Five factor markers discussed by
[Goldberg (1992)](https://doi.org/10.1037/1040-3590.4.1.26).

The original file had 19,719 rows and 57 columns: seven demographic or technical
variables (`race`, `age`, `engnat`, `gender`, `hand`, `source`, and `country`)
and 50 personality items. For compatibility with the application, the
experimental file retained only the 50 numeric personality items. One row
containing a response of `0` was removed because valid item responses range from
1 to 5.

The resulting `OCEAN_app.csv` file therefore contains:

- **19,718 rows** (respondents);
- **50 numeric columns** (personality items);
- no missing values; and
- values from **1 to 5**, where 1 means disagree, 3 means neutral, and 5 means
  agree.

#### Meaning of the original non-item columns

| Column | Meaning | Used in EFA |
|---|---|---|
| `race` | Self-reported race category | No |
| `age` | Age in years | No |
| `engnat` | Whether English is the respondent's native language | No |
| `gender` | Self-reported gender | No |
| `hand` | Writing hand: left, right, or both | No |
| `source` | Technical/source indicator from data collection | No |
| `country` | Country represented by an ISO country code | No |

#### Meaning of the 50 analyzed columns

The prefix identifies the intended domain: `E` = Extraversion, `N` =
Neuroticism, `A` = Agreeableness, `C` = Conscientiousness, and `O` = Openness
to Experience. “Reverse” marks negatively worded items whose expected loading
has the opposite sign.

| Column | Questionnaire statement | Expected domain/direction |
|---|---|---|
| `E1` | I am the life of the party. | Extraversion |
| `E2` | I do not talk a lot. | Extraversion, reverse |
| `E3` | I feel comfortable around people. | Extraversion |
| `E4` | I keep in the background. | Extraversion, reverse |
| `E5` | I start conversations. | Extraversion |
| `E6` | I have little to say. | Extraversion, reverse |
| `E7` | I talk to many different people at parties. | Extraversion |
| `E8` | I do not like to draw attention to myself. | Extraversion, reverse |
| `E9` | I do not mind being the center of attention. | Extraversion |
| `E10` | I am quiet around strangers. | Extraversion, reverse |
| `N1` | I get stressed out easily. | Neuroticism |
| `N2` | I am relaxed most of the time. | Neuroticism, reverse |
| `N3` | I worry about things. | Neuroticism |
| `N4` | I seldom feel blue. | Neuroticism, reverse |
| `N5` | I am easily disturbed. | Neuroticism |
| `N6` | I get upset easily. | Neuroticism |
| `N7` | I change my mood a lot. | Neuroticism |
| `N8` | I have frequent mood swings. | Neuroticism |
| `N9` | I get irritated easily. | Neuroticism |
| `N10` | I often feel blue. | Neuroticism |
| `A1` | I feel little concern for others. | Agreeableness, reverse |
| `A2` | I am interested in people. | Agreeableness |
| `A3` | I insult people. | Agreeableness, reverse |
| `A4` | I sympathize with others' feelings. | Agreeableness |
| `A5` | I am not interested in other people's problems. | Agreeableness, reverse |
| `A6` | I have a soft heart. | Agreeableness |
| `A7` | I am not really interested in others. | Agreeableness, reverse |
| `A8` | I take time out for others. | Agreeableness |
| `A9` | I feel others' emotions. | Agreeableness |
| `A10` | I make people feel at ease. | Agreeableness |
| `C1` | I am always prepared. | Conscientiousness |
| `C2` | I leave my belongings around. | Conscientiousness, reverse |
| `C3` | I pay attention to details. | Conscientiousness |
| `C4` | I make a mess of things. | Conscientiousness, reverse |
| `C5` | I get chores done right away. | Conscientiousness |
| `C6` | I often forget to return things to their proper place. | Conscientiousness, reverse |
| `C7` | I like order. | Conscientiousness |
| `C8` | I shirk my duties. | Conscientiousness, reverse |
| `C9` | I follow a schedule. | Conscientiousness |
| `C10` | I am exacting in my work. | Conscientiousness |
| `O1` | I have a rich vocabulary. | Openness |
| `O2` | I have difficulty understanding abstract ideas. | Openness, reverse |
| `O3` | I have a vivid imagination. | Openness |
| `O4` | I am not interested in abstract ideas. | Openness, reverse |
| `O5` | I have excellent ideas. | Openness |
| `O6` | I do not have a good imagination. | Openness, reverse |
| `O7` | I am quick to understand things. | Openness |
| `O8` | I use difficult words. | Openness |
| `O9` | I spend time reflecting on things. | Openness |
| `O10` | I am full of ideas. | Openness |

### 2.2 Sample dataset

`sample.csv` is a small demonstration file stored in the project repository.
No external source or semantic codebook is provided, so it must be treated as
synthetic test data rather than a substantive research dataset.

It contains:

- **10 rows**;
- **3 numeric columns**;
- no missing values; and
- observed values from **1 to 10**.

| Column | Meaning |
|---|---|
| `A` | First synthetic numeric variable; no documented real-world meaning |
| `B` | Second synthetic numeric variable; no documented real-world meaning |
| `C` | Third synthetic numeric variable; no documented real-world meaning |

The means (standard deviations) are 5.50 (3.03) for A, 4.50 (2.17) for B, and
4.90 (2.77) for C.

## 3. Experimental Setup

### 3.1 Software environment

| Component | Version/configuration |
|---|---|
| Python | 3.12.13 |
| pandas | 3.0.3 |
| NumPy | 2.5.0 |
| scikit-learn | 1.5.2 |
| factor-analyzer | 0.5.1 |
| Extraction method | Minimum residual (`minres`) |
| Rotation | Varimax |
| Loading threshold | Absolute loading ≥ 0.40 |
| Automatic retention | Kaiser criterion: retain every eigenvalue > 1 |

### 3.2 Processing procedure

1. Load the comma-separated numeric file with pandas.
2. Reject empty files, missing values, and non-numeric columns.
3. Standardize every variable to zero mean and unit variance using
   `StandardScaler`.
4. Calculate eigenvalues from the correlation matrix.
5. Select all factors with eigenvalues strictly greater than 1 when the factor
   count is left blank.
6. Estimate the factor model using minimum residual extraction.
7. Apply orthogonal Varimax rotation.
8. Report variables whose absolute rotated loading is at least 0.40.

Kaiser–Meyer–Olkin (KMO) sampling adequacy and Bartlett's test of sphericity
were additionally calculated for this report. The application's optional Ollama
step was not used as a quantitative metric because the local Ollama service was
not available during the experiment. Factor names were therefore assigned from
the established OCEAN codebook and the observed loading patterns.

For OCEAN, two solutions were examined:

- the application's automatic **eight-factor** Kaiser solution; and
- a theory-guided **five-factor** solution matching the established OCEAN
  measurement model.

For `sample.csv`, the automatic one-factor solution was examined.

## 4. Experimental Results

### 4.1 OCEAN: suitability for factor analysis

| Diagnostic | Result | Interpretation |
|---|---:|---|
| KMO | 0.9099 | Excellent common-factor adequacy |
| Bartlett χ² | 376,656.90 | Correlations differ strongly from an identity matrix |
| Bartlett p-value | < 0.001 | Factor analysis is statistically justified |
| Eigenvalues > 1 | 8 | Kaiser retains eight factors |

The first eight eigenvalues were 8.0501, 4.6150, 3.7480, 3.5526, 2.7639,
1.5738, 1.3289, and 1.0540.

#### Automatic eight-factor solution

The eight-factor solution explained **44.86%** of total variance. The individual
rotated proportions were 10.05%, 9.16%, 7.55%, 6.69%, 4.51%, 3.59%, 1.87%,
and 1.44%.

The first four factors cleanly recovered Extraversion, Neuroticism,
Agreeableness, and Conscientiousness. Openness was divided between Factors 5
and 6. Factor 7 contained no item above the 0.40 reporting threshold, while
Factor 8 contained only N8 (loading 0.4608), which also loaded strongly on the
main Neuroticism factor.

This is evidence of **Kaiser over-extraction**. Although all eight retained
eigenvalues satisfy the application's strict rule, the last factors are weak
or not substantively distinct. An eigenvalue-only rule should therefore not be
treated as proof that every retained factor is interpretable.

#### Theory-guided five-factor solution

The five-factor solution explained **39.62%** of total variance:

| Factor | Interpretation | Variance | Items with \|loading\| ≥ 0.40 |
|---|---|---:|---|
| 1 | Extraversion | 9.98% | E1–E10 |
| 2 | Neuroticism | 9.22% | N1, N2, N3, N5–N10 |
| 3 | Agreeableness | 7.53% | A1–A9 |
| 4 | Conscientiousness | 6.55% | C1–C10 |
| 5 | Openness | 6.34% | O1–O8, O10 |

Selected rotated loadings are shown below. Negative values are expected for
reverse-worded items and support, rather than contradict, the interpretation.

| Factor | Strongest observed loadings |
|---|---|
| Extraversion | E7 = 0.7301, E5 = 0.7259, E4 = −0.7016, E2 = −0.6775, E1 = 0.6700 |
| Neuroticism | N6 = 0.7420, N8 = 0.7338, N9 = 0.7065, N7 = 0.7010, N1 = 0.6864 |
| Agreeableness | A4 = 0.7820, A9 = 0.6915, A5 = −0.6563, A7 = −0.6266, A6 = 0.5873 |
| Conscientiousness | C9 = 0.6249, C5 = 0.6227, C1 = 0.5986, C6 = −0.5832, C4 = −0.5561 |
| Openness | O10 = 0.6627, O1 = 0.5930, O5 = 0.5824, O2 = −0.5571, O8 = 0.5513 |

Three items did not reach the 0.40 reporting threshold in the five-factor
solution: N4, A10, and O9. This does not necessarily mean that they are invalid;
it means their loadings were weaker under this extraction, rotation, and
threshold combination.

#### OCEAN discussion

The results provide strong empirical support for the expected Big Five
structure. Each theory-guided factor is dominated by items from exactly one
OCEAN domain, and reverse-keyed statements generally have the expected negative
sign. The five-factor model is more parsimonious and interpretable than the
automatic eight-factor model, despite explaining 5.24 percentage points less
variance.

For this dataset, the recommended application setting is therefore **5
factors**, `minres` extraction, Varimax rotation, and a loading threshold of
0.40. The automatic Kaiser result should still be displayed because it follows
the configured rule, but the report should state that theoretical knowledge and
factor interpretability favor five factors.

### 4.2 Sample dataset results

| Diagnostic | Result | Interpretation |
|---|---:|---|
| KMO | 0.4649 | Poor sampling adequacy |
| Bartlett χ² | 10.4320 | Some non-zero correlation is present |
| Bartlett p-value | 0.0152 | Significant at the 0.05 level |
| Eigenvalues | 2.0833, 0.7716, 0.1451 | Kaiser retains one factor |

The single extracted factor explained **59.95%** of total variance. Its rotated
(effectively unrotated, because only one factor exists) loadings were:

| Variable | Loading |
|---|---:|
| B | −1.0274 |
| C | 0.7226 |
| A | −0.4698 |

#### Sample discussion

The negative loadings indicate that A and B vary in the opposite direction from
C along the extracted dimension. However, this factor should not be given a
substantive name because the variables have no documented meanings.

More importantly, the dataset has only 10 observations for three variables,
its KMO is below 0.50, and the loading for B exceeds 1 in absolute value. The
latter is a **Heywood-type improper solution** and indicates an unstable model.
Although Bartlett's test is significant and Kaiser returns one factor, those
facts do not overcome the very small sample and poor adequacy. This dataset is
useful for checking that the software runs, but it is not suitable for reliable
scientific inference.

## 5. Overall Conclusions

1. The application successfully processed both compatible numeric CSV files.
2. The OCEAN dataset is highly suitable for EFA and strongly recovers the
   expected five personality dimensions.
3. The Kaiser criterion retains eight OCEAN factors, but the last three factors
   are weak, fragmented, or redundant. A five-factor solution is better aligned
   with theory and has clearer simple structure.
4. The sample dataset produces one factor, but its poor KMO, tiny sample size,
   undocumented variable meanings, and improper loading make it unsuitable for
   substantive interpretation.
5. Future versions should consider reporting KMO and Bartlett diagnostics and
   supplementing Kaiser retention with a scree plot or parallel analysis.

## 6. Reproducibility Notes

- OCEAN input used by the application: `data/OCEAN_app.csv`
- Sample input: `data/sample.csv`
- OCEAN rows removed during cleaning: 1
- Random sampling: none
- Loading cutoff: 0.40
- All calculations were deterministic under the stated software environment.

## References

1. Open-Source Psychometrics Project. *Raw data from online personality tests.*
   https://openpsychometrics.org/_rawdata/
2. Kabacoff, R. *Big 5 Personality Factors—dataset documentation.*
   https://rkabacoff.github.io/qacr/reference/big5.html
3. Goldberg, L. R. (1992). The development of markers for the Big-Five factor
   structure. *Psychological Assessment, 4*(1), 26–42.
   https://doi.org/10.1037/1040-3590.4.1.26
