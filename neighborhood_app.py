from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Category, Place
from user_actions import createUser, getUserID
from functools import wraps
from flask import Flask, render_template, request, make_response, session
from flask import flash, redirect, url_for, jsonify
from flask_seasurf import SeaSurf
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import json
import httplib2
import requests

APPLICATION_NAME = "Neighborhood Guide"
app = Flask(__name__)
csrf = SeaSurf(app)

G_CLIENT_ID = json.loads(
    open('g_client_secrets.json', 'r').read())['web']['client_id']

# Connect to database and create session
engine = create_engine('sqlite:///neighborhood.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()


# Loads all categories and renders specified templates
def renderGuidePage(template, **kwargs):
    categories = db_session.query(Category).order_by(asc(Category.name))
    return render_template(template, categories=categories, **kwargs)


# Login requirement decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session['username'] is None:
            flash('Login required.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
# Home page
def showGuide():
    places = db_session.query(Place).order_by(desc(Place.id)).limit(5)
    return renderGuidePage('main.html',
                           places=places)


@app.route('/login/')
# Login
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    session['state'] = state
    return renderGuidePage('login.html', STATE=state)


@csrf.exempt
@app.route('/gconnect', methods=['POST'])
# Google authentication
def gconnect():
    # Validate state token
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('g_client_secrets.json', scope='')
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
    if result['issued_to'] != G_CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = session.get('credentials')
    stored_gplus_id = session.get('gplus_id')
    if stored_credentials and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id
    session['credentials'] = credentials.to_json()

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']
    session['provider'] = 'google'

    # See if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id

    output = ''
    output += 'Welcome, '
    output += session['username']
    output += '!'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % session['username'])
    print "done!"
    return output


# Disconnect based on provider
@app.route('/logout/')
def showLogout():
    if 'provider' in session:
        if session['provider'] == 'google':
            gdisconnect()
            del session['gplus_id']
            del session['credentials']
        del session['username']
        del session['email']
        del session['picture']
        del session['user_id']
        del session['provider']
        flash("You have successfully been logged out.")
    else:
        flash("You were not logged in")
    return redirect(url_for('showGuide'))


@app.route('/gdisconnect')
# Disconnect from Google login
def gdisconnect():
    # Only disconnect a connected user.
    credentials = session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = session.get('access_token')
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
    return redirect(url_for('showGuide'))


@app.route('/places/<int:categoryID>/')
# Show list of places by category
def showCategory(categoryID):
    activeCategory = db_session.query(Category).filter_by(
        id=categoryID).one()
    categoryPlaces = db_session.query(Place).filter_by(
        category=activeCategory).all()
    return renderGuidePage('category.html',
                           selected_category=activeCategory,
                           selected_places=categoryPlaces)


@app.route('/places/<int:categoryID>/<int:placeID>/')
# Show individual place's page
def showPlace(categoryID, placeID):
    activePlace = db_session.query(Place).filter_by(id=placeID).one()
    return renderGuidePage('place.html',
                           selected_place=activePlace)


@app.route('/places/new/', methods=['GET', 'POST'])
@login_required
# Allow logged in user to create a new place to add to guide
def newPlace():
    if request.method == 'POST':
        matched_category = db_session.query(Category).filter_by(
            name=request.form['category']).one()
        newPlace = Place(
            name=request.form['name'],
            neighborhood=request.form['neighborhood'],
            description=request.form['description'],
            category_id=matched_category.id,
            user_id=session['user_id'])
        db_session.add(newPlace)
        flash('New place "%s" successfully created.' % newPlace.name)
        db_session.commit()
        return redirect(url_for('showPlace',
                                categoryID=newPlace.category_id,
                                placeID=newPlace.id))
    else:
        return renderGuidePage('newplace.html')


@app.route('/places/<int:categoryID>/<int:placeID>/edit/',
           methods=['GET', 'POST'])
@login_required
# Allow logged in user to edit an existing place in guide
def editPlace(categoryID, placeID):
    activePlace = db_session.query(Place).filter_by(id=placeID).one()
    if activePlace.user_id == session['user_id']:
        if request.method == 'POST':
            if (request.form['name'] and
               request.form['name'] != activePlace.name):
                activePlace.name = request.form['name']
                flash(
                    'Place name successfully changed to "%s".'
                    % activePlace.name)
            if (request.form['neighborhood'] and
               request.form['neighborhood'] != activePlace.neighborhood):
                activePlace.neighborhood = request.form['neighborhood']
                flash(
                    'Place neighborhood successfully changed to "%s".'
                    % activePlace.neighborhood)
            if (request.form['category'] and
               request.form['category'] != activePlace.category.name):
                matched_category = db_session.query(Category).filter_by(
                    name=request.form['category']).one()
                activePlace.category = matched_category
                flash(
                    'Place category successfully changed to "%s".'
                    % activePlace.category.name)
            if (request.form['description'] and
               request.form['description'] != activePlace.description):
                activePlace.description = request.form['description']
                flash(
                    'Place description successfully changed to "%s".'
                    % activePlace.description)
            db_session.add(activePlace)
            db_session.commit()
            return redirect(url_for('showPlace',
                                    categoryID=activePlace.category_id,
                                    placeID=activePlace.id))
        else:
            return renderGuidePage('editplace.html',
                                   place=activePlace)
    else:
        flash(
            'Error: You do not have permission to edit %s.'
            % activePlace.name)
        return redirect(url_for('showPlace',
                                categoryID=activePlace.category_id,
                                placeID=activePlace.id))


@app.route('/places/<int:categoryID>/<int:placeID>/delete/')
@login_required
# Allow logged in user to edit an existing place in guide
def deletePlace(categoryID, placeID):
    activePlace = db_session.query(Place).filter_by(id=placeID).one()
    if activePlace.user_id == session['user_id']:
        db_session.delete(activePlace)
        flash('%s successfully deleted.' % activePlace.name)
        db_session.commit()
        return redirect(url_for('showCategory',
                                categoryID=activePlace.category_id))
    else:
        flash(
            'Error: You do not have permission to delete %s.'
            % activePlace.name)
        return redirect(url_for('showPlace',
                                categoryID=activePlace.category_id,
                                placeID=activePlace.id))


@app.route('/places/<int:categoryID>/children/JSON/')
# JSON APIs to view information for all places in a category
def categoryPlacesJSON(categoryID):
    activeCategory = db_session.query(Category).filter_by(
        id=categoryID).one()
    categoryPlaces = db_session.query(Place).filter_by(
        category=activeCategory).all()
    return jsonify(CategoryPlaces=[i.serialize for i in categoryPlaces])


@app.route('/places/<int:categoryID>/self/JSON/')
# JSON APIs to view information for a category
def categorySelfJSON(categoryID):
    activeCategory = db_session.query(Category).filter_by(
        id=categoryID).one()
    return jsonify(CategorySelf=activeCategory.serialize)


@app.route('/places/<int:categoryID>/<int:placeID>/JSON/')
# JSON APIs to view information for a place
def placeJSON(categoryID, placeID):
    activePlace = db_session.query(Place).filter_by(
        id=placeID).one()
    return jsonify(Place=activePlace.serialize)


if __name__ == '__main__':
    app.secret_key = 'professor_pipsqueak'
    app.debug = True
    app.run()
