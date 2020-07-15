///////GLOBAL VARS vvvvvvv
var dbprefix = 'http://asimov.westeurope.cloudapp.azure.com:8887';
// var dbprefix = ""
//create the global ue4(...) helper function
"object"!=typeof ue||"object"!=typeof ue.interface?("object"!=typeof ue&&(ue={}),ue.interface={},ue.interface.broadcast=function(e,t){if("string"==typeof e){var o=[e,""];void 0!==t&&(o[1]=t);var n=encodeURIComponent(JSON.stringify(o));"object"==typeof history&&"function"==typeof history.pushState?(history.pushState({},"","#"+n),history.pushState({},"","#"+encodeURIComponent("[]"))):(document.location.hash=n,document.location.hash=encodeURIComponent("[]"))}}):function(e){ue.interface={},ue.interface.broadcast=function(t,o){"string"==typeof t&&(void 0!==o?e.broadcast(t,JSON.stringify(o)):e.broadcast(t,""))}}(ue.interface),(ue4=ue.interface.broadcast);
////  API DEFENITION
//// DONT TOUCH THIS FILE
function logger(message){
    console.log(message);
    ue4("log",message);
}

var dbdata;
var thisNamespace;
var allNamespaces = [];
var mySelection = [];
var mySearchResult = [];
var mySelectionName = "";



////put functions that POST to Flask HERE vvv
function UpdateNamespace(name) {

    thisNamespace = dbdata.find(o => o.namespace === name);
    console.log(thisNamespace);

    GetDbSelections(); //LOAD SELECTION FILES FOR PROJECT
}

function GetDbFileNames() {

    path = dbprefix + '/api/namespace/summary' ;
    $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        dataType: "json",
        success: function(response) {
        // POPULATE UI DROPDOWN
            dbdata = response.slice(); //DEEP COPY !!!!
            allNamespaces = response.slice();

            response[0].layouts.forEach(function(item)
            {
                 $('#layouts').append($('<option>', {value: item,text: item}));
            });

            $('#layouts').val(response[0].layouts[0]);   //SET ACTIVE SLOT
            $("#layouts").selectmenu("refresh");                          //AND SHOW


            response.forEach(function(item)
            {
                 $('#namespaces').append($('<option>', {value:  item.namespace, text:  item.namespace}));
            });

            $('#namespaces').val('ppi');
            $("#namespaces").selectmenu("refresh");
            UpdateNamespace('ppi');

        },

        error: function(err) {
        console.log(err);

        }
    });
//event.preventDefault();

}


function setActiveSearchRow(row_num) {
  console.log("setting " + row_num);
  if($("#search_bar").attr("active_row") != row_num) {
    $("#search_bar").attr("active_row", row_num)
    clearButtons("autocomp");
    clearButtons("taxonomy_bar");
    $('#search_txt').val("")
  }
}



////Search and auto complete dynamic button factory
function GetDbSearchTerms(name, namespace, search_attr_id) {
  console.log("running");
  // var search_attr_id = 1;


    path = dbprefix + "/api/ppi/attribute/?prefix="+ name + "&namespace="+ namespace;
    //console.log(path);
    if (name.length > 1){
    $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        dataType: "json",
        success: function(response) {

          //clearButtons("autocomp");

          $('#autocomp').empty();
            response.forEach(function(item)
            {
                createButton(item.name,item.id,$("#autocomp"), search_attr_id);
            });

        console.log(response);
        },

        error: function(err) {
        console.log(err);

        }
    });
    }
}

function createButton(Bname,Bid,Parent, search_attr_id) {
  console.log("creating hover");

    var r=$('<input/>').attr({
        type: "button",
        id: Bid,
        value: Bname,
    });
    Parent.append(r);
    $(r).button();
    $(r).click(function() {
        $("#searchInput" + search_attr_id).text(Bname);
        $("#searchInput" + search_attr_id).attr("searchID",Bid);
    });

}

function createDropdownButton(Bname,Bid,Parent, depth, children, search_attr_id) {

    var r=$('<input/>').attr({
        type: "button",
        id: Bid,
        value: "\u25BC " + Bname

    });
    Parent.append(r);
    $(r).button();
    $(r).click(function() {
        $("#searchInput" + search_attr_id).text(Bname);
        $("#searchInput" + search_attr_id).attr("searchID",Bid);
      console.log(search_attr_id);
        AddChildren(children, depth, search_attr_id);
    });
}

