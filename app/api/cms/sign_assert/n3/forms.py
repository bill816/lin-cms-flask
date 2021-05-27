from flask.ext.wtf import Form
from flask.ext.uploads import UploadSet, IMAGES
from wtforms import TextField
from flask.ext.wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired
from werkzeug import secure_filename

images = UploadSet('images', IMAGES)

class MyUploadForm(Form):
	"""
	Proof of concept form class for image upload by user
	"""
	name = TextField('name', validators=[DataRequired()])

	upload = FileField('image', validators=[
		FileRequired(),
		FileAllowed(images, 'Images only!')
		])		
	