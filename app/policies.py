from flask import render_template, redirect, url_for
from app import app

@app.route('/privacy/')
def privacy_policy():
    return render_template('policies/privacy.html')

@app.route('/family-fun/')
def family_fun():
    return render_template('policies/familyfun.html')

@app.route('/credits/')
def credits():
    return render_template('credits.html')
