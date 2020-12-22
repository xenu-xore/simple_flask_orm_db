from flask import redirect, render_template, Blueprint, \
    flash, url_for, request, Response
from .forms import CreateArticle, CreateCategory, EditArticles
from flask_login import login_user, logout_user, \
    login_required
from cms import db
from cms.models import Category, Articles
from cms.articles.translate import transliterate

# from flask_paginate import Pagination, get_page_parameter

articles_blueprint = Blueprint('articles', __name__)


@articles_blueprint.route('/create_article/', methods=['GET', 'POST'])
@login_required
def create_article():
    form = CreateArticle(request.form)
    try:
        form.select_category.choices = [("", "---")] + [(g.id, g.name_category) for g in Category.query.all()]
        if request.method == 'POST' or request.method == "GET" and form.validate_on_submit():

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
            except Exception as error:
                flash(f'Что-то пошло не так: {error}')
                return redirect(url_for('articles.create_article'))
        return render_template('user_templates/create_article.html', form=form)
    except Exception as error:
        return render_template('error/error_404.html', error=error), 404


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
        except Exception as error:
            flash(f'Что-то пошло не так {error}')
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


@articles_blueprint.route('/category/')
def get_all_categories():
    categories = Category.query.all()
    return render_template('user_templates/get_all_categories.html', categories=categories)


@articles_blueprint.route('/edit_article/<string:slug_art>/', methods=['GET', 'POST'])
@login_required
def edit_article(slug_art):
    try:
        art = Articles.query.filter_by(slug_art=slug_art).first()
        form = EditArticles(request.form,obj=art)
        form.select_cat.choices = [("", "Выберите категорию")] + \
                                  [(g.id, g.name_category) for g in Category.query.order_by('name_category')]
        if request.method == 'POST' or request.method == "GET" and form.validate_on_submit():

            try:
                form.populate_obj(art)
                art.title = form.title.data,
                art.short_description = form.short_description.data,
                art.article = form.article.data,
                art.category_id = form.select_cat.data,
                art.slug_art = transliterate(form.slug_art.data)

                db.session.commit()
                flash(art.title)
                return redirect(url_for('articles.edit_article', slug_art=art.slug_art))
            except Exception as error:
                flash(f'Что-то пошло не так: {error}')
                return redirect(url_for('articles.edit_article', slug_art=art.slug_art))

        return render_template('user_templates/edit_article.html', form=form, art=art)

    except Exception as error:
        return render_template('user_templates/edit_article.html', error=error)
