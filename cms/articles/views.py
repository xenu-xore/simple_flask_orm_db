from flask import redirect, render_template, Blueprint, \
    flash, url_for, request, Response
from .forms import CreateArticle, CreateCategory
from flask_login import login_user, logout_user, \
    login_required
from cms import db
from cms.models import Category, Articles
from cms.articles.translate import transliterate

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
                slug_art=transliterate(form.slug_art.data).lower()
            )
            try:
                db.session.add(article)
                db.session.commit()
                return redirect(url_for('/'))
            except:
                flash('Что-то пошло не так')
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
        except:
            flash('Что-то пошло не так')
            return redirect(url_for('articles.create_category'))
    return render_template('user_templates/create_category.html', form=form)


@articles_blueprint.route('/articles/')
def get_all_articles():
    # articles = Articles.query.all()
    articles = Articles.query.order_by(Articles.date_publisher.desc()).all()
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
