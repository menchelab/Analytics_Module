from flask import Flask, jsonify, request,g, render_template
from flask import Flask, flash, request, redirect, url_for
from flask import Flask, session

from werkzeug.utils import secure_filename
import click
from flask import current_app, g
from flask.cli import with_appcontext

from flask_cors import CORS, cross_origin
if __name__ == '__main__':
    from tables import *
else:
    from .tables import *
from werkzeug.contrib.cache import SimpleCache


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
cors = CORS(app, send_wildcard=True)
app.config['CORS_HEADERS'] = 'Content-Type'
cache = SimpleCache()
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


@app.route("/")
def hello():
    g.namespaces = Data.summary()
    if g.namespaces:
        g.selected_namespace = g.namespaces[0]
    g.subnetwork = {"nodes": [1, 2, 3, 4, 5], "edges": [[1, 2], [2, 4], [3, 5], [2, 5]]}
    g.subnetwork2 = {}
    g.subnetwork2["nodes"] = [{"id": str(x), "group": str(x)} for x in  g.subnetwork["nodes"]]
    g.subnetwork2["links"] = [{"source": x[0], "target": x[1]} for x in  g.subnetwork["edges"]]
    return render_template('dashboard_demo.html', name="jen")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    print("namespace", request.args.get("namespace"))
    form = request.form.to_dict()
    print(request.files)
    if form["namespace"] == "New":
        namespace = form["new_name"]
        Upload.create_new_namespace(form["new_name"])
    else:
        namespace = form["existing_namespace"]
    if not namespace:
        return "namespace fail"
    Upload.create_new_temp_namespace(namespace)
    layout_files = request.files.getlist("layouts")
    print(layout_files)
    if len(layout_files) > 0 and len(layout_files[0].filename) > 0:
        print("loading layouts", len(layout_files))
        Upload.upload_layouts(namespace, layout_files)
    edge_files = request.files.getlist("links")
    if len(edge_files) > 0 and len(edge_files[0].filename) > 0:
        Upload.upload_edges(namespace, edge_files)
    attribute_files = request.files.getlist("attributes")
    if len(attribute_files) > 0:
        Upload.upload_attributes(namespace, attribute_files)
    label_files = request.files.getlist("labels")
    if len(label_files) > 0:
        Upload.upload_labels(namespace, request.files.getlist("labels"))
    return "success"
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file',
                                filename=filename))

@app.route('/uploaded_file', methods=['GET'])
def uploaded_file():
    filename = request.args.get('filename')
    return render_template('uploaded_file.html', filename=filename)

@app.route('/<string:db_namespace>/search', methods=['GET'])
def old_swimmer(db_namespace):
    return render_template('dd_dash.html')

@app.route('/swimmer', methods=['GET'])
def swimmer():
    return render_template('dd_dash.html')

########
# Data #
########

@app.route("/api/namespace/summary", methods=["GET"])
@cross_origin()
def get_summary():
    return jsonify(Data.summary())


@app.route("/api/<string:db_namespace>/subgraph",  methods=['GET'])
@cross_origin()
def get_subgraph(db_namespace):
    nodes = request.args.getlist('node_ids')
    attribute = request.args.getlist('attribute_id')
    if attribute:
        nodes = [node["id"] for node in Node.nodes_for_attribute(db_namespace, attribute)]
    if not nodes:
        return "Fail"
    edges = Edge.for_nodelist(db_namespace, nodes)
    nodes = Node.get(db_namespace, nodes)
    return jsonify({"nodes": nodes, "edges": edges})



########
# Node #
########

@app.route("/api/<string:db_namespace>/node",  methods=['GET'])
@cross_origin()
def nodes(db_namespace):
    prefix = request.args.get('prefix') or ""
    symbols = request.args.getlist("symbols")
    external_ids = request.args.getlist("external_ids")
    node_ids = request.args.getlist("id")
    neighbors = request.args.getlist("neighbor")
    random = request.args.get('random') or None
    attribute_ids = request.args.getlist("attribute_id")
    print(node_ids)
    if random:
        return jsonify(Node.show_random(random, db_namespace))
    if node_ids:
        return jsonify(Node.get(db_namespace, node_ids))
    if external_ids:
        return jsonify(Node.get_by_external_ids(db_namespace, external_ids))
    if symbols:
        return jsonify(Node.get_by_symbols(db_namespace, symbols))
    if neighbors:
        return jsonify(Node.get_neighbors(db_namespace, neighbors))
    if attribute_ids:
        return jsonify(Node.nodes_for_attribute(db_namespace, attribute_ids))
    return jsonify(Node.nodes_for_autocomplete(db_namespace, prefix))



