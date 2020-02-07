from flask import Flask, jsonify, request,g, render_template
from flask import Flask, flash, request, redirect, url_for
from flask import Flask, session
from flask import Session

from werkzeug.utils import secure_filename
import click
from flask import current_app, g
from flask.cli import with_appcontext

from flask_cors import CORS, cross_origin
from .tables import *
from werkzeug.contrib.cache import SimpleCache


app = Flask(__name__)
sess = Session()
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
cache = SimpleCache()
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


@app.route("/")
def hello():
    g.user = {'username': "Jen", 'happiness': 'fleeting'}
    return render_template('hello.html', name="jen")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        print(request.data)
        #print(request.args)
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
        #print(request.files.get("layouts"))
        Upload.create_new_temp_namespace(namespace)
        Upload.upload_to_new_namespace(namespace, request.files.getlist("layouts"))
        Upload.upload_edges_to_new_namespace(namespace, request.files.getlist("links"))
        Upload.upload_labels_to_new_namespace(namespace, request.files.getlist("labels"))
        return "hello"
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
    data = Data.summary()
    print(data)
    return render_template('upload.html', data=data)

@app.route('/uploaded_file', methods=['GET'])
def uploaded_file():
    filename = request.args.get('filename')
    print("g")
    return render_template('uploaded_file.html', filename=filename)


@app.route("/sepptest",  methods=['GET'])
def sepptest():
    return ",".join([str(x) for x in range(200000)])

########
# Data #
########

@app.route("/api/namespace/summary", methods=["GET"])
@cross_origin()
def get_summary():
    return jsonify(Data.summary())


########
# Node #
########

@app.route("/api/node/prefix/<string:db_namespace>/<string:name_prefix>",  methods=['GET'])
@cross_origin()
def nodes_for_prefix(db_namespace,name_prefix):
    return jsonify(Node.nodes_for_autocomplete(db_namespace, name_prefix))

@app.route("/api/node/",  methods=['GET'])
@cross_origin()
def nodes():
    db_namespace = request.args.get('namespace') or "Datadivr_jen"
    prefix = request.args.get('prefix') or ""
    node_ids = request.args.getlist("id")
    max_nodes = request.args.get('max_nodes')
    print(node_ids)
    return jsonify(Node.nodes_for_autocomplete(db_namespace, prefix))

@app.route("/api/node/search/<string:namespace>", methods=['GET', 'POST'])
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


@app.route("/api/node/attribute/<string:db_namespace>/<string:attribute_id>",  methods=['GET'])
@cross_origin()
def nodes_for_attribute(db_namespace, attribute_id):
    return jsonify(Node.nodes_for_attribute(db_namespace, attribute_id))


@app.route("/api/node/random/<string:db_namespace>", methods=['GET'])
@cross_origin()
def get_random_nodes(db_namespace):
    return jsonify(Node.show_random(10, db_namespace))

#############
# Attribute #
#############

@app.route("/api/attribute/node/<string:db_namespace>/<int:node_id>/<string:attr_namespace>",  methods=['GET'])
@cross_origin()
def attributes_for_node(db_namespace, node_id, attr_namespace):
    if attr_namespace == 'all':
        attr_namespace = None
    return jsonify(Attribute.attributes_for_node(db_namespace, node_id, attr_namespace))

# Cache database call for attribute taxonomy to prevent repeated queries.
def get_attribute_taxonomy(db_namespace, root_node_id):
    zkey = 'attribute_taxonomy_parents-%s-%d' % (db_namespace, root_node_id)
    dtc = cache.get(zkey)
    if dtc is None:
        dtc = AttributeTaxonomy.construct_taxonomy(db_namespace, root_node_id)
        cache.set(zkey, dtc, timeout=5 * 60 * 60 * 24)
    return dtc

@app.route("/api/attribute_taxonomy/<string:db_namespace>/<int:root_node_id>", methods=['GET'])
@cross_origin()
def taxonomy(db_namespace, root_node_id):
    return jsonify(get_attribute_taxonomy(db_namespace, root_node_id))

@app.route("/api/attribute/prefix/<string:db_namespace>/<string:name_prefix>/<string:attr_namespace>", methods=['GET'])
@cross_origin()
def attributes_for_prefix(db_namespace, name_prefix, attr_namespace):
    if attr_namespace == 'all':
        attr_namespace = None
    return jsonify(Attribute.attributes_for_autocomplete(db_namespace, name_prefix, attr_namespace))

@app.route("/api/attribute/<string:db_namespace>/<string:attr_namespace>", methods=['GET'])
@cross_origin()
def all_attribute_names(db_namespace, attr_namespace):
    if attr_namespace == 'all':
        attr_namespace = None
    return jsonify(Attribute.all_attribute_names(db_namespace, attr_namespace))


###########
# Article #
###########

@app.route("/api/article/<string:namespace>/pubid/<int:pubid>",  methods=['GET'])
@cross_origin()
def article_for_pubid(namespace, pubid):
    return jsonify(Article.article_for_pubid(namespace, pubid))

@app.route("/api/article/<string:namespace>/node/<int:node_id>",  methods=['GET'])
@cross_origin()
def articles_for_node(namespace, node_id):
    return jsonify(Article.articles_for_node(namespace, node_id))

########
# Edge #
########

@app.route("/api/edge/<string:namespace>")
@cross_origin()
def get_edge(namespace):
    # TODO(Jen): Hack - namespaces should be supported!
    return jsonify(Edge.all(namespace))


##########
# Layout #
##########

@app.route("/api/layout/<string:db_namespace>/<string:layout_namespace>")
@cross_origin()
def get_layout(db_namespace, layout_namespace):
    return jsonify(Layout.fetch(db_namespace, layout_namespace))



#########
# Label #
#########

@app.route("/api/label/<string:db_namespace>/<string:label_namespace>")
@cross_origin()
def get_label(db_namespace, label_namespace):
    return jsonify(Label.fetch(db_namespace, label_namespace))

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
    app.config['SECRET_KEY'] = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)

    app.debug = True
    app.run()
