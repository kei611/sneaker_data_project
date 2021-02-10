#################
#### imports ####
#################
 
from flask import render_template, Blueprint, request, redirect, url_for, flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os
import pickle

from project import db, app
from project.models import Sneaker, User
from .forms import AddSneakerForm, EditSneakerForm, PredPriceForm
from .vectorizer import concat_features


cur_dir = os.path.dirname(__file__)
clf5 = pickle.load(open(os.path.join(cur_dir, 'objects', 'classifier5.pkl'), 'rb'))

################
#### config ####
################
 
sneakers_blueprint = Blueprint('sneakers', __name__)
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

##########################
#### helper functions ####
##########################

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'info')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def classify(retail_price, img_name, text):

    X = concat_features(retail_price, img_name, text)
    y = clf5.predict(X)
    proba = clf5.predict_proba(X).max()

    if y == 'lv0':
        price_min = retail_price - 10000
        pred = 'Less than {} JPY'.format(price_min)
    elif y == 'lv1':
        price_min = retail_price - 10000
        price_max = retail_price - 2500
        pred = '{} - {} JPY'.format(price_min, price_max)
    elif y == 'lv2':
        price_min = retail_price - 2500
        price_max = retail_price + 2500
        pred = '{} - {} JPY'.format(price_min, price_max)
    elif y == 'lv3':
        price_min = retail_price + 2500
        price_max = retail_price + 10000
        pred = '{} - {} JPY'.format(price_min, price_max)
    elif y == 'lv4':
        price_max = retail_price + 10000
        pred = 'More than {} JPY'.format(price_max)

    return pred, proba


################
#### routes ####
################
 
@sneakers_blueprint.route('/')
def public_sneakers():
    all_public_sneakers = Sneaker.query.filter_by(is_public=True)
    return render_template('public_sneakers.html', public_sneakers=all_public_sneakers)


@sneakers_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_sneaker():
    # Cannot pass in 'request.form' to AddRecipeForm constructor, as this will cause 'request.files' to not be
    # sent to the form.  This will cause AddRecipeForm to not see the file data.
    # Flask-WTF handles passing form data to the form, so not parameters need to be included.
    form = AddSneakerForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # check if the post request has the recipe_image part
            if 'sneaker_image' not in request.files:
                flash('No sneaker image provided!')
                return redirect(request.url)

            file = request.files['sneaker_image']

            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if not file:
                flash('File is empty!')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOADS_DEFAULT_DEST'], filename)
                file.save(filepath)
                url = os.path.join(app.config['UPLOADS_DEFAULT_URL'], filename)
            else:
                filename = ''
                url = ''

            name = form.sneaker_model_name.data
            price = form.sneaker_retail_price.data

            new_sneaker = Sneaker(name, price, current_user.id, form.sneaker_public.data, filename, url)
            
            db.session.add(new_sneaker)
            db.session.commit()
            flash('New sneaker, {}, added!'.format(new_sneaker.sneaker_model_name), 'success')
            return redirect(url_for('sneakers.user_sneakers'))
        else:
            flash_errors(form)
            flash('ERROR! Sneaker was not added.', 'error')

    return render_template('add_sneaker.html', form=form)


@sneakers_blueprint.route('/sneakers')
@login_required
def user_sneakers():
    all_user_sneakers = Sneaker.query.filter_by(user_id=current_user.id)
    return render_template('user_sneakers.html', user_sneakers=all_user_sneakers)


@sneakers_blueprint.route('/sneaker/<sneaker_id>')
def sneaker_details(sneaker_id):
    # sneaker_with_user = db.session.query(Sneaker, User).join(User).filter(Sneaker.id == sneaker_id).first()
    sneaker = Sneaker.query.filter_by(id=sneaker_id).first_or_404()
    
    # if sneaker_with_user is not None:
    if sneaker.is_public:
        return render_template('sneaker_detail.html', sneaker=sneaker)
    else:
        if current_user.is_authenticated and sneaker.user_id == current_user.id:
            return render_template('sneaker_detail.html', sneaker=sneaker)
        else:
            flash('Error! Incorrect permissions to access this sneaker.', 'error')

    return redirect(url_for('sneakers.public_sneakers'))


@sneakers_blueprint.route('/delete/<sneaker_id>')
@login_required
def delete_sneaker(sneaker_id):
    sneaker = Sneaker.query.filter_by(id=sneaker_id).first_or_404()

    if not sneaker.user_id == current_user.id:
        flash('Error! Incorrect permissions to delete this sneaker.', 'error')
        return redirect(url_for('sneakers.public_sneakers'))

    db.session.delete(sneaker)
    db.session.commit()
    flash('{} was deleted.'.format(sneaker.sneaker_model_name), 'success')
    return redirect(url_for('sneakers.user_sneakers'))


