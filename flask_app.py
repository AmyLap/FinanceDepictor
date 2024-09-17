from flask import Flask, render_template, request
import os
import json
import pandas as pd
import datetime
from scripts.category_functions import CategoryFunctions
from scripts.categories_manager import CategoriesManager

app = Flask(__name__)
categorised_df = pd.read_json("logs\\categorised.json")

cf = CategoryFunctions(categorised_df)
cm = CategoriesManager()
categories_dict = cm.get_categories()

@app.context_processor
def inject_variables():
    
    categories_list = list(categories_dict.keys())
    return_dict = {
        "categories_list": categories_list
        }
    return return_dict

@app.route('/')
def home():
    pass
    return render_template('home.html')


@app.route('/year/<year>') 
def year(year=None):
    
    year_dict = cf.year(year)
    return render_template('year.html', year=year, data_dict=year_dict)

@app.route('/monthly')
def monthly():
    # Add up the categorised amounts
    df_sumed = categorised_df.groupby(['Year', 'Month', 'Category'])['Amount'].sum().reset_index()
    unique_years = df_sumed['Year'].unique()
    result_dict = {}
    for _year in unique_years:
        result_dict[_year] = {}
        year_df = df_sumed[df_sumed['Year'] == _year]
        if bool(len(year_df)):
            result_dict[_year] = year_df.set_index('Category')['Amount'].to_dict()
    return render_template('monthly_graphs.html', data_dict=result_dict)

@app.route('/categories')
def categories():
    return render_template('categories.html')

@app.route('/years')
def years():
    return render_template('years.html')

@app.route('/categories/<category>')
def category(category=None):
    result_dict = cf.subcategory(category)
    return render_template('category.html', title=category, data_dict=result_dict, category=category)

@app.route('/other')
def other():
    result_dict = cf.other()
    return render_template('graph.html', title="Other", data_dict=result_dict)

@app.route('/<category>/<year>')
def year_and_category(year=None, category=None):
    result_dict = cf.year_category(year, category)
    return render_template('graph.html', title=f'{year} > {category}', data_dict=result_dict)

@app.route('/<year>/<category>')
def category_and_year(year=None, category=None):
    result_dict = cf.year_category(year, category)
    return render_template('graph.html', title=f'{year} > {category}', data_dict=result_dict)

# @app.route('/edit_category/)
# def category_edit_list(category=None):
#     return render_template('graph.html', title='Categories Editor', data_dict=list(categories_dict.keys()).sort())

if __name__ == '__main__':
    app.run(debug=True, port=8070)