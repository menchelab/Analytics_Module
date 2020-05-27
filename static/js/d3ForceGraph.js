
var inputdata = {
    "nodes": [
      {"id": "Knapp", "group": 1},
      {"id": "Bock", "group": 2},
      {"id": "Binder", "group": 3},
      {"id": "Bergthaler", "group": 4},
      {"id": "Boztug", "group": 5},
      {"id": "Bennett", "group": 6},
      {"id": "Superti-Furga", "group": 7},
      {"id": "Loizou", "group": 8},
      {"id": "Kralovics", "group": 9},
      {"id": "Kubicek", "group": 10},
      {"id": "Menche", "group": 11}
    ],
    "links": [
      {"source": "Knapp", "target": "Bock", "value": 4},
      {"source": "Knapp", "target": "Binder", "value": 6},
      {"source": "Knapp", "target": "Bergthaler", "value": 2},
      {"source": "Knapp", "target": "Boztug", "value": 1},
      {"source": "Knapp", "target": "Bennett", "value": 9}
    ]
  };
  
var inputdata1 ={
  "nodes": [
    {"id": "Myriel", "group": 1},
    {"id": "Napoleon", "group": 1}

  ],
  "links": [
    {"source": "Napoleon", "target": "Myriel", "value": 1}
  ]
};

  

    
function drawit(data) {
     // if (error) throw error;
     d3.selectAll("svg > *").remove();
     var svg = d3.select("svg"),
     width = +svg.attr("width"),
     height = +svg.attr("height");
    
    var color = d3.scaleOrdinal(d3.schemeCategory20);
    
    var simulation = d3.forceSimulation()
        
        .force("link", d3.forceLink().id(function(d) { return d.id; }))
        .force("charge", d3.forceManyBody().strength(-5.5))
        .force("center", d3.forceCenter(width / 2, height / 2));

    
    
    var link = svg.append("g")
          .attr("class", "links")
        .selectAll("line")
        .data(data.links)
        .enter().append("line")
          .attr("stroke-width", function(d) { return Math.sqrt(d.value) + 2; });
    
    var node = svg.append("g")
          .attr("class", "nodes")
        .selectAll("circle")
        .data(data.nodes)
        .enter().append("circle")
         .attr("r", function(d) { return d.r *10 + 2; })
          //.attr("r",10.44)
          .attr("fill", function(d) { return color(d.group); })
          .call(d3.drag()
              .on("start", dragstarted)
              .on("drag", dragged)
              .on("end", dragended));
    
      node.append("title")
          .text(function(d) { return d.id; });
    
      simulation
          .nodes(data.nodes)
          .on("tick", ticked);
    
      simulation.force("link")
          .links(data.links);
    
                      function ticked() {
                        

                      
                        link
                            .attr("x1", function(d) { return d.source.x; })
                            .attr("y1", function(d) { return d.source.y; })
                            .attr("x2", function(d) { return d.target.x; })
                            .attr("y2", function(d) { return d.target.y; });
                    
                        node
                            .attr("cx", function(d) { return d.x; })
                            .attr("cy", function(d) { return d.y; });
                      }
      
      logger("drawit ran");
      
          function dragstarted(d) {
          if (!d3.event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
          logger( d.id);
        }
        
        function dragged(d) {
          d.fx = d3.event.x;
          d.fy = d3.event.y;
        }
        
        function dragended(d) {
          if (!d3.event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }
     

     
    };
  
    function reloadForceLayout (data){
        drawit(data);
    }  
    
    function clearForceLayout (data){
        d3.selectAll("svg > *").remove();
    }  
