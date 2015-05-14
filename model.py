from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


###################
# Model definitions

class User(db.Model):
	"""User of Mineralchemy website."""

	__tablename__ = "users"

	user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	firstname = db.Column(db.String(64), nullable=True)
	lastname = db.Column(db.String(64), nullable=True)
	email = db.Column(db.String(64), nullable=False)
	password = db.Column(db.String(64), nullable=False)

	def __repr__(self):
		"""Representation when printed"""
		return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class Favorite(db.Model):
	"""Favorite listings of users."""

	__tablename__ = "favorites"

	favorite_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
	etsy_listing_id = db.Column(db.Integer, nullable=False)

	user = db.relationship("User", backref=db.backref("favorites", order_by=favorite_id))

	def __repr__(self):
		"""Representation when printed"""

		return "<favorite_id=%s user_id=%s etsy_listing_id=%s" % (self.favorite_id, self.user_id, self.etsy_listing_id)


###################
# Helper functions

def connect_to_db(app):
	"""Connect the database to the Flask app."""

	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mineralchemy.db'
	db.app = app
	db.init_app(app)


if __name__ == "__main__":
	from server import app
	connect_to_db(app)
	print "Connected to Mineralchemy database."