use ppi;

delete attribute_taxonomies
from attribute_taxonomies
join attributes on parent_id = attributes.id
where attributes.namespace = "SELECTION";

delete nodes_attributes
from nodes_attributes
join attributes on attribute_id = attributes.id
where attributes.namespace = "SELECTION";

delete attributes
from attributes
where namespace = "SELECTION";
