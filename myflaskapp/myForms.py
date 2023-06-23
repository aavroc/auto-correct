
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class ValidationForm(FlaskForm):
    text = TextAreaField('Text', validators=[DataRequired()], render_kw={"rows": 14}, default='word1 word2 word3 word4 longword5 word6 word7 word8 word9 lastword10')
    words = StringField('Words', validators=[DataRequired()])
    submit = SubmitField('Validate')