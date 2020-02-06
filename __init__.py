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

@app.route("/api/edge/<string:namespace>")
@cross_origin()
def get_edge(namespace):
    # TODO(Jen): Hack - namespaces should be supported!
    namespace = 'ppi'
    return jsonify(Edge.all(namespace))


##########
# Layout #
##########

@app.route("/api/layout/<string:db_namespace>><string:layout_namespace>")
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
