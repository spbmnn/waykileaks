from flask import render_template
from app import app
from app.models import Quote
import random

BG_IMAGES = (
    {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/8/8d/Freudenberg_sg_Switzerland.jpg',
        'attr': 'Christoph Michels',
        'license': 'CC BY 2.5'
    },
    {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/e/ed/Paysage_karabagh_02.jpg',
        'attr': 'Bouarf',
        'license': 'CC BY-SA 3.0'
    },
    {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/6/69/K%C3%B6cherbaumwald-01.jpg',
        'attr': 'Hans Stieglitz',
        'license': 'CC BY-SA 3.0'
    },
    {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/7/73/Bali_Khila_Rajgad_Maharashtra.jpg',
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
