## My Lab Notebook for CS1066 PSet #6

Sylvia Deng

VIDEO-LINK: https://harvard.zoom.us/rec/share/AvcWtiSdEVz9DImAGCA30ZhHvEqbHMGEUbfNE5ztSk6rYnS_g8SqRPVOGKv7tjNp.0B8uXHDsU9nsTymr?from=hub

----
----

### ACTIVITY #1: Keyword Search

----

Space where you can document what you learn about TF-IDF and BM-25 (UNGRADED).

> INSERT-YOUR-NOTES

----

Text of my first prompt (in **Part 1b**):

> Find a good example where both algos return the same California recap, and another example where BM-25 clearly beats TF-IDF on a Princeton game.

How the AI's response to this prompt helped my thinking (or not):

*   The response helped me turn the assignment into two separate tests: one where I expected both methods to find the same recap, and one where I hoped their rankings would differ.
*   California seemed like a useful first test because it is a specific opponent, so I could easily tell whether the result was relevant.
*   The Princeton suggestion gave me a second direction to explore, but I still needed to run both methods and check whether the results supported my expectation.

----

Text of my next prompt:

> Find a good example where BM-25 should rank a Princeton upset more strongly than TF-IDF, and explain why the query is a good test.

How the AI's response to this prompt helped my thinking (or not):

*   The response suggested using “Harvard upset Princeton in the Ivy race,” so I tried that query with both methods.
*   The results did not show a clear BM-25 win. Both methods ranked Princeton recaps first. I expected a more obvious difference, so checking the output made me reconsider the AI's prediction.
*   I also noticed that the two methods use different score scales. Instead of comparing the numbers directly, I should probably focus on which recaps each method ranked highest.
*   The prompt helped me form a testable idea, but the results showed that this particular query was not strong evidence for the claim I hoped to demonstrate.

----

Text of my next prompt:

> The Princeton query returned Princeton recaps near the top for both methods, so it does not clearly show BM-25's top choice is better. Find and test a query whose results make that distinction visible; don't use the difference in raw scores as proof, since the score scales differ.

How the AI's response to this prompt helped my thinking (or not):

*   This time I tested a detail from a specific recap rather than asking generally for an “upset”: “The Crimson made quick work of the Lions and built a lead by driving the margin up.”
*   BM-25 ranked **Harvard Turns an Early Deficit into a 20-Point Win** first. That recap describes Harvard's 75-55 win over Columbia, including a lead that grew to 22.
*   TF-IDF ranked losses to Dartmouth and Yale first, rather than that Columbia win. For this query, BM-25's top result was the better match to the game I had in mind.
*   I learned to judge this comparison by the relevance of the top results, not by comparing BM-25's and TF-IDF's raw scores. This was a stronger example than my first Princeton attempt because the two methods actually led me to different games.

----

Text of my next prompt:

> Give me a query where both methods should find the California recap, but do not make it too obviously the same as the title.

How the AI's response to this prompt helped my thinking (or not):

*   The response helped me phrase the search as a question someone might actually ask.
*   I tested “Harvard beat California in a close road game,” and both methods ranked the California recap first. That gave me the agreement example I was looking for.
*   The query still includes several strong clues—Harvard, California, and road—so it is not a test with completely different wording. I should be precise about what it shows.
*   This also helped me separate agreement in ranking from score size. The scores look different, but they are not directly comparable between methods.

----
----

### ACTIVITY #2: Semantic Search

----

Space where you can document your thoughts on Part 2a (UNGRADED).

> INSERT-YOUR-NOTES

----

Text of my first prompt (in **Part 2b**):

> Rewrite one Harvard recap so it is still easy for a person to recognize, but not easy for keyword search to match using the original title words.

How the AI's response to this prompt moved your work forward (or not):

*   The response clarified the goal for me, which is to keep the same game story recognizable while changing the wording enough that exact word overlap is less helpful.
*   It made me think about the difference between rewriting a recap and writing a paraphrased search query.
*   I chose the existing Columbia recap about Harvard's 75-55 win and rewrote it as semantic-rewrite-columbia.md. I kept the key scoring sequence but changed the article's wording.
*   Doing the rewrite made the task more concrete. I had to preserve what happened in the game while making the recap sound different, rather than just inventing a search query.

----

Text of my next prompt:

> Describe a Harvard game using late-game defense, a clutch comeback, and a road win without using the original title words or obvious matchup terms.

How the AI's response to this prompt moved your work forward (or not):

*   The response gave me a descriptive query to try: “A resilient Harvard team used a late defensive stand and a flurry of clutch shots to erase a halftime deficit and beat a tough California squad on the road.”
*   Semantic search ranked the California recap first, which was encouraging and gave me a concrete result to inspect.
*   My query still names Harvard and California and mentions a road game. Those clues may have helped, so this is not a clean demonstration that the search relied only on meaning.
*   The first query was also too generic. It ranked several unrelated future recaps describing a late push. I needed a query tied more closely to the rewritten article's particular sequence of events.

----

Text of my next prompt:

> Find a semantic query that clearly matches a California comeback recap without using the same exact keywords as the recap title.

How the AI's response to this prompt moved your work forward (or not):

*   The response helped me focus on describing the game's events rather than just repeating its title.
*   It led me back to the California query, which did find the California recap first, but it still included the team names and the road setting. Those terms made the result less convincing as a semantic-only match.
*   I learned that changing the wording of a title is not enough if the query still gives away the matchup. I needed to remove those clues and test a different, rewritten recap.

----

Text of my next prompt:

> Choose and rewrite a recap, then test a query with no obvious shared matchup terms.

How the AI's response to this prompt moved your work forward (or not):

*   I rewrote the Columbia recap and tried: “21 in succession changed 22-15 to 36-22 at intermission; the other side narrowed things to 43-41, yet subsequent figures were 70-48 and 75-55.”
*   This time the rewritten file, Harvard Turns an Early Deficit into a 20-Point Win, ranked first in semantic search (0.395). The next results were other recaps with scores of 0.3345 and 0.3331.
*   The query shares the score figures with the recap, but not its nontrivial wording. It describes the same run of events in different language, which makes this a better semantic example than the California query.
*   Comparing the matching passage with the query helped me explain the result. Both describe the shift from a 22-15 deficit to a 36-22 halftime lead, the opponent closing the gap to 43-41, and Harvard pulling away to win 75-55.
