window.downloadFile = function (sUrl) {

    // iOS devices do not support downloading. We have to inform user about this.
    if (/(iP)/g.test(navigator.userAgent)) {
      alert('Your device does not support files downloading. Please try again in desktop browser.');
      return false;
    }

    // If in Chrome or Safari - download via virtual link click
    if (window.downloadFile.isChrome || window.downloadFile.isSafari) {
      // Creating new link node.
      var link = document.createElement('a');
      link.href = sUrl;

      if (link.download !== undefined) {
        // Set HTML5 download attribute. This will prevent file from opening if supported.
        var fileName = sUrl.substring(sUrl.lastIndexOf('/') + 1, sUrl.length);
        link.download = fileName;
      }

      // Dispatching click event.
      if (document.createEvent) {
        var e = document.createEvent('MouseEvents');
        e.initEvent('click', true, true);
        link.dispatchEvent(e);
        return true;
      }
    }

    // Force file download (whether supported by server).
    if (sUrl.indexOf('?') === -1) {
      sUrl += '?download';
    }

    window.open(sUrl, '_self');
    return true;
};



function prepareData() {
  var data = {};

  data.search_input = encodeURIComponent($("#text-box").val());
  data.vendor = encodeURIComponent($('#vendors').val());
  data.department = encodeURIComponent($('#departments').val());
  // data.officer = encodeURIComponent($('#officers').val());
  data.current_page = document.querySelector('#pagination').getAttribute('data-current-page');

  console.log(data);

  return data;
}

function buildSearch(data) {
  var query_string = '?';

  if (data.search_input !== '') {
    query_string = query_string + "query=" + data.search_input;
  }

  if (data.vendor !== '') {
    if (query_string !== '?') {
      query_string = query_string + '&';
    }
    query_string = query_string + "vendor=" + data.vendor;
  }

  if (data.department !== '') {
    if (query_string !== '?') {
      query_string = query_string + '&';
    }
    query_string = query_string + "department=" + data.department;
  }

  // if (data.officer !== '') {
  //   if (query_string !== '?') {
  //     query_string = query_string + '&';
  //   }
  //   query_string = query_string + "officer=" + data.officer;
  // }

  if (data.current_page !== '') {
    if (query_string !== '?') {
      query_string = query_string + '&';
    }
    query_string = query_string + "page=" + data.current_page;
  }

  if (query_string == '?') {
    query_string = "";
  }

  return query_string;
}

function setHandlers() {
  $("#next").on("click", function(e) {
    next();
  });

  $("#previous").on("click", function(e) {
    previous();
  });

  $("#search-button").on("click", function() {
    getSearch();  // todo: Need to have GET at first, POST afterward.
  });

  $(".open-button").on("click", function(event) {
    // event.stopPropagation();
    var id = $(this).parents(".contract-preview").attr("id");
    window.location.href = '/contracts/contract/' + id;
  });

  $(".download-button").on("click", function(event) {
    // event.stopPropagation();
    downloadFile("/contracts/download/" + $(this).parents(".contract-preview").attr("id"));
  });
}

function handlePost(data){
  $("#contract-results").html(data);
  results = $("#pagination").attr("data-total");
  if (results > 0){
    id = $(".contract-preview").first().attr("id");
  }
  setHandlers();
}

function previous() {
  // searchQuery =  $("#pagination").attr("data-query") + "&&offset:" + $("#pagination").attr("data-offset");

  // $.post("previous/" + searchQuery, function(data, status) {
  //   handlePost(data);
  //   });

  var new_current_page = $("#pagination").attr("data-current-page") - 1;
  document.querySelector('#pagination').setAttribute('data-current-page', new_current_page);
  
  postSearch();
}

function next() {
  // searchQuery =  $("#pagination").attr("data-query") + "&&offset:" + $("#pagination").attr("data-offset");
  // $.post("next/" + searchQuery, function(data, status) {
  //   handlePost(data);
  // });

  var new_current_page = $("#pagination").attr("data-current-page") + 1;
  document.querySelector('#pagination').setAttribute('data-current-page', new_current_page);
  
  postSearch();
}

function getSearch() {
  var data = prepareData();

  var query_string = buildSearch(data);
  console.log(query_string);
  
  window.location.href = '/contracts/search/' + query_string;
}

function postSearch() {
  var data = prepareData();

  var query_string = buildSearch(data);
  console.log(query_string);
  
  data.current_page = $("#pagination").attr("data-current-page");

  $.ajax({
    type: 'POST',
    url: "/contracts/search/" + query_string,
    data: data,
    contentType: "application/json; charset=utf-8",
    success: function(info) {
      console.log('info: ', info);
      handlePost(data);
    }
  });
}

function checkForChanges() {
  if ($('.t402-elided').length > 0) {
    setTimeout(checkForChanges, 1000);
    console.log('Trying again in one second.');
  } else {
    console.log('Survey completed or skipped. Adding in advancedsearch');
    //var html = $("#blockOfStuff").html();
    //$("#post-gcs").html(html);
  }
}

$("#advanced-search").on("click", function() {
  var display = document.getElementById("filters").style.display;
  if (display === "block") {
    document.getElementById('filters').style.display = 'none';
    document.getElementById('advanced-search').innerHTML = 'Show advanced search <i class="fa fa-caret-down"></i>';
  } else {
    document.getElementById('filters').style.display = 'block';
    document.getElementById('advanced-search').innerHTML = 'Hide advanced search <i class="fa fa-caret-up"></i>';
  }
});

$(document).ready(function() {
  // $("#DV-container").children().first().children().first().addClass('selected-viewer');

  $(".contract-preview").first().addClass("selected");

  $(document).keypress(function(e) {
    if (e.which == 13) {
      getSearch();  // todo: Need to have GET at first, POST afterward.
    }
  });

  setHandlers();
});

window.downloadFile.isChrome = navigator.userAgent.toLowerCase().indexOf('chrome') > -1;
window.downloadFile.isSafari = navigator.userAgent.toLowerCase().indexOf('safari') > -1;
