This is a short description for running and installing moses.
First of all, follow the instructions in this video to install moses properly and colloquate all the files in the correct folders:

https://www.youtube.com/watch?v=aaalgJoRy54

Eventually, create a folder containing a folder "corps" with six files: train.nl/mrl, test.nl/mrl and tune.nl/mrl
and "mosespipe.sh"(mosespipe should be in the main folder, not in "corps").

The last step is to run the script.

"listfile" contains the n-best translations
"outputOfTest.txt" contains the resulting translations

For the full run with evaluation use "runsmt.sh" ("mosespipe.sh" should still be adapted).
"record" will contain the selection history. Evaluation results will be displayed in the shell.