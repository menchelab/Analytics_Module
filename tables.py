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
        return cursor

    @staticmethod
    def sanitize_string(string):
        string = string.replace("'", r"\'")
        print("helloz", string)
        return string

class Gene:

    @staticmethod
    def all():
        query = """

        """

    @staticmethod
    def show_random(num_to_show):
        query = "SELECT name, entrez_id FROM genes ORDER BY RAND() LIMIT %d" % num_to_show
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def genes_for_disease(disease_id):
        query = """
            SELECT DISTINCT gene.holo_id
            FROM genes
            JOIN genes_diseases ON genes.id = genes_diseases.gene_id
            JOIN disease_taxonomy ON genes_diseases.disease_id = disease_taxonomy.child_id
            JOIN diseases ON diseases.id = disease_taxonomy.parent_id
            WHERE genes.holo_id IS NOT NULL
            AND diseases.do_id = '%s'
        """
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def genes_for_go_category(go_category_id):
        query = """
            SELECT DISTINCT genes.holo_id
            FROM genes
            JOIN genes_go_categories ON genes.id = genes_go_categories.gene_id
            JOIN go_taxonomy ON genes_go_categories.go_category_id = go_taxonomy.child_id
            JOIN go_categories ON go_categories.id = go_taxonomy.parent_id
            WHERE genes.holo_id IS NOT NULL
            AND go_categories.go_id = '%s'
        """ % go_category_id
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def genes_for_autocomplete(name_prefix):
        query = """
            SELECT genes.entrez_id, genes.symbol
            FROM genes
            WHERE LOWER(genes.symbol) like LOWER('%s')
            AND genes.holo_id IS NOT NULL
        """ % (Base.sanitize_string(name_prefix) + '%')
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def search(clauses):
        have_name = False
        have_diseases = False
        have_go_categories = False
        filter_clauses = []
        select_clauses = []

        def filter_clause(subject, object):
            print(subject)
            if subject == "name_like":
                have_name = True
                return [" LOWER(genes.symbol) like LOWER('%s') " % (Base.sanitize_string(object) + "%"),
                        ["name", object.lower()]]
            column = ""
            if subject == "disease":
                column = "do_id"
                have_diseases = True
            else:
                column = "go_id"
                have_go_categories = True

            return ["%s = '%s'" % (column, object),
                    [column, object]]

        for x in range(5):
            andor = clauses["predicate%d" % x] if "predicate%d" % x in clauses else "AND"
            if "subject%d" % x not in clauses or clauses["subject%d" % x] == "undefined" \
            or "object%d" % x not in clauses or clauses["object%d" % x] == "undefined":
                break
            if clauses["subject%d" % x] == "disease":
                have_diseases = True
            elif clauses["subject%d" % x] == "name_like":
                pass
            else:
                have_go_categories = True
            new_clause = filter_clause(clauses["subject%d" % x], clauses["object%d" % x] )
            if andor == "AND":
                filter_clauses.append(new_clause[0])
                select_clauses.append([new_clause[1]])
            else:
                filter_clauses[-1]= filter_clauses[-1] + " OR " + new_clause[0]
                select_clauses[-1].append(new_clause[1])
        if not filter_clauses:
            print("no filter clauses!")
            return([])
        if have_name and not have_diseases and not have_go_categories:
            name_select_clause = """
                SELECT name, symbol, entrez_id FROM genes WHERE
            """
            query = name_select_clause + " AND ".join(filter_clauses)
            cursor = Base.execute_query(query)
            return cursor.fetchall()

        print(filter_clauses)
        print(have_diseases, have_go_categories)
        genes_to_names = {}
        if have_diseases and have_go_categories:
            name_disease_select_clause = """
            SELECT DISTINCT genes.name, genes.symbol, genes.entrez_id,
                GROUP_CONCAT(DISTINCT diseases.do_id) AS do_id,
                GROUP_CONCAT(DISTINCT go_categories.go_id) as go_id
            FROM genes
            JOIN genes_diseases ON genes_diseases.gene_id = genes.id
            JOIN disease_taxonomy ON genes_diseases.disease_id = disease_taxonomy.child_id
            JOIN diseases ON diseases.id = disease_taxonomy.parent_id
            JOIN genes_go_categories ON genes.id = genes_go_categories.gene_id
            JOIN go_taxonomy ON genes_go_categories.go_category_id = go_taxonomy.child_id
            JOIN go_categories ON go_categories.id = go_taxonomy.parent_id
            WHERE %s
            GROUP BY 1, 2, 3
            """ % " OR ".join(filter_clauses)
        elif have_diseases:
            name_disease_select_clause = """
            SELECT DISTINCT genes.name, genes.symbol, genes.entrez_id,
                GROUP_CONCAT(DISTINCT diseases.do_id) AS do_id,
                "" as go_id
            FROM genes
            JOIN genes_diseases ON genes_diseases.gene_id = genes.id
            JOIN disease_taxonomy ON genes_diseases.disease_id = disease_taxonomy.child_id
            JOIN diseases ON diseases.id = disease_taxonomy.parent_id
            WHERE %s
            GROUP BY 1, 2, 3
            """ % " OR ".join(filter_clauses)
        else:
            name_disease_select_clause = """
            SELECT DISTINCT genes.name, genes.symbol, genes.entrez_id,
                "" as do_id,
                GROUP_CONCAT(DISTINCT go_categories.go_id) as go_id
            FROM genes
            JOIN genes_go_categories ON genes.id = genes_go_categories.gene_id
            JOIN go_taxonomy ON genes_go_categories.go_category_id = go_taxonomy.child_id
            JOIN go_categories ON go_categories.id = go_taxonomy.parent_id
            WHERE %s
            GROUP BY 1, 2, 3
            """ % " OR ".join(filter_clauses)
        query = name_disease_select_clause
        cursor = Base.execute_query(query)
        disease_table = cursor.fetchall()
        genes_to_diseases = {x["entrez_id"]: x["do_id"].split(",") for x in disease_table}
        genes_to_go_categories = {x["entrez_id"]: x["go_id"].split(",") for x in disease_table}
        genes_to_names_d = {x["entrez_id"]: {'name': x['name'], 'symbol': x['symbol']} for x in disease_table}
        genes_to_names = {**genes_to_names, **genes_to_names_d}

        candidate_genes = set(genes_to_names.keys())
        for clause in select_clauses:
            keep_genes = set()
            for subclause in clause:
                print(clause)
                print(subclause)
                if subclause[0] == "name":
                    new_candidates = [x for x in candidate_genes if subclause[1].lower() in genes_to_names[x]["name"]]
                elif subclause[0] == "do_id":
                    new_candidates = [x for x in candidate_genes if subclause[1] in genes_to_diseases[x]]
                else:
                    new_candidates = [x for x in candidate_genes if subclause[1] in genes_to_go_categories[x]]
                for x in new_candidates:
                    keep_genes.add(x)
            candidate_genes = keep_genes
        return[{"entrez_id": x, "name": genes_to_names[x]["name"], "symbol": genes_to_names[x]["symbol"]} for x in candidate_genes]

