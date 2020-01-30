from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from .tables import *
from werkzeug.contrib.cache import SimpleCache


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
cache = SimpleCache()





@app.route("/")
def hello():
    return "Hello, I love Digital Ocean!"
@app.route("/sepptest",  methods=['GET'])
def sepptest():
    return ",".join([str(x) for x in range(200000)])

######d
# Data
#

@app.route("/api/namespace/summary", methods=["GET"])
@cross_origin()
def get_summary():
    return jsonify(Data.summary())


########
# Node #
########

@app.route("/api/node/prefix/<string:name_prefix>",  methods=['GET'])
@cross_origin()
def nodes_for_prefix(name_prefix):
    return jsonify(Node.nodes_for_autocomplete(name_prefix))

# @app.route("/api/node/search", methods=['GET', 'POST'])
# @cross_origin()
# def search():
#     data = request.form
#     results = node.search(data)
#     return jsonify(results)

@app.route("/api/node/attribute/<string:attribute_id>",  methods=['GET'])
@cross_origin()
def nodes_for_attribute(attribute_id):
    return jsonify(Node.nodes_for_attribute(attribute_id))


@app.route("/api/node/random", methods=['GET'])
@cross_origin()
def get_random_nodes():
    return jsonify(Node.show_random(10))

@app.route("/api/node/prefix", methods=['GET'])
@cross_origin()
def all_node_names():
    return jsonify(Node.all())

#############
# Attribute #
#############

@app.route("/api/attribute/node/<int:node_id>/<string:namespace>",  methods=['GET'])
@cross_origin()
def attributes_for_node(node_id, namespace):
    if namespace == 'all':
        namespace = None
    return jsonify(Attribute.attributes_for_node(node_id, namespace))

# Cache database call for attribute taxonomy to prevent repeated queries.
def get_attribute_taxonomy(root_node_id):
    zkey = 'attribute_taxonomy_parents-%d' % root_node_id
    dtc = cache.get(zkey)
    if dtc is None:
        dtc = AttributeTaxonomy.construct_taxonomy(root_node_id)
        cache.set(zkey, dtc, timeout=5 * 60 * 60 * 24)
    return dtc

@app.route("/api/attribute_taxonomy/<int:root_node_id>", methods=['GET'])
@cross_origin()
def taxonomy(root_node_id):
    return jsonify(get_attribute_taxonomy(root_node_id))

@app.route("/api/attribute/prefix/<string:name_prefix>/<string:namespace>", methods=['GET'])
@cross_origin()
def attributes_for_prefix(name_prefix, namespace):
    if namespace == 'all':
        namespace = None
    return jsonify(Attribute.attributes_for_autocomplete(name_prefix, namespace))

@app.route("/api/attribute/<string:namespace>", methods=['GET'])
@cross_origin()
def all_attribute_names(namespace):
    print(namespace)
    if namespace == 'all':
        namespace = None
    return jsonify(Attribute.all_attribute_names(namespace))


###########
# Article #
###########

@app.route("/api/article/pubid/<int:pubid>",  methods=['GET'])
@cross_origin()
def article_for_pubid(pubid):
    return jsonify(Article.article_for_pubid(pubid))

@app.route("/api/article/node/<int:node_id>",  methods=['GET'])
@cross_origin()
def articles_for_node(node_id):
    return jsonify(Article.articles_for_node(node_id))

########
# Edge #
########

@app.route("/api/edge/<string:namespace>/<string:layout>")
@cross_origin()
def get_edge(namespace, layout):
    # TODO(Jen): Hack - namespaces should be supported!
    namespace = 'ppi'
    return jsonify(Edge.all(namespace, layout))


##########
# Layout #
##########

@app.route("/api/layout/<string:namespace>")
@cross_origin()
def get_layout(namespace):
    return jsonify(Layout.fetch(namespace))



#########
# Label #
#########

@app.route("/api/label/<string:namespace>")
@cross_origin()
def get_label(namespace):
    return jsonify(label.fetch(namespace))

#############
# SavedView #
#############
# @app.route("/api/saved_views/<string:username>/<string:view_name>", methods=['GET'])
# @cross_origin()
# def get_saved_view(username, view_name):
#     return jsonify(SavedView.get(username, view_name))
#
# @app.route("/api/saved_views/create", methods=['POST'])
# @cross_origin()
# def create_saved_view():
#     data = request.form
#     return jsonify(SavedView.create(data))



if __name__ == "__main__":
    app.run()
