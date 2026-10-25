# 0008: Count a family's inventors from one publication, not from every name in the family

**Date:** 2026-10-25. **Whose:** Claude's, correcting its own loader (`google_patents_inventors`); the owner can
overturn it.

**Context.** The loader first counted every distinct harmonised inventor name across a family's publications. Its first
run, on 2026-10-25 once BigQuery access worked, gave 7,945,706 family–inventor rows for 1,548,276 families: 5.13
inventors per family. The docstring expected "a few" double counts. A check in BigQuery (12.1 GB scanned) found that the
publication naming the most inventors in each family names 2.67 on average (4,131,009 in all). So counting names across
the family nearly doubled the inventors. Google's harmonised names still differ between a family's publications (a
middle initial, a different transliteration of a Japanese, Chinese or Korean name), and a family has 9.2 publications on
average, so one person shows up under several names.

**Decision.** Each family's inventors are those of one representative publication: the one naming the most inventors,
then the one giving a country for the most of them, then the lowest publication number (so the choice is repeatable).
Countries are filled in from the rest of the family:
1. the representative publication's own country for the inventor;
2. else the country most often given to the same harmonised name elsewhere in the family;
3. else the country most often given to a name with the same first two words (surname and first given name), which
   catches "SMITH JOHN" against "SMITH JOHN A". This step only borrows a country; it never merges two people in the
   count.

`country_basis` records which step gave the country. The raw query's cache file is now named after a hash of the query,
so a changed query runs again instead of reading an old result.

**Why not merge names instead.** Merging names that look alike (same first two words, say) would fix middle initials
but not transliterations, and would wrongly merge two different people of the same name in a family (a father and son,
or two common names). The representative publication is a list of distinct people written by one office at one time.

**Cost.** A family member that adds an inventor (a divisional or continuation, say) is missed, so the counts per family
are lower bounds. The 4,131,009 total is exactly the sum of the largest publication in each family, so the loss is only
inventors who never appear on that publication.

**Checked (descriptive), on the corrected run.**
- 4,131,009 inventors in 1,548,276 families, 88.3% of `google_patents`' 1,753,104 families (the rest name no
  inventors in Google's data).
- Country unknown: 546,899 inventors (13.2%), down from 25.4% in the first run. The country came from the
  representative publication for 3,523,712, from the same name for 56,180 and from the first two words for 4,218.
- Inventors in Australia: 206,120 (255,481 in the first run).
- Estimated gender: 85.1% of inventors have an estimate (80.0% from their name and country, the rest from the name
  alone). The average probability of being a woman is 0.135 overall and 0.121 for inventors in Australia.
- Two countries need care in Stage 1. For China, 31.9% of estimates are between 0.2 and 0.8 (romanised Chinese names
  carry little gender information), and the average is 0.336. For Korea, only 52.2% have an estimate and the average
  is 0.321; Korean given names are often split across two words in harmonised names ("KIM JONG HO"), so the second word
  alone may be matched. Both averages are well above other countries' and should not be used until checked against an
  outside benchmark.