function deselect(e) {
  $('.pop').hide(function() {
    e.removeClass('selected');
  });    
}

function createNodeButton(Bname,Bsym,Bid,Parent) {
 //for resultList

    var r=$('<input/>').attr({
        type: "button",
        id: Bid,
        value: Bsym

    });
    var p = '#' + Parent;
    $(p).append(r);
    $(r).button();
      $(r).click(function(event) {
        console.log(event.pageX);
        let left = event.pageX;
        let top = event.pageY;
        if($(r).hasClass('selected')) {
          deselect($(this));
        } else {
          $(this).addClass('selected');
          $('#node_name').html(Bname)
          $('.pop').css({top:top, left:left})
          $('.pop').show();
        }
        return false;
      }
    );
    $(r).click(function() {
       // $("#searchInput1").text(Bname);
      //  $("#searchInput1").attr("searchID",Bid);
        console.log(Bname + " " + Bid + " " + Parent);
      path = dbprefix + "/api/"+ thisNamespace.namespace + "/attribute/?node_id=" + Bid ;
      $.ajax({
          type: "GET",
          url: path,
          contentType: "application/json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
          //data: payload,
          dataType: "json",
        success: function(response) {
          for (var i = 0; i < 100 && i < response.length ; i++) {

            createAttributeButton(response[i].name,response[i].id,"attributes_list");

          }
          $('#tabs').tabs( "option", "active", 5 );

        }
      });
  }
    )};

function createAttributeButton(name, id, Parent) {
 //for resultList

    var r=$('<input/>').attr({
        type: "button",
        id: id,
        value: name

    });
    var p = '#' + Parent;
    $(p).append(r);
    $(r).button();
    $(r).click(function() {
       // $("#searchInput1").text(Bname);
      //  $("#searchInput1").attr("searchID",Bid);
        console.log(name + " " + id + " " + Parent);

  }
    )};


function clearButtons(parent){
  const myNode = document.getElementById(parent);
  while (myNode.firstChild) {
    myNode.removeChild(myNode.firstChild);
  }
}

function GetDbSelections() {

    path = dbprefix + "/api/"+ thisNamespace.namespace + "/attribute/?namespace=SELECTION" ;
    console.log(path)
    $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        dataType: "json",
        success: function(response) {
            response.forEach(function(item)
            {
                 $('#selections').append($('<option>', {value: item.id, text: item.name}));
            });
            $("#selections").selectmenu("refresh");
            $("#selections").prop("selectedIndex", 0);
        },
        error: function(err) {
          console.log("whoops, error");
        console.log(err);

        }
    });
//event.preventDefault();

}

function SimpleSearch(id) {
    var input_string = ""
    for (var i = 1; i <=4; i++) {
      if ($("#searchInput" + i).text() != "INPUT" + i) {
        console.log("INPUT" + i);
        console.log($("#searchInput" + i).text());
        console.log($("#searchInput" + i).text() == "INPUT" + i);
        input_string = input_string.concat(
          "predicate", (i-1), "=",
          $("#searchPredicate" + i).val(),
          "&subject", i-1, "=attribute&object", i-1, "=",
          $("#searchInput" + i).attr("searchID"), "&"
        )
      }
    }
    path = dbprefix + "/api/"+ thisNamespace.namespace + "/node/search?" + input_string
  console.log(path);
        $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        dataType: "json",
        success: function(response) {

          console.log(response);
            response.mode = $('#searchMode1').val();
            console.log(response);
            document.getElementById("sResults").innerHTML = "FOUND " + response.nodes.length + " NODES FOR " + $('#searchInput1').text();
            ue4("LoadSelectionDB", response);

            document.getElementById("ResultsLabel").innerHTML = "FOUND " + response.nodes.length + " NODES FOR " + $('#searchInput1').text();
            clearButtons("ResultList");

/*             response.nodes.forEach(function(item)
            {

            }); */

            for (var i = 0; i < 5000 && i < response.nodes.length ; i++) {
              createNodeButton(response.nodes[i].name,response.nodes[i].symbol,response.nodes[i].node_id,"ResultList");
            }
            mySearchResult = response.nodes;
            PopulateSearchResults();
            $('#results').show();
        },

        error: function(err) {
        console.log(err);

        }
    });
//event.preventDefault();
}

