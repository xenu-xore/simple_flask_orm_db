from flask import redirect, render_template, Blueprint, \
    flash, url_for, request, Response
from .forms import CreateCategory, EditCategory
from flask_login import login_user, logout_user, \
    login_required
from cms import db
import psycopg2.errorcodes as rew
from cms.models import Category
from cms.articles.translate import transliterate
import sqlalchemy

# from flask_paginate import Pagination, get_page_parameter

category_blueprint = Blueprint('category', __name__)

# UNIQUE_VIOLATION для slug_cat, slug_art
i = 0


@category_blueprint.route('/create_category/', methods=['GET', 'POST'])
@login_required
def create_category():
    form = CreateCategory(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        category = Category(
            name_category=form.name_category.data,
            slug_cat=transliterate(form.slug_cat.data)
        )
        try:
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('category.create_category'))
        except sqlalchemy.exc.SQLAlchemyError as error:
            foo = 0
            goo = 0
            try:
                foo = rew.lookup(error.orig.pgcode)
            except:
                goo = error.params[1]
            if foo == 'UNIQUE_VIOLATION' or goo == category.slug_cat:
                flash(f"Дублирование URL: {error.orig}")
                db.session.rollback()
                global i
                i += 1
                category = Category(
                    name_category=category.name_category + '-' + str(i),
                    slug_cat=category.slug_cat + '-' + str(i)
                )

                db.session.add(category)
                db.session.commit()
                #     flash(f"Дублирование URL: {error.params[1]}")
                return redirect(url_for('category.create_category'))
    return render_template('user_templates/category/create_category.html', form=form)


@category_blueprint.route('/category/<string:slug_cat>/')
def detail_category(slug_cat):
    category = Category.query.filter_by(slug_cat=slug_cat).one_or_none()

    if category is not None:
        return render_template('user_templates/category/detail_category.html', category_one=category)

    else:
        return render_template('error/error_404.html'), 404


@category_blueprint.route('/category/', methods=['GET'], defaults={"page": 1})
@category_blueprint.route('/category/<int:page>/', methods=['GET'])
def get_all_categories(page):
    page = page
    per_page = 3  # Количество статей на 1 странице
    categories = Category.query.order_by(Category.name_category.desc()).paginate(page, per_page, error_out=True)
    return render_template('user_templates/category/get_all_categories.html', categories=categories)


@category_blueprint.route('/edit_category/<string:slug_cat>/', methods=['GET', 'POST'])
@login_required
def edit_category(slug_cat):
    try:
        cat = Category.query.filter_by(slug_cat=slug_cat).one_or_none()

        if cat is not None:
            form = EditCategory(request.form, obj=cat)

            if request.method == 'POST' and form.validate_on_submit():
                form.populate_obj(cat)
                cat.name_category = form.name_category.data
                cat.slug_cat = transliterate(form.slug_cat.data)

                try:
                    db.session.commit()
                    flash(u'Сведения обновлены!')
                    return redirect(url_for('category.edit_category', slug_cat=cat.slug_cat))
                except Exception as error:
                    flash(f'Что-то пошло не так: {error}')
                    return redirect(url_for('category.edit_category', slug_cat=cat.slug_cat))

            return render_template('user_templates/category/edit_category.html', form=form, cat=cat)
        else:
            return render_template('error/error_404.html'), 404
    except Exception as error:
        return render_template('user_templates/category/edit_category.html', error=error)
