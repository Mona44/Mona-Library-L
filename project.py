#!/usr/bin/python
# -*- coding: utf-8 -*-

# Database imports
from database_setup import Base, Genre, Book, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc
from flask import Flask, render_template, request, redirect, url_for, flash,\
    jsonify
# session imports
from flask import session as login_session
import random
import string
# Authentication imports
from oauth2client.client import AccessTokenCredentials
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import os

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Book Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///BookGenre.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps(
            'Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    print(type(answer))
    data = answer.json()
    print data
    login_session['username'] = data.get('name', data['email'])
    login_session['picture'] = data.get('picture')
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # Check if user exists, if it doesn't make a new one
    user_id = getUserID(data['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '"style="-webkit-border-radius:150px;-moz-border-radius:150px;">'

    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'],
        provider=login_session['provider'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(
        email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps(
            'Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# JSON APIs to view Restaurant Information


@app.route('/genres/<int:genre_id>/books/JSON')
def genrebooksJSON(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    books = session.query(Book).filter_by(
        genre_id=genre_id).all()
    return jsonify(Bookitems=[i.serialize for i in books])


@app.route('/genres/<int:genre_id>/books/<int:book_id>/JSON')
def bookItemJSON(genre_id, book_id):
    book_Item = session.query(Book).filter_by(id=book_id).one()
    return jsonify(book_Item=book_Item.serialize)


@app.route('/genres/JSON')
def genresJSON():
    genres = session.query(Genre).all()
    return jsonify(genres=[g.serialize for g in genres])


@app.route('/books/JSON')
def booksJSON():
    books = session.query(Book).all()
    return jsonify(books=[g.serialize for g in books])

# Home Page


@app.route('/')
def home():
    return render_template('Home.html')

# Show all Genres


@app.route('/genres/')
def showgenres():
    genres = session.query(Genre).order_by(asc(Genre.name)).all()
    if 'username' not in login_session:
        return render_template('publicgenres.html', genres=genres)
    else:
        return render_template('genres.html', genres=genres)

# Show all books


@app.route('/genres/<int:genre_id>/')
@app.route('/genres/<int:genre_id>/books')
def showbooks(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    creator = getUserInfo(genre.user_id)
    books = session.query(Book).filter_by(genre_id=genre_id).all()
    if 'username' not in login_session:
        return render_template(
            'publicbooks.html',
            genre=genre,
            books=books,
            creator=creator)
    else:
        return render_template(
            'books.html',
            genre=genre,
            books=books,
            creator=creator)

# create a new genre


@app.route('/genres/new', methods=['GET', 'POST'])
def newgenre():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        login_session['user_id'] = getUserID(login_session['email'])
        newgenreitem = Genre(
            name=request.form['name'], user_id=login_session.get('user_id'))
        session.add(newgenreitem)
        flash('New Genre successfully created!', 'success')
        session.commit()

        return redirect(url_for('showgenres'))
    else:
        return render_template('newgenre.html')

# Create a new book


@app.route('/genres/<int:genre_id>/new/', methods=['GET', 'POST'])
def newbookItem(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    genre = session.query(Genre).filter_by(id=genre_id).one()
    genres = session.query(Genre).all()
    if 'username'in login_session:
        if request.method == 'POST':
            newBook = Book(
                genre_id=request.form['genre_id'],
                name=request.form['name'],
                author=request.form['author'],
                price=request.form['price'],
                description=request.form['description'],
                user_id=login_session['user_id'])
            session.add(newBook)
            session.commit()
            flash('New Book Item Successfully added!')
            return redirect(url_for('showbooks', genre_id=genre_id))
        else:
            return render_template(
                'newbookitem.html',
                genres=genres,
                genre=genre,
                genre_id=genre_id)

# Edit a genre


@app.route('/genres/<int:genre_id>/edit', methods=['GET', 'POST'])
def editgenre(genre_id):
    editedGenre = session.query(Genre).filter_by(id=genre_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedGenre.user_id != login_session['user_id']:
        flash("You are not authorized to edit this Genre. Please create your own Genre in order to edit.")  # NOQA
        return redirect(url_for('showbooks', genre_id=genre_id))
    if request.method == 'POST':
        if request.form['name']:
            editedGenre.name = request.form['name']
        session.add(editedGenre)
        flash('Genre Successfully Edited!')
        session.commit()
        return redirect(url_for('showbooks', genre_id=genre_id))
    else:
        return render_template(
            'editgenre.html',
            genre_id=genre_id,
            Gitem=editedGenre)

# Edit a book details


@app.route(
    '/genres/<int:genre_id>/<int:book_id>/edit/',
    methods=[
        'GET',
        'POST'])
def editbookItem(genre_id, book_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Book).filter_by(id=book_id).one()
    genre = session.query(Genre).filter_by(id=genre_id).one()
    if login_session['user_id'] != editedItem.user_id:
        flash("You are not authorized to edit book items to this genre. Please create your own genre in order to edit items.")  # NOQA
        return redirect(url_for('showbooks', genre_id=genre_id))
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['author']:
            editedItem.author = request.form['author']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        flash('Book Item Successfully Edited!')
        session.commit()
        return redirect(url_for('showbooks', genre_id=genre_id))
    else:
        return render_template(
            'editbookitem.html',
            genre_id=genre_id,
            book_id=book_id,
            item=editedItem)

# Delete a genre


@app.route('/genres/<int:genre_id>/delete', methods=['GET', 'POST'])
def deletegenre(genre_id):
    deletegenreitem = session.query(
        Genre).filter_by(id=genre_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if deletegenreitem.user_id != login_session['user_id']:
        flash("You are not authorized to delete this genre.Please create your own genre in order to delete.")  # NOQA
        return redirect(url_for('showbooks', genre_id=genre_id))

    if request.method == 'POST':
        session.delete(deletegenreitem)
        flash('%s Successfully Deleted' % deletegenreitem.name)
        session.commit()
        return redirect(url_for('showgenres', genre_id=genre_id))
    else:
        return render_template(
            'deletegenre.html',
            genre_id=genre_id,
            genre=deletegenreitem)

# Delete a book


@app.route(
    '/genres/<int:genre_id>/<int:book_id>/delete/',
    methods=[
        'GET',
        'POST'])
def deletebookItem(genre_id, book_id):
    if 'username' not in login_session:
        return redirect('/login')
    genre = session.query(Genre).filter_by(id=genre_id).one()
    deleteitem = session.query(Book).filter_by(id=book_id).one()
    if login_session['user_id'] != deleteitem.user_id:
        flash("You are not authorized to delete book items to this genre. Please create your own genre in order to delete items.")  # NOQA
        return redirect(url_for('showbooks', genre_id=genre_id))
    if request.method == 'POST':
        session.delete(deleteitem)
        session.commit()
        flash('Book Item Successfully Deleted!')
        return redirect(url_for('showbooks', genre_id=genre_id))
    else:
        return render_template('deletebookitem.html', item=deleteitem)

# Disconnect based on provider


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            if 'gplus_id' in login_session:
                del login_session['gplus_id']
            if 'credentials' in login_session:
                del login_session['access_token']
        if 'username' in login_session:
            del login_session['username']
        if 'email' in login_session:
            del login_session['email']
        if 'picture' in login_session:
            del login_session['picture']
        if 'user_id' in login_session:
            del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out!")
        return redirect(url_for('home'))
    else:
        flash("You were not logged in")
        return redirect(url_for('home'))


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


if __name__ == '__main__':
    app.secret_key = 'NKjzwlqlxGWI9VJx_M0Rn9gh'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
