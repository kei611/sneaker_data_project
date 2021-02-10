
# Create the database tables, add some initial data, and commit to the database
from project import db
from project.models import Sneaker, User


# drop all of the existing database tables
db.drop_all()

# create the database and the database table
db.create_all()

# insert admin user data
admin_user = User(email='admin@sneakershelf.com', plaintext_password='AdMiNpAsSwOrD', role='admin')
db.session.add(admin_user)

# insert user data
user1 = User('kanyejesus@gmail.com', 'password1234')
user2 = User('loveyeezy@gmail.com', 'PaSsWoRd')
user3 = User('blaa@blaa.com', 'MyFavPassword')
db.session.add(user1)
db.session.add(user2)
db.session.add(user3)

# insert sneaker data
sneaker1 = Sneaker('adidas don issue 2 white black gold', 10000, admin_user.id, False, 'adidas-don-issue-2-white-black-gold.jpg', 'http://localhost:5000/static/img/adidas-don-issue-2-white-black-gold.jpg')
sneaker2 = Sneaker('adidas yeezy boost 350 v2 natural', 14000, admin_user.id, True, 'adidas-yeezy-boost-350-v2-natural.jpg', 'http://localhost:5000/static/img/adidas-yeezy-boost-350-v2-natural.jpg')
sneaker3 = Sneaker('adidas zx 2k 4d grey four solar orange', 9000, user1.id, True, 'adidas-zx-2k-4d-grey-four-solar-orange.jpg', 'http://localhost:5000/static/img/adidas-zx-2k-4d-grey-four-solar-orange.jpg')
db.session.add(sneaker1)
db.session.add(sneaker2)
db.session.add(sneaker3)

db.session.commit()


#ターミナルからはsneaker_projectに移動してpython -m instance.db_createで実行
