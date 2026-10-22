## My Lab Notebook for CS1066 PSet #5

Sylvia Deng

NOTE: There is no video in this pset as you'll demo in section.

----
----

### ACTIVITY #1 (UNGRADED)

We don't require you to write anything around this first activity, but we leave space in case you decide to keep your own notes (**a good practice**). We won't grade anything in this section.

----

> SPACE FOR YOUR OWN NOTES

----
----

### ACTIVITY #2 (UNGRADED)

Again, you aren't required to write anything around this activity, but we leave space in case you decide to keep your own notes. We won't grade anything in this section.

----

> SPACE FOR YOUR OWN NOTES


----
----

### ACTIVITY #3 (UNGRADED)

This is your first at-home work, but it should be fairly straightforward. Make sure you understand what we ask, which you might see on a quiz. But, we won't grade anything in this section.

----

> SPACE FOR YOUR OWN NOTES

----
----

### ACTIVITY #4 (GRADED!!!)

----

Text of my first prompt:

> Write a Python program in /m11 that lets the user search the existing exoplanets SQLite database. Use the schema created by m11/load_exoplanets.py. Let the user filter planets by planet name or host-star name, minimum and maximum planet radius, minimum and maximum orbital period, discovery method, and transit flag. Only search observations from the latest retrieval so a planet isn’t shown more than once. Explain how to run the program and test it using the database that already exists.

Reflections on success/failure of this prompt:

*   The prompt was mostly successful, as it produced a command-line program that allows searching for the database without downloading more data (as required).
*   I searched for planets around 55 Cnc and saw five results, from 55 Cnc b through 55 Cnc f.
*   I also asked for planets with radii between 1 and 2 Earth radii that were detected by transit. The program returned 15 matches, and the rows showed the requested radius range and a transit flag of 1.
*   These tests made it easy to see that I can combine filters and search the database without downloading data again. The results were useful, although the table looked a bit crowded in my terminal.
*   This prompt was very concise and contains only the necessary constraints. The AI was able to figure out a lot of details of the database, partially thanks to the existing metadata.

----

Text of my next prompt:

> Please improve the search results table formatting so columns remain clearly separated and aligned in a normal terminal, including when values are long. Keep the search behavior unchanged. Then test the radius and transit filters again.

Reflections on success/failure of this prompt:

*   I tried the revised display and reran the radius and transit search; it still returned the same 15 planets.
*   The change split each planet's information across two tables. Although the columns were narrower, I found it less convenient to match each planet with its measurements.
*   After comparing the outputs, I decided the original single-table display was already readable for my use, so I did not keep the formatting change.

----
----

### ACTIVITY #5 (GRADED!!!)

----

Three fields you pick: planet radius (`pl_rade`), orbital period (`pl_orbper`), and equilibrium temperature (`pl_eqt`).

----

Text of my first prompt:

> Write a Python program in /m11 that provides a browser-based interface for searching the existing exoplanets.db. It should allow entering minimum and maximum values for planet radius (`pl_rade`), orbital period (`pl_orbper`), and equilibrium temperature (`pl_eqt`). Return the top five planets matching all three ranges, ranked by closeness to the midpoint of each range, and show the results in the browser. Save the criteria and ranked results to a JSON file. Do not download more data. Explain how to run and test the program.

Reflections on success/failure of this prompt:

*   It successfully creates a small local web server.
*   I tested the browser form and played with all three fields. It displayed the top matching planets and saved required fields and ranking scores in JSON.
*   I also tested an invalid range where the minimum was greater than the maximum; the program showed an error instead of running the search.
*   I liked that the ranking rule is shown in the browser and saved with the results, so it is clear how the list was produced.
*   However, I think the results section can be clearer and include more explanation for the benefit of users.

----

Text of my next prompt:

> Improve the results section of the exoplanet candidate page. Show the three selected ranges above the results, add a rank number to each result, and briefly explain that a lower score means the planet's measurements are closer to the range midpoints. Keep the search and ranking behavior unchanged. Test it with ranges that return matches and ranges that return no matches.

Reflections on success/failure of this prompt:

*   The results now show the selected ranges and a rank number, and explain how to interpret the score. This makes the list easier to understand without changing how candidates are filtered or ranked.
*   I tested ranges that returned candidates and ranges that returned no matches. The successful search still returned the same top five, while the empty search showed its criteria and a clear no-match message.
*   I think this prompt tells AI the required changes clearly, so AI was able to implement it efficiently.

----
----

**FINAL QUESTIONS:** Review your work on ALL parts of this pset and answer the following questions.

-   What aspects of working with databases still feel uncomfortably hazy?

Designing normalized tables and deciding which information belongs in a shared table versus an observation table still feel somewhat hazy.

-   How did you decide what aspects of the database your query program should focus on?

For Activity 4, I focused on fields that make it easy to find and compare planets, such as planet and host-star names, radius, orbital period, discovery method, and transit status. For Activity 5, I chose radius, orbital period, and equilibrium temperature because they are measurable planet characteristics that can be bounded with ranges. The SQLite schema and the selected fields in the downloaded data helped me choose fields that were actually available. I also discussed with AI for advice.

-   Briefly describe how you decided on the interface in Activity #5.

I chose a browser-based form with minimum and maximum inputs for each of the three fields, so I could set the search criteria without editing code. The page displays the top five matches and their ranking scores, and saves the criteria and results to JSON. I used distance from the middle of each range as the ranking rule and added the selected ranges and rank numbers to make the output easier to interpret. I made these decisions by imagining how I would like to use this tool and what information I would like to see if I were a real user.
