/////// USER EDITABLE
/////// HERE ARE BUTTON MAPPINGS FROM HTML FILE
/////// AND CALLS TO FLASK AND DataDiVR_API

// add MAPPINGS TO UI ELEMENTS HERE //

$(document).ready(function () {


  //LOAD NAMESPACE MENU TAB 1
  $("#namespaces").selectmenu();

  $('#namespaces').on('selectmenuselect', function () {
    var name = $('#namespaces').find(':selected').text();
    //console.log(name);
    console.log(name);
    UpdateNamespace(name);
  });

$(function () {
    $("#test").button();
    $("#test").click(function (event) {
        event.preventDefault();
        console.log("This button does literally nothing!");
    });
});




  $(function () {
    $("#tabs").tabs();
    $("#right").tabs();

  });


  //selection menu tab-2

   $(function () {
        $("#selectMode").selectmenu();
        $('#selectMode').append($('<option>', {value: "NEW",text: "NEW",}));
        $('#selectMode').append($('<option>', {value: "ADD",text: "ADD",}));
        $('#selectMode').append($('<option>', {value: "SUB",text: "SUB",}));
        $('#selectMode').val("NEW");   //SET ACTIVE SLOT
        $('#selectMode').hide();
        $('#selectMode').selectmenu("refresh");

    });

    $('#selectMode').on('selectmenuselect', function () {
      // Do something useful I guess
      console.log($('#selectMode').val());
    });




  $("#selections").selectmenu();

// $('#selections').on('selectmenuselect', function () {
//      var id = $('#selections').find(':selected').val();
//      const name = $('#selections').find(':selected').text();
// 
//      path = dbprefix + "/api/"+ thisNamespace.namespace + "/node/search?subject0=attribute&object0=" + id ;
//      $.ajax({
//          type: "GET",
//          url: path,
//          contentType: "application/json",
//          //data: payload,
//          dataType: "json",
//          headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
//        success: function(response) {
//          mySearchResult = response.nodes;
//          PopulateSearchResults();
//          if (mySelection.length == 0 && mySelectionName.length == 0) {
//            mySelection = mySearchResult.slice();
//            mySelectionName = name;
//            PopulateShoppingCart();
//          }
//          // Open the results tab, which is 4 when 0-indexed.
//          $('#tabs').tabs( "option", "active", 3 );
//        }
//      });
//    });


  $(function () {
  $("#LoadSelection").button();
  $("#LoadSelection").click(function (event) {

    event.preventDefault();
    var id = $('#selections').find(':selected').val();
    const name = $('#selections').find(':selected').text();
    console.log(id, name);

    path = dbprefix + "/api/"+ thisNamespace.namespace + "/node/search?subject0=attribute&object0=" + id ;
    $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        //data: payload,
        dataType: "json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
      success: function(response) {
        console.log(path);
        mySearchResult = response.nodes;
        PopulateSearchResults();
        // if (mySelection.length == 0 && mySelectionName.length == 0) {
        //   mySelection = mySearchResult.slice();
        //   mySelectionName = name;
        //   PopulateShoppingCart();
        // }
        // Open the results tab, which is 4 when 0-indexed.
        // $('#tabs').tabs( "option", "active", 3 );
        $('#results').show();
      }
    });
    });
    });


  // SLIDERS FOR RANDOMWALK tab-6


  $(function () {
    $("#slider-restart_probability").slider({
      range: "max",
      min: 1,
      max: 100,
      value: 90,
      slide: function (event, ui) {
        $("#restart_probability").html(ui.value / 100);
      }
    });
  });

    $("#start_randomwalk_button").button();
  $("#start_randomwalk_button").click( function() {
    let nodes = $('#shopping_cart_inner').children().map(function() {return $(this).attr("id")});
    let restart_probability = $("#slider-restart_probability").slider("value") / 100;

    startRandomWalk(restart_probability, nodes);

  });



