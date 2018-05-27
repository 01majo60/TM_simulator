from app import db

class Tmachine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    definicia = db.Column(db.String(100), index=True, unique=True)
    tm_d_n_x = db.Column(db.String(16), index=True, unique=False)

    def __repr__(self):
        return '<Tmachine {}>'.format(self.definicia)  
