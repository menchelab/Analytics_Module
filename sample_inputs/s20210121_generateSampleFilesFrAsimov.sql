# exploration
SELECT * FROM nodes LIMIT 500;
SELECT * FROM labels LIMIT 500;
SELECT * FROM layouts LIMIT 300;
SELECT DISTINCT namespace FROM layouts LIMIT 300;
SELECT * FROM nodes_attributes LIMIT 300;
SELECT * FROM attributes LIMIT 300;


# query sample edge list file
SELECT node1_id, node2_id FROM edges
INNER JOIN (SELECT id FROM nodes LIMIT 500) AS n 
ON n.id = edges.node1_id
INNER JOIN (SELECT id FROM nodes LIMIT 500) AS m 
ON m.id = edges.node2_id
LIMIT 1000;


# query sample attributes file
SELECT node_id, attribute_id, namespace, name, description FROM nodes_attributes
INNER JOIN (SELECT id FROM nodes LIMIT 500) AS n 
ON n.id = nodes_attributes.node_id
INNER JOIN attributes as att
ON att.id = nodes_attributes.attribute_id
LIMIT 20000;

# query sample layout file
SELECT node_id, x_loc, y_loc, z_loc, r_val, g_val, b_val, a_val, namespace FROM layouts
INNER JOIN (SELECT id FROM nodes LIMIT 500) AS n 
ON n.id = layouts.node_id LIMIT 1000;

# query sample labels file
SELECT x_loc, y_loc, z_loc, text, namespace FROM labels LIMIT 500;