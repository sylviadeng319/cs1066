## My Lab Notebook for CS1066 PSet #4

Sylvia Deng

INSERT-YOUR-VIDEO-LINK (after completing this assignment)

----
----

### Document Your Iterations with AI

----

Text of my first prompt (copied from the pset directions):

> The folder `m09/data_room` was prepared by a startup I'm looking to acquire. In it, focus on the `people` folder. In the directory `m09/pset4`, create an interactive app in Python using Streamlit that allows me to run scenarios on the number of people I can bring on. Use a Python virtual environment for any packages that need to be installed. The app should implement a slider that sets the total headcount number, and it should display the total cost (based on compensation) for a team of that size. Prioritize people by compensation.

Reflections on success/failure of this prompt:

*   The Streamlit app ran without any error.
*   AI was able to figure out the packages needed for the virtual environment and created a requirements.txt file.
*   It also implemented the slider as described in the prompt, and I was able to run scenarios smoothly.
*   The prompt did not ask the AI to display an explicit list of employees, but the AI created a scrollable table to display the information of the employees under the selected scenario. I liked this design because it was clear and allowed me to ensure that people were prioritized by compensation.
*   I also liked the little question mark icon the AI added, which lets users hover to see a note explaining how the displayed total compensation was calculated.
*   In general, AI did a pretty good job.

----

Text of my next prompt:

> When selecting employees, prioritze people by highest compensation by default, but allow users to change it to priortize by lowest compensation. 

A refinement strategy from class: Y

If Yes, which one: **Add constraints.** 

Reflections on success/failure of this prompt:

*   The AI successfully added a dropdown to allow switching between the two choices. The default choice was also set.
*   However I was not a fan of the dropdown design choice because it added extra steps for users. I had to click on the dropdown to see or change the options.
*   Overall the functionality worked, but the design choice wasn't the best.


----

Text of my next prompt:

> The current compensation priority selection uses a dropdown but only has two options, unnecessarily complicated the page. Replace it with a toggle switch to make the current priority visually clearer and can be changed with one click. Place it under the slider, aligned to the right.

A refinement strategy from class: Y

If Yes, which one: **Describe the problem, not just the symptom**

Reflections on success/failure of this prompt:

*   The AI removed the dropdown and implemented a toggle switch. It successfully placed the switch at the position I specified. 
*   The default setting was preserved, and I was able to toggle the swtich and see the compensation and selected employees change. 
*   I think explaining the problem to AI helps it better understand the intention of our prompt, and can effectively reduce the number of iterations.

----

Text of my next prompt:

> Add a view selector allowing users to switch between the existing employee table and a hierarchy diagram. Arrange the employees as an org chart using the reports_to relationships. When an employee is hovered over, show the same information currently shown in the table. 

A refinement strategy from class: Y

If Yes, which one: **Provide examples or references.**

Reflections on success/failure of this prompt:

*   The AI successfully created a button to select between table and org chart views. 
*   The org chart correctly uses the roster's reporting relationships.
*   However, the AI failed to add the hovering effect. The org chart view does not display any specific information about the employees, except for their names. 
*   I was surprised that the hover effect wasn't implemented. It's possible that the AI neglected that part or there was some error in the code. In either way, the prompt would probably work better if I asked the AI to test the functionality.
*   The layout was also a bit tight, so the employee names were very small.
*   I also did not like the placeholder manager the AI put above employees who didn't have a superviser. It made the org chart somewhat confusing.

----

Text of my next prompt:

>  For the org chart view, make sure the following criteria is met: 1. Hovering over any employee displays all four fields shsown in the table (name, role, department, and annual baqse compensation). Test this in the running app. 2. The name of each employee should be clear and see to read. 3. Employees without a manager should not have anything above them. 4. The style of the org chart should align with the rest of the webpage.

A refinement strategy from class: N

If Yes, which one: ...INSERT THE BOLD TITLE FROM THE CLASSNOTES...

Reflections on success/failure of this prompt:

*   The org chart now correctly shows the employee's information when I hover over an employee.
*   The AI also made the employee names much easier to read, and employees without a manager appear at the top without a placeholder manager above them.
*   This iteration shows that stating acceptance criteria helps cover important behavior and layout details and makes sure the designed funcitionalities work as intended.

----

Text of my next prompt:

> Add the option to select one or more "must-have positions" from the available employee roles. If the headcount is too small to include all must-have roles, show a clear message instead of silently leaving one out. 

A refinement strategy from class: N

If Yes, which one: ...INSERT THE BOLD TITLE FROM THE CLASSNOTES...

Reflections on success/failure of this prompt:

*   The app now allows me to select one or more must-have positions from the available roles, and it includes an employee for each selected role.
*   It fills any remaining headcount according to the compensation-priority setting, so the required roles and compensation preference work together.
*   When I selected more must-have roles than the headcount allowed, the app displayed a clear message instead of silently leaving out a role.
*   This was a useful new strategy because I specified both what the result must include and what the app should do when those requirements cannot all be met.

----
----

### Share Your Best NEW Refinement Strategy

As you see in `cn09`,

1.  Write a short phrase that covers one of your new refinement strategies.

**Strategy: Specify required choices and infeasible cases**

2.  Give a two pairs of "do" and "don't" examples.

- **Do:** “Include one employee for each selected must-have position, then fill remaining seats by compensation priority.”
- **Don't:** “Let me choose some positions to include.”

3.  Add any description that helps others to use this refinement strategy.

Tell the AI what the result must include and what it should do if the user's
choices make that result impossible.

Being explicit about both the required outcome and the failure case helps the
AI avoid silently ignoring a requirement or guessing how to resolve a conflict.
