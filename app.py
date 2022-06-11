
# Imports
#----------------------------------------------------------------------------#
from asyncio.base_subprocess import WriteSubprocessPipeProto
import sys


import sys
import json
from datetime import datetime
from flask_migrate import Migrate
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler, exception
import flask_sqlalchemy
from flask_wtf import Form
from jmespath import search
from forms import *
from flask_wtf.csrf import CSRFProtect
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
CSRFProtect(app)
db = SQLAlchemy(app)
migrate=Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.column(db.String(200))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link =db.Column(db.String(150))
    seeking_talent=db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(600))
    shows = db.relationship('Show')
    artists=  db.relationship('Artist',secondary='shows',back_populates='venues')
   

 
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link =db.Column(db.String(500))
    seeking_venue = db.Column(db.String(250))
    seeking_description = db.Column(db.String(210))
    shows = db.relationship('Show')
    venues = db.relationship(
      'Venue',
      secondary='shows',
      back_populates='artists'
    )
    
    #Artistlist= db.Column(db.Integer, db.ForeignKey('Artistlist.id'), nullable =False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.



class Show(db.Model):
  __tablename__ ='shows'
  id = db.Column(db.Integer, primary_key =True)
  start_time = db.Column(db.DateTime, nullable=False)
  artist = db.relationship('Artist')
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete='CASCADE'), nullable=False)
  venue = db.relationship('Venue')
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete='CASCADE'), nullable= False)


 


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime



#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------



@app.route('/venues')
def venues():

  data_areas = []

  areas = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()


  for area in areas:
    data_venues = []


    venues = Venue.query.filter_by(state=area.state).filter_by(city= area.city).all()


    for venue in venues:

      upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all()

      data_venues.append({
        'id':venue.id,
        'name':venue.name,
        'num_upcoming_shows': len(upcoming_shows)
      })

      data_areas.append({
        'city':area.city,
        'state':area.state,
        'venues':data_venues
      })
  return render_template ('pages/venues.html', areas=data_areas)
          

  

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term =request.form['search_term']
  search="%{}%".format(search_term)

  venues = Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.name.match(search)) \

  data_venues = []
  for venue in venues:
    upcoming_shows = db.session.query(Show),filter(Show.venue_id ==venue.id).filter(Show.start_time > datetime.now()).all()

    data_venues.append({
      'id':venue.id,
      'name':venue.name,
      'upcoming_shows':len(upcoming_shows)

      })

  results = {
    'venues':data_venues,
    'count':len(venues)
  }
  return render_template('pages/search_vennues.html', results=results, search_term=request.form.get('search_term', ''))


        
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"



  

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  data_venue =Venue.query.filter(Venue.id == venue_id).first()

  upcoming_shows = Show.query.filter(Show.venue_id ==venue_id).filter(Show.start_time > datetime.now()).all()

  if len(upcoming_shows) >  0:
    data_upcoming_shows = []
    for upcoming_show in upcoming_shows:
          artist=Artist.query.filter(Artist.id == upcoming_show.artist_id) .first()

          data_upcoming_shows.append({
            'artist_id':artist.id,
            'artist_name': artist.name,
            'artist_image_link':artist.image_link,
            'start_time':str(upcoming_show.start_time)
          })
    data_venue.upcoming_shows = data_upcoming_shows
    data_venue.uupcoming_shows_count = len(data_upcoming_shows)

  past_shows =Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
  if len(past_shows) > 0:
      data_past_shows = []



      for past_show in past_shows:
        artist = Artist.query.filter(Artist.id == past_show.artist_id) .first()

        data_past_shows.append({
          'artist_id': artist.id,
          'artist_name':artist.name,
          'artist_image_link': artist.image_link,
          'start_time':str(past_show.start_time)
         })

      data_venue.past_shows = data_past_shows
      data_venue.pats_shows_count = len(data_past_shows)

  return render_template('pages/show_venue.html', venue=data_venue)

