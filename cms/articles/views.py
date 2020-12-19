from flask import redirect, render_template, Blueprint, \
    flash, url_for, request
from .forms import CreateArticle, CreateCategory
from flask_login import login_user, logout_user, \
    login_required
from cms import db
from cms.models import Category, Articles

articles_blueprint = Blueprint('articles', __name__)



@articles_blueprint.route('/create_article/', methods=['GET', 'POST'])
@login_required
def create_article():
    form = CreateArticle(request.form)
    form.select_category.choices = [("", "---")] + [(g.id, g.name_category) for g in Category.query.all()]
    if request.method == 'POST' or request.method == "GET" and form.validate_on_submit():
        article = Articles(
            title=form.title.data,
            short_description=form.short_description.data,
            article=form.article.data,
            category_id=form.select_category.data
        )
        try:
            db.session.add(article)
            db.session.commit()
            return redirect(url_for('/'))
        except:
            flash('Что-то пошло не так')
            return redirect(url_for('articles.create_article'))
    return render_template('user_templates/create_article.html', form=form)


@articles_blueprint.route('/create_category/', methods=['GET', 'POST'])
@login_required
def create_category():
    form = CreateCategory(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        category = Category(
            name_category=form.name_category.data,
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
    articles= Articles.query.all()
    cat = Articles()

    return render_template('user_templates/get_all_articles.html', articles=articles,
                           category=cat,
                           )

@articles_blueprint.route('/articles/<int:id>')
def detal_articles(id):
    article = Articles.query.get(id)
    return render_template('user_templates/detal_article.html', article=article)