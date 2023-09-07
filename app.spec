# create exe
pyinstaller -F --add-data "templates;templates" --add-data "static;static" app.py