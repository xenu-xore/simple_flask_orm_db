from flask import redirect, render_template, Blueprint, \
    flash, url_for, request, Response
from .forms import CreateArticle, EditArticles
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

                if goo:
                    flash(f"Дублирование URL: {error.params[1]}")
                    return redirect(url_for('articles.create_article'))
                elif foo:
                    flash(f"Дублирование URL: {foo}")
                    return redirect(url_for('articles.create_article'))

    return render_template('user_templates/articles/create_article.html', form=form)


@articles_blueprint.route('/articles/', methods=['GET'], defaults={"page": 1})
@articles_blueprint.route('/articles/<int:page>/', methods=['GET'])
def get_all_articles(page):
    page = page
    per_page = 3  # Количество статей на 1 странице
    articles = Articles.query.order_by(Articles.date_publisher.desc()).paginate(page, per_page, error_out=True)
    return render_template('user_templates/articles/get_all_articles.html', articles=articles)


@articles_blueprint.route('/articles/<string:slug_art>/')
def detail_article(slug_art):
    article = Articles.query.filter_by(slug_art=slug_art).one_or_none()

    if article is not None:
        return render_template('user_templates/articles/detail_article.html', article_one=article)

    else:
        return render_template('error/error_404.html'), 404


@articles_blueprint.route('/edit_article/<string:slug_art>/', methods=['GET', 'POST'])
@login_required
def edit_article(slug_art):
    try:
        art = Articles.query.filter_by(slug_art=slug_art).one_or_none()
        if art is not None:
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

            return render_template('user_templates/articles/edit_article.html', form=form, art=art)
        else:
            return render_template('error/error_404.html'), 404
    except Exception as error:
        return render_template('user_templates/articles/edit_article.html', error=error)
