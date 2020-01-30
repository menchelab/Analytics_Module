def build_taxonomy(db_results, root_node):
    children_dict = {}
    id_to_node = {x["id"] : x for x in db_results}
    for node in db_results:
        if node["distance"] == 1:
            if node["id"] in children_dict:
                children_dict[node["id"]].append(node["child_id"])
            elif node["id"] != node["child_id"]:
                children_dict[node["id"]] = [node["child_id"]]
    def represent_node(node_id):
        return id_to_node[node_id]["name"]
    def build_children(node_id):
        if node_id in children_dict:
            return {"id": id_to_node[node_id]["id"], "name": represent_node(node_id),
                    "childnodes": [build_children(x) for x in children_dict[node_id]]
                    }
        return {"id": id_to_node[node_id]["id"], "name": represent_node(node_id), "childnodes":[]}
    results = build_children(root_node)
    return results
