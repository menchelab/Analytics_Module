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

  $('#selections').on('selectmenuselect', function () {
    var id = $('#selections').find(':selected').val();

    // Compute search string.
    if ($("#searchInput1").text() != "INPUT1") {
      input_string = input_string.concat(input_string, "predicate0=", $(search))
    }

    path = dbprefix + "/api/"+ thisNamespace.namespace + "/node/search?subject0=attribute&object0=" + id ;
    $.ajax({
        type: "GET",
        url: path,
        contentType: "application/json",
        //data: payload,
        dataType: "json",
        headers: { "Authorization": "Basic " + btoa('steveballmer' + ":" + 'code peaceful canon shorter')},
      success: function(response) {
        for (var i = 0; i < 100 && i < response.nodes.length ; i++) {
            createNodeButton(response.nodes[i].name,response.nodes[i].symbol,response.nodes[i].node_id,"ResultList");
        }
        // Open the results tab, which is 4 when 0-indexed.
        $('#tabs').tabs( "option", "active", 3 );
      }
    });
  });


  $(function () {
    $("#LoadSelection").button();
        $("#LoadSelection").click(function (event) {
            event.preventDefault();
            console.log($("#selectMode").val() + " " + $("#selections").val() );
        });
    });

  $(function () {
    $("#saveSel").button();
    $("#saveSel").click(function (event) {
      event.preventDefault();
      console.log("do something useful");
    });
  });

  // SLIDERS FOR RANDOMWALK tab-6


  $(function () {
    $("#slider-restart_probability").slider({
      range: "max",
      min: 1,
      max: 100,
      value: 20,
      slide: function (event, ui) {
        $("#restart_probability").html(ui.value / 100);
      }
    });
    $("#restart_probability").val($("#slider-range-min").slider("value"));
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
        $('#searchMode1').append($('<option>', {value: "NEW",text: "NEW",}));
        $('#searchMode1').append($('<option>', {value: "ADD",text: "ADD",}));
        $('#searchMode1').append($('<option>', {value: "SUB",text: "SUB",}));
        $('#searchMode1').val("NEW");   //SET ACTIVE SLOT
        $('#searchMode1').hide();
        $('#searchMode1').selectmenu("refresh");

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
        ActivateVRkeyboard("SaveSearch");
    });
 });

  //buttons fuer randomwalk

  $(function () {
    $("#start_randomwalk_button").button();
    $("#start_randomwalk_button").click(function (event) {
      event.preventDefault();
      var span_Text = document.getElementById("restart_probability").innerText;
      console.log(span_Text)
      // ue4("StartRandomWalk", span_Text);
      reloadForceLayout (inputdata1);
    });
  });

  $(function () {
    $("#clear_randomwalk_button").button();
    $("#clear_randomwalk_button").click(function (event) {
      event.preventDefault();
      ue4("ClearRandomWalk", "bla");
      clearForceLayout (inputdata);
    });
  });

  ///////INIT HERE

 GetDbFileNames();

});
