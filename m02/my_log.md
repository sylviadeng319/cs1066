## My Lab Notebook for CS1066 PSet #1

Sylvia Deng

INSERT-YOUR-VIDEO-LINK (after completing this assignment)

----
----

### SUBTASK #1: Prompt for the Search Term

----
Text of my first prompt:

> Work in the directory `m02`. In the script `trends_save.py`, the `query` string is currently hard-coded. Modify the script so that it prompts the user for the query.

Reflections on success/failure of this prompt:

*   The edited `trends_save.py` ran successfully. 
*   The AI claimed that it would do the minimal change while it was working. In future prompts, especially when modifying a larger script, I could explicitly ask the AI to preserve the existing structure and make only necessary changes.
*   `trends_plot.py` also ran successfully. No further iteration was needed because the prompt identified the exact script, variable, and desired behavior clearly.

----
**FINAL REFLECTION:** Review your work. Write a brief statement of what you might have done differently in hindsight, or defend why your work was a good approach.

My prompt worked on the first pass, probably because this was a simple one-line change. I think it is helpful to make the instructions clear by specifying which directory to work in, which script to modify, and which variable to change. I think mentioning the specific variable is good approach when we have a good understanding of the script and the intended change is simple. However if the script is long or the change is more complicated, it may be better to describe the desired behavior and let the AI figure out which parts of the code need to be changed.

----
----

### SUBTASK #2: Just One Tool

----
Text of my first prompt:

> Work in the directory `m02`. In a new script called `my_tool.py`, run both `trends_save.py` and `trends_plot.py`, so I get both outputs by running only `my_tool.py`.

Reflections on success/failure of this prompt:

*   `my_tool.py` ran successfully. I liked how it added terminal messages such as "Running trends_save.py" because they make it clearer to the user what the tool is doing.
*   One thing I noticed is that my prompt focused on the final behavior rather than telling the AI exactly how to implement it. This gave the AI some flexibility in choosing how to connect the two scripts while still producing the result I wanted.

----
**FINAL REFLECTION:** Review your work. Write a brief statement of what you might have done differently in hindsight, or defend why your work was a good approach.

I think my approach was effective because I made it clear what output I wanted from the new script without over-specifying how the AI should implement it. As before, I identified the directory, the new script to create, the two existing scripts to run, and the final result I wanted. This gave the AI enough guidance and allowed it to decide how to connect the two scripts.


----
----

### NEW TASK: Improve the Tool

----
Another idea that aligns with this challenge:

> If the user wants to run the tool for a geographic region other than "US", they currently have to go into the code and change it manually, which wastes time. 

> Could you change tool's operation so that it prompts the user for a geographic region? The default should explicitly be set to "US" and the user should be able to skip the prompt by pressing Enter so that it does not interrupt the current workflow.

----
Which improvement I chose to implement (put an X on the line):

_X_  The professor's example idea

___  My idea above

----
Text of my first prompt:

> Work in the directory `m02`. Modify the script `trends_save.py` so that it picks a reasonably thoughtful name for the output csv. It should check if the name already exists, and if it does, prompt the user for a name.

Reflections on success/failure of this prompt:

*   I decomposed the improvement into two subtasks because the csv filename is created before the plot is generated. First, I focused on giving the csv a meaningful name; then I planned to make the image name depend on that csv name.
*   The name of the csv was changed successfully, but I think it would be better if we can keep the "scraped_data" as a suffix and also include the geographic location. 

----
Text of my next prompt:


> Modify the script `trends_save.py` so that the name it picks for the output csv has "scraped_data" as a suffix and includes the geographic location. 

Reflections on success/failure of this prompt:

*   This prompt worked better because I specified exactly what I want as a "reasonably meaningful" name and reduced the ambiguity for AI.
*   By testing the result, I also realized that the user no longer had the option to intentionally overwrite the old output.

----
Text of my next prompt:


> Modify the script `trends_save.py` so that when the name already exists, the user has the option to either overwrite the existing file or pick a new name.

Reflections on success/failure of this prompt:

*   This prompt worked because I clearly described the two actions available when a filename already exists.
*   This iteration made me realize that I also need to think about how a user would interact with the tool in less common situations when framing the prompt.

----
Text of my next prompt:


> Work in the directory `m02`. Modify the script `trends_plot.py` so that it picks a name for the output image. The name should be associated with the name of the input csv. The script should check if the name already exists, and if it does, user should have the option to either overwrite the existing file or pick a new name.

Reflections on success/failure of this prompt:

*   This prompt is for the second subtask.
*   It failed because although the AI updated the output image naming logic, it did not update the input CSV name used by `trends_plot.py`.
*   I realized that I should have explicitly told the AI to make `trends_plot.py` use the CSV file generated by the updated `trends_save.py`. The dependencies between scripts should be stated explicitly in my prompt. 

----
Text of my next prompt:


> Modify `trends_plot.py` so that it uses the CSV file generated by the updated `trends_save.py` as its input. Keep the output image naming behavior from the previous change, but remove "scraped_data" from the image filename. The image name should still be based on the search query and geographic location.

Reflections on success/failure of this prompt:

*    This prompt worked successfully because I clearly specified the issues from the previous attempt. The final image name reflected the search query and geographic location more clearly.

----
**FINAL REFLECTION:** Review your work. Write a brief statement of what you might have done differently in hindsight, or defend why your work was a good approach.

In hindsight, I would have planned the naming behavior more carefully before writing my first prompt. I later realized that `trends_plot.py` also needed to use the updated CSV filename. I also did not think about overwrite behavior until after testing the first version. If I did this again, I would first define the full workflow, including how the CSV and image should be named, how the two scripts should connect, and what should happen when a file already exists. This would make my prompts more complete and reduce the number of revisions needed.

----
----

### Final Questions

1.  In your own words, give names to the steps in the problem-solving process you followed.

    1. Decompose the problem
    2. Frame the (sub)task
    3. Generate the prompt
    4. Judge the output
    5. Iterate (2, 3, 4)
    

2.  Which step do you find most challenging, and why?

    I find framing the task to be most challenging because I need to balance the amount of details I put in my prompt to make sure the AI has clear and concise instruction.

3.  What two questions do you have about how Python expresses the tasks you might ask it to do?

    1. How does Python pass information, such as filenames or user input, from one function or script to another?

    2. How does Python decide what action to take when different conditions occur, such as whether a file already exists?


----
----

### Other's Review

... YOU DO NOTHING HERE; ANOTHER STUDENT WILL COMPLETE THIS PART IN SECTION ...

----
----

### AI's Review

... PASTE AI'S FEEDBACK ON THIS LAB NOTEBOOK HERE ...
