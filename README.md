# Boun Registration Tools

Scrapes a chosen department's schedule into a DataFrame.  It then turns that data into classroom schedules and saves it as sheets on a single Excel file.  That data could be turned into many things, but currently, that's what it does.

## Known shortcomings

- Cannot handle rows on schedule that are missing Classrooms (or anything that has unequal number Days/Hours/Classrooms, in general).  See, for example, INT 320.01 on <https://registration.bogazici.edu.tr/scripts/sch.asp?donem=2024/2025-1&kisaadi=TR&bolum=TRANSLATION+AND+INTERPRETING+STUDIES>.
  - I don't see any proper way to fix this.
- Will suffer with overly-quirky Hour specifications, e.g., 1213 (is it 12-13, 12-1-3, 1-2-13, or 1-2-1-3?).  It can handle some mildly-quirky specifications such as 1011 (10 is definitely 10 and it assumes the 11 that follows it is 11), however.
  - This can be fixed by checking the number of Days specified, since it's representation is unambiguous.  It also is very unlikely that the number of Days and Hours is mismatched.  A MWF 1213 (12-1-3 or 1-2-13?) would still remain undecipherable, however.
- No support for weekends.  I don't know how they are specificed—have never seen an example.