class Disease:
    @staticmethod
    def diseases_for_gene(entrez_id):
        query = """
            SELECT DISTINCT diseases.do_id, diseases.name
            FROM diseases
            JOIN disease_taxonomy ON diseases.id = disease_taxonomy.parent_id
            JOIN genes_diseases ON genes_diseases.disease_id = disease_taxonomy.child_id
            JOIN genes ON genes_diseases.gene_id = genes.id
            WHERE genes.entrez_id = %s
        """ % entrez_id
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def diseases_for_autocomplete(name_prefix):
        query = """
            SELECT diseases.do_id, diseases.name
            FROM diseases
            WHERE LOWER(diseases.name) like LOWER('%s')
        """ % (Base.sanitize_string(name_prefix) + '%')
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def all_disease_names():
        query = """
            SElECT DISTINCT diseases.do_id, diseases.name
            FROM diseases
        """
        cursor = Base.execute_query(query)
        return cursor.fetchall()

class DiseaseTaxonomy:

    @staticmethod
    def construct_taxonomy(root_node):
        start_time = datetime.datetime.now()
        query = """
            SELECT DISTINCT diseases.id, diseases.do_id AS external_id,
                diseases.name, disease_taxonomy.child_id, disease_taxonomy.distance
            FROM diseases
            JOIN disease_taxonomy ON disease_taxonomy.parent_id = diseases.id AND disease_taxonomy.distance IN (0, 1)
            JOIN disease_taxonomy dt2 on diseases.id = dt2.child_id and dt2.parent_id = %s
        """ % root_node
        cursor = Base.execute_query(query)
        db_results = cursor.fetchall()
        return build_taxonomy(db_results, root_node)

