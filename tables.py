import random
import datetime
import sys
import os
import json
from .db_config import DATABASE as dbconf
from .table_utils.taxonomy import *
from . import populate_db_data_agnostic
# from db_config import DATABASE as dbconf
# from table_utils.taxonomy import *
import logging
import pymysql
import pymysql.cursors
import random
import networkx as nx
import numpy as np

# Cache database call for attribute taxonomy to prevent repeated queries.
def get_cached_edges(cache, db_namespace):
    zkey = "edges_" + db_namespace
    dtc = cache.get(zkey)
    if dtc is None:
        print("!!!!!!! querying")
        query = """
        SELECT edges.node1_id, edges.node2_id
        FROM %s.edges
        """ % db_namespace
        cursor = Base.execute_query(query)
        edges = cursor.fetchall()
        dtc = [[x["node1_id"], x["node2_id"]] for x in edges]
        cache.set(zkey, dtc, timeout=5 * 60 * 60 * 24)
    return dtc


class Base:
    @staticmethod
    def execute_query(query, db = None):
        if not db:
            db = dbconf['database']
        connection = pymysql.connect(host=dbconf["host"],
                             user=dbconf["user"],
                             password=dbconf["password"],
                             db=db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        #print(query)
        cursor.execute(query)
        connection.commit()
        connection.close()
        return cursor

    def execute_queries(queries, db = None):
        if not db:
            db = dbconf['database']
        connection = pymysql.connect(host=dbconf["host"],
                             user=dbconf["user"],
                             password=dbconf["password"],
                             db=db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        #print(query)
        for query in queries:
            cursor.execute(query)
        connection.commit()
        connection.close()
        return cursor

    @staticmethod
    def sanitize_string(string):
        string = string.replace("'", r"\'")
        print("helloz", string)
        return string

class Data:
    @staticmethod
    def describe_namespace(namespace):
        query = """
            SELECT DISTINCT namespace from %s.layouts
        """ % namespace
        cursor = Base.execute_query(query)
        layouts = cursor.fetchall()
        query = """
            SELECT DISTINCT namespace from %s.labels
        """ % namespace
        cursor = Base.execute_query(query)
        labels = cursor.fetchall()
        return {"namespace": namespace,
                "layouts": [x["namespace"] for x in layouts],
                "labels": [x["namespace"] for x in labels]}
    @staticmethod
    def summary():
        query = """
            SELECT name FROM Datadivr_meta.namespaces
        """
        cursor = Base.execute_query(query)
        namespaces = [x["name"] for x in cursor.fetchall()]

        return [Data.describe_namespace(namespace) for namespace in namespaces]


class Node:

    @staticmethod
    def all(db_namespace):
        query = """
            SELECT DISTINCT name, symbol, id FROM %s.nodes
        """ % db_namespace
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def get(db_namespace, node_ids):
        query = """
            SELECT DISTINCT name, symbol, id FROM %s.nodes where id in (%s)
        """ % (db_namespace, ",".join(node_ids))
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def get_sym_name(db_namespace, node_ids):
        print('get functions gets:', node_ids)
        # print('and makes sql strg:', ",".join(node_ids))
        spc = [str(x)+',' for x in node_ids]
        spl_str = ''
        spl_str = spl_str.join(spc)
        spl_str = '(' + spl_str[:-1] + ')'
        print(spl_str)
        query = """
            SELECT DISTINCT name, symbol, id as node_id FROM %s.nodes where id in %s
        """ % (db_namespace,spl_str)
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    # CS: get single one
    @staticmethod
    def get_single_sym_name(db_namespace, node_id):
        print('get functions gets:', node_id)
        query = """
            SELECT DISTINCT name, symbol, id as node_id FROM %s.nodes where id = %s
        """ % (db_namespace,node_id)
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def get_neighbors(db_namespace, node_ids):
        query = """
            SELECT DISTINCT name, symbol, nodes.id FROM %s.nodes
            JOIN %s.edges on nodes.id = edges.node1_id
            WHERE edges.node2_id in (%s)
        """ % (db_namespace, db_namespace, ",".join(node_ids))
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def get_by_external_ids(db_namespace, external_ids):
        query = """
            SELECT DISTINCT name, symbol, id FROM %s.nodes where external_id in (%s)
        """ % (db_namespace, ",".join(external_ids))
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def get_by_symbols(db_namespace, symbols):
        query = """
            SELECT DISTINCT name, symbol, id FROM %s.nodes where symbol in ('%s')
        """ % (db_namespace, "','".join(symbols))
        cursor = Base.execute_query(query)
        return cursor.fetchall()


    @staticmethod
    def show_random(num_to_show, db_namespace):
        query = "SELECT name, symbol, id FROM %s.nodes ORDER BY RAND() LIMIT %d" % (db_namespace, num_to_show)
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def nodes_for_attribute(db_namespace, attr_id):
        #JOIN %s.attribute_taxonomies ON nodes_attributes.attribute_id = attribute_taxonomies.child_id
        #    AND attribute_taxonomies.parent_id in (%s)
        query = """
            SELECT DISTINCT nodes.id AS node_id, nodes.name, nodes.symbol
            FROM %s.nodes
            JOIN %s.nodes_attributes ON nodes.id = nodes_attributes.node_id
            JOIN %s.attribute_taxonomies at on at.child_id = attribute_id
            AND parent_id in (%s)
        """ % (db_namespace, db_namespace, db_namespace, ",".join(attr_id))
        cursor = Base.execute_query(query)
        return {"nodes": cursor.fetchall()}

    @staticmethod
    def nodes_for_autocomplete(db_namespace, name_prefix):
        query = """
            SELECT nodes.id, nodes.symbol, nodes.name
            FROM %s.nodes
            WHERE LOWER(nodes.symbol) like LOWER('%s')
            OR LOWER(nodes.name) like LOWER('%s')
        """ % (db_namespace, Base.sanitize_string(name_prefix) + '%', Base.sanitize_string(name_prefix) + '%')
        cursor = Base.execute_query(query)
        return cursor.fetchall()


    @staticmethod
    def gene_card(namespace, node, cache):
        # num_trials = 100000

        query = """
            SELECT * FROM %s.gene_card WHERE node_id = %s
        """ %(namespace,node)
        cursor = Base.execute_query(query)
        data = cursor.fetchall()
        # print(data)
        nid = [x["node_id"] for x in data][0]
        symbol = [x["symbol"] for x in data][0]
        name = [x["gene_name"] for x in data][0]
        k = [x["degree"] for x in data][0]
        funs = [x["functions"] for x in data][0]
        dis = [x["diseases"] for x in data][0]
        # print(nid,symbol,name,k)

        l_functions = []
        for fs in funs.split('|'):
            l_functions.append(fs)

        l_diseases = []
        for ds in dis.split('|'):
            l_diseases.append(ds)

        # print('gene_data', gene_data)
        query2 = """
            SELECT
                aa.external_id symbol,
                na.value value
            FROM %s.nodes_attributes na
            INNER JOIN %s.attributes aa
            ON na.attribute_id = aa.id
            WHERE na.node_id = %s
            AND aa.namespace = 'GTEx'
        """ %(namespace,namespace,node)
        cursor = Base.execute_query(query2)
        data2 = cursor.fetchall()

        gene_data = [{'node_id': nid,'symbol': symbol,'name': name, 'degree': k,
                        'functions': l_functions, 'diseases': l_diseases,
                    'tissue': data2}]
        # print('gene_data', gene_data)

        return gene_data


    @staticmethod
    def random_walk(namespace, starting_nodes, variants, restart_probability, max_elements, cache):
        num_trials = 100000

        edges = get_cached_edges(cache, namespace)
        neighbors = {}
        for edge in edges:
            if edge[0] not in neighbors.keys():
                neighbors[edge[0]] = [edge[1]]
            else:
                neighbors[edge[0]].append(edge[1])
        visited_nodes = [0] * 20000
        starting_node = random.choice(starting_nodes)


        for i in range (num_trials):
            if random.random() < restart_probability:
                starting_node = random.choice(starting_nodes)
            else:
                starting_node = random.choice(neighbors[starting_node])
            visited_nodes[starting_node] += 1

        query2 = """
            SELECT DISTINCT name, symbol, id FROM %s.nodes
        """ % namespace
        cursor = Base.execute_query(query2)
        d_i_name = cursor.fetchall()
        d_i_name = {x["id"]: x["symbol"] for x in d_i_name}

        # set group 0 for seed, group 2 for genes matching with given variant list, 1 else
        d_node2group = {}
        # print('visited nodes',visited_nodes )
        for i, x in enumerate(visited_nodes):
            if i in starting_nodes:
                d_node2group[i] = 0
            elif i in variants:
                d_node2group[i] = 2
            else:
                d_node2group[i] = 1

        min_frequency = 0
        kept_values = [{'id': i,'symbol': d_i_name[i],'group': d_node2group[i], 'frequency': 1.0*x/num_trials} for i, x in enumerate(visited_nodes) if x > min_frequency*num_trials]

        # print('kept_values:', kept_values)
        kept_values.sort(key=lambda x: x['frequency'], reverse=True)
        kept_values = kept_values[:max_elements]

        # add variants if not empty
        if len(variants)>0:
            add_variants = [{'id': i,'symbol': d_i_name[i],'group': d_node2group[i], 'frequency': 1.0*x/num_trials} for i, x in enumerate(visited_nodes) if i in variants]
            add_variants.sort(key=lambda x: x['frequency'], reverse=True)
            # print('added variants', add_variants)
            kept_values +=  add_variants
            # print('added variants', add_variants)

        kept_node_ids = [x['id'] for x in kept_values]

        edges_kept = [(x,y) for x,y in edges if (x in kept_node_ids and y in kept_node_ids)]
        # print('edges:', edges_kept)
        l_edges_kept = [{'source':s,'target':t,'value':1} for s,t in edges_kept]
        d_data_kept = {'nodes': kept_values,'links': l_edges_kept}

        return d_data_kept

    @staticmethod
    def shortest_path(db_namespace, from_id, to_id):
        #DB query for edges
        print("Path from ", from_id," to ",to_id)
        query = """
                SELECT edges.node1_id, edges.node2_id
                FROM %s.edges
        """ % db_namespace
        cursor = Base.execute_query(query)
        edges = cursor.fetchall()
        G = nx.Graph()
        for x in edges:
            s = x['node1_id']
            t = x['node2_id']
            G.add_edge(s,t)
        sp = nx.shortest_path(G, source=int(from_id), target=int(to_id))
        print('path nodes:', sp)

        # get symbol and name, but in order (CSedit: 20200710)
        # TODO: do this in not stupid way.
        out_str = ''
        for eaSp in sp:
            sym_name_data = Node.get_single_sym_name(db_namespace, eaSp)
            out_str += str(json.dumps(sym_name_data))[1:-1] + ','
        json_out = '{"nodes":[' + out_str[:-1] + ']}'

        # # get symbol and name
        # sym_name_data = Node.get_sym_name(db_namespace, sp)
        # # jsonify output
        # out_str = ''
        # for x in sym_name_data:
        #     out_str += str(json.dumps(x)) + ','
        # json_out = '{"nodes":[' + out_str[:-1] + ']}'

        return json_out


    @staticmethod
    def connect_set_dfs(db_namespace, seeds, variants, cache):

        # PPI GENERATOR
        #DB query for edges
        # query = """
        #         SELECT edges.node1_id, edges.node2_id
        #         FROM %s.edges
        # """ % db_namespace
        # cursor = Base.execute_query(query)
        # edges = cursor.fetchall()
        edges = get_cached_edges(cache, db_namespace)

        G = nx.Graph()
        for x in edges:
            # s = x['node1_id']
            # t = x['node2_id']
            s = x[0]
            t = x[1]
            G.add_edge(s,t)

        print(G.number_of_nodes())
        print(G.number_of_edges())

        print(seeds)

        l_linkerset = []
        for start_variant in variants:
            # start_variant = list(l_vars_onppi)[1]
            # print('start at variant: %s (k = %s)' %(start_variant,G_ppi.degree(start_variant)))
            cc = 1
            for path in nx.dfs_edges(G,start_variant,2):
                if path[0] in seeds:
        #             print(cc,set(path),'SEED REACHED at d=1')
                    l_linkerset.append(path[0])
                if path[1] in seeds:
        #             print(cc,set(path),'SEED REACHED at d=2')
                    l_linkerset.append(path[0])
                    l_linkerset.append(path[1])
                else:
                    pass
            #         print(cc,set(path))
                cc += 1
        set_linkers = set(l_linkerset) - set(seeds)

        out_str = '{"seeds":['
        for x in seeds:
            out_str += str(json.dumps(x)) + ','
        out_str = out_str[:-1] + '],"variants":['

        for x in variants:
            out_str += str(json.dumps(x)) + ','
        out_str = out_str[:-1] + '],"linker":['

        for x in set_linkers:
            out_str += str(json.dumps(x)) + ','
        out_str = out_str[:-1] + ']}'

        return out_str


################################################################################
################################################################################
    @staticmethod
    def random_walk_dock2(namespace, starting_nodes, variants, restart_probability, max_elements, cache):
        num_trials = 100000

        edges = get_cached_edges(cache, namespace)
        neighbors = {}
        for edge in edges:
            if edge[0] not in neighbors.keys():
                neighbors[edge[0]] = [edge[1]]
            else:
                neighbors[edge[0]].append(edge[1])
        visited_nodes = [0] * 20000
        starting_node = random.choice(starting_nodes)


        for i in range (num_trials):
            if random.random() < restart_probability:
                starting_node = random.choice(starting_nodes)
            else:
                starting_node = random.choice(neighbors[starting_node])
            visited_nodes[starting_node] += 1

        query2 = """
            SELECT DISTINCT name, symbol, id FROM %s.nodes
        """ % namespace
        cursor = Base.execute_query(query2)
        d_i_name = cursor.fetchall()
        d_i_name = {x["id"]: x["symbol"] for x in d_i_name}

        # set group 0 for seed, group 2 for genes matching with given variant list, 1 else
        d_node2group = {}
        # print('visited nodes',visited_nodes )
        for i, x in enumerate(visited_nodes):
            if i in starting_nodes:
                d_node2group[i] = 0
            elif i in variants:
                d_node2group[i] = 2
            else:
                d_node2group[i] = 1

        min_frequency = 0
        kept_values = [{'id': i,'symbol': d_i_name[i],'group': d_node2group[i], 'frequency': 1.0*x/num_trials} for i, x in enumerate(visited_nodes) if x > min_frequency*num_trials]

        # print('kept_values:', kept_values)
        kept_values.sort(key=lambda x: x['frequency'], reverse=True)
        kept_values = kept_values[:max_elements]

        # add variants if not empty
        if len(variants)>0:
            add_variants = [{'id': i,'symbol': d_i_name[i],'group': d_node2group[i], 'frequency': 1.0*x/num_trials} for i, x in enumerate(visited_nodes) if i in variants]
            add_variants.sort(key=lambda x: x['frequency'], reverse=True)
            # print('added variants', add_variants)
            kept_values +=  add_variants
            # print('added variants', add_variants)

        # kept_node_ids = [x['id'] for x in kept_values]
        #
        # edges_kept = [(x,y) for x,y in edges if (x in kept_node_ids and y in kept_node_ids)]
        # print('edges:', edges_kept)
        # l_edges_kept = [{'source':s,'target':t,'values':1} for s,t in edges_kept]
        # d_data_kept = {'nodes': kept_values,'links': l_edges_kept}


        ##########################
        # Attach variants to seeds with deep-first-search
        G = nx.Graph()
        for x in edges:
            # s = x['node1_id']
            # t = x['node2_id']
            s = x[0]
            t = x[1]
            G.add_edge(s,t)

        # print(G.number_of_nodes())
        # print(G.number_of_edges())
        seeds = starting_nodes
        print(seeds)

        l_linkerset = []
        for start_variant in variants:
            # start_variant = list(l_vars_onppi)[1]
            # print('start at variant: %s (k = %s)' %(start_variant,G_ppi.degree(start_variant)))
            cc = 1
            for path in nx.dfs_edges(G,start_variant,2):
                if path[0] in seeds:
        #             print(cc,set(path),'SEED REACHED at d=1')
                    l_linkerset.append(path[0])
                if path[1] in seeds:
        #             print(cc,set(path),'SEED REACHED at d=2')
                    l_linkerset.append(path[0])
                    l_linkerset.append(path[1])
                else:
                    pass
            #         print(cc,set(path))
                cc += 1
        set_nodes = set(l_linkerset) | set(seeds) | set(variants)

        edges_kept = [(x,y) for x,y in edges if (x in set_nodes and y in set_nodes)]

        # joerg anfang
        # adding all nodes in set_nodes to the list of kept_values
        # find missing nodes:
        missing_nodes = set_nodes - set([x['id'] for x in kept_values])
        #print ("%s %s %s nodes report" % (len(missing_nodes),len(set_nodes),len(set([x['id'] for x in kept_values]))))
        # add the missing nodes with correct info (hardcoding 0 as frequency:
        missing_nodes_with_info = [{'id': i,'symbol': d_i_name[i],'group': d_node2group[i], 'frequency': 0.0} for i in missing_nodes]
        kept_values += missing_nodes_with_info
        #print ( missing_nodes_with_info)
        # joerg ende

        l_edges_kept = [{'source':s,'target':t,'value':1} for s,t in edges_kept]
        d_data_kept = {'nodes': kept_values,'links': l_edges_kept}

        return d_data_kept
################################################################################
################################################################################

    @staticmethod
    def layout(db_namespace, nodes,cache):

        # PPI GENERATOR
        #DB query for edges
        # query = """
        #         SELECT edges.node1_id, edges.node2_id
        #         FROM %s.edges
        # """ % db_namespace
        # cursor = Base.execute_query(query)
        # edges = cursor.fetchall()
        edges = get_cached_edges(cache, db_namespace)

        G = nx.Graph()
        for x in edges:
            s = x[0]
            t = x[1]
            G.add_edge(s,t)


        G_sub = nx.subgraph(G,nodes)

        Glcc = G_sub.subgraph(max(nx.connected_components(G_sub), key=len))  # extract lcc graph

        pos = nx.spring_layout(Glcc,dim=3)


        # NORMALIZAION
        l_x = [xyz[0] for k, xyz in sorted(pos.items())]
        l_y = [xyz[1] for k, xyz in sorted(pos.items())]
        l_z = [xyz[2] for k, xyz in sorted(pos.items())]
        x_min = min(l_x)
        x_max = max(l_x)
        y_min = min(l_y)
        y_max = max(l_y)
        z_min = min(l_z)
        z_max = max(l_z)
        l_xn = [(x-x_min)/(x_max-x_min) for x in l_x]
        l_yn = [(y-y_min)/(y_max-y_min) for y in l_y]
        l_zn = [(z-z_min)/(z_max-z_min) for z in l_z]

        pos_norm = {}
        for i,gene in enumerate(sorted(pos.keys())):
            pos_norm[gene] = (l_xn[i],l_yn[i],l_zn[i])

        # query2 = """
        #     SELECT DISTINCT name, symbol, id FROM %s.nodes
        # """ % db_namespace
        # cursor = Base.execute_query(query2)
        # d_i_name = cursor.fetchall()
        # d_i_name = {x["id"]: x["symbol"] for x in d_i_name}

        # result = [{'id': i,'symbol': d_i_name[i], 'x': xyz[0], 'y': xyz[1], 'z': xyz[2]} for i, xyz in pos_norm.items()]
        result = [{'a': [str(i)], 'v': [xyz[0],xyz[1],xyz[2],0,0,0,0]} for i, xyz in pos_norm.items()]

        # print('result:', result)


        return result

    @staticmethod
    def scale_selection(db_namespace, nodes,layout,cache):
        # scaling factor
        a = .2

        str_nodes = ",".join(nodes)
        # print(str_nodes)
        query = """
                SELECT
                    node_id,
                    x_loc,
                    y_loc,
                    z_loc
                FROM %s.layouts
                WHERE namespace = '%s'
                AND node_id in (%s)
        """ %(db_namespace,layout,str_nodes)
        cursor = Base.execute_query(query)
        data = cursor.fetchall()
        print(data)
        d_node_xyz = {x["node_id"]: (x["x_loc"],x["y_loc"],x["z_loc"]) for x in data}
        xm = np.mean([x['x_loc'] for x in data])
        ym = np.mean([x['y_loc'] for x in data])
        zm = np.mean([x['z_loc'] for x in data])

        d_node_xyz_scaled = {}
        for node, xyz in d_node_xyz.items():
            x = xyz[0]
            xs =  a*x + (1-a)*xm
            y = xyz[1]
            ys =  a*y + (1-a)*ym
            z = xyz[2]
            zs =  a*z + (1-a)*zm
            d_node_xyz_scaled[node] = (xs,ys,zs)

        # query2 = """
        #     SELECT DISTINCT name, symbol, id FROM %s.nodes
        # """ % db_namespace
        # cursor = Base.execute_query(query2)
        # d_i_name = cursor.fetchall()
        # d_i_name = {x["id"]: x["symbol"] for x in d_i_name}

        # result = [{'id': i,'symbol': d_i_name[i], 'x': xyz[0], 'y': xyz[1], 'z': xyz[2]} for i, xyz in d_node_xyz_scaled.items()]
        result = [{'a': [str(i)], 'v': [xyz[0],xyz[1],xyz[2],0,0,0,0]} for i, xyz in d_node_xyz_scaled.items()]

        # print('result:', result)
        #

        return result


    @staticmethod
    def search(db_namespace, clauses):
        print(clauses)
        have_name = False
        have_attributes = False
        filter_clauses = []
        select_clauses = []

        def filter_clause(subject, object):
            print(subject)
            if subject == "name_like":
                have_name = True
                return [" LOWER(nodes.symbol) like LOWER('%s') " % (Base.sanitize_string(object) + "%"),
                        ["name", object.lower()]]
                column = ""
            else:
                column = "attribute_id"
                have_attributes = True

            return ["%s = '%s'" % (column, object),
                    [column, object]]

        # def get_summary_stats(gene_set):
        #     query = """
        #     SELECT attributes.name, prevalence, count(distinct jgenes.id) as gene_number
        #     FROM attributes
        #     JOIN attribute_taxonomies on diseases.id = parent_id
        #     JOIN nodes_attributes ON nodes_attibutes.attriute_id = child_id
        #     JOIN (select * from nodes where id in (%s)) jgenes ON jgenes.id = nodes_attributes.node_id
        #     JOIN disease_counts on disease_counts.disease_id = diseases.id
        #     WHERE prevalence > 25
        #     GROUP BY 1, 2
        #     ORDER BY 3 DESC
        #     LIMIT 200
        #     """ % ",".join([str(gene["entrez_id"]) for gene in gene_set])
        #     cursor = Base.execute_query(query)
        #     results = cursor.fetchall()
        #     results = [{"name": x["name"], "gene_number": round(x["gene_number"]/x["prevalence"]* len(results), 2)} for x in results]
        #     results.sort(reverse=True, key=lambda x: x["gene_number"])
        #     return results[:10]


        for x in range(5):
            andor = clauses["predicate%d" % x] if "predicate%d" % x in clauses else "AND"
            if "subject%d" % x not in clauses or clauses["subject%d" % x] == "undefined" \
            or "object%d" % x not in clauses or clauses["object%d" % x] == "undefined":
                break
            if clauses["subject%d" % x] == "name_like":
                have_name = True
            else:
                have_attributes = True
            new_clause = filter_clause(clauses["subject%d" % x], clauses["object%d" % x] )
            if andor == "AND":
                filter_clauses.append(new_clause[0])
                select_clauses.append([new_clause[1]])
            else:
                filter_clauses[-1]= filter_clauses[-1] + " OR " + new_clause[0]
                select_clauses[-1].append(new_clause[1])
        if not filter_clauses:
            print("no filter clauses!")
            return({"nodes": [], "summary_stats": []})
        if have_name and not have_attributes:
            name_select_clause = """
                SELECT id AS node_id, name, symbol FROM %s.nodes WHERE
            """ % db_namespace
            query = name_select_clause + " AND ".join(filter_clauses)
            cursor = Base.execute_query(query)
            nodes = cursor.fetchall()
            return({"nodes": nodes})

        print(filter_clauses)
        print(have_attributes)
        nodes_to_names = {}
        nodes_to_attributes = {}
        if have_attributes:
            name_attribute_select_clause = """
            SELECT DISTINCT node_id, nodes.name, nodes.symbol,
                GROUP_CONCAT(DISTINCT attribute_taxonomies.parent_id) as attribute_id
            FROM %s.nodes
            JOIN %s.nodes_attributes ON nodes.id = nodes_attributes.node_id
            JOIN %s.attribute_taxonomies ON nodes_attributes.attribute_id = attribute_taxonomies.child_id
            WHERE %s
            GROUP BY 1, 2, 3
            """ % (db_namespace, db_namespace, db_namespace, " OR ".join(filter_clauses))
            query = name_attribute_select_clause
            cursor = Base.execute_query(query)
            attr_table = cursor.fetchall()
            print(attr_table)
            print(query)
            nodes_to_attributes = {x["node_id"]: x["attribute_id"].split(",") for x in attr_table}
            nodes_to_names = {x["node_id"]: {'name': x['name'], 'symbol': x['symbol']} for x in attr_table}
        #nodes_to_attributes = {**nodes_to_attributes, **nodes_to_attributes_d}

        candidate_nodes = set(nodes_to_attributes.keys())
        #print("candidate_nodes", candidate_nodes)
        print(len(candidate_nodes))
        for clause in select_clauses:
            keep_nodes = set()
            for subclause in clause:
                print(clause)
                print(subclause)
                if subclause[0] == "name":
                    new_candidates = [x for x in candidate_nodes if subclause[1].lower() in nodes_to_names[x]["name"]]
                else:
                    new_candidates = [x for x in candidate_nodes if subclause[1] in nodes_to_attributes[x]]
                for x in new_candidates:
                    keep_nodes.add(x)
            candidate_nodes = keep_nodes
        nodes = [{"node_id": x, "name": nodes_to_names[x]["name"], "symbol": nodes_to_names[x]["symbol"]} for x in candidate_nodes]
        return({"nodes": nodes})

class Attribute:
    @staticmethod
    def attributes_for_node(db_namespace, node_id, attr_namespace=None):
        namespace_clause = " AND a.namespace = \"%s\"" % attr_namespace if attr_namespace else ""
        query = """
            SELECT DISTINCT a.id, a.external_id, a.name, a.description, a.namespace, distance, na.value
            FROM %s.attributes a
            JOIN %s.attribute_taxonomies at ON a.id = at.parent_id
            JOIN %s.nodes_attributes na ON na.attribute_id = at.child_id
            WHERE node_id = %s
            %s
        """ % (db_namespace, db_namespace, db_namespace, node_id, namespace_clause)
        cursor = Base.execute_query(query)
        results = cursor.fetchall()
        attributes = {}
        for result in results:
            if result["id"] in attributes:
                attributes[result["id"]] = attributes[result["id"]] + [""] * (result["distance"] + 1 - len(attributes[result["id"]]))
                attributes[result["id"]][result["distance"]] = result["name"]
            else:
                attributes[result["id"]] = [""] * (result["distance"]) + [result["name"]]
        return [{"id": result["id"],
                 "full_name": "/".join(attributes[result["id"]][:-1][::-1]),
                 "external_id": result["external_id"],
                 "name": result["name"],
                 "value": result["value"],
                 "description": result["description"]} for result in results]

    @staticmethod
    def children(db_namespace, attr_id):
        query = """
            SELECT nodes.id, nodes.name, nodes.symbol
            FROM %s.nodes n JOIN  %s.attribute_taxonomies at on %s.id = at.child_id
            WHERE parent_id = %s
        """ % (db_namespace, attr_id)


    @staticmethod
    def attributes_for_autocomplete(db_namespace, name_prefix, attr_namespace=None):
        namespace_clause = " AND namespace = \"%s\"" % attr_namespace if attr_namespace else ""
        query = """
            SELECT attributes.id, attributes.external_id, attributes.name, namespace
            FROM %s.attributes
            WHERE LOWER(attributes.name) like LOWER('%s')
            %s
        """ % (db_namespace, Base.sanitize_string(name_prefix) + '%', namespace_clause)
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def attributes_for_external_ids(db_namespace, external_ids, attr_namespace=None):
        namespace_clause = " AND namespace = \"%s\"" % attr_namespace if attr_namespace else ""
        query = """
            SELECT attributes.id, attributes.external_id, attributes.name, namespace
            FROM %s.attributes
            WHERE attributes.external_id in ('%s')
            %s
        """ % (db_namespace, "','".join(external_ids), namespace_clause)
        print(query)
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def all_attribute_names(db_namespace, attr_namespace=None):
        namespace_clause = " WHERE namespace = \"%s\"" % attr_namespace if attr_namespace else ""
        query = """
            SElECT DISTINCT attributes.id, attributes.external_id, attributes.name, namespace
            FROM %s.attributes
            %s
        """ % (db_namespace, namespace_clause)
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def get_attribute_namespaces(db_namespace):
        query = """
            SElECT DISTINCT namespace
            FROM %s.attributes
        """ % (db_namespace)
        cursor = Base.execute_query(query)
        namespaces = cursor.fetchall()
        return [x["namespace"] for x in namespaces]

    @staticmethod
    def create_selection(db_namespace, selection_name, node_ids):
        #Validate that the namespace is new
        query = """
            SELECT * FROM %s.attributes
            WHERE namespace = "SELECTION"
            AND LOWER(name) like "%s"
            LIMIT 1
        """ %(db_namespace, selection_name.lower())
        cursor = Base.execute_query(query)
        namespaces = cursor.fetchall()
        if namespaces:
            return({"status": "FAIL", "reason": "selection with that name already exists"})
        # Validate node IDs.
        node_ids = set(node_ids)
        query = """
            SELECT id FROM %s.nodes
            WHERE id in (%s)
        """ %(db_namespace, ",".join([str(x) for x in node_ids]))
        cursor = Base.execute_query(query)
        matched_ids = {x["id"] for x in cursor.fetchall()}
        print(matched_ids)
        if len(matched_ids) < len(node_ids):
            unmatched = set(node_ids) - matched_ids
            return({"status": "FAIL", "reason": "invalid node IDs in query: %s" % ",".join([str(x) for x in unmatched])})
        query = """
            INSERT INTO %s.attributes(name, namespace)
            VALUES ("%s", "SELECTION")
        """ %(db_namespace, selection_name)
        cursor = Base.execute_query(query)
        query = """
            SELECT id
            FROM %s.attributes
            ORDER BY id desc
            LIMIT 1
        """ %(db_namespace)
        cursor = Base.execute_query(query)
        attr_id = cursor.fetchone()["id"]
        query = """
            INSERT INTO %s.attribute_taxonomies(child_id, parent_id, distance, namespace)
            VALUES (%d, %d, 0, "SELECTION")
        """ % (db_namespace, attr_id, attr_id)
        cursor = Base.execute_query(query)
        query = """
            INSERT INTO %s.nodes_attributes(node_id, attribute_id)
            VALUES %s
        """ %(db_namespace, ",".join(['(%s, %d)' % (x, attr_id) for x in node_ids]))
        cursor = Base.execute_query(query)
        return {"status":"OK"}

    @staticmethod
    def attribute2attribute(db_namespace,att_id):
        query = """
                SELECT
                    # aa1.external_id,
                    # aa1.name,
                    aa2.id int_id,
                    aa2.name phenotype
                FROM %s.attribute_relations ar
                INNER JOIN %s.attributes aa1
                ON aa1.id = ar.attr1_id
                INNER JOIN %s.attributes aa2
                ON aa2.id = ar.attr2_id
                WHERE ar.attr1_id = '%s'
        """ % (db_namespace,db_namespace,db_namespace,att_id)
        cursor = Base.execute_query(query)
        data = cursor.fetchall()
        print(data)
        # return [x["namespace"] for x in namespaces]
        return data

class AttributeTaxonomy:
    @staticmethod
    def get_root(db_namespace, taxonomy_name):
        query = """
        SELECT id from %s.attributes
        WHERE namespace = "%s"
        AND root_node;
        """ % (db_namespace, taxonomy_name)
        cursor = Base.execute_query(query)
        db_results = cursor.fetchall()
        if len(db_results) == 0:
            return None
        return db_results[0]["id"]

    @staticmethod
    def construct_taxonomy(namespace, root_node):
        start_time = datetime.datetime.now()
        query = """
            SELECT DISTINCT attributes.id,
                attributes.name, attribute_taxonomies.child_id, attribute_taxonomies.distance
            FROM %s.attributes
            JOIN %s.attribute_taxonomies ON attribute_taxonomies.parent_id = attributes.id
                AND attribute_taxonomies.distance IN (0, 1)
            JOIN %s.attribute_taxonomies dt2 on attributes.id = dt2.child_id and dt2.parent_id = %s
        """ % (namespace, namespace, namespace, root_node)
        cursor = Base.execute_query(query)
        db_results = cursor.fetchall()
        return build_taxonomy(db_results, root_node)

class Article:
    @staticmethod
    def article_for_pubid(namespace, pub_id):
        query = """
            SELECT articles.authors_list, articles.abstract, articles.title,
                DATE_FORMAT(CURDATE(), '%s') AS publication_date,
                "Fake Journal" AS publication, 10000 as citation_count
            FROM %s.articles
            WHERE articles.type = "pubmed"
            AND articles.external_id = '%s'
        """ % ("%Y-%m-%d", namespace, pub_id)
        cursor = Base.execute_query(query)
        return cursor.fetchone()

    @staticmethod
    def articles_for_node(namespace, node_id):
        query = """
            SELECT articles.external_id, articles.title,
                DATE_FORMAT(CURDATE(), '%s') AS publication_date,
                "Fake Journal" AS publication, 10000 as citation_count
            FROM %s.articles
            JOIN %s.nodes_articles ON nodes_articles.article_id = articles.id
            JOIN %s.nodes ON nodes.id = nodes_articles.node_id
            WHERE articles.type = 'pubmed'
            AND nodes.id = '%s'
            ORDER BY articles.publication_date desc
        """ % ("%Y-%m-%d", namespace, namespace, namespace, node_id)
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
        FROM %s.edges
        WHERE edges.node1_id < edges.node2_id
        """ % namespace
        cursor = Base.execute_query(query)
        results = cursor.fetchall()
        return {"start": [r["node1_id"] for r in results], "end": [r["node2_id"] for r in results]}

    @staticmethod
    def for_nodelist(namespace, nodes):
        print(nodes)
        query = """
        SELECT node1_id, node2_id
        FROM %s.edges
        WHERe node1_id in (%s) and node2_id in (%s)
        """ % (namespace, ",".join([str(node) for node in nodes]),  ",".join([str(node) for node in nodes]))
        cursor = Base.execute_query(query)
        results = cursor.fetchall()
        return [{"source": r["node1_id"], "target": r["node2_id"]} for r in results]

    @staticmethod
    def by_node(namespace):
        query = """
        SELECT node1_id AS node_id, GROUP_CONCAT(node2_id) as neighbors
        FROM (select node1_id, node2_id from  %s.edges UNION ALL select node2_id as node1_id, node1_id as node2_id from %s.edges) tbl
        GROUP BY 1
        """ % (namespace, namespace)
        print(query)
        cursor = Base.execute_query(query)
        results = cursor.fetchall()
        print(results[:10])

class Layout:
    @staticmethod
    def all_namespaces(db_namespace):
        query = """
        SELECT DISTINCT namespace, count(*)
        FROM layouts
        GROUP BY 1
        """
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def fetch(db_namespace, layout_namespace):
        query = """
        SELECT node_id, n.symbol, n.name, x_loc, y_loc, z_loc, r_val, g_val, b_val, a_val
        FROM %s.layouts
        JOIN nodes n on n.id = layouts.node_id
        WHERE namespace = "%s"
        """ % (db_namespace, layout_namespace)
        cursor = Base.execute_query(query)
        layout = cursor.fetchall()
        return [{'v': [r["x_loc"], r["y_loc"], r["z_loc"], r["r_val"], r["g_val"], r["b_val"], r["a_val"] ],
                 'a': [str(r["node_id"]), r["symbol"], r["name"]]} for r in layout]

class Label:
    @staticmethod
    def all_namespaces(db_namespace):
        query = """
        SELECT DISTINCT namespace, count(*)
        FROM %s.labels
        GROUP BY 1
        """ % db_namespace
        cursor = Base.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def fetch(db_namespace, label_namespace):
        query = """
        SELECT text, x_loc, y_loc, z_loc
        FROM %s.labels
        WHERE namespace = "%s"
        """ % (db_namespace, label_namespace)
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


ERRORS_TO_SHOW = 5
def asciitable(headers, rows):
  if len(rows) > 0:
    lens = []
    for i in range(len(rows[0])):
      lens.append(len(max([x[i] for x in rows] + [headers[i]],key=lambda x:len(str(x)))))
    formats = []
    hformats = []
    for i in range(len(rows[0])):
      if isinstance(rows[0][i], int):
        formats.append("%%%ds" % lens[i])
      else:
        formats.append("%%-%ds" % lens[i])
      hformats.append("%%-%ds" % lens[i])
    pattern = " | ".join(formats)
    hpattern = " | ".join(hformats)
    separator = "-+-".join(['-' * n for n in lens])
    print(hpattern % tuple(headers))
    print (separator)
    for line in rows:
        print (pattern % tuple(str(t) for t in line))
  elif len(rows) == 1:
    row = rows[0]
    hwidth = len(max(row._fields,key=lambda x: len(x)))
    for i in range(len(row)):
      print("%*s = %s" % (hwidth,row._fields[i],row[i]))


def validate_coordinate(x):
    try:
        x = float(x)
        return x >= 0 and x <= 1
    except:
        return False


def validate_color_value(x):
    try:
        x = int(x)
        return x >= 0 and x <= 255
    except:
        return False


def validate_index(x, num_points):
    try:
        x = int(x)
        return x < num_points
    except:
        return False

def validate_layout(layout):
    line_count = 0
    bad_lines = {"len": [], "xyz":[], "rgb":[], "dup": []}
    num_col_errors = 0
    num_xyz_errors = 0
    num_rgb_errors = 0
    num_id_errors = 0
    ids = {}
    #print(layout[0])
    for i, line in enumerate(layout):
        if not line:
            continue
        line_count += 1
        line = line.split(",")
        if len(line) != 9:
            num_col_errors += 1
            if num_col_errors < ERRORS_TO_SHOW:
                bad_lines["len"].append(["Illegal number of columns", 9, len(line), i, ",".join(line)])
        try:
            if len(line[0]) == 0:
                num_id_errors += 1
                if num_id < ERRORS_TO_SHOW:
                    bad_lines["id"].append(["Missing ID", "string or numeric ID", line[0], i, ",".join(line)])
            else:
                if line[0] in ids:
                    num_id_errors += 1
                    if num_id < ERRORS_TO_SHOW:
                        bad_lines["id"].append(["Duplicate ID", "All ids must be unique", line[x], i, ""])
            ids.add(line[0])
        except:
            pass
        try:
            for x in range(1, 4):
                if x >= len(line):
                    continue
                if not validate_coordinate(line[x]):
                    num_xyz_errors += 1
                    if num_xyz_errors > ERRORS_TO_SHOW:
                        bad_lines["xyz"].append(["illegal XYZ values", "float 0 <= f <= 1", line[x], i, ",".join(line)])
        except:
            pass
        try:
            for x in range(4, 8):
                if x >= len(line):
                    continue
                if not validate_color_value(line[x]):
                    num_rgb_errors += 1
                    if num_rgb_errors > ERRORS_TO_SHOW:
                        bad_lines["rgb"].append(["illegal RGBA values", "int 0 <= i <= 255", line[x],
                                          i, ",".join(line)])
        except:
            pass
        try:
            if len(line[8]) == 0:
                if num_id_errors < ERRORS_TO_SHOW:
                    bad_lines["name"].append(["Missing namespace", "namespace", line[x], i, ""])
                num_id_errors += 1
        except:
            pass
    total_errors = num_id_errors + num_col_errors + num_xyz_errors + num_rgb_errors
    print("errors", num_id_errors, num_col_errors, num_xyz_errors, num_rgb_errors)
    print(bad_lines)
    print(len(layout), total_errors, bad_lines)
    return(len(layout), total_errors, bad_lines)

def validate_edges(namespace, links):
    column_errors = []
    num_col_errors = 0

    for i, line in enumerate(links.split("\n")):
        if not line:
            continue
        line = line.split(",")
        # Validate number of columns
        if len(line) != 2:
            num_col_errors += 1
            if num_col_errors < ERRORS_TO_SHOW:
                column_errors.append(["Illegal number of columns", 2, len(line), i, ",".join(line)])
    return(len(links), num_col_errors, column_errors)

def validate_attributes(namespace, attributes):
    # Columns are node_id, attribute_id, attribute_namespace, attribute_name, attribute_description
    column_errors = []
    num_col_errors = 0
    print(attributes)

    for i, line in enumerate(attributes.split("\n")):
        if not line:
            continue  # Ignore empty lines.
        line = line.split(",")
        print("line is ")
        print(line)
        # Validate number of columns
        if len(line) != 5:
            num_col_errors += 1
            if num_col_errors < ERRORS_TO_SHOW:
                column_errors.append(["Illegal number of columns", 5, len(line), i, ",".join(line)])
        elif len(line[0]) < 1 or len(line[1]) < 1 or len(line[2]) < 1:
            num_col_errors += 1
            if num_col_errors < ERRORS_TO_SHOW:
                column_errors.append(["Missing values", "First three columns must be nonempty", "", i, ",".join(line)])
    return(len(attributes), num_col_errors, column_errors)


def add_attributes_to_db(namespace, attributes):
    Base.execute_query("DROP TABLE IF EXISTS `tmp_%s`.`attributes`" % namespace)
    Base.execute_query('''
    CREATE TABLE IF NOT EXISTS `tmp_%s`.`attributes` (
      `node_id` varchar(255) not null,
      `attribute_id` varchar(255) not null,
      `attribute_namespace` varchar(255) NOT NULL,
      `attribute_name` varchar(255) DEFAULT NULL,
      `attribute_description` varchar(255) DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    ''' % namespace
    )
    query = "INSERT INTO `tmp_%s`.attributes VALUES (%s)" % \
            (namespace,
             "),(".join([",".join(['"%s"' % i for x in attributes for i in x.split(",")])]))
    cursor = Base.execute_query(query)
    if run_db_attribute_validations(namespace):
        print("problem!")
    else:
        write_attributes(namespace)

def add_layout_to_db(namespace, filename, layout):
    Base.execute_query("DROP TABLE IF EXISTS `tmp_%s`.`layouts_tmp`" % namespace)
    Base.execute_query('''
    CREATE TABLE IF NOT EXISTS `tmp_%s`.`layouts_tmp` (
      `id` varchar(255) not null,
      `x_loc` float(10,7) DEFAULT NULL,
      `y_loc` float(10,7) DEFAULT NULL,
      `z_loc` float(10,7) DEFAULT NULL,
      `r_val` int(11) DEFAULT NULL,
      `g_val` int(11) DEFAULT NULL,
      `b_val` int(11) DEFAULT NULL,
      `a_val` int(11) DEFAULT NULL,
      `namespace` varchar(255) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    ''' % namespace
    )
    # layout_rows = [ "(" + ",".join(line.split(",")[:7]) +
    #                "".join([',"',line.split(",")[-1], '","', filename, '")']) \
    #                for i , line in enumerate(layout)]
    layout_rows = ["(" + ",".join(line.split(",")[:-1]) + ',"' + line.split(",")[-1] + '"' + ")" for line in layout]
    query = """
    insert into `tmp_%s`.layouts_tmp (id, x_loc, y_loc, z_loc, r_val, g_val, b_val, a_val, namespace)
    values %s
    """ % (namespace, ",".join(layout_rows))
    #print(query)
    cursor = Base.execute_query(query)
    if run_db_layout_validations(namespace):
        pass
        # return errors
        print("layouts already in DB!")
    else:
        write_layouts(namespace)

def add_edges_to_db(namespace, filename, layout):
    Base.execute_query("DROP TABLE IF EXISTS `tmp_%s`.`edges_tmp`" % namespace)
    Base.execute_query('''
    CREATE TABLE IF NOT EXISTS `tmp_%s`.`edges_tmp` (
      `node1` varchar(255) NOT NULL,
      `node2` varchar(255) NOT NULL,
      `namespace` varchar(255) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    ''' % namespace
    )
    lines = layout.split("\n")
    query = "insert into `tmp_%s`.edges_tmp (node1, node2, namespace) values %s" % \
            (namespace, ",".join(["(%s, '%s')" % (line, filename) for line in layout.split("\n")]))
    cursor = Base.execute_query(query)
    if run_db_edge_validations(namespace):
        pass
        # return errors
        print("edges already in DB!")
    else:
        write_edges(namespace)

def add_labels_to_db(namespace, filename, labels):
    Base.execute_query("DROP TABLE IF EXISTS `%s`.`labels_tmp`" % namespace)
    Base.execute_query('''
    CREATE TABLE IF NOT EXISTS `tmp_%s`.`labels_tmp` (
      `x_loc` float(10,7) DEFAULT NULL,
      `y_loc` float(10,7) DEFAULT NULL,
      `z_loc` float(10,7) DEFAULT NULL,
      `text` varchar(255) not null,
      `namespace` varchar(255) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    ''' % namespace
    )
    lines = labels.split("\n")
    query = "insert into `tmp_%s`.labels_tmp (x_loc, y_loc, z_loc, text, namespace) values %s" % \
            (namespace, ",".join(["(%s, %s, %s,\"%s\",\"%s\")" % tuple(line.split(",")  + [filename]) for line in lines]))
    cursor = Base.execute_query(query)
    if run_db_label_validations(namespace):
        pass
        # return errors
        print("namespace already in DB!")
    else:
        write_labels(namespace)

def run_db_layout_validations(namespace):
    # Namespaces
    query = """
    SELECT DISTINCT tmp.namespace
    FROM %s.layouts l
    JOIN tmp_%s.layouts_tmp tmp on l.namespace = tmp.namespace
    """ % (namespace, namespace)
    cursor = Base.execute_query(query)
    namespace_conflicts = cursor.fetchall()
    return namespace_conflicts

def run_db_label_validations(namespace):
    # Namespaces
    query = """
    SELECT DISTINCT tmp.namespace
    FROM %s.labels l
    JOIN tmp_%s.labels_tmp tmp on l.namespace = tmp.namespace
    """ % (namespace, namespace)
    cursor = Base.execute_query(query)
    namespace_conflicts = cursor.fetchall()
    return namespace_conflicts

def run_db_edge_validations(namespace):
    # Namespaces
    query = """
    SELECT DISTINCT node1
    FROM tmp_%s.edges_tmp e
    LEFT JOIN %s.nodes n ON n.external_id = e.node1
    WHERE n.id IS NULL
    """ % (namespace, namespace)
    cursor = Base.execute_query(query)
    unknown_nodes = cursor.fetchall()
    return unknown_nodes

def run_db_attribute_validations(namespace):
    query = """
    SELECT DISTINCT node_id
    FROM tmp_%s.attributes a
    LEFT JOIN %s.nodes n ON n.external_id = a.node_id
    WHERE n.id IS NULL
    """ % (namespace, namespace)
    cursor = Base.execute_query(query)
    unknown_nodes = cursor.fetchall()
    print(unknown_nodes)
    return unknown_nodes

def write_layouts(namespace):
    query = """
    INSERT INTO %s.nodes (external_id)
    SELECT tmp.id
    FROM tmp_%s.layouts_tmp tmp
    LEFT JOIN %s.nodes n on n.external_id = tmp.id
    WHERE n.id IS NULL
    """ % (namespace, namespace, namespace)
    cursor = Base.execute_query(query)

    query = """
    INSERT INTO %s.layouts(node_id, x_loc, y_loc, z_loc, r_val, g_val, b_val, a_val, namespace)
    SELECT n.id, x_loc, y_loc, z_loc, r_val, g_val, b_val, a_val, namespace
    FROM tmp_%s.layouts_tmp tmp
    JOIN %s.nodes n on n.external_id = tmp.id
    """ % (namespace, namespace, namespace)
    cursor = Base.execute_query(query)


def write_attributes(namespace):
    queries = []
    query = """
    INSERT INTO %s.attributes(external_id, namespace, name, description)
    SELECT attribute_id, attribute_namespace, max(attribute_name), max(attribute_description)
    FROM `tmp_%s`.attributes new_attrs
    LEFT JOIN %s.attributes attrs ON attrs.external_id = new_attrs.attribute_id
        AND attrs.namespace = new_attrs.attribute_namespace
    WHERE attrs.id IS NULL
    GROUP BY 1, 2
    """ % (namespace, namespace, namespace)
    print(query)
    queries.append(query)

    query = """
    INSERT INTO %s.attribute_taxonomies(parent_id, child_id, distance, namespace)
    SELECT attrs.id, attrs.id, 1, attrs.namespace
    FROM `%s`.attributes attrs
    JOIN `tmp_%s`.attributes new_attrs on new_attrs.attribute_id = attrs.external_id
    LEFT JOIN `%s`.attribute_taxonomies at ON at.parent_id = attrs.id
        AND at.child_id = attrs.id AND at.namespace = attrs.namespace
        WHERE at.id IS NULL
    """ % (namespace, namespace, namespace, namespace)
    print(query)
    queries.append(query)

    query = """
    INSERT INTO %s.nodes_attributes(node_id, attribute_id)
    SELECT nodes.id, attrs.id
    FROM `%s`.attributes attrs
    JOIN `tmp_%s`.attributes new_attrs on new_attrs.attribute_id = attrs.external_id
    JOIN `%s`.nodes ON nodes.external_id = new_attrs.node_id
    LEFT JOIN `%s`.nodes_attributes na ON na.node_id = nodes.id
        AND na.attribute_id = attrs.id
        WHERE na.id IS NULL
    """ % (namespace, namespace, namespace, namespace, namespace)
    queries.append(query)
    cursor = Base.execute_queries(queries)

def write_edges(namespace):
    # Namespaces
    query = """
    INSERT INTO %s.edges(node1_id, node2_id, namespace)
    SELECT n1.id, n2.id, tmp.namespace
    FROM tmp_%s.edges_tmp tmp
    JOIN %s.nodes n1 on n1.external_id = tmp.node1
    JOIN %s.nodes n2 on n2.external_id = tmp.node2
    LEFT JOIN %s.edges e on n1.id = e.node1_id and n2.id = e.node2_id
    WHERE e.id IS NULL

    """ % (namespace, namespace, namespace, namespace, namespace)
    cursor = Base.execute_query(query)
    query = """
    INSERT INTO %s.edges(node1_id, node2_id, namespace)
    SELECT n2.id, n1.id, tmp.namespace
    FROM tmp_%s.edges_tmp tmp
    JOIN %s.nodes n1 on n1.external_id = tmp.node1
    JOIN %s.nodes n2 on n2.external_id = tmp.node2
    LEFT JOIN %s.edges e on n1.id = e.node1_id and n2.id = e.node2_id
    WHERE e.id IS NULL

    """ % (namespace, namespace, namespace, namespace, namespace)
    cursor = Base.execute_query(query)


def write_labels(namespace):

    query = """
    INSERT INTO %s.labels(text, x_loc, y_loc, z_loc, namespace)
    SELECT text, x_loc, y_loc, z_loc, namespace
    FROM tmp_%s.labels_tmp tmp
    """ % (namespace, namespace)
    cursor = Base.execute_query(query)


class Upload:
    @staticmethod
    def create_new_namespace(namespace):
        query = "DROP DATABASE IF EXISTS %s" % namespace
        cursor = Base.execute_query(query)
        query = "DELETE FROM Datadivr_meta.namespaces WHERE name = \"%s\"" % namespace
        cursor = Base.execute_query(query)

        query = "CREATE DATABASE %s" % namespace
        cursor = Base.execute_query(query)

        connection = pymysql.connect(host=dbconf["host"],
                             user=dbconf["user"],
                             password=dbconf["password"],
                             db=namespace,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        #print(query)
        populate_db_data_agnostic.create_tables(cursor)
        connection.commit()
        query = "INSERT INTO Datadivr_meta.namespaces (name) VALUES (\"%s\")" % namespace
        cursor = Base.execute_query(query)
        #query = "GRANT ALL PRIVILEGES ON `%s`.* TO `%s`;" % (namespace, dbconf["user"])
        #cursor = Base.execute_query(query)


    def create_new_temp_namespace(namespace):
        query = "DROP DATABASE IF EXISTS tmp_%s" % namespace
        cursor = Base.execute_query(query)

        query = "CREATE DATABASE tmp_%s" % namespace
        cursor = Base.execute_query(query)



    @staticmethod
    def upload_layouts(namespace, layout_files):
        print("layout files", layout_files)
        for file in layout_files:
            # TODO: fix the below line to account for dots in filenames
            name = file.filename.split(".")[0]
            contents = file.read().decode('utf-8')
            x = validate_layout(contents.split("\n"))
            print("layout errors are", x)
            if x[1] == 0:
                add_layout_to_db(namespace, name, contents.rstrip().split("\n"))

    def upload_edges(namespace, links_files):
        print("links_files", links_files)
        for file in links_files:
            # TODO: fix the below line to account for dots in filenames
            name = file.filename.split(".")[0]
            contents = file.read().decode('utf-8')
            if not contents:
                continue
            if contents[-1] == "\n":
                contents = contents[:-1]
            x = validate_edges(None, contents)
            if x[1] == 0:
                print(name)
                add_edges_to_db(namespace, name, contents)
            else:
                print(x)
                print("!!! Error!!!!")

    def upload_attributes(namespace, attribute_files):
        for file in attribute_files:
            name = file.filename.split(".")[0]
            contents = file.read().decode('utf-8')
            x = validate_attributes(namespace, contents)
            print("attribute errors are", x)
            if x[1] == 0:
                add_attributes_to_db(namespace, contents.rstrip().split("\n"))

    def upload_labels(namespace, labels_files):
        print("labels_files", labels_files)
        for file in labels_files:
            # TODO: fix the below line to account for dots in filenames
            name = file.filename.split(".")[0]
            contents = file.read().decode('utf-8')
            if not contents:
                continue
            if contents[-1] == "\n":
                contents = contents[:-1]
            #x = validate_edges(None, contents)
            x = [0, 0, 0]
            if True or x[1] == 0:
                print(name)
                add_labels_to_db(namespace, name, contents)
            else:
                print(x)
                print("!!! Error!!!!")

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
