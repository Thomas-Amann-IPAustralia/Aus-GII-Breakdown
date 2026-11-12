# Refresh report: what a re-run of the notebooks would move

Written by `python -m atlas.refresh report` on 2026-11-12 (ADR 0059). The three notebooks were run again **in a copy**; the reviewed notebooks and the atlas are unchanged. Each number an observation quotes was read again at the place it came from.

## In brief

- **231 observations compared.** 229 have every traced number where it was; 1 has at least one that moved; 0 have a place that no longer exists; 0 sit under a cell that failed in the copy; 1 has prose already corrected to the new value, above a stored output that was never run again.
- **5,462 numbers traced to a place:** 5,460 the same, 1 moved, 0 with their place gone.
- **Runs:** 01_univariate.ipynb in 2 min 55 s (0 cells failed); 02_bivariate.ipynb in 7 min 32 s (0 cells failed); 03_multivariate.ipynb in 17 min 4 s (0 cells failed).

## Numbers that moved (1 observation)

Old value, then what the same place holds now.

### U1: The register data list each application once, with few gaps where values are expected

12 of 13 traced numbers are the same.

- **89** is now **90** (line | # rows, # columns)

## Prose already corrected, output not yet run again (1 observation)

A dated correction put the words right and quotes the old value; the re-run agrees with the words.

### U22: The monthly timeline runs from 1904, with each series starting where its records can be trusted

6 of 7 traced numbers are the same.

- **79** is now **86** (line | # months, January # to September #; # columns)

## Nothing moved (229 observations)

U0, U2, U3, U4, U5, U6, U7, U8, U9, U10, U11, U12, U13, U14, U15, U16, U17, U18, U19, U20, U21, U31, U32, U33, U34, U35, U36, U37, U38, U39, U40, U88, U89, U90, U91, U92, U93, U94, U95, U96, U97, U98, U99, U100, U101, U102, U103, U104, U105, U106, U107, U41, U42, U43, U44, U45, U46, U47, U112, U126, U48, U49, U50, U51, U52, U53, U54, U55, U56, U57, U58, U59, U60, U61, U62, U117, U118, U63, U64, U65, U66, U67, U68, U69, U70, U71, U72, U115, U120, U23, U24, U25, U26, U27, U28, U29, U30, U108, U109, U110, U111, U125, U113, U116, U123, U124, U73, U74, U75, U76, U77, U78, U79, U114, U119, U80, U81, U82, U83, U84, U127, U85, U86, U87, U121, U122, B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15, B16, B17, B18, B19, B55, B20, B21, B22, B23, B24, B25, B26, B50, B51, B27, B28, B29, B30, B31, B58, B59, B32, B33, B34, B35, B61, B36, B37, B38, B39, B47, B48, B49, B52, B56, B63, B40, B41, B42, B43, B53, B54, B57, B60, B44, B45, B46, B62, M1, M2, M3, M4, M5, M6, M7, M26, M27, M28, M40, M8, M9, M10, M11, M12, M29, M30, M13, M14, M15, M16, M31, M32, M17, M18, M33, M19, M20, M25, M34, M35, M36, M39, M21, M22, M37, M23, M24, M38

## What this report cannot see

- **241 quoted numbers are not traced** to a place (worked out by arithmetic, read off a chart, or from outside the outputs). A re-run could move them unseen.
- **75 are read on another observation's page**, and are reported there.
- **Charts** are not compared: a number that exists only in a drawing is not traced.
- Years and one-digit numbers are not traced; a two-digit number only where exactly one place holds it.