// TAB4 SEARCH
// $(function () {
      $(".search-attribute").each( function() {
        var id_num = $(this).attr('id').substr(-1);
        $(this).selectmenu();
        $(this).append($('<option>', {value: "DISEASE",text: "DISEASE",}));
        $(this).append($('<option>', {value: "PATHWAY",text: "PATHWAY",}));
        $(this).append($('<option>', {value: "molecular_function",text: "molecular_function",}));
        $(this).append($('<option>', {value: "cellular_component",text: "cellular_component",}));
        $(this).append($('<option>', {value: "biological_process",text: "biological_process",}));
        $(this).append($('<option>', {value: "TISSUE",text: "TISSUE",}));
        $(this).append($('<option>', {value: "HUMAN_PHENOTYPE",text: "HUMAN_PHENOTYPE",}));
        $(this).val("TISSUE");   //SET ACTIVE SLOT
        $(this).selectmenu("refresh");
    $(this).on('selectmenuselect', function () {
        var name = $(this).find(':selected').text();
        GetAttributeTaxonomy(name, id_num);
      })

    });
//     });


$(".search-predicate").each(function() {
    $(this).selectmenu();
    $(this).append($('<option>', {value: "AND",text: "AND",}));
    $(this).append($('<option>', {value: "OR",text: "OR",}));
    $(this).val("AND");   //SET ACTIVE SLOT
    $(this).selectmenu("refresh");
  });
$("#searchPredicate1-button").hide();


  $(function () {
    $(".search-button").each( function() {
      $(this).button();
      $(this).attr("searchID", -1);
      $(this).click(function (event) {
        event.preventDefault();
    });
    });
  });

  for (var i = 2; i <= 4; i++) {
  $("#showInput" + i).click(function(event) {
      event.preventDefault();
      $(this).hide();
    $("#search_field_" + $(this).attr("id").substr(-1)).show();
    setActiveSearchRow($(this).attr("id").substr(-1))

    });
  };

  for (var i = 2; i <= 4; i++) {
  $("#hideInput" + i).click(function(event) {
      event.preventDefault();
      $("#showInput" + $(this).attr("id").substr(-1)).show();
      setActiveSearchRow($(this).attr("id").substr(-1) - 1)

    console.log($("#searchAttribute" + $(this).attr("id").substr(-1)));
      $("#searchInput" + $(this).attr("id").substr(-1)).text('INPUT'+$(this).attr("id").substr(-1))
    $("#search_field_" + $(this).attr("id").substr(-1)).hide();

  });
  };

  //desktop version input field1
    setActiveSearchRow(1);

   $("#search_txt").keyup(function(){
      console.log("clicked", $("#search_bar").attr("active_row"));
     GetDbSearchTerms($(this).val(),
       $('#searchAttribute' + $("#search_bar").attr("active_row")).val(),
      $("#search_bar").attr("active_row")
     );
   });


    $(function () {
        $("#searchMode1").selectmenu();

    });

  for (var i = 1; i <= 4; i++) {
    $('#SearchPredicate' + i).click(function() {
      setActiveSearchRow($(this).attr("id").substr(-1))
    });
    $('#SearchAttribute' + i).click(function() {
      setActiveSearchRow($(this).attr("id").substr(-1))
    });
  }


 $(function () {
    $("#searchGO").button();
    $("#searchGO").click(function (event) {
        event.preventDefault();
        var id = $("#searchInput" + $("#search_bar").attr("active_row")).attr("searchID");

        SimpleSearch(id);
    });
 });

  $(function () {
    $("#SaveSearch").button();
    $("#SaveSearch").click(function (event) {
      event.preventDefault();
      let action = $('#searchMode1').val();
      if (action == "NEW") {
        mySelection = mySearchResult.slice();
        mySelectionName = "";
      } else if (action == "ADD") {
        let existing_ids = mySelection.map(function(node) {return node.node_id})
        mySearchResult.forEach(function(node) {
          if (!(existing_ids.includes(node.node_id))) {
            mySelection.push(node);
          }
        })
      } else if (action == "INT") {
        let new_ids = mySearchResult.map(function(node) {return node.node_id})
        mySelection = mySelection.filter(function(node) {
          var node_id = node.node_id;
          return new_ids.includes(node.node_id);
        })
      } else if (action == "SUB") {
        let new_ids = mySearchResult.map(function(node) {return node.node_id})
        mySelection = mySelection.filter(function(node) {
          return !(new_ids.includes(node.node_id));
        })
      }
      PopulateShoppingCart();
    });
 });

  //buttons fuer randomwalk

