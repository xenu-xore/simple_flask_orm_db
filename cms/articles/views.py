from flask import redirect, render_template, Blueprint, \
    flash, url_for, request, Response
from .forms import CreateArticle, CreateCategory, EditArticles, EditCategory
from flask_login import login_user, logout_user, \
    login_required
from cms import db
import psycopg2.errorcodes as rew
from cms.models import Category, Articles
from cms.articles.translate import transliterate
import sqlalchemy

# from flask_paginate import Pagination, get_page_parameter

articles_blueprint = Blueprint('articles', __name__)

# UNIQUE_VIOLATION для slug_cat, slug_art
i = 0


@articles_blueprint.route('/create_article/', methods=['GET', 'POST'])
@login_required
def create_article():
    form = CreateArticle(request.form)
    form.select_category.choices = [("", "---")] + [(g.id, g.name_category) for g in Category.query.all()]
    if request.method == 'POST' and form.validate_on_submit():

        article = Articles(
            title=form.title.data,
            short_description=form.short_description.data,
            article=form.article.data,
            category_id=form.select_category.data,
            slug_art=transliterate(form.slug_art.data)
        )
        try:
            db.session.add(article)
            db.session.commit()
            return redirect(url_for('articles.create_article'))

        except sqlalchemy.exc.SQLAlchemyError as error:

            foo = 0
            goo = 0
            try:
                foo = rew.lookup(error.orig.pgcode)
            except:
                goo = error.params[4]

            if foo == 'UNIQUE_VIOLATION' or goo == article.slug_art:
                global i
                i += 1
                flash(f"Дублирование URL: {goo, article.slug_art}")
                db.session.rollback()
                article = Articles(
                    title=article.title + '-' + str(i),
                    short_description=form.short_description.data,
                    article=form.article.data,
                    category_id=form.select_category.data,
                    slug_art=article.slug_art + '-' + str(i)
                )

                db.session.add(article)
                db.session.commit()
                flash(f"Дублирование URL: {error.params[1]}")
                return redirect(url_for('articles.create_article'))

    return render_template('user_templates/create_article.html', form=form)


@articles_blueprint.route('/create_category/', methods=['GET', 'POST'])
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
            return redirect(url_for('articles.create_category'))
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
                return redirect(url_for('articles.create_category'))
    return render_template('user_templates/create_category.html', form=form)


@articles_blueprint.route('/articles/', methods=['GET'], defaults={"page": 1})
@articles_blueprint.route('/articles/<int:page>/', methods=['GET'])
def get_all_articles(page):
    # articles = Articles.query.all()

    page = page
    per_page = 3  # Количество статей на 1 странице
    articles = Articles.query.order_by(Articles.date_publisher.desc()).paginate(page, per_page, error_out=False)
    return render_template('user_templates/get_all_articles.html', articles=articles)


@articles_blueprint.route('/articles/<string:slug_art>/')
def detail_article(slug_art):
    article = Articles.query.filter_by(slug_art=slug_art).one_or_none()

    if article is not None:
        return render_template('user_templates/detail_article.html', article_one=article)

    else:
        return render_template('error/error_404.html'), 404


@articles_blueprint.route('/category/<string:slug_cat>/')
def detail_category(slug_cat):
    category = Category.query.filter_by(slug_cat=slug_cat).one_or_none()

    if category is not None:
        return render_template('user_templates/detail_category.html', category_one=category)

    else:
        return render_template('error/error_404.html'), 404


@articles_blueprint.route('/category/', methods=['GET'], defaults={"page": 1})
@articles_blueprint.route('/category/<int:page>/', methods=['GET'])
def get_all_categories(page):
    page = page
    per_page = 3  # Количество статей на 1 странице
    categories = Category.query.order_by(Category.name_category.desc()).paginate(page, per_page, error_out=False)
    return render_template('user_templates/get_all_categories.html', categories=categories)


@articles_blueprint.route('/edit_article/<string:slug_art>/', methods=['GET', 'POST'])
@login_required
def edit_article(slug_art):
    try:
        art = Articles.query.filter_by(slug_art=slug_art).first()
        form = EditArticles(request.form, obj=art)
        form.select_cat.choices = [(art.category_owner.id, art.category_owner.name_category)] + \
                                  [(g.id, g.name_category) for g in Category.query.order_by('name_category') \
                                   if g.name_category != art.category_owner.name_category]

        if request.method == 'POST' and form.validate_on_submit():
            form.populate_obj(art)
            art.title = form.title.data
            art.short_description = form.short_description.data
            art.article = form.article.data
            art.category_id = form.select_cat.data
            art.slug_art = transliterate(form.slug_art.data)

            try:
                db.session.commit()
                flash(u'Сведения обновлены!')
                return redirect(url_for('articles.edit_article', slug_art=art.slug_art))
            except Exception as error:
                flash(f'Что-то пошло не так: {error}')
                return redirect(url_for('articles.edit_article', slug_art=art.slug_art))

        return render_template('user_templates/edit_article.html', form=form, art=art)

    except Exception as error:
        return render_template('user_templates/edit_article.html', error=error)


@articles_blueprint.route('/edit_category/<string:slug_cat>/', methods=['GET', 'POST'])
@login_required
def edit_category(slug_cat):
    try:
        cat = Category.query.filter_by(slug_cat=slug_cat).one_or_none()

        print(cat)
        form = EditCategory(request.form, obj=cat)

        if request.method == 'POST' and form.validate_on_submit():
            form.populate_obj(cat)
            cat.name_category = form.name_category.data
            cat.slug_cat = transliterate(form.slug_cat.data)

            try:
                db.session.commit()
                flash(u'Сведения обновлены!')
                return redirect(url_for('articles.edit_category', slug_cat=cat.slug_cat))
            except Exception as error:
                flash(f'Что-то пошло не так: {error}')
                return redirect(url_for('articles.edit_category', slug_cat=cat.slug_cat))

        return render_template('user_templates/edit_category.html', form=form, cat=cat)

    except Exception as error:
        return render_template('user_templates/edit_category.html', error=error)
