#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Book, User
engine = create_engine('sqlite:///BookGenre.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Dummy Users
User1 = User(name="Mona Elwadi", email="mona.elwadi@gmail.com",
             picture='https://www.returntosourcewellbeing.com/wp-content/'
             'uploads/2018/01/I-Choose-Myself.png', provider='google')
session.add(User1)
session.commit()

User2 = User(name="Book surfer", picture='https://www.ossian.lib.ia.us/images/'
             'srpall/srpteen2015/book-surfer.jpg',
             email="booksurfer2day@gmail.com", provider='google')
session.add(User2)
session.commit()

# Menu for Self-Help Genre books

Genre1 = Genre(user=User1, name="Self-Help")
session.add(Genre1)
session.commit()

book1 = Book(
    user=User1,
    name="The Monk who sold his Ferrari: A Fable about fulfilling "
    "your dreams & reaching your destiny",
    author="Robin Sharma",
    description="An inspiring tale that provides a step by step approach to"
    "living with greater courage, balance, abundance & joy.",
    price="$13.59",
    genre=Genre1)
session.add(book1)
session.commit()

book2 = Book(
    user=User1,
    name="Feel the Fear...and Do It Anyway",
    author="Susan Jeffers",
    description="Enduring Guide to self empowerment,"
    " that inspires us with dynamic techniques and profound concepts that have"
    "helped countless people grab hold of their fears and move forward with"
    "their lives.",
    price="$12.80",
    genre=Genre1)
session.add(book2)
session.commit()

book3 = Book(
    user=User1,
    name="The Power of Intention",
    author="Dr. Wayne W. Dyer",
    description="The book explores intention as something you do as an enrgy"
    "you are a part of. This is the first book to look at intention as a field"
    "of enrgy that you can access to begin co-creating your life wiht the"
    "power of intention.",
    price="$12.73",
    genre=Genre1)
session.add(book3)
session.commit()

# Menu for literature & Fiction Genre books

Genre2 = Genre(user=User1, name="Literature & Fiction")
session.add(Genre2)
session.commit()

book1 = Book(
    user=User1,
    name="The Legacy of Lucy Harte",
    author="Emma Heatherington",
    description="Sometimes time is all we have with"
    "the people we love. Maggie O'Hara Knows better than must that life can"
    "change in aheartbeat.18 Years ago, she was given the most precious gift a"
    "second hand heart and a second chance at life. Always thankfull, Maggie"
    "has never forgotten Lucy Harte..the little girl who saved her life."
    "But as Maggie's own life begins to fall apart, and her heart is broken in"
    "love, she loses sigt of everthing she has to live for..."
    "Until an unexpected letter changes Maggie's life.",
    price="$5.76",
    genre=Genre2)

session.add(book1)
session.commit()

book2 = Book(
    user=User1,
    name="The House of New Beginnings",
    author="Lucy Diamond",
    description="In an elegant Regency house near the"
    "Brighton seafront, 3 tenants have more in common than they know. "
    "A shocking revelation has led Rosa to start over as a sous chef. The work"
    " is gruelling but it's a distraction. Until she comes up against the"
    " stroppy teenager next door who challenges her lifestyle choices."
    " What if Rosa's passion for food could lead her to more interesting"
    " places? Having followed her childhood sweetheart down south, Georgie is"
    " busily carving out a new career in journalism. Throwing herself into the"
    " city's delights if un, but before she knows it she's sliding headlong"
    " into all kinds of trouble. Nursing a devastating loss, charlotte just"
    "wants to keep her head down. But Margot, the glamorous older lady on"
    "the top floor has other ideas. Like it or not, Charlotte must confront"
    " the outside world and the possibilities it still holds.As the women"
    " find each other, hope surfaces, friendships blossom and a"
    "whole new chapter unfolds for them.",
    price="$9.53",
    genre=Genre2)

session.add(book2)
session.commit()

book3 = Book(
    user=User1,
    name="Where The Light Gets In",
    author="Lucy Dillon",
    description="You know those cracks in your heart, Lorna, where things"
    "didn't work out. but you picked yourself up and carried on? That's where"
    "the fear gets out and where the light gets in. An inspiring,"
    "life enhancing novel that will make you see your life afresh.",
    price="$7.97",
    genre=Genre2)

session.add(book3)
session.commit()


# Menu for Young Adult books

Genre3 = Genre(user=User2, name="Young Adult")
session.add(Genre3)
session.commit()

book1 = Book(
    user=User2,
    name="The Selection",
    author="Kiera Cass",
    description="Prepare to be swept into a world of breathless "
    "fairy tale romance, swoonworthy characters, glittering gowns and fierce"
    "intrigue. For 35 girls, the Selection is the chance of a lifetime."
    "The opportunity to esccape a rigid caste system, live in a palace and"
    "compete for the heart of gorgeous Prince Maxon. But for America Singer,"
    "being selected is a nightmare. It means turning her back on her secret"
    " love with Aspen, who is a caste below her, and competing for a crown she"
    " doesn't want. Then America meets Prince Maxon and realizes that the life"
    "she's always dreamed of may not compare to a future she never imagined.",
    price="$7.99",
    genre=Genre3)

session.add(book1)
session.commit()

book2 = Book(
    user=User2,
    name="The Hunger Games",
    author="Suzanne Collins",
    description="In the ruins of a place once known as North America lies the"
    "nation of Panem, a shining Capitol surrounded by twelve outlying"
    "districts.Long ago the districts waged war on the Capitol and were "
    "defeated.As part of the surrender terms, each district agreed to send one"
    "boy and one girl to appear in an annual televised event called,"
    "'The Hunger Games',"
    "a fight to the death on live TV. Sixteen-year-old Katniss Everdeen,"
    "who lives alone with her mother and younger sister, regards it as a "
    "death sentence when she is forced to represent her district in the"
    "Games.The terrain, rules, and"
    "level of audience participation may change but one thing is constant:"
    " kill or be killed.",
    price="$8.79",
    genre=Genre3)

session.add(book2)
session.commit()

# Menu for Kids books

Genre4 = Genre(user=User1, name="Kids")
session.add(Genre4)
session.commit()

book1 = Book(
    user=User1,
    name="Winnie-the-Pooh",
    author="A. A. Milne",
    description="Since 1926, Winne the Pooh and his friends Piglet, Owl,"
    "Tigger and the ever doleful Eeyore have endured as the unforgettable"
    "creations of A.A. Milne, who wrote this book for his son, Christopher"
    " Robin, and Ernest H. Shepard, who lovingly gave Pooh and his companions"
    " shape. These characters and their stories are timeless treasures of "
    "childhood that continue to speak to all of us with the kind of "
    "freshness and heart that distinguishes true storytelling.",
    price="$5.73",
    genre=Genre4)

session.add(book1)
session.commit()

book2 = Book(
    user=User1,
    name="Harry Potter and the Sorcerer's Stone",
    author="J.K. Rowling",
    description="Harry Potter has never been the star of a Quidditch team,"
    " scoring points while riding a broom far above the ground. He knows no"
    " spells, has never helped to hatch a dragon, and has never worn a cloak"
    " of invisibility. All he knows is a miserable life with the Dursleys, his"
    " horrible aunt and uncle, and their abominable son, Dudley "
    "a great big swollen spoiled bully. Harry's room is a tiny closet at the"
    " foot of the stairs, and he hasn't had a birthday party in eleven years."
    " But all that is about to change when a mysterious letter arrives by owl"
    " messenger: a letter with an invitation to an incredible place that Harry"
    " and anyone who reads about him will find unforgettable.",
    price="$14.90",
    genre=Genre4)

session.add(book2)
session.commit()

print "added menu items!"