#  Create Venue
#  ----------------------------------------------------------------






@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  form=VenueForm    
    
  name = request.form['name']
  city = request.form['city']
  state =request.form['state']
  address=request.form['phone']
  phone=request.form['phone']
  genres=request.form.getlist('genre')
  image_link= request.form['image_link']
  facebook_link = request.form['facebook_link']
  website_link =request.form['website_link']
  seeking_talent =True if 'seeking_talent' in request.form else False
  seeking_description =request.form['seeking_description']

  try:

      venue =Venue(
        name=name,
        city=city,
        state=state,
        address=address,
        phone=phone,
        genres =genres,
        image_link=image_link,
        facebook_link=facebook_link,
        website_link=website_link,
        seeking_talent=seeking_talent,
        seeking_description=seeking_description,
      )
      db.session.add(venue)
      db.session.commit()
  except Exception:
      error =True
      db.session.rollback()
      print(sys.exe_info())


  if error:
      flash('an error occured. Venue', + request.form['name'] + 'could not belisted')
  if not error:
      
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  return render_template('pages/home.html')




@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error  = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except exception as e:
    error = True
    db.session.rollback()
    print(sys.exe_info())
    return render_template('errors/500.html', error=str(e))
  finally:
    db.session.close()


  if error:
    flash('An error occured. Venue could not completed.', 'danger')
  if not error:
    flash('Venue was successfully deleted!', 'success')
    return render_template('pages/home.html')
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------



@app.route('/artists')
def artists():


  data_artists = Artist.query.with_entities(Artist.id, Artist.name).order_by('id').all()

 

  return render_template('pages/artists.html', artists=data_artists)
  


@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term =request.form['search_term']
  search = "%{}".format(search_term)


  artist =Artist.query.with_entities(Artist.id, Artist.name).filter(Artist.name.match(search)).all()


  data_artists = []

  for artist in artists:

    upcoming_shows = db.session.query(Show).filter(Show.artist_id ==artist.id).filter(Show.start_time > datetime.now()).all()

    data_artists.append({
          'id':artist.id,
          'name':artist.name,
          'num_upcoming_shows':len(upcoming_shows)
        })

      
  results = {
        'data':data_artists,
        'count':len(artists)
     }
      
  return render_template('pages/search_artists.html', results=results, search_term=request.form.get('search_term', ''))
      

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  # shows the artist page with the given artist_id
 
  # TODO: replace with real artist data from the artist table, using artist_id
  data = Artist.query.filter(Artist.id == artist_id).first()
  upcoming_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now())


  if len(upcoming_shows) > 0:
    data_upcoming_shows = []

    for upcoming_show in upcoming_shows:
      venue =Venue.query.filter(Venue.id == upcoming_show.venue_id).first()


      data_upcoming_shows.append({'venue_id':venue.id,'venue_name':venue.name,'venue_image_link':venue.image_link,'start_time':str(upcoming_show.start_time)})
    
      data.upcoming_shows = data_upcoming_shows
      data.upcoming_shows_count = len(data_upcoming_shows)

  
  past_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()

  if len(past_shows) > 0:
    data_past_shows = []

    for past_show in  past_shows:
      venue =Venue.query.filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()


      data_past_shows.append({
        'venue_id': venue.id,
        'venue_name':venue.name,
        'venue_image_link':venue.image_link,
        'start_time':str(past_show.start_time)

      })

      data.past_shows = data_past_shows
      data.past_shows_count = len(data_past_shows)

  return render_template('pages/show_artist.html', artist = data)








