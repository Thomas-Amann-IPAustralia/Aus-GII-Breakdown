# Glossary

Terms used in this project, in plain English. Add a term the first time the analysis uses it.

## The IP system

| Term | Meaning |
|---|---|
| **IP right** | A legal right over an idea, brand or design, granted by IP Australia: a patent, trade mark, design or plant breeder's right. In the `rights` lens, one row is one right. |
| **Patent** | Protection for an invention: up to 20 years (25 for some medicines), in return for publishing how it works. |
| **Standard patent** | The usual patent, examined in full before it is granted. |
| **Provisional application** | A cheap placeholder that secures a filing date for 12 months. It is never granted itself; the applicant must follow it with a full application. |
| **Innovation patent** | A cheaper, shorter (8-year) patent for smaller steps. It was phased out: no new ones could be filed after 25 August 2021. |
| **Trade mark** | Protection for a brand (a name, logo, sound and so on) used for particular goods or services. It can be renewed indefinitely. |
| **Design** | Protection for how a product looks (its shape, pattern or ornamentation), for up to 10 years. |
| **Plant breeder's right (PBR)** | Protection for a new plant variety. |
| **Application, registration, grant** | A right starts as an application. If it passes examination it is *registered* (trade marks, designs) or *granted* (patents). |
| **Lapse** | A right ends early because the owner stopped paying its renewal fees. Lapse is a signal that the owner judged the right no longer worth its cost. |
| **Priority date** | The earliest filing date the application can claim, which may be from an earlier filing overseas. |
| **Attorney or agent** | A professional who files for the applicant. Applicants who file without one are *self-filers*. |
| **IPC class** | The International Patent Classification: a code for the technology a patent covers (for example `A61K`, medical preparations). |
| **WIPO technology field** | One of 35 broad technology areas that WIPO builds from IPC classes. |
| **Nice class** | One of the 45 classes of goods and services a trade mark is registered for (for example class 35, advertising and business services). |
| **Locarno class** | The international classification for designs. |
| **PCT, Madrid, Hague** | International filing routes, for patents, trade marks and designs respectively. |
| **IP RAPID** | IP Australia's open data on every Australian IP right, updated weekly. The `rights` lens is built from it. |
| **IPLORD** | IP Australia's longitudinal research dataset, which links IP applicants to businesses. |

## Businesses and places

| Term | Meaning |
|---|---|
| **ABN** | Australian Business Number: the identifier that joins IP Australia's data to the business registers, the R&D Tax Incentive, AusTender and the tax data. In the `firms` lens, one row is one ABN. |
| **ABR** | The Australian Business Register, which holds every ABN. |
| **ASIC** | The Australian Securities and Investments Commission, which registers companies. |
| **GST-registered** | Registered for the Goods and Services Tax. This is compulsory at a turnover of $75,000 or more, so it is used as a rough marker of an actively trading business. |
| **R&D Tax Incentive (RDTI)** | A tax offset for research and development. The ATO publishes who claimed it and how much they spent. |
| **AusTender** | The register of Australian Government contracts. |
| **Tax transparency reports** | The ATO's published income and tax of large entities: total income of $100m or more ($200m for Australian-owned private companies until 2021-22). |
| **Postal area (POA)** | The ABS's version of a postcode area, which can be matched to Census and other data. In the `regions` lens, one row is one postal area. |
| **SA2** | Statistical Area Level 2: an ABS area of roughly 3,000 to 25,000 people. |
| **Remoteness area** | The ABS's five classes of remoteness, from Major Cities to Very Remote. |
| **SEIFA** | The ABS's Socio-Economic Indexes for Areas, built from the Census. There are four indexes:<br>- **IRSAD**: advantage and disadvantage combined.<br>- **IRSD**: disadvantage only.<br>- **IER**: economic resources.<br>- **IEO**: education and occupation.<br>A *decile* of 1 is the most disadvantaged tenth of areas, and 10 the most advantaged. |
| **Financial year (FY)** | July to June, named by the year it ends: FY2026 is July 2025 to June 2026. |

## The analysis

| Term | Meaning |
|---|---|
| **Corpus** | All the data collected for this project (`docs/catalogue.md`). |
| **Lens** | One analysis-ready table with one row per thing being studied: a right, a firm, a place, or a country in a year. The EDA works one lens at a time. |
| **Unit of analysis** | What one row stands for. Counting or averaging only makes sense once this is clear. |
| **EDA** | Exploratory data analysis: getting to know the data before trying to answer questions with it. |
| **Univariate, bivariate, multivariate** | Looking at one variable at a time, at two together, or at several together. These are the EDA's three stages. |
| **Distribution** | How the values of a variable are spread out: which values are common and which are rare. |
| **Mean and median** | The average, and the middle value. When a few very large values pull the mean up, the median is the better guide to a "typical" value. |
| **Skew** | Lopsidedness. *Right-skewed* data has a long tail of large values, as with most counts of IP filings, where a few firms file thousands of applications and most file one. |
| **Outlier** | A value far from the rest. Here this follows the box-plot rule: more than 1.5 times the middle half's width beyond the middle half. An outlier is not necessarily an error. |
| **Box plot** | A chart of the middle half of the values (the box), the median (the line inside it) and the outliers (the dots). |
| **KDE** | A smoothed outline of a histogram. |
| **Log scale** | An axis where each step is ten times the last, so very small and very large values fit on one chart. |
| **Binning artefact** | A peak or gap that appears only because of how a histogram's bars were drawn. It is checked by redrawing with different bar widths. |
| **Correlation (Pearson r)** | A number from -1 to 1 for how closely two variables follow a straight line. 0 means no straight-line link. |
| **Spearman rho** | Like r, but it asks only whether one variable rises as the other rises, in any shape. It is robust to extreme values. |
| **LOWESS** | A smooth trend line that follows the data without assuming it is straight. |
| **p-value** | How surprising a result would be if there were no real link. With very large samples, tiny and unimportant links still get tiny p-values, so the size of the link matters more. |
| **Effect size** | How big a difference or link is, as opposed to whether it is "significant". |
| **95% interval** | The range that plausibly contains the true value. Rates use the Wilson interval, which behaves well for small groups and rates near 0% or 100%. |
| **Mann-Whitney, Kruskal-Wallis** | Tests of whether groups differ (two groups, or more). They work on ranks, so a few extreme values can't drive the result. |
| **Confounder** | A third factor that drives two things and makes them look linked. For example, firm size drives both R&D and patenting. |
| **Partial correlation** | The link between two variables after removing what one or more other variables explain. |
| **PCA** | Principal component analysis: it combines many related variables into a few summary measures. |
| **VIF** | Variance inflation factor: how far a variable can be predicted from the others. Above about 5 to 10, the variables are repeating one another. |
| **Clustering (k-means)** | Sorting rows into groups that look alike across several variables. The *silhouette* score (-1 to 1) says how well separated the groups are. |
| **Spurious correlation** | A link with no real connection behind it. It is common between time series that all trend upward over the same years. |
| **Strength of evidence** | Every observation is labelled with one of four strengths, from the research goal:<br>- **descriptive**: what the data shows;<br>- **observational**: a link that may have other explanations;<br>- **causal**: an effect, shown by a suitable design;<br>- **projected**: an estimate of the future. |
| **Additionality** | What happens *because of* a right or an intervention, compared with what would have happened anyway. It is the research goal's central test. |
| **Natural experiment** | A change (a new fee or rule, say) that affects some people and not others, for reasons unrelated to their outcomes. Comparing the two groups comes close to an experiment. |
