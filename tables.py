import random
import datetime
import sys
import os
from .db_config import DATABASE as dbconf
from .table_utils.taxonomy import *
import logging
import pymysql
import pymysql.cursors


class Base:
    @staticmethod
    def execute_query(query):
        connection = pymysql.connect(host=dbconf["host"],
                             user=dbconf["user"],
                             password=dbconf["password"],
                             db=dbconf['database'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        print(query)
        cursor.execute(query)
        connection.commit()
        return cursor

    @staticmethod
    def sanitize_string(string):
        string = string.replace("'", r"\'")
        print("helloz", string)
        return string

class Data:
    @staticmethod
    def summary():
        query = """
            SELECT DISTINCT namespace from layouts
        """
        cursor = Base.execute_query(query)
        layouts = cursor.fetchall()
        query = """
            SELECT DISTINCT namespace from labels
        """
        cursor = Base.execute_query(query)
        labels = cursor.fetchall()
        return [{"namespace": "ppi",
                "layouts": [x["namespace"] for x in layouts],
                "labels": [x["namespace"] for x in labels]}]


class Node:

    @staticmethod
    def all():
        query = """
            SELECT DISTINCT name, symbol, id FROM nodes
        """
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def show_random(num_to_show):
        query = "SELECT name, symbol, id FROM nodes ORDER BY RAND() LIMIT %d" % num_to_show
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def nodes_for_attribute(attr_id):
        query = """
            SELECT DISTINCT node.id
            FROM nodes
            JOIN nodes_attributes ON nodes.id = nodes_attributes.node_id
            JOIN attribute_taxonomies ON nodes_attributes.attribute_id = attribute_taxonomies.child_id
            AND attribute_taxonomies.parent_id = %d
        """ % attr_id
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def nodes_for_autocomplete(name_prefix):
        query = """
            SELECT nodes.id, nodes.symbol, nodes.name
            FROM nodes
            WHERE LOWER(nodes.symbol) like LOWER('%s')
            OR LOWER(nodes.name) like LOWER('%s')
        """ % (Base.sanitize_string(name_prefix) + '%', Base.sanitize_string(name_prefix) + '%')
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    # @staticmethod
    # def search(clauses):
    #     print(clauses)
    #     have_name = False
    #     have_diseases = False
    #     have_go_categories = False
    #     filter_clauses = []
    #     select_clauses = []

    #     def filter_clause(subject, object):
    #         print(subject)
    #         if subject == "name_like":
    #             have_name = True
    #             return [" LOWER(genes.symbol) like LOWER('%s') " % (Base.sanitize_string(object) + "%"),
    #                     ["name", object.lower()]]
    #         column = ""
    #         if subject == "disease":
    #             column = "do_id"
    #             have_diseases = True
    #         else:
    #             column = "go_id"
    #             have_go_categories = True

    #         return ["%s = '%s'" % (column, object),
    #                 [column, object]]

    #     def get_summary_stats(gene_set):
    #         query = """
    #         SELECT diseases.name, prevalence, count(distinct jgenes.id) as gene_number
    #         FROM diseases
    #         JOIN disease_taxonomy on diseases.id = parent_id
    #         JOIN genes_diseases ON genes_diseases.disease_id = child_id
    #         JOIN (select * from genes  where entrez_id in (%s)) jgenes ON jgenes.id = genes_diseases.gene_id
    #         JOIN disease_counts on disease_counts.disease_id = diseases.id
    #         WHERE prevalence > 25
    #         GROUP BY 1, 2
    #         ORDER BY 3 DESC
    #         LIMIT 200
    #         """ % ",".join([str(gene["entrez_id"]) for gene in gene_set])
    #         cursor = Base.execute_query(query)
    #         results = cursor.fetchall()
    #         results = [{"name": x["name"], "gene_number": round(x["gene_number"]/x["prevalence"]* len(results), 2)} for x in results]
    #         results.sort(reverse=True, key=lambda x: x["gene_number"])
    #         return results[:10]


    #     for x in range(5):
    #         andor = clauses["predicate%d" % x] if "predicate%d" % x in clauses else "AND"
    #         if "subject%d" % x not in clauses or clauses["subject%d" % x] == "undefined" \
    #         or "object%d" % x not in clauses or clauses["object%d" % x] == "undefined":
    #             break
    #         if clauses["subject%d" % x] == "disease":
    #             have_diseases = True
    #         elif clauses["subject%d" % x] == "name_like":
    #             have_name = True
    #         else:
    #             have_go_categories = True
    #         new_clause = filter_clause(clauses["subject%d" % x], clauses["object%d" % x] )
    #         if andor == "AND":
    #             filter_clauses.append(new_clause[0])
    #             select_clauses.append([new_clause[1]])
    #         else:
    #             filter_clauses[-1]= filter_clauses[-1] + " OR " + new_clause[0]
    #             select_clauses[-1].append(new_clause[1])
    #     if not filter_clauses:
    #         print("no filter clauses!")
    #         return({"genes": [], "summary_stats": []})
    #     if have_name and not have_diseases and not have_go_categories:
    #         name_select_clause = """
    #             SELECT name, symbol, entrez_id FROM genes WHERE
    #         """
    #         print("hello! I'm just a name")
    #         query = name_select_clause + " AND ".join(filter_clauses)
    #         cursor = Base.execute_query(query)
    #         genes = cursor.fetchall()
    #         return({"genes": genes, "summary_stats": get_summary_stats(genes)})

    #     print(filter_clauses)
    #     print(have_diseases, have_go_categories)
    #     genes_to_names = {}
    #     if have_diseases and have_go_categories:
    #         name_disease_select_clause = """
    #         SELECT DISTINCT genes.name, genes.symbol, genes.entrez_id,
    #             GROUP_CONCAT(DISTINCT diseases.do_id) AS do_id,
    #             GROUP_CONCAT(DISTINCT go_categories.go_id) as go_id
    #         FROM genes
    #         JOIN genes_diseases ON genes_diseases.gene_id = genes.id
    #         JOIN disease_taxonomy ON genes_diseases.disease_id = disease_taxonomy.child_id
    #         JOIN diseases ON diseases.id = disease_taxonomy.parent_id
    #         JOIN genes_go_categories ON genes.id = genes_go_categories.gene_id
    #         JOIN go_taxonomy ON genes_go_categories.go_category_id = go_taxonomy.child_id
    #         JOIN go_categories ON go_categories.id = go_taxonomy.parent_id
    #         WHERE %s
    #         GROUP BY 1, 2, 3
    #         """ % " OR ".join(filter_clauses)
    #     elif have_diseases:
    #         name_disease_select_clause = """
    #         SELECT DISTINCT genes.name, genes.symbol, genes.entrez_id,
    #             GROUP_CONCAT(DISTINCT diseases.do_id) AS do_id,
    #             "" as go_id
    #         FROM genes
    #         JOIN genes_diseases ON genes_diseases.gene_id = genes.id
    #         JOIN disease_taxonomy ON genes_diseases.disease_id = disease_taxonomy.child_id
    #         JOIN diseases ON diseases.id = disease_taxonomy.parent_id
    #         WHERE %s
    #         GROUP BY 1, 2, 3
    #         """ % " OR ".join(filter_clauses)
    #     elif have_go_categories:
    #         name_disease_select_clause = """
    #         SELECT DISTINCT genes.name, genes.symbol, genes.entrez_id,
    #             "" as do_id,
    #             GROUP_CONCAT(DISTINCT go_categories.go_id) as go_id
    #         FROM genes
    #         JOIN genes_go_categories ON genes.id = genes_go_categories.gene_id
    #         JOIN go_taxonomy ON genes_go_categories.go_category_id = go_taxonomy.child_id
    #         JOIN go_categories ON go_categories.id = go_taxonomy.parent_id
    #         WHERE %s
    #         GROUP BY 1, 2, 3
    #         """ % " OR ".join(filter_clauses)
    #     query = name_disease_select_clause
    #     cursor = Base.execute_query(query)
    #     disease_table = cursor.fetchall()
    #     genes_to_diseases = {x["entrez_id"]: x["do_id"].split(",") for x in disease_table}
    #     genes_to_go_categories = {x["entrez_id"]: x["go_id"].split(",") for x in disease_table}
    #     genes_to_names_d = {x["entrez_id"]: {'name': x['name'], 'symbol': x['symbol']} for x in disease_table}
    #     genes_to_names = {**genes_to_names, **genes_to_names_d}

    #     candidate_genes = set(genes_to_names.keys())
    #     for clause in select_clauses:
    #         keep_genes = set()
    #         for subclause in clause:
    #             print(clause)
    #             print(subclause)
    #             if subclause[0] == "name":
    #                 new_candidates = [x for x in candidate_genes if subclause[1].lower() in genes_to_names[x]["name"]]
    #             elif subclause[0] == "do_id":
    #                 new_candidates = [x for x in candidate_genes if subclause[1] in genes_to_diseases[x]]
    #             else:
    #                 new_candidates = [x for x in candidate_genes if subclause[1] in genes_to_go_categories[x]]
    #             for x in new_candidates:
    #                 keep_genes.add(x)
    #         candidate_genes = keep_genes
    #     genes = [{"entrez_id": x, "name": genes_to_names[x]["name"], "symbol": genes_to_names[x]["symbol"]} for x in candidate_genes]
    #     return({"genes": genes, "summary_stats": get_summary_stats(genes)})

class Attribute:
    @staticmethod
    def attributes_for_node(node_id, namespace=None):
        namespace_clause = " AND a.namespace = \"%s\"" % namespace if namespace else ""
        query = """
            SELECT DISTINCT a.id, a.name, a.description, a.namespace, distance
            FROM attributes a
            JOIN attribute_taxonomies at ON a.id = at.parent_id
            JOIN nodes_attributes na ON na.attribute_id = at.child_id
            WHERE node_id = %d
            %s
        """ % (node_id, namespace_clause)
        cursor = Base.execute_query(query)
        results = cursor.fetchall()
        attributes = {}
        for result in results:
            if result["id"] in attributes:
                attributes[result["id"]] = attributes[result["id"]] + [""] * (result["distance"] + 1 - len(attributes[result["id"]]))
                print(result["id"])
                print(attributes[result["id"]])
                print(result["distance"])
                attributes[result["id"]][result["distance"]] = result["name"]
            else:
                attributes[result["id"]] = [""] * (result["distance"]) + [result["name"]]
        return [{"id": result["id"],
                 "full_name": "/".join(attributes[result["id"]][:-1][::-1]),
                 "name": result["name"],
                 "description": result["description"]} for result in results]

    @staticmethod
    def attributes_for_autocomplete(name_prefix, namespace=None):
        namespace_clause = " AND namespace = \"%s\"" % namespace if namespace else ""
        query = """
            SELECT attributes.id, attributes.name, namespace
            FROM attributes
            WHERE LOWER(attributes.name) like LOWER('%s')
            %s
        """ % (Base.sanitize_string(name_prefix) + '%', namespace_clause)
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def all_attribute_names(namespace=None):
        namespace_clause = " WHERE namespace = \"%s\"" % namespace if namespace else ""
        query = """
            SElECT DISTINCT attributes.id, attributes.name, namespace
            FROM attributes
            %s
        """ % namespace_clause
        cursor = Base.execute_query(query)
        return cursor.fetchall()

class AttributeTaxonomy:

    @staticmethod
    def construct_taxonomy(root_node):
        start_time = datetime.datetime.now()
        query = """
            SELECT DISTINCT attributes.id,
                attributes.name, attribute_taxonomies.child_id, attribute_taxonomies.distance
            FROM attributes
            JOIN attribute_taxonomies ON attribute_taxonomies.parent_id = attributes.id
                AND attribute_taxonomies.distance IN (0, 1)
            JOIN attribute_taxonomies dt2 on attributes.id = dt2.child_id and dt2.parent_id = %s
        """ % root_node
        cursor = Base.execute_query(query)
        db_results = cursor.fetchall()
        return build_taxonomy(db_results, root_node)

class Article:
    @staticmethod
    def article_for_pubid(pub_id):
        query = """
            SELECT articles.authors_list, articles.abstract, articles.title,
                DATE_FORMAT(CURDATE(), '%s') AS publication_date,
                "Fake Journal" AS publication, 10000 as citation_count
            FROM articles
            WHERE articles.type = "pubmed"
            AND articles.external_id = '%s'
        """ % ("%Y-%m-%d", pub_id)
        cursor = Base.execute_query(query)
        return cursor.fetchone()

    @staticmethod
    def articles_for_node(entrez_id):
        query = """
            SELECT articles.external_id, articles.title,
                DATE_FORMAT(CURDATE(), '%s') AS publication_date,
                "Fake Journal" AS publication, 10000 as citation_count
            FROM articles
            JOIN nodes_articles ON nodes_articles.article_id = articles.id
            JOIN nodes ON nodes.id = nodes_articles.node_id
            WHERE articles.type = 'pubmed'
            AND nodes.id = '%s'
            ORDER BY articles.publication_date desc
        """ % ("%Y-%m-%d", entrez_id)
        cursor = Base.execute_query(query)
        return cursor.fetchall()

# class GoCategory:
#     @staticmethod
#     def go_categories_for_gene(entrez_id, namespace):
#         namespace_filter =  "" if namespace ==  'all' else "AND go_categories.namespace = '%s'" % namespace
#         query = """
#             SELECT DISTINCT go_categories.go_id, go_categories.name, distance, genes_go_categories.go_category_id
#             FROM go_categories
#             JOIN go_taxonomy ON go_categories.id = go_taxonomy.parent_id
#             JOIN genes_go_categories ON genes_go_categories.go_category_id = go_taxonomy.child_id
#             JOIN genes ON genes.id = genes_go_categories.gene_id
#             WHERE genes.entrez_id = '%s'
#             AND go_categories.go_id NOT IN ("GO:0003674", "GO:0005575", "GO:0008150")
#             %s
#         """ % (entrez_id, namespace_filter)
#         cursor = Base.execute_query(query)
#         results = cursor.fetchall()
#         gos = {}
#         for result in results:
#             print(result)
#             if result["go_category_id"] in gos:
#                 gos[result["go_category_id"]] = gos[result["go_category_id"]] + [""] * (result["distance"] + 1 - len(gos[result["go_category_id"]]))
#                 print(result["go_category_id"])
#                 print(gos[result["go_category_id"]])
#                 print(result["distance"])
#                 gos[result["go_category_id"]][result["distance"]] = result["name"]
#             else:
#                 gos[result["go_category_id"]] = [""] * (result["distance"]) + [result["name"]]
#         return [{"id": key, "name": "/".join(value[:-1][::-1])} for key, value in gos.items()]
#
#     @staticmethod
#     def go_categories_for_autocomplete(name_prefix):
#         query = """
#             SELECT go_categories.go_id, go_categories.name
#             FROM go_categories
#             WHERE LOWER(go_categories.name) like LOWER('%s')
#         """ % (name_prefix + '%')
#         cursor = Base.execute_query(query)
#         return cursor.fetchall()
#
#     def go_category_names_for_branch(branch_name):
#         query = """
#             SELECT DISTINCT go_categories.go_id, go_categories.name
#             FROM genes_go_categories
#             JOIN go_taxonomy on go_taxonomy.child_id = genes_go_categories.go_category_id
#             JOIN go_categories ON go_categories.id = go_taxonomy.parent_id
#             WHERE namespace = '%s'
#         """ % branch_name
#         cursor = Base.execute_query(query)
#         return cursor.fetchall()
#
# class GoTaxonomy:
#     @staticmethod
#     def construct_taxonomy(root_node):
#         start_time = datetime.datetime.now()
#         query = """
#             SELECT DISTINCT go_categories.id, go_categories.go_id AS external_id,
#                 go_categories.name, go_taxonomy.child_id, go_taxonomy.distance
#             FROM go_categories
#             JOIN go_taxonomy ON go_taxonomy.parent_id = go_categories.id AND go_taxonomy.distance IN (0, 1)
#             JOIN go_taxonomy gt2 on go_categories.id = gt2.child_id and gt2.parent_id = %s
#         """ % root_node
#         cursor = Base.execute_query(query)
#         db_results = cursor.fetchall()
#         return build_taxonomy(db_results, root_node)

class Edge:
    @staticmethod
    def all(namespace):
        query = """
        SELECT edges.node1_id, edges.node2_id
        FROM edges
        WHERE edges.node1_id < edges.node2_id
        """
        cursor = Base.execute_query(query)
        results = cursor.fetchall()
        return [[r["node1_id"] for r in results], [r["node2_id"] for r in results]]

class Layout:
    @staticmethod
    def all_namespaces():
        query = """
        SELECT DISTINCT namespace, count(*)
        FROM layouts
        GROUP BY 1
        """
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def fetch(namespace):
        query = """
        SELECT node_id, n.symbol, n.name, x_loc, y_loc, z_loc, r_val, g_val, b_val, a_val
        FROM layouts
        JOIN nodes n on n.id = layouts.node_id
        WHERE namespace = "%s"
        """ % namespace
        cursor = Base.execute_query(query)
        layout = cursor.fetchall()
        return [{'v': [r["x_loc"], r["y_loc"], r["z_loc"], r["r_val"], r["g_val"], r["b_val"], r["a_val"] ],
                 'a': [str(r["node_id"]), r["symbol"], r["name"]]} for r in layout]

class Label:
    @staticmethod
    def all_namespaces():
        query = """
        SELECT DISTINCT namespace, count(*)
        FROM labels
        GROUP BY 1
        """
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def fetch(namespace):
        query = """
        SELECT text, x_loc, y_loc, z_loc
        FROM labels
        WHERE namespace = "%s"
        """ % namespace
        cursor = Base.execute_query(query)
        label = cursor.fetchall()
        return [{'loc': [r["x_loc"], r["y_loc"], r["z_loc"]],
                 'text': r["text"]} for r in label]

# class SavedView:
#     @staticmethod
#     def get(username, view_name):
#         query = """
#         SELECT saved_views.username, saved_views.view_name, saved_views.session_info
#         FROM Datadivr_sessions.saved_views
#         WHERE saved_views.username = '%s'
#         AND saved_views.view_name = '%s'
#         """ % (username, view_name)
#         cursor = Base.execute_query(query)
#         return cursor.fetchall()
#
#     @staticmethod
#     def create(data):
#         username = data["username"]
#         view_name = data["view_name"]
#         session_info = data["session_info"]
#         query = """
#         INSERT INTO Datadivr_sessions.saved_views (username, view_name, session_info)
#         VALUES ('%s', '%s', '%s')
#         """ % (username, view_name, session_info)
#         cursor = Base.execute_query(query)



if __name__ == '__main__':
    #dbconf = db_config.asimov

    # print(Gene.genes_for_disease("DOID:0001816"))
    #a, b = Article.article_for_pubid("27325740")
    #print(b, a)
    #print(Node.nodes_for_autocomplete("sl"))
    #print(Disease.diseases_for_gene(19))
    #print(Gene.gene_search("", "undefined", "GO:0019835"))
    #print(Attribute.attributes_for_node( 4, "DISEASE"))
    print(Layout.all_namespaces())
    print(Layout.fetch("spring"))

