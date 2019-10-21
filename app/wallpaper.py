from flask import render_template
from app import app
from app.models import Quote
import random

BG_IMAGES = (
    {
        'url': '/static/img/bg/0.jpg',
        'attr': 'Christoph Michels',
        'license': 'CC BY 2.5'
    },
    #{
    #    'url': '/static/img/bg/1.jpg',
    #    'attr': 'Balkhovitin',
    #    'license': 'CC BY-SA 3.0'
    #},
    {
        'url': '/static/img/bg/2.jpg',
        'attr': 'Bouarf',
        'license': 'CC BY-SA 3.0'
    },
    {
        'url': '/static/img/bg/3.jpg',
        'attr': 'Hans Stieglitz',
        'license': 'CC BY-SA 3.0'
    },
    {
        'url': '/static/img/bg/4.jpg',
        'attr': 'Cj.samson',
        'license': 'CC BY 3.0'
    },
)

@app.route('/q/<id>/')
def fancy_quote(id):
    id = int(id)
    quote = Quote.query.filter_by(id=id).first_or_404()
    return render_template('wallpaper.html',
        bg_image=BG_IMAGES[random.randrange(0,len(BG_IMAGES))], quote=quote,
        title="On {}".format(quote.topic))
