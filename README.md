# auto-correct

This is a fast way to mass-correct Canvas submissions.

Some type of dubmissions will be rated automatically.

## Install

python3 needs to be installed, then
pip install flask
pip install canvas

create a directory temp in static

(virtual environment, venv is not needed, but can be installed)

To run the code you need to create a flask config file ile.

Create myflaskapp/config.py
(rename example-config.py to config.py and change values)

flask run --debug --reload

--

# Wishlist/Ideas

## Done

- Multitrheaded, performance enhancement (factor 2) using threads per assignment and per download (png, jpg and pdf).
  cleaned up (old) code in the porcess

- Show all PNG's and PDF next to the selectedfule_type.
    Done, So the requested file_type is shown. If more submitted, the first one is shown or the one that mathes the requested
    filename. Next to this *all* PNG's and PDF's are shown.

- PDF
    Same as PNG, but HTML but use <embed></embed>
        Done but the embed HTML node does not scale as nice as a picture. Therfor the embed object gets a link at the bootom to open
        it full size in antoher window.
    (only partly tested)

- Show comments from students
    Done - but not tested yet with student comments, only with teacher's comments.

- Change score when feedabck is changed.
    Done - with flickering effect.

- Add txt
    Done - not tested yet.

- Add css as file format.
    Open

- Add example picture to rate form (this is what is should look like)
    Pictures need to be stored on server...enough capacity?

- Add button to Canvas from rate-scherm, when pressed the rate check-box is unselected and the Canvas rating screen is opened.
    Need canvas userid in rate screen.
    Done.

- Add button indien niet goed, om te overriden naar 'correct'.
    Done


## rejected

- Refacture listUnratedAssignments into OOP
    OOP Object in Python does not copy properties by value to list (copying object is standard 'by reference'), so less usefull?
    -> defered


## partly

- Show all attachment names
    (Partly done) Now only on attachments shown in AC.


## open

- Add student name to feedback & test words

- Test if number of attachments is correct, if not, propose 0-rating.
    Change in CM to record number of requested att.

- When score is higher than max or higher than 80% of max if attempt > 3, ask confirmation, or alert.

- Define words based on submissions - auto suggesting word list

- Bug , when [] is defeined as match word the algorithm goes wrong, probably also with {} ...?

- Nakijk-parameters, makkelijker exporteren van ene cohort naar andere, hoe???
    - eenmalige koppeling met id's?

- Cache directories splitsen JSON en IMG

- Cache directories clean-up, each.... (config)?

- json for grade form has one record for every attachment. Should have one record for every submission in which there is a list of attachments.
  this means refacturing listUnratedAssignments(item) and refacturing the grade.html view template. The template wouild become simpler
  because there is no need anymore for inserting objects in teh DOM. At this moment the first att. is rendered after which the next attachment 
  (if any) will be inserted by JS in teh DOM (reason is that we first only would show one attachment).