#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/', methods=['GET'])
def edit_artistedit(artist_id):

  artist = Artist.query.filter(Artist.id == artist_id).first()

  form = ArtistForm()
  form.name.data  =artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data= artist.seeking_venue
  form.seeking_description.data =artist.seeking_description
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error =False
  name = request.form['name']
  city = request.form['city']
  state =request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  image_link = request.form['image_link']
  facebook_link  = request.form['facebook_link']
  website_link =request.form['website_link']
  seeking_talent  = True if 'seeking_talent' in request.form else False
  seeking_description = request.form['seeking_description']

  try:
    
    artist = Artist.query.get(artist_id)

    artist.name = name
    artist.city = city
    artist.state =state
    artist.phone = phone
    artist.genres = genres
    artist.image_link = image_link
    artist.facebook_link  = facebook_link
    artist.website_link =website_link
    artist.seeking_talent  = seeking_talent
    seeking_description = seeking_description

  except exception:
    error =True
    db.session.rollback()
    print(sys.exe_info())

  finally:
    db.session.close()

  if error:

    flash('Artist' + request.form['name'] + 'was successfully added!' 'success')

  if not error:
    flash('Artist', +request.form['name'] + 'was updated successful')

  return redirect(url_for('show_artist', artist_id=artist_id))







@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  venue = Venue.query.filter(Venue.id == venue_id).first()

  form = VenueForm()
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)


  # TODO: populate form with values from venue with ID <venue_id>

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  error = False

  error = False
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form('genres')
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  website_link = request.form['website_link']
  seeking_talent = True if 'seeking_talent' in request.form else False
  seeking_description = request.form['seeking_description']


  try:

    venue = venue.query.get(venue_id)
    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.genres = genres
    venue.image_link = image_link
    venue.facebook_link = facebook_link
    venue.website_lin= website_link
    venue.seeking_talent = seeking_talent
    venue.seeking_description = seeking_description

    db.session.commit()

  except Exception:
    error = True
    db.session.rollback()
    print(sys.exe_info())

  finally:
    db.session.close()


  if error:
  
    flash('An error occured. venue' + name +'could not be updated.', 'danger')

  if not error:
    flash('Venue' + name + 'was successful updated', 'success')

  return redirect(url_for('show_venue', venue_id=venue_id))
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
 # return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)




@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error=False
  form =ArtistForm()
  
 
     


    
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  image_link=request.form['image_link']
  facebook_link =request.form['facebook_link']
  website_link =request.form['website_link']
  seeking_venue = True if 'seeking' in request.form else False
  seeking_description=request.form['seeking_description']

  try:
      artist = Artist(
        name = name,
        city=city,
        state= state,
        phone =phone,
        genres=genres,
        image_link=image_link,
        facebook_link =facebook_link,
        website_link=website_link,
        seeking_venue= seeking_venue,
        seeking_description=seeking_description,
        )

      db.session.add(artist)
      db.session.commit()

  except exception:
      error =True
      db.session.rollback()
      print(sys.exe_info())
  finally:
      db.session.close()


  if error:
      
        
      flash('An error occured. Artist' + request.form['name'] + 'could not be listed.', 'danger')

  if not error:
      flash(
        'Artist' + request.form['name'] + 'was succesfully listed')


  return render_template('pages/home.html')


  



  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []

  shows = db.session.query(Venue.name,Artist.name,Artist.image_link,Show.venue_id,Show.artist_id,Show.start_time).filter(Venue.id == Show.venue_id, Artist.id ==Show.artist_id)


  for show in shows:
    data.append({
      'venue_name':show[0],
      'artist_name':show[1],
      'artist_image_link':show[2],
      'venue_id':show[4],
      'start_time':str(show[5])

    })

  return render_template('pages/shows.html', shows=data)
    

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  error = False


  artist_id =request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']

  try:
    shows = Show(
      artist_id = artist_id,
      venue_id =venue_id,
      start_time=start_time,

    )


    db.session.add(shows)
    db.session.commit()


  except Exception:
    error =True
    db.session.rollback()
    print(sys.exe_info())
  finally:
    db.session.close()


  if error:
   
    flash(
      'An error occured. show could not listed.','danger'
    )

  if not error:
    flash('show was successfully listed', 'success')

  return render_template ('pages/home.html')


  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
