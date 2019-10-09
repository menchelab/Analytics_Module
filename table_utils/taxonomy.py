def build_taxonomy(db_results, root_node):
    result_dict = {}
    id_to_node = {x["id"] : x for x in db_results}
    for node in db_results:
        if node["distance"] == 1:
            if node["id"] in result_dict:
                result_dict[node["id"]].append(node["child_id"])
            elif node["id"] != node["child_id"]:
                result_dict[node["id"]] = [node["child_id"]]
    def represent_node(node_id):
        return " - ".join([id_to_node[node_id]["external_id"], id_to_node[node_id]["name"]])
    def build_children(node_id):
        if node_id in result_dict:
            return {"id": id_to_node[node_id]["external_id"], "name": represent_node(node_id),
                    "childnodes": [build_children(x) for x in result_dict[node_id]]
                    }
        return {"id": id_to_node[node_id]["external_id"], "name": represent_node(node_id), "childnodes":[]}
    results = build_children(root_node)
    return results