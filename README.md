# auto-correct

This is a fast way to mass correct Canvas submissions.

Some tpye of dubmissions will be rated automatically.

Work in progress.

To run the code you need to create a faslk config file.

Create myflaskapp/config.py

config={
    'API_URL':'https://api-url.server.es',
    'API_KEY':'API Key',
    'default_feedback':['Well done!', 'Top!', '...']
    }


# Wishlist/Ideas

- Show all PNG's and PDF next to the selectedfule_type.
    Done, So the requested file_type is shown. If more submitted, the first one is shown or the one that mathes the requested
    filename. Next to this *all* PNG's and PDF's are shown.

- PDF
    Same as PNG, but HTML but use <embed></embed>
        Done but the embed HTML node does not scale as nice as a picture. Therfor the embed object gets a link at the bootom to open
        it full size in antoher window.
    (only partly tested)

- Show comments from students

- Define words based on submissions - auto suggesting word list