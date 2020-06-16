create temporary table attrs_with_nodes as select distinct attributes.id from attributes join attribute_taxonomies on attributes.id = parent_id join nodes_attributes on child_id = attribute_id;
delete attributes.* from attributes left join attrs_with_nodes on attributes.id = attrs_with_nodes.id where attrs_with_nodes.id is null;