import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), "..")))
from . import db_config
#import db_config
import pymysql
import networkx as nx

'''
This code populates the tables explicitly used by the DataDiVR to present information.

Although the rest of the code is database-agnostic, please note that these scripts
make very heavy use of raw queries and therefore are only compatible with MySQL.


tables:
    nodes
    edges

'''


def create_nodes(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `nodes` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `external_id` varchar(50) DEFAULT NULL,
      `name` varchar(155) DEFAULT NULL,
      `symbol` varchar(155) DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `ix_nodes_external_id` (`external_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    '''
    )

def create_attributes(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `attributes` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `external_id` varchar(100) DEFAULT NULL,
      `name` varchar(1000) DEFAULT NULL,
      `description` varchar(4000) DEFAULT NULL,
      `namespace` varchar(155) NOT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `ix_attributes_external_id` (`external_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    '''
    )
def create_nodes_attributes(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `nodes_attributes` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `node_id` int(11) DEFAULT NULL,
      `attribute_id` int(11) DEFAULT NULL,
      `value` double DEFAULT NULL,
      PRIMARY KEY (`id`),
      KEY `node_id` (`node_id`),
      KEY `attribute_id` (`attribute_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    '''
    )

def create_attribute_taxonomies(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `attribute_taxonomies` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `child_id` int(11) DEFAULT NULL,
      `parent_id` int(11) DEFAULT NULL,
      `distance` int(11) DEFAULT NULL,
      `namespace` varchar(155) NOT NULL,
      PRIMARY KEY (`id`),
      KEY `child_id` (`child_id`),
      KEY `parent_id` (`parent_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    '''
    )

def create_attribute_relations(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `attribute_relations` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `attr1_id` int(11) DEFAULT NULL,
      `attr2_id` int(11) DEFAULT NULL,
      `value` double DEFAULT NULL,
      `comment` varchar(1000) DEFAULT NULL,
      PRIMARY KEY (`id`),
      KEY `attr1_id` (`attr1_id`),
      KEY `attr2_id` (`attr2_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    '''
    )

def create_articles(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `articles` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `external_id` int(11) DEFAULT NULL,
      `title` varchar(2000) DEFAULT NULL,
      `authors_list` varchar(4000) DEFAULT NULL,
      `abstract` varchar(10000) DEFAULT NULL,
      `type` varchar(100) DEFAULT NULL,
      `publication_date` date DEFAULT NULL,
      `url` varchar(200) DEFAULT NULL,
      PRIMARY KEY (`id`),
      KEY `ix_articles_external_id` (`external_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    '''
    )


def create_nodes_articles(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `nodes_articles` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `node_id` int(11) DEFAULT NULL,
      `article_id` int(11) DEFAULT NULL,
      PRIMARY KEY (`id`),
      KEY `node_id` (`node_id`),
      KEY `article_id` (`article_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    '''
    )

def create_edges(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `edges` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `node1_id` int(11) DEFAULT NULL,
      `node2_id` int(11) DEFAULT NULL,
      `namespace` varchar(255) NOT NULL,
      PRIMARY KEY (`id`),
      KEY `node1_id` (`node1_id`),
      KEY `node2_id` (`node2_id`),
      KEY `namespace` (`namespace`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    '''
    )

def create_layouts(cursor):
    cursor.execute('''
    DROP TABLE IF EXISTS `layouts`
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `layouts` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `node_id` int(11) NOT NULL,
      `x_loc` float(10,7) DEFAULT NULL,
      `y_loc` float(10,7) DEFAULT NULL,
      `z_loc` float(10,7) DEFAULT NULL,
      `r_val` int(11) DEFAULT NULL,
      `g_val` int(11) DEFAULT NULL,
      `b_val` int(11) DEFAULT NULL,
      `a_val` int(11) DEFAULT NULL,
      `namespace` varchar(255) NOT NULL,
      PRIMARY KEY (`id`),
      KEY `namespace` (`namespace`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    '''
    )

def create_labels(cursor):
    cursor.execute('''
    DROP TABLE IF EXISTS `labels`
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `labels` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `text` varchar(100) DEFAULT NULL,
      `x_loc` float(10,7) DEFAULT NULL,
      `y_loc` float(10,7) DEFAULT NULL,
      `z_loc` float(10,7) DEFAULT NULL,
      `namespace` varchar(255) NOT NULL,
      PRIMARY KEY (`id`),
      KEY `namespace` (`namespace`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    '''
    )

def create_tables(cursor):
    create_nodes(cursor)
    create_edges(cursor)
    create_attributes(cursor)
    create_nodes_attributes(cursor)
    create_attribute_taxonomies(cursor)
    create_articles(cursor)
    create_nodes_articles(cursor)
    create_layouts(cursor)
    create_labels(cursor)

def populate_genes(cursor):
    query = '''
    INSERT INTO nodes(external_id, name, symbol)
    SELECT CONVERT(Entrez_Gene_ID_NCBI, SIGNED), Approved_Name, Approved_Symbol
    FROM GenesGO.hgnc_complete h
    WHERE h.Entrez_Gene_ID_NCBI != ""
    AND CONVERT(Entrez_Gene_ID_NCBI, SIGNED) > 0
    AND Entrez_Gene_ID_NCBI IS NOT NULL
    AND h.Locus_Type IN
    ("gene with protein product", "immunoglobulin gene", "T cell receptor gene")
    '''
    cursor.execute(query)


def populate_diseases(cursor):
    query = '''
    INSERT INTO attributes (external_id, name, namespace)
    SELECT do.do_id, do.do_name, "DISEASE"
    FROM Gene2Disease.disease_ontology do
    WHERE do.is_obsolete != 'true';
    '''
    cursor.execute(query)

def populate_disease_taxonomy(cursor):
    query = '''
    SELECT do_id, is_a
    FROM Gene2Disease.disease_ontology
    WHERE is_obsolete != 'true';
    '''
    cursor.execute(query)
    disease_tree_data = cursor.fetchall()

    query = '''
    SELECT id, external_id FROM attributes where namespace = "DISEASE";
    '''
    cursor.execute(query)
    db.commit()
    node_ids = cursor.fetchall()
    node_ids = {row[1]: row[0] for row in node_ids}

    tree = nx.DiGraph()

    for row in disease_tree_data:
        do_id, is_a = row
        if not is_a:
            continue
        parent_do_id = is_a.split(" ! ")[0]
        tree.add_edge(parent_do_id, do_id)

    edges = {}
    def add_ancestors(n_node, o_node, dist=1):
        ancestors = tree.in_edges(n_node)
        for ancestor in ancestors:
            key = "%d->%d" % (node_ids[ancestor[0]], node_ids[o_node])
            if key not in edges:
                edges[key] = dist
            else:
                edges[key] = min(dist, edges[key])
            add_ancestors(ancestor[0], o_node, dist+1)

    for node in tree.nodes:
        key = "%d->%d" % (node_ids[node], node_ids[node])
        edges[key] = 0
        add_ancestors(node, node, 1)



    values = ",".join(["(%s)" % ",".join(x.split("->") +  [str(edges[x])] + ['"DISEASE"']) for x in edges])
    query = '''
    INSERT INTO attribute_taxonomies (parent_id, child_id, distance, namespace) VALUES %s
    ''' % values
    cursor.execute(query)

def populate_genes_diseases(cursor):
    query = '''
    INSERT INTO nodes_attributes(node_id, attribute_id)
    SELECT g.id, d.id
    FROM nodes g
    JOIN Gene2Disease.gene2disease gd ON g.external_id = gd.entrezID
    JOIN HumanPhenotypes.umlsmapping mp
    ON mp.disease_ID = gd.diseaseID
    JOIN attributes d
    ON right(d.external_id, length(d.external_id) - 5) = mp.identifier
    WHERE mp.vocabulary = 'DO'
    AND d.namespace = "DISEASE"
    '''
    cursor.execute(query)

def populate_articles(cursor):
    query = '''
    INSERT INTO articles(
        external_id, title, authors_list, abstract, type, url)
    SELECT DISTINCT a.pubid, b.title, REPLACE(b.author, ",", ", "), b.abstract, "pubmed", a.pubmedurl
    FROM Datadivr.gene2pubid a
    JOIN Datadivr.pubid2text b
    ON a.pubid = b.pubid AND a.pubid IS NOT NULL

    '''
    cursor.execute(query)


def populate_genes_articles(cursor):
    query = '''
    INSERT INTO nodes_articles(node_id, article_id)
    SELECT g.id, a.id
    FROM nodes g
    JOIN Datadivr.gene2pubid gp ON g.external_id = gp.entrez AND g.external_id IS NOT NULL
    JOIN articles a ON a.external_id = gp.pubid and a.type="pubmed"
    '''
    cursor.execute(query)

def populate_go_categories(cursor):
    query = '''
    INSERT INTO attributes (external_id, name, namespace, description)
    SELECT DISTINCT go_id, go_name, namespace, def
    FROM Datadivr.GO_tree
    '''
    cursor.execute(query)

def populate_genes_go_categories(cursor):
    query = '''
    INSERT INTO nodes_attributes(node_id, attribute_id)
    SELECT DISTINCT g.id, gc.id
    FROM GenesGO.Gene2GO_human h
    JOIN nodes g ON g.external_id = h.entrezid
    JOIN attributes gc ON gc.external_id = h.go_id
    AND gc.namespace != "DISEASE"
    WHERE h.entrezid != '-'
    AND h.evidence != 'ND'
    AND h.evidence != 'IEA'
    AND h.evidence != 'IPI'
    '''
    cursor.execute(query)

def populate_go_taxonomy(cursor):
    query = '''
    SELECT go_id, is_a, relationship
    FROM GenesGO.GO_tree
    WHERE is_obsolete != 'true';
    '''
    cursor.execute(query)
    gene_tree_data = cursor.fetchall()
    '''
        "        # 2nd condition to make a link\n",
    "        # Node A get a directed link to B whenever there is B as part_of/regulates in the list of the 'relationship' column\n",
    "        c = 0\n",
    "        for x in data_tree:\n",
    "            go_id = x[0]\n",
    "            is_a = x[1]\n",
    "            rel = x[2]\n",
    "            n_entries_inCol = int(rel.count('!')) \n",
    "            if n_entries_inCol > 0:\n",
    "                for n in range(0,n_entries_inCol):\n",
    "                    c += 1\n",
    "                    #print(rel.split('!')[n][-11:-1])\n",
    "                    G.add_edge(go_id,rel.split('!')[n][-11:-1])        \n",
    '''

    query = '''
    SELECT id, external_id FROM attributes where namespace in ("biological_process", "cellular_component", "molecular_function");
    '''
    cursor.execute(query)
    node_ids = cursor.fetchall()
    node_ids = {row[1]: row[0] for row in node_ids}

    tree = nx.DiGraph()

    for row in gene_tree_data:
        go_id, is_a, rel = row
        if not is_a:
            continue
        parent_go_id = is_a.split(" ! ")[0]
        tree.add_edge(parent_go_id, go_id)

    edges = {}
    def add_ancestors(n_node, o_node, dist=1):
        ancestors = tree.in_edges(n_node)
        for ancestor in ancestors:
            key = "%d->%d" % (node_ids[ancestor[0]], node_ids[o_node])
            if key not in edges:
                edges[key] = dist
            else:
                edges[key] = min(dist, edges[key])
            add_ancestors(ancestor[0], o_node, dist+1)

    for node in tree.nodes:
        key = "%d->%d" % (node_ids[node], node_ids[node])
        edges[key] = 0
        add_ancestors(node, node, 1)



    values = ",".join(["(%s)" % ",".join(x.split("->") +  [str(edges[x]), '"GO"']) for x in edges])
    query = '''
    INSERT INTO attribute_taxonomies (parent_id, child_id, distance, namespace) VALUES %s
    ''' % values
    cursor.execute(query)


def populate_ppi(cursor):
    query = '''
    INSERT INTO edges (node1_id, node2_id, namespace)
    SELECT n1.id as g_from, n2.id  as g_to, "ppi"
    FROM networks.PPI_hippie2017 e
    JOIN nodes n1 ON n1.external_id = e.entrez_1
    JOIN nodes n2 ON n2.external_id = e.entrez_2 and n1.id != n2.id
    WHERE e.author != ''
    UNION
    SELECT n2.id as g_from, n1.id as g_to, "ppi"
    FROM networks.PPI_hippie2017 e
    JOIN nodes n1 ON n1.external_id = e.entrez_1
    JOIN nodes n2 ON n2.external_id = e.entrez_2  and n1.id != n2.id
    WHERE e.author != ''
    '''
    cursor.execute(query)

def populate_hp_categories(cursor):
    query = '''
    INSERT INTO ppi.attributes (external_id, name, namespace, description)
    SELECT DISTINCT hp_id, hp_name, "HUMAN_PHENOTYPE", def
    FROM HumanPhenotypes.phenotype_tree
    WHERE is_obsolete != 'true';
    '''
    cursor.execute(query)

def populate_genes_hp_categories(cursor):
    query = '''
    INSERT INTO ppi.nodes_attributes(node_id, attribute_id)
    SELECT DISTINCT g.id, gc.id
    FROM HumanPhenotypes.disease_gene_phenotype_all h
    JOIN ppi.nodes g ON g.external_id = h.gene_id_entrez
    JOIN ppi.attributes gc ON gc.external_id = h.HPO_ID
    AND gc.namespace = "HUMAN_PHENOTYPE"
    '''
    cursor.execute(query)

def populate_hp_taxonomy(cursor):
    query = '''
    SELECT hp_id, is_a
    FROM HumanPhenotypes.phenotype_tree
    WHERE is_obsolete != 'true';
    '''
    cursor.execute(query)
    gene_tree_data = cursor.fetchall()

    query = '''
    SELECT id, external_id FROM attributes where namespace = "HUMAN_PHENOTYPE";
    '''
    cursor.execute(query)
    node_ids = cursor.fetchall()
    node_ids = {row[1]: row[0] for row in node_ids}

    tree = nx.DiGraph()

    for row in gene_tree_data:
        go_id, is_a = row
        if not is_a:
            continue
        parent_go_id = is_a.split(" ! ")[0]
        tree.add_edge(parent_go_id, go_id)

    edges = {}
    def add_ancestors(n_node, o_node, dist=1):
        ancestors = tree.in_edges(n_node)
        for ancestor in ancestors:
            key = "%d->%d" % (node_ids[ancestor[0]], node_ids[o_node])
            if key not in edges:
                edges[key] = dist
            else:
                edges[key] = min(dist, edges[key])
            add_ancestors(ancestor[0], o_node, dist+1)

    for node in tree.nodes:
        key = "%d->%d" % (node_ids[node], node_ids[node])
        edges[key] = 0
        add_ancestors(node, node, 1)

    values = ",".join(["(%s)" % ",".join(x.split("->") +  [str(edges[x]), '"HUMAN_PHENOTYPE"']) for x in edges])
    query = '''
    INSERT INTO attribute_taxonomies (parent_id, child_id, distance, namespace) VALUES %s
    ''' % values
    cursor.execute(query)

def populate_layouts(cursor):

    filename = "1_spring"
    layouts_file = '/Users/eiofinova/Projects/DataDiVR/viveNet/Content/data/layouts/%s.csv' % filename
    with open(layouts_file, 'r') as f:
        positions = [l.split(",")[:-1] + [l.split(",")[-1].split(";")[1]] for l in f.readlines()]

    print(positions[:3])

    print(",".join(["(" + ",".join(p) + ")" for p in positions[:2]]))

    cursor.execute("DROP TABLE IF EXISTS `tmp_layouts` ")
    cursor.execute('''
    CREATE TABLE `tmp_layouts` (
      `x_loc` float(10,6) DEFAULT NULL,
      `y_loc` float(10,6) DEFAULT NULL,
      `z_loc` float(10,6) DEFAULT NULL,
      `r_val` int(11) DEFAULT NULL,
      `g_val` int(11) DEFAULT NULL,
      `b_val` int(11) DEFAULT NULL,
      `a_val` int(11) DEFAULT NULL,
      `entrez_id` int(11) DEFAULT NULL
    )
    '''
    )
    cursor.execute('''
    INSERT INTO `tmp_layouts` VALUES %s
    ''' % ",".join(["(" + ",".join(p) + ")" for p in positions]))

    cursor.execute('''
    INSERT INTO `layouts` (node_id, x_loc, y_loc, z_loc, r_val, g_val, b_val, a_val, namespace)
    SELECT n.id, x_loc, y_loc, z_loc, r_val, g_val, b_val, a_val, "%s"
    FROM `tmp_layouts` tl
    JOIN nodes n on n.external_id = tl.entrez_id
    ''' % filename)

    cursor.execute("DROP TABLE IF EXISTS `tmp_layouts` ")

def populate_labels(cursor):
    filename = "1_spring"
    labels_file = '/Users/eiofinova/Projects/DataDiVR/viveNet/Content/data/labels/%s.csv' % filename
    with open(labels_file, 'r') as f:
        positions = [l[:-1].split(",")[:-1] +
                     ['"' + l[:-1].split(",")[-1] + '"' ]  +
                     ['"'  + filename + '"' ] for l in f.readlines()]
    cursor.execute('''
    INSERT INTO `labels`
    (x_loc, y_loc, z_loc, text, namespace)
    VALUES %s
    ''' % ",".join(["(" + ",".join(p) + ")" for p in positions]))


#select count(*) from edges left join layouts on edges.node1_id = layouts.node_id and layouts.namespace = "1_spring" where layouts.node_id is null;

def populate_pathways(cursor):
    query = '''
    INSERT INTO attributes(external_id, name, description, namespace)
    SELECT std_symbol, std_name, short_descr, "PATHWAY")
    FROM Gene2Pathways.pathway_description
    WHERE organism = 'Homo sapiens'
    '''
    cursor.execute(query)

    query = '''
    INSERT INTO nodes_attributes(node_id, attribute_id)
    SELECT nodes.id, attributes.id
    FROM Gene2Pathways.gene2pathways gp
    JOIN nodes ON gp.gene_entID = nodes.external_id
    JOIN attributes ON gp.label = attributes.name AND attributes.namespace = 'PATHWAY'
    '''
    cursor.execute(query)


def populate_tissues(cursor):
    query = '''
    INSERT INTO attributes(external_id, name, description, namespace)
    SELECT DISTINCT CONCAT(tissue, " - ", cell_type),
                    CONCAT(tissue, " - ", cell_type),
                    CONCAT(tissue, " - ", cell_type), "TISSUE"
    FROM Gene2Tissue.gene2tissue
    WHERE level_class != "Not detected" AND reliabilty != "Uncertain"
    '''
    cursor.execute(query)

    query = '''
    INSERT INTO nodes_attributes(node_id, attribute_id)
    SELECT nodes.id, attributes.id
    FROM Gene2Tissue.gene2tissue gt
    JOIN nodes ON gt.genesymbol = nodes.symbol
    JOIN attributes ON CONCAT(tissue, " - ", cell_type) = attributes.external_id
                    AND attributes.namespace = 'TISSUE'
    WHERE level_class != "Not detected" AND reliabilty != "Uncertain"
    '''
    cursor.execute(query)


def populate_base_tables(cursor):
    populate_genes(cursor)
    print("nodes")
    populate_diseases(cursor)
    print("diseases")
    populate_genes_diseases(cursor)
    print("nodes_diseases")
    populate_go_categories(cursor)
    print("go_categories")
    populate_genes_go_categories(cursor)
    print("nodes_go_categories")
    db.commit()
    populate_disease_taxonomy(cursor)
    print("disease_taxonomy")
    populate_go_taxonomy(cursor)
    print("go_taxonomy")
    populate_ppi(cursor)
    print("ppi")
    populate_articles(cursor)
    print("articles")
    populate_genes_articles(cursor)
    print("nodes_articles")
    populate_layouts(cursor)
    print("layouts")
    populate_labels(cursor)
    print("labels")




if __name__ == '__main__':
    DB = "ppi"
    print("Hello!")
    dbconf = db_config.asimov_admin
    print(dbconf)
    # db = pymysql.connect(dbconf["host"], dbconf["user"],
    #                      dbconf["password"], db=dbconf["database"])
    # cursor = db.cursor()
    # cursor.execute("DROP DATABASE IF EXISTS " + DB)
    # cursor.execute("CREATE DATABASE " + DB)
    # db.commit()
    # db.close()

    db = pymysql.connect(dbconf["host"], dbconf["user"],
                         dbconf["password"], db=DB)
    cursor = db.cursor()

    #create_tables(cursor);
    #populate_base_tables(cursor);
    #populate_layouts(cursor)
    #populate_labels(cursor)
    populate_hp_taxonomy(cursor)

    print("Hello!")
    cursor.close()
    db.commit()
    db.close()

    #TODO:
    # - Show summary stats of old vs new db
    # Print commands to replace old with new