class Article:
    @staticmethod
    def article_for_pubid(pub_id):
        query = """
            SELECT articles.authors_list, articles.abstract
            FROM articles
            WHERE articles.type = "pubmed"
            AND articles.external_id = '%s'
        """ % pub_id
        cursor = Base.execute_query(query)
        return cursor.fetchone()

    @staticmethod
    def articles_for_gene(entrez_id):
        query = """
            SELECT articles.external_id, articles.title
            FROM articles
            JOIN genes_articles ON genes_articles.article_id = articles.id
            JOIN genes ON genes.id = genes_articles.gene_id
            WHERE articles.type = 'pubmed'
            AND genes.entrez_id = '%s'
        """ % entrez_id
        cursor = Base.execute_query(query)
        return cursor.fetchall()

class GoCategory:
    @staticmethod
    def go_categories_for_gene(entrez_id, namespace):
        namespace_filter =  "" if namespace ==  'all' else "AND go_categories.namespace = '%s'" % namespace
        query = """
            SELECT DISTINCT go_categories.go_id, go_categories.name
            FROM go_categories
            JOIN go_taxonomy ON go_categories.id = go_taxonomy.parent_id
            JOIN genes_go_categories ON genes_go_categories.go_category_id = go_taxonomy.child_id
            JOIN genes ON genes.id = genes_go_categories.gene_id
            WHERE genes.entrez_id = '%s'
            AND go_categories.go_id NOT IN ("GO:0003674", "GO:0005575", "GO:0008150")
            %s
        """ % (entrez_id, namespace_filter)
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def go_categories_for_autocomplete(name_prefix):
        query = """
            SELECT go_categories.go_id, go_categories.name
            FROM go_categories
            WHERE LOWER(go_categories.name) like LOWER('%s')
        """ % (name_prefix + '%')
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    def go_category_names_for_branch(branch_name):
        query = """
            SELECT go_categories.go_id, go_categories.name
            FROM go_categories
            WHERE namespace = '%s'
        """ % branch_name
        cursor = Base.execute_query(query)
        return cursor.fetchall()

class GoTaxonomy:
    @staticmethod
    def construct_taxonomy(root_node):
        start_time = datetime.datetime.now()
        query = """
            SELECT DISTINCT go_categories.id, go_categories.go_id AS external_id,
                go_categories.name, go_taxonomy.child_id, go_taxonomy.distance
            FROM go_categories
            JOIN go_taxonomy ON go_taxonomy.parent_id = go_categories.id AND go_taxonomy.distance IN (0, 1)
            JOIN go_taxonomy gt2 on go_categories.id = gt2.child_id and gt2.parent_id = %s
        """ % root_node
        cursor = Base.execute_query(query)
        db_results = cursor.fetchall()
        return build_taxonomy(db_results, root_node)

class PPI:
    @staticmethod
    def all():
        query = """
        SELECT ppi.gene1_id, ppi.gene2_id,
               genes1.entrez_id as gene1_entrez_id,
               genes2.entrez_id as gene2_entrez_id
        FROM ppi
        JOIN genes genes1 on ppi.gene1_id = genes1.id
        JOIN genes genes2 on ppi.gene2_id = genes2.id
        WHERE ppi.gene1_id < ppi.gene2_id
        """
        cursor = Base.execute_query(query)
        return cursor.fetchall()


if __name__ == '__main__':
    #logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)
    # dbconf = db_config.asimov

    # print(Gene.genes_for_disease("DOID:0001816"))
    #a, b = Article.article_for_pubid("27325740")
    #print(b, a)
    #print(Gene.genes_for_autocomplete("sl"))
    #print(Disease.diseases_for_gene(19))
    print(Gene.gene_search("", "undefined", "GO:0019835"))
    print(GoCategory.go_categories_for_gene( "8542", "all"))
    print(GoTaxonomy.construct_taxonomy(2740))