function AddChild(parent, child, depth, search_attr_id) {
  if(child.childnodes.length == 0) {
    createButton(child.name, child.id, parent, search_attr_id);
    $('#' +child.id).attr("depth", depth)
  } else {  //(child.childnodes.length >= 1){
    createDropdownButton(child.name, child.id, parent, depth, child.childnodes, search_attr_id);
  }
    if (depth%2 == 0) {$('#'+child.id).css("background-color", "#3e67ff")}

}

function AddChildren(children, depth, search_attr_id) {
  if (typeof depth == typeof undefined) {
    console.log("undefined depth of children")
  }
  depth = depth || 1
  $("#taxonomy_bar").children().each(function(i) {
    var child = $(this)
    var attr = $(this).attr('depth')
    if (typeof attr !== typeof undefined && attr !== false && attr > depth) {
       child.remove();
    };
  });
  new_bar = $('<p>');
  new_bar.addClass('taxo_display');
  new_bar.attr("depth", depth + 1)
  $("#taxonomy_bar").append(new_bar);
  children.forEach(function(child) {
    AddChild(new_bar, child, depth + 1, search_attr_id)});
}

function GetAttributeTaxonomy(name, search_attr_id) {
  $(".taxo_display").remove();

  path = dbprefix + "/api/"+ "ppi" + "/attribute_taxonomy/?namespace=" + name ;
    var ajaxTime= new Date().getTime();
    console.log(path)
    $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
       dataType: "json",
        success: function(response) {
          var totalTime = new Date().getTime()-ajaxTime;
          console.log("total time" , totalTime)

          new_bar = $('<p>');
          new_bar.addClass('taxo_display');
          $("#taxonomy_bar").append(new_bar)
          if (typeof response.childnodes !== typeof undefined) {
            response.childnodes.forEach(function(item) {
              AddChild(new_bar, item, 1, search_attr_id);
            });
            totalTime = new Date().getTime()-ajaxTime;
              console.log("total time" , totalTime)
          }
        },

        error: function(err) {
        console.log(err);

        }
    });
//event.preventDefault();

}

function SaveSelectionDB(data) {
  console.log(JSON.stringify(data));

   payload = JSON.stringify(data);
    //console.log(payload);
    path = dbprefix + "/api/ppi/selection/create";
    $.ajax({
        type: "POST",
        url: path,
        contentType: "application/json",
        data: payload,
        dataType: "json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        success: function(response) {

            console.log(response);
            },
        error: function(err) {
        console.log(err);
        }
    });
//event.preventDefault();
}

function PopulateShoppingCart() {
  $("#shopping_cart_inner").empty();
  if (mySelection.length == 0) {
    mySelectionName = '';
    $('#selection_name_button').prop('disabled',true).css('opacity', 0.5);
    $('#selection_name_input').val("").css('opacity', 0.5);
    return;
  }
  $('#selection_name_button').prop('disabled', false).css('opacity', 1.0);
  $('#selection_name_input').val(mySelectionName).css('opacity', 1.0);
  for (var i = 0; i < mySelection.length; i++) {
    createNodeButton(mySelection[i].name,
      mySelection[i].symbol,mySelection[i].node_id,
      "shopping_cart_inner");
  }
}

function PopulateSearchResults() {
  $("#ResultList").empty();
  for (var i = 0; i < mySearchResult.length; i++) {
    createNodeButton(mySearchResult[i].name,
      mySearchResult[i].symbol,mySearchResult[i].node_id,
      "ResultList");
  }
}

function startRandomWalk(restart_probability, nodes) {
  let data = {}
  data["restart_probability"] = 0.9
  data["min_frequency"] = 0.00001
  data["node_ids"] = Array.from(nodes)
  payload = JSON.stringify(data);
  console.log(payload)
  path = dbprefix + "/api/ppi/node/random_walk";
    $.ajax({
        type: "POST",
        url: path,
        contentType: "application/json",
        data: payload,
        dataType: "json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
        success: function(response) {
          mySearchResult = response.nodes;
          mySearchResult.forEach(function(elem) {elem["node_id"] = elem.id;})

          console.log(response);
          PopulateSearchResults();
          $('#tabs').tabs( "option", "active", 3 );
          $('#random_walk_display').show();
          $('#force_graph').show();
          drawBarChart(response.nodes)
          reloadForceLayout(response)
            },
        error: function(err) {
        console.log(err);
        }
    });

}
