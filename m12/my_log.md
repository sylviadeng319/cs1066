## My Lab Notebook for CS1066 PSet #6

Sylvia Deng

INSERT-YOUR-VIDEO-LINK (after completing this assignment)

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
*   I used a generated set of future recaps for my search tests, rather than documenting a rewrite of one existing recap here. So the response helped me understand the intended approach.
*   That distinction changed how I interpret my semantic-search result. It is a useful trial but not by itself proof.

----

Text of my next prompt:

> Describe a Harvard game using late-game defense, a clutch comeback, and a road win without using the original title words or obvious matchup terms.

How the AI's response to this prompt moved your work forward (or not):

*   The response gave me a descriptive query to try: “A resilient Harvard team used a late defensive stand and a flurry of clutch shots to erase a halftime deficit and beat a tough California squad on the road.”
*   Semantic search ranked the California recap first, which was encouraging and gave me a concrete result to inspect.
*   My query still names Harvard and California and mentions a road game. Those clues may have helped, so this is not a clean demonstration that the search relied only on meaning.
*   The run helped me see how I could make the test stronger: remove the names and obvious matchup details, then see whether the intended recap still ranks first.

----

Text of my next prompt:

> Find a semantic query that clearly matches a California comeback recap without using the same exact keywords as the recap title.

How the AI's response to this prompt moved your work forward (or not):

*   The response helped me focus on describing the game's events rather than just repeating its title.
*   I wanted the query to sound like something a person might say when recalling a game. The suggested wording gave me a starting point, although I still needed to judge whether it avoided too many identifying terms.
*   The California result was easy to explain, but the query retained the team names and road setting.
*   This made me realize that a convincing test needs both a meaningful paraphrase and a check that the paraphrase does not give away the answer through names or other obvious keywords.
