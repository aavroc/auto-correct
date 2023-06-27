# auto-correct

This is a fast way to mass-correct Canvas submissions.

Some type of dubmissions will be rated automatically.

## Install

python3 needs to be installed, then
pip install flask
pip install canvas

(virtual environment, venv is not needed, but can be installed)

To run the code you need to create a flask config file ile.

Create myflaskapp/config.py

config={
    'API_URL':'https://api-url.server.es',
    'API_KEY':'API Key',
    'default_feedback':['Well done!', 'Top!', '...']
    }


flask run --debug --reload

--

# Wishlist/Ideas

## Closed

- Show all PNG's and PDF next to the selectedfule_type.
    Done, So the requested file_type is shown. If more submitted, the first one is shown or the one that mathes the requested
    filename. Next to this *all* PNG's and PDF's are shown.

- PDF
    Same as PNG, but HTML but use <embed></embed>
        Done but the embed HTML node does not scale as nice as a picture. Therfor the embed object gets a link at the bootom to open
        it full size in antoher window.
    (only partly tested)

- Show comments from students
    Done - but noit tested yet with student comments, only with teacher's comments.

- Change score when feedabck is changed.
    Done - with flickering effect.

## Open

- When score is higher than max or higher than 80% of max if attempt > 3, ask confirmation, or alert.

- Define words based on submissions - auto suggesting word list