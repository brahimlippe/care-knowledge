from server import db, User, Category, Video
db.drop_all()
db.create_all()
#db.session.add(User(name='admin', password=b'$2b$10$MuqRlqo2SC97TU3Z6BmBBe7vrs9ARVBBOv3WmfjquY9MXwbyshxfy', admin=True, email='brahim.pro@protonmail.com'))
db.session.add(User(name='bra', password=b'$2b$10$9kmb6L0/J6MxBp8HK2EJ3eE/rgx.HC1pjIvO3YPVZwfn2h1yGslXS', email='brahim.sahbi@gmail.com'))
db.session.commit()
nutrition=Category(name='nutrition')
psychology=Category(name='psychology')
video1=Video(link='https://www.youtube.com/embed/KD-FmeueFUo')
video1.categories.append(nutrition)
video2=Video(link='https://www.youtube.com/embed/p79D6u-6pN4')
video2.categories.append(nutrition)
video3=Video(link='https://www.youtube.com/embed/K3ksKkCOgTw')
video3.categories.append(nutrition)
video4=Video(link='https://www.youtube.com/embed/vo4pMVb0R6M')
video4.categories.append(psychology)
db.session.add(nutrition)
db.session.add(psychology)
db.session.add(video1)
db.session.add(video2)
db.session.add(video3)
db.session.add(video4)
db.session.commit()