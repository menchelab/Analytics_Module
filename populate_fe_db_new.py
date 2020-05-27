import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), "..")))
import db_config
import pymysql
import networkx as nx

'''
This code populates the tables explicitly used by the DataDiVR to present information.

Although the rest of the code is database-agnostic, please note that these scripts
make very heavy use of raw queries and therefore are only compatible with MySQL.
'''

def populate_genes(cursor):
    cursor.execute("CREATE table Datadivr_tmp.genes LIKE Datadivr_fe.genes")
    query = '''
    INSERT INTO Datadivr_tmp.genes(entrez_id, name, symbol, holo_id)
    SELECT CONVERT(Entrez_Gene_ID_NCBI, SIGNED), Approved_Name, Approved_Symbol, l.holoid
    FROM GenesGO.hgnc_complete h
    LEFT JOIN Datadivr.Holo_lookup l ON l.entrezid = CONVERT(Entrez_Gene_ID_NCBI, SIGNED)
    WHERE h.Entrez_Gene_ID_NCBI != ""
    AND CONVERT(Entrez_Gene_ID_NCBI, SIGNED) > 0
    AND Entrez_Gene_ID_NCBI IS NOT NULL
    AND h.Locus_Type IN
    ("gene with protein product", "immunoglobulin gene", "T cell receptor gene")
    '''
    cursor.execute(query)

def populate_diseases(cursor):
    cursor.execute("CREATE TABLE Datadivr_tmp.diseases LIKE Datadivr_fe.diseases")
    cursor.execute("CREATE TABLE Datadivr_tmp.disease_taxonomy LIKE Datadivr_fe.disease_taxonomy")
    query = '''
    INSERT INTO Datadivr_tmp.diseases (do_id, name)
    SELECT do.do_id, do.do_name
    FROM Gene2Disease.disease_ontology do
    WHERE do.is_obsolete != 'true';
    '''
    cursor.execute(query)