// $(function () {
//     $("#start_randomwalk_button").button();
//     $("#start_randomwalk_button").click(function (event) {
//       event.preventDefault();
//       var span_Text = document.getElementById("restart_probability").innerText;
//       console.log(span_Text)
//       // ue4("StartRandomWalk", span_Text);
//       reloadForceLayout (inputdata1);
//     });
//   });

  $(function () {
    $("#clear_randomwalk_button").button();
    $("#clear_randomwalk_button").click(function (event) {
      event.preventDefault();
      clearForceLayout (inputdata);
    });
  });

  $("#clear_cart").button();
  $("#save_cart").button();
  $("#clear_cart").click(function (event) {
    mySelection = [];
    PopulateShoppingCart();
  });
  $("#save_cart").click(function (event) {
    SaveSelectionDB({"selection_name": $('#selection_name_input').val(),
      "node_ids": mySelection.map(item => item.node_id)});
  });


$("#upload_button").button();
$("input:radio[name='namespace']").change( function() {
  if ($(this).val() == "New") {
    $("#new_namespace_name").show();
  } else {
    $("#new_namespace_name").hide();

  }
});

$('form :input').on('change input', function() {
  console.log("changed!");
  var formData = new FormData(document.getElementById('upload_form'));
  let namespace = formData.get("namespace");
  if (namespace == "New") {
    existing_selections = allNamespaces.map(function(x) {return x.namespace});
    let new_name = formData.get("new_name");
      $("#submit_warnings").html("Please provide a new name!")
      $("#upload_button").attr("disabled", true).addClass("ui-state-disabled");
    if (new_name == "") {
    } else if (existing_selections.includes(new_name)) {
      $("#submit_warnings").html("This name is already taken!")
      $("#upload_button").attr("disabled", true).addClass("ui-state-disabled");
      return
    } else if (formData.get("layouts").size > 0)  {  // We need at least one layout to create a namespace
      $("#submit_warnings").html("")
      $("#upload_button").attr("disabled", false).removeClass("ui-state-disabled");
      return
    } else {
      $("#submit_warnings").html("Please add at least one layout to create a new namespace!")
      $("#upload_button").attr("disabled", true).addClass("ui-state-disabled");
    }
  } else {
    if (formData.get('layouts').size > 0 ||
        formData.get('links').size > 0 ||
        formData.get('labels').size > 0 ||
        formData.get('attributes').size > 0) {
      $("#submit_warnings").html("")
      $("#upload_button").attr("disabled", false).removeClass("ui-state-disabled");
      return
    }
  }
  $("#submit_warnings").html("Please add at least one object to upload!")
  $("#upload_button").attr("disabled", true).addClass("ui-state-disabled");
});




$("#upload_form").submit(function(event) {
  event.preventDefault();

  var form = $(this);
  var formData = new FormData(this);
  if (formData.get("namespace") == 'existing') {
    formData.append('existing_namespace', $('#namespaces').val());
  }
  let it = formData.keys();
  let result = it.next();
  while (!result.done) {
 console.log(result.value); // 1 3 5 7 9
    console.log(formData.get(result.value))
 result = it.next();
}


  var url = "/upload";
  $.ajax({
    type: "POST",
    url: url,
    data: formData, // serializes the form's elements.
    cache: false,
    contentType: false,
    processData: false,
    success: function(data)
    {
        console.log("Uploaded successfully!"); // show response from the php script.
    }
  });

});


$(function() {
  $('.hover_button').on('hover', function() {
    if($(this).hasClass('selected')) {
      deselect($(this));
    } else {
      $(this).addClass('selected');
      $('.pop').slideFadeToggle();
    }
    return false;
  }
  );

  $('.close').on('click', function() {
    deselect($('#contact'));
    return false;
  });
});

$.fn.slideFadeToggle = function(easing, callback) {
  return this.animate({ opacity: 'toggle', height: 'toggle' }, 'fast', easing, callback);
};

$("#show_attributes_list").click(function() {
  $("#attributes_list").show();
  $("#show_attributes_list").hide();
  $('.pop').css({top:100, left:100, height:600, width:700})
});
$("#node_popup_close").click(function() {
  $("#show_attributes_list").show();
  $("#node_popup").hide();
});

// Hide popup if clicked outside of it.
$(document).mouseup(function(e)
{
    var container = $("#node_popup");

    // if the target of the click isn't the container nor a descendant of the container
    if (!container.is(e.target) && container.has(e.target).length === 0)
    {
        container.hide();
    }
});

  ///////INIT HERE

 GetDbFileNames();

});
