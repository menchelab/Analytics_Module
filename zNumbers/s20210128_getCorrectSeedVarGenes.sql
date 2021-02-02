SELECT * FROM nodes;

SELECT * FROM nodes WHERE symbol in ('CD3G', 'C6', 'LAT', 'G6PD', 'C7', 'TCF3');

SELECT * FROM attributes;
SELECT DISTINCT namespace FROM attributes;

SELECT * FROM attributes WHERE namespace='SELECTION';

SELECT * FROM nodes
INNER JOIN (SELECT node_id, attribute_id FROM nodes_attributes WHERE attribute_id = '87975') as seeds
ON seeds.node_id = nodes.id LIMIT 500;

SELECT * FROM nodes
INNER JOIN (SELECT node_id, attribute_id FROM nodes_attributes WHERE attribute_id = '87974') as variants
ON variants.node_id = nodes.id LIMIT 500;