@sneakers_blueprint.route('/edit/<sneaker_id>', methods=['GET', 'POST'])
@login_required
def edit_sneaker(sneaker_id):
    # Cannot pass in 'request.form' to EditRecipeForm constructor, as this will cause 'request.files' to not be
    # sent to the form.  This will cause RecipeForm to not see the file data.
    # Flask-WTF handles passing form data to the form, so not parameters need to be included.
    form = EditSneakerForm()
    sneaker = Sneaker.query.filter_by(id=sneaker_id).first_or_404()

    if not sneaker.user_id == current_user.id:
        flash('Error! Incorrect permissions to edit this sneaker.', 'error')
        return redirect(url_for('sneakers.public_sneakers'))

    if request.method == 'POST':
        if form.validate_on_submit():
            update_counter = 0

            if form.sneaker_model_name.data is not None and form.sneaker_model_name.data != sneaker.sneaker_model_name:
                flash('DEBUG: Updating sneaker.sneaker_model_name to {}.'.format(form.sneaker_model_name.data), 'debug')
                update_counter += 1
                sneaker.sneaker_model_name = form.sneaker_model_name.data

            if form.sneaker_retail_price.data is not None and form.sneaker_retail_price.data != sneaker.sneaker_retail_price:
                flash('DEBUG: Updating sneaker.sneaker_retail_price to {}.'.format(form.sneaker_retail_price.data), 'debug')
                update_counter += 1
                sneaker.sneaker_retail_price = form.sneaker_retail_price.data

            if form.sneaker_public.data != sneaker.is_public:
                flash('DEBUG: Updating sneaker.is_public to {}.'.format(form.sneaker_public.data), 'debug')
                update_counter += 1
                sneaker.is_public = form.sneaker_public.data

            if form.sneaker_image.has_file():
                flash('DEBUG: Updating sneaker.image_filename to {}.'.format(form.sneaker_image.data), 'debug')
                update_counter += 1
                file = request.files['sneaker_image']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename))
                url = os.path.join(app.config['UPLOADED_IMAGES_URL'], filename)
                sneaker.image_filename = filename
                sneaker.image_url = url

            if update_counter > 0:
                db.session.add(sneaker)
                db.session.commit()
                flash('Sneaker has been updated for {}.'.format(sneaker.sneaker_model_name), 'success')
            else:
                flash('No updates made to the sneaker ({}). Please update at least one field.'.format(sneaker.sneaker_model_name), 'error')

            return redirect(url_for('sneakers.sneaker_details', sneaker_id=sneaker_id))
        else:
            flash_errors(form)
            flash('ERROR! Sneaker was not edited.', 'error')

    return render_template('edit_sneaker.html', form=form, sneaker=sneaker)


@sneakers_blueprint.route('/admin/delete/<sneaker_id>')
@login_required
def admin_delete_sneaker(sneaker_id):
    sneaker = Sneaker.query.filter_by(id=sneaker_id).first_or_404()

    if not current_user.role == 'admin':
        flash('Error! Incorrect permissions to delete this sneaker.', 'error')
        return redirect(url_for('sneakers.public_sneakers'))

    db.session.delete(sneaker)
    db.session.commit()
    flash('{} was deleted.'.format(sneaker.sneaker_model_name), 'success')
    return redirect(url_for('sneakers.admin_view_sneakers'))


@sneakers_blueprint.route('/admin/edit/<sneaker_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_sneaker(sneaker_id):
    # Cannot pass in 'request.form' to EditRecipeForm constructor, as this will cause 'request.files' to not be
    # sent to the form.  This will cause RecipeForm to not see the file data.
    # Flask-WTF handles passing form data to the form, so not parameters need to be included.
    form = EditSneakerForm()
    sneaker = Sneaker.query.filter_by(id=sneaker_id).first_or_404()

    if current_user.role != 'admin':
        abort(403)

    if request.method == 'POST':
        if form.validate_on_submit():
            sneaker.import_form_data(request, form)
            db.session.add(sneaker)
            db.session.commit()
            flash('Sneaker has been updated for {}'.format(sneaker.sneaker_model_name), 'success')
            return redirect(url_for('sneakers.admin_view_sneakers'))
        else:
            flash_errors(form)
            flash('ERROR! Sneaker was not edited.', 'error')

    return render_template('admin_edit_sneaker.html', form=form, sneaker=sneaker)


@sneakers_blueprint.route('/admin_view_sneakers')
@login_required
def admin_view_sneakers():
    if current_user.role != 'admin':
        abort(403)
    else:
        sneakers = Sneaker.query.order_by(Sneaker.id).all()
        return render_template('admin_view_sneakers.html', sneakers=sneakers)
    return redirect(url_for('users.login'))



#POST method is to allow the user to submit the form data
#GET method is to allow the user to receive the form
@sneakers_blueprint.route('/pred', methods=['GET', 'POST'])
def pred_price():
    # Cannot pass in 'request.form' to AddSneakerForm constructor, as this will cause 'request.files' to not be
    # sent to the form.  This will cause AddSneakerForm to not see the file data.
    # Flask-WTF handles passing form data to the form, so not parameters need to be included.
    form = PredPriceForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # check if the post request has the recipe_image part
            if 'sneaker_image' not in request.files:
                flash('No sneaker image provided!')
                return redirect(request.url)

            file = request.files['sneaker_image']

            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if not file:
                flash('File is empty!')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOADS_DEFAULT_DEST'], filename)
                file.save(filepath)
                url = os.path.join(app.config['UPLOADS_DEFAULT_URL'], filename)
            else:
                filename = ''
                url = ''

            name = form.sneaker_model_name.data
            price = form.sneaker_retail_price.data

            # new_sneaker = Sneaker(name, 
            # price, 
            # filename, 
            # url)

            # db.session.add(new_sneaker)
            # db.session.commit()
            # flash('New sneaker, {}, added!'.format(new_sneaker.sneaker_model_name), 'success')
            
            pred, proba = classify(price, filepath, name)
            
            return render_template('results.html', 
            content_name=name, 
            content_price=price,
            prediction=pred, 
            probability=round(proba*100, 2))

        else:
            flash_errors(form)
            flash('ERROR! Sneaker was not added.', 'error')
        
    return render_template('pred_price.html', form=form)