## IP_CELINE: implement GSEA
@app.route('/api/<string:db_namespace>/node/gsea', methods=['GET', 'POST'])
@cross_origin()
def gsea(db_namespace):
    if request.method == 'POST':
        #data = request.form
        data = request.get_json()
        print('in POST')
    else:
        data = request#.args
        print([i for i in request.args.keys()])
    return jsonify(Node.gsea(db_namespace))

@app.route('/api/<string:db_namespace>/node/random_walk', methods=['GET', 'POST'])
@cross_origin()
def random_walk(db_namespace):
    if request.method == 'POST':
        #data = request.form
        data =request.get_json()
    else:
        data = request.args
#    node_ids = data.node_ids
    node_ids = [int(x) for x in data['node_ids']]
    if 'variants' in data.keys():
        variants = [int(x) for x in data['variants']]
    else:
        variants = []

    # print(node_ids)
    #node_ids = [int(x) for x in data.getlist("node_ids")]
    restart_probability = data["restart_probability"]
    restart_probability = float(restart_probability or 0.9)
    if "max_elements" in data.keys():
        max_elements = data["max_elements"]
    else:
        max_elements = 200

    return jsonify(Node.random_walk(db_namespace,node_ids,variants,restart_probability,max_elements, cache))

@app.route('/api/<string:db_namespace>/node/random_walk_dock2', methods=['GET', 'POST'])
@cross_origin()
def random_walk_dock2(db_namespace):
    if request.method == 'POST':
        #data = request.form
        data =request.get_json()
    else:
        data = request.args
#    node_ids = data.node_ids
    node_ids = [int(x) for x in data['node_ids']]
    if 'variants' in data.keys():
        variants = [int(x) for x in data['variants']]
    else:
        variants = []

    # print(node_ids)
    #node_ids = [int(x) for x in data.getlist("node_ids")]
    restart_probability = data["restart_probability"]
    restart_probability = float(restart_probability or 0.9)
    if "max_elements" in data.keys():
        max_elements = data["max_elements"]
    else:
        max_elements = 200

    return jsonify(Node.random_walk_dock2(db_namespace,node_ids,variants,restart_probability,max_elements, cache))


@app.route('/api/<string:db_namespace>/node/gene_card', methods=['GET'])
@cross_origin()
def gene_card(db_namespace):

    node_id = request.args.get("node_id")
    return jsonify(Node.gene_card(db_namespace, node_id, cache))

@app.route('/api/<string:db_namespace>/node/shortest_path', methods=['GET'])
@cross_origin()
def shortest_path(db_namespace):

    from_id = request.args.get("from")
    to_id = request.args.get("to")
    return Node.shortest_path(db_namespace, from_id, to_id)

# @app.route('/api/<string:db_namespace>/node/expression', methods=['GET'])
# @cross_origin()
# def shortest_path(db_namespace):
#
#     from_id = request.args.get("from")
#     to_id = request.args.get("to")
#     return Node.expression(db_namespace, from_id, to_id)
#
@app.route('/api/<string:db_namespace>/node/connect_set_dfs', methods=['POST'])
@cross_origin()
def connect_set_dfs(db_namespace):
    data =request.get_json()
    seeds = data["seeds"]
    variants = data["variants"]

    return Node.connect_set_dfs(db_namespace, seeds, variants,cache)



@app.route('/api/<string:db_namespace>/node/sub_layout', methods=['POST'])
@cross_origin()
def sub_layout(db_namespace):

    data =request.get_json()

#    node_ids = data.node_ids
    node_ids = [int(x) for x in data['node_ids']]

    return jsonify(Node.layout(db_namespace,node_ids, cache))

@app.route('/api/<string:db_namespace>/node/scale_selection', methods=['POST'])
@cross_origin()
def scale_selection(db_namespace):

    data =request.get_json()

#    node_ids = data.node_ids
    node_ids = [str(x) for x in data['node_ids']]
    layout =  data['layout']

    return jsonify(Node.scale_selection(db_namespace,node_ids,layout, cache))



@app.route("/api/<string:namespace>/node/search", methods=['GET', 'POST'])
@cross_origin()
def search(namespace):
    if request.method == 'POST':
        data = request.form
        results = Node.search(namespace, data)
        return jsonify(results)
    else:
        data = request.args
        results = Node.search(namespace, data)
        return jsonify(results)


#############
# Attribute #
#############

@app.route("/api/<string:db_namespace>/attribute/",  methods=['GET'])
@cross_origin()
def attributes_for_node(db_namespace):
    attr_namespace = request.args.get("namespace") or None
    node_id = request.args.get("node_id")
    external_ids = request.args.getlist("external_ids")
    if node_id:
        return jsonify(Attribute.attributes_for_node(db_namespace, node_id, attr_namespace))
    prefix = request.args.get("prefix") or ""
    if prefix:
        return jsonify(Attribute.attributes_for_autocomplete(db_namespace, prefix, attr_namespace))
    if external_ids:
        return jsonify(Attribute.attributes_for_external_ids(db_namespace, external_ids))
    if attr_namespace:
        return jsonify(Attribute.all_attribute_names(db_namespace, attr_namespace))
    else:
        return "no arguments supplied!"

