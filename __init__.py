from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from .tables import *


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
def hello():
    return "Hello, I love Digital Ocean!"
@app.route("/sepptest",  methods=['GET'])
def sepptest():
    return ",".join([str(x) for x in range(200000)])

########
# Gene #
########

@app.route("/api/gene/prefix/<string:name_prefix>",  methods=['GET'])
@cross_origin()
def genes_for_prefix(name_prefix):
    return jsonify(Gene.genes_for_autocomplete(name_prefix))

@app.route("/api/gene/search", methods=['GET', 'POST'])
@cross_origin()
def search():
    data = request.form
    print(data)
    results = Gene.search(data)
    return jsonify(results)

@app.route("/api/gene/disease/<string:disease_id>",  methods=['GET'])
@cross_origin()
def genes_for_disease(disease_id):
    return jsonify(Gene.genes_for_disease(disease_id))

@app.route("/api/gene/go_category/<string:go_category_id>",  methods=['GET'])
@cross_origin()
def genes_for_go_category(go_category_id):
    return jsonify(Gene.genes_for_go_category(disease_id))

@app.route("/api/gene/random", methods=['GET'])
@cross_origin()
def get_random_genes():
    return jsonify(Gene.show_random(10))


###########
# Disease #
###########

@app.route("/api/disease/gene/<int:entrez_id>",  methods=['GET'])
@cross_origin()
def diseases_for_gene(entrez_id):
    return jsonify(Disease.diseases_for_gene(entrez_id))

@app.route("/api/disease_taxonomy/<int:root_node_id>", methods=['GET'])
@cross_origin()
def do_taxonomy(root_node_id):
    return jsonify(
        DiseaseTaxonomy.construct_taxonomy(5840))

###########
# Article #
###########

@app.route("/api/article/pubid/<int:pubid>",  methods=['GET'])
@cross_origin()
def article_for_pubid(pubid):
    return jsonify(Article.article_for_pubid(pubid))

@app.route("/api/article/gene/<int:entrez_id>",  methods=['GET'])
@cross_origin()
def articles_for_gene(entrez_id):
    return jsonify(Article.articles_for_gene(entrez_id))

##############
# GoCategory #
##############

@app.route("/api/go_category/gene/<string:namespace>/<int:entrez_id>",  methods=['GET'])
@cross_origin()
def go_category_for_gene(namespace, entrez_id):
    return jsonify(GoCategory.go_categories_for_gene(entrez_id, namespace))

@app.route("/api/go_taxonomy/<int:root_node_id>")
@cross_origin()
def go_taxonomy(root_node_id):
    return jsonify(GoTaxonomy.construct_taxonomy(root_node_id))



if __name__ == "__main__":
    app.run()