def populate_disease_taxonomy(cursor):
    cursor.execute("CREATE TABLE Datadivr_tmp.disease_taxonomy LIKE Datadivr_fe.disease_taxonomy")
    query = '''
    SELECT do_id, is_a
    FROM Gene2Disease.disease_ontology
    WHERE is_obsolete != 'true';
    '''
    cursor.execute(query)
    disease_tree_data = cursor.fetchall()

    query = '''
    SELECT id, do_id FROM Datadivr_tmp.diseases
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



    values = ",".join(["(%s)" % ",".join(x.split("->") +  [str(edges[x])]) for x in edges])
    query = '''
    INSERT INTO Datadivr_tmp.disease_taxonomy (parent_id, child_id, distance) VALUES %s
    ''' % values
    cursor.execute(query)

def populate_genes_diseases(cursor):
    cursor.execute("CREATE TABLE Datadivr_tmp.genes_diseases LIKE Datadivr_fe.genes_diseases")
    query = '''
    INSERT INTO Datadivr_tmp.genes_diseases(gene_id, disease_id)
    SELECT g.id, d.id
    FROM Datadivr_tmp.genes g
    JOIN Gene2Disease.gene2disease_all gd ON g.entrez_id = gd.entrezID
    JOIN HumanPhenotypes.umlsmapping mp
    ON mp.disease_ID = gd.diseaseID
    JOIN Datadivr_tmp.diseases d
    ON right(d.do_id, length(d.do_id) - 5) = mp.identifier
    '''
    cursor.execute(query)

def populate_articles(cursor):
    cursor.execute("CREATE TABLE Datadivr_tmp.articles LIKE Datadivr_fe.articles")
    query = '''
    INSERT INTO Datadivr_tmp.articles(
        external_id, title, authors_list, abstract, type, url)
    SELECT DISTINCT a.pubid, b.title, REPLACE(b.author, ",", ", "), b.abstract, "pubmed", a.pubmedurl
    FROM Datadivr.gene2pubid a
    JOIN Datadivr.pubid2text b
    ON a.pubid = b.pubid AND a.pubid IS NOT NULL

    '''
    cursor.execute(query)


def populate_genes_articles(cursor):
    cursor.execute("CREATE TABLE Datadivr_tmp.genes_articles LIKE Datadivr_fe.genes_articles")
    query = '''
    INSERT INTO Datadivr_tmp.genes_articles(gene_id, article_id)
    SELECT g.id, a.id
    FROM Datadivr_tmp.genes g
    JOIN Datadivr.gene2pubid gp ON g.entrez_id = gp.entrez AND g.entrez_id IS NOT NULL
    JOIN Datadivr_tmp.articles a ON a.external_id = gp.pubid and a.type="pubmed"
    '''
    cursor.execute(query)

def populate_go_categories(cursor):
    cursor.execute("CREATE TABLE Datadivr_tmp.go_categories LIKE Datadivr_fe.go_categories")
    query = '''
    INSERT INTO Datadivr_tmp.go_categories(go_id, name, namespace, description)
    SELECT DISTINCT go_id, go_name, namespace, def
    FROM Datadivr.GO_tree
    '''
    cursor.execute(query)

def populate_genes_go_categories(cursor):
    cursor.execute("CREATE TABLE Datadivr_tmp.genes_go_categories LIKE Datadivr_fe.genes_go_categories")
    query = '''
    INSERT INTO Datadivr_tmp.genes_go_categories(gene_id, go_category_id)
    SELECT DISTINCT g.id, gc.id
    FROM GenesGO.Gene2GO_human h
    JOIN Datadivr_tmp.genes g ON g.entrez_id = h.entrezid
    JOIN Datadivr_tmp.go_categories gc ON gc.go_id = h.go_id
    WHERE h.entrezid != '-'
    AND h.evidence != 'ND'
    AND h.evidence != 'IEA'
    AND h.evidence != 'IPI'
    '''
    cursor.execute(query)

def populate_go_taxonomy(cursor):
    cursor.execute("CREATE TABLE Datadivr_tmp.go_taxonomy LIKE Datadivr_fe.go_taxonomy")

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
    SELECT id, go_id FROM Datadivr_tmp.go_categories
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



    values = ",".join(["(%s)" % ",".join(x.split("->") +  [str(edges[x])]) for x in edges])
    query = '''
    INSERT INTO Datadivr_tmp.go_taxonomy (parent_id, child_id, distance) VALUES %s
    ''' % values
    cursor.execute(query)


def populate_ppi(cursor):
    cursor.execute("CREATE TABLE Datadivr_tmp.ppi LIKE Datadivr_fe.ppi")
    query = '''
    INSERT INTO Datadivr_tmp.ppi (gene1_id, gene2_id)
    SELECT DISTINCT * FROM (
    SELECT g1.id as g_from, g2.id  as g_to
    FROM networks.PPI_hippie2017 e
    JOIN GenesGO.hgnc_complete g1 ON e.entrez_1 = g1.Entrez_Gene_ID_NCBI
    JOIN GenesGO.hgnc_complete g2 ON e.entrez_2 = g2.Entrez_Gene_ID_NCBI
    JOIN Datadivr_tmp.genes g1 ON g1.entrez_id = e.entrez_1
    JOIN Datadivr_tmp.genes g2 ON g2.entrez_id = e.entrez_2
    WHERE e.author != '' AND e.entrez_1 != e.entrez_2
    AND g1.Locus_Type in ('T cell receptor gene', 'gene with protein product', 'immunoglobulin gene')
    AND g2.Locus_Type in ('T cell receptor gene', 'gene with protein product', 'immunoglobulin gene')
    UNION
    SELECT g2.id as g_from, g1.id as g_to
    FROM networks.PPI_hippie2017 e
    JOIN GenesGO.hgnc_complete g1 ON e.entrez_1 = g1.Entrez_Gene_ID_NCBI
    JOIN GenesGO.hgnc_complete g2 ON e.entrez_2 = g2.Entrez_Gene_ID_NCBI
    JOIN Datadivr_tmp.genes g1 ON g1.entrez_id = e.entrez_1
    JOIN Datadivr_tmp.genes g2 ON g2.entrez_id = e.entrez_2
    WHERE e.author != '' AND e.entrez_1 != e.entrez_2
    AND g1.Locus_Type in ('T cell receptor gene', 'gene with protein product', 'immunoglobulin gene')
    AND g2.Locus_Type in ('T cell receptor gene', 'gene with protein product', 'immunoglobulin gene')) tbl
    '''
    cursor.execute(query)

def populate_speech_keywords(cursor):
    cursor.execute("CREATE TABLE Datadivr_tmp.speech_keywords LIKE Datadivr_fe.speech_keywords")
    query = '''
    INSERT INTO Datadivr_tmp.speech_keywords(keyword, standardized, type)
    SELECT DISTINCT keyword, standardized, type from Datadivr.speech_keywords;
    '''
    cursor.execute(query)




if __name__ == '__main__':
    print("Hello!")
    dbconf = db_config.menche_admin
    db = pymysql.connect(dbconf["host"], dbconf["user"], dbconf["pasword"])
    cursor = db.cursor()
    cursor.execute("DROP DATABASE IF EXISTS Datadivr_tmp")
    cursor.execute("CREATE DATABASE Datadivr_tmp")
    db.commit()

    print("Hello!")
    populate_genes(cursor)
    print("genes")
    populate_diseases(cursor)
    print("diseases")
    populate_genes_diseases(cursor)
    print("genes_diseases")
    populate_articles(cursor)
    print("articles")
    populate_genes_articles(cursor)
    print("genes_articles")
    populate_go_categories(cursor)
    print("go_categories")
    populate_genes_go_categories(cursor)
    print("genes_go_categories")
    db.commit()
    populate_disease_taxonomy(cursor)
    print("disease_taxonomy")
    populate_go_taxonomy(cursor)
    print("go_taxonomy")
    populate_ppi(cursor)
    print("ppi")
    populate_speech_keywords(cursor)
    print("speech_keywords")
    cursor.close()
    db.commit()
    db.close()

    #TODO:
    # - Show summary stats of old vs new db
    # Print commands to replace old with new