@app.route("/api/<string:db_namespace>/attribute/delete/<int:attr_id>",  methods=['GET'])
@cross_origin()
def delete_attribute(db_namespace, attr_id):
    return Attribute.delete(db_namespace, attr_id)


# Cache database call for attribute taxonomy to prevent repeated queries.
def get_attribute_taxonomy(db_namespace, root_node_id):
    zkey = 'attribute_taxonomy_parents-%s-%d' % (db_namespace, root_node_id)
    dtc = cache.get(zkey)
    if dtc is None:
        print("!!FEFDKJBFSKD")
        dtc = AttributeTaxonomy.construct_taxonomy(db_namespace, root_node_id)
        cache.set(zkey, dtc, timeout=5 * 60 * 60 * 24 * 1000)
    return dtc

@app.route("/api/<string:db_namespace>/attribute_taxonomy/<int:root_node_id>", methods=['GET'])
@cross_origin()
def taxonomy(db_namespace, root_node_id):
    return jsonify(get_attribute_taxonomy(db_namespace, root_node_id))

@app.route("/api/<string:db_namespace>/attribute_taxonomy/", methods=['GET'])
@cross_origin()
def taxonomy_from_name(db_namespace):
    taxonomy_name = request.args.get("namespace")
    root_node_id = AttributeTaxonomy.get_root(db_namespace, taxonomy_name)
    if root_node_id:
        return jsonify(get_attribute_taxonomy(db_namespace, root_node_id))
    else:
        return jsonify([])

@app.route("/api/<string:db_namespace>/attribute/namespaces", methods=["GET"])
@cross_origin()
def attribute_namespaces(db_namespace):
    return jsonify(Attribute.get_attribute_namespaces(db_namespace))

@app.route("/api/<string:db_namespace>/selection/create", methods=['GET', 'POST'])
@cross_origin()
def create_selection(db_namespace):
    if request.method == 'POST':
        data = request.form
        selection_name = data.get("selection_name")
        node_ids = data.get("node_ids")
        if not data:
            data = request.get_json(force=True)
            selection_name = data["selection_name"]
            node_ids = data["node_ids"]
    else:
        data = request.args
        selection_name = data.get("selection_name")
        node_ids = data.get("node_ids")
    if not selection_name or not node_ids:
        return jsonify({"status": "FAIL", "reason": "invalid request"})
    return jsonify(Attribute.create_selection(db_namespace, selection_name, node_ids))


@app.route("/api/<string:db_namespace>/attribute/attribute2attribute", methods=["GET"])
@cross_origin()
def attribute2attribute(db_namespace):
    att_id = request.args.get("att_id")
    return jsonify(Attribute.attribute2attribute(db_namespace,att_id))



###########
# Article #
###########

@app.route("/api/<string:namespace>/article",  methods=['GET'])
@cross_origin()
def article(namespace):
    pubid = request.args.get('pubid')
    if pubid:
        return jsonify(Article.article_for_pubid(namespace, pubid))
    node_id = request.args.get("node_id") or 0
    return jsonify(Article.articles_for_node(namespace, node_id))


########
# Edge #
########

@app.route("/api/<string:namespace>/edge", methods=['GET'])
@cross_origin()
def get_edge(namespace):
    data = request.args
    node_ids = data.get("node_id")
    if node_ids:
        return jsonify(Edge.for_nodelist(node_ids))
    return jsonify(Edge.all(namespace))


##########
# Layout #
##########

@app.route("/api/<string:db_namespace>/layout/<string:layout_namespace>")
@cross_origin()
def get_layout(db_namespace, layout_namespace):
    return jsonify(Layout.fetch(db_namespace, layout_namespace))


#########
# Label #
#########

@app.route("/api/<string:db_namespace>/label/<string:label_namespace>")
@cross_origin()
def get_label(db_namespace, label_namespace):
    return jsonify(Label.fetch(db_namespace, label_namespace))


##################
# EXPORT RESULTS #
##################

@app.route('/api/<string:db_namespace>/export/results', methods=['POST'])
@cross_origin()
def export_dashboard_data(db_namespace):

    data =request.get_json()
    Exports.export_dashboard_data(db_namespace,data)
    return 0


@app.route('/api/<string:db_namespace>/import/results2swimmer')
@cross_origin()
def import_json2swimmer(db_namespace):

    return Exports.import_json2swimmer(db_namespace)


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

    app.debug = True
    app.run()
