function prepareData() {
  var data = {};

  data.search_input = encodeURIComponent($("#text-box").val());
  data.vendor = encodeURIComponent($('#vendors').val());
  data.department = encodeURIComponent($('#departments').val());
  data.officer = encodeURIComponent($('#officers').val());
  data.current_page = document.querySelector('#pagination');

  // console.log(document.querySelector('#pagination'));
  // console.log(typeof document.querySelector('#pagination'));

  if (data.current_page === null) {
    // console.log(data.current_page);
    // console.log(typeof data.current_page);
    data.current_page = 1;
  } else {
    // console.log(data.current_page);
    // console.log(typeof data.current_page);
    var current_page = document.querySelector('#pagination').getAttribute('data-current-page');
    data.current_page = parseInt(current_page, 10);
  }

  // console.log('Parameters collected:', data);

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

  if (data.officer !== '') {
    if (query_string !== '?') {
      query_string = query_string + '&';
    }
    query_string = query_string + "officer=" + data.officer;
  }

  if (data.current_page !== '' && data.current_page !== 1) {
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
  $("#next").on("click", function() {
    next();
  });

  $("#previous").on("click", function() {
    previous();
  });

  $(".search-button").on("click", function() {
    getSearch();
  });

  // $(".open-button").on("click", function() {
  //   var id = $(this).parents(".contract-row").attr("id");
  //   window.location.href = '/contracts/contract/' + id;
  // });

  // $(".download").on("click", function() {
  //   var id = $(this).parents(".contract-row").attr("id");
  //   downloadFile("/contracts/download/" + id);
  // });

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

  $(".clear-all").on("click", function() {
    document.getElementById('text-box').value = '';
    document.getElementById('vendors').value = '';
    document.getElementById('departments').value = '';
    document.getElementById('officers').value = '';
  });
}

function populateSearchParameters(data) {

  // console.log('Parameter data returned:', data);

  document.getElementById('text-box').value = data.search_input;
  document.getElementById('vendors').value = data.vendor;
  document.getElementById('departments').value = data.department;
  document.getElementById('officers').value = data.officer;

  if (data.vendor !== '' || data.department !== '' || data.officer !== '') {
    document.getElementById('filters').style.display = 'block';
    document.getElementById('advanced-search').innerHTML = '<a>Hide advanced search <i class="fa fa-caret-up"></i></a>';
  }
}

// function getDataFromUrl() {
//   var data = {};

//   // data.search_input = encodeURIComponent($("#text-box").val());
//   // data.vendor = encodeURIComponent($('#vendors').val());
//   // data.department = encodeURIComponent($('#departments').val());
//   // data.officer = encodeURIComponent($('#officers').val());
//   // data.current_page = document.querySelector('#pagination');


//   var url_query = window.location.search.substring(0).match(/query\=(.*)/i);
//   if (url_query !== null) {
//     var query_text = decodeURIComponent(url_query[1]);
//     data.search_input = query_text;
//   }

//   var url_vendors = window.location.search.substring(0).match(/vendors\=(.*)/i);
//   if (url_vendors !== null) {
//     var vendor_text = decodeURIComponent(url_vendors[1]);
//     data.vendor = vendor_text;
//   }

//   var url_departments = window.location.search.substring(0).match(/departments\=(.*)/i);
//   if (url_departments !== null) {
//     var departments_text = decodeURIComponent(url_departments[1]);
//     data.department = departments_text;
//   }

//   var url_officers = window.location.search.substring(0).match(/officers\=(.*)/i);
//   if (url_officers !== null) {
//     var officers_text = decodeURIComponent(url_officers[1]);
//     data.officer = officers_text;
//   }

//   var url_page = window.location.search.substring(0).match(/page\=(.*)/i);
//   if (url_page !== null) {
//     var page_text = decodeURIComponent(url_page[1]);
//     data.current_page = page_text;
//   }

//   return data;
// }

function getSearch(keep_current_page) {
  var data = prepareData();

  if (keep_current_page !== 1) {
    data.current_page = 1;
  }

  // data = checkForNewSearchParameters(data);

  var query_string = buildSearch(data);
  
  // console.log('Query string:', query_string);
  
  window.location.href = '/contracts/search/' + query_string;
}

$(document).ready(function() {
  $(document).keypress(function(e) {
    if (e.which == 13) {
      getSearch();  // todo: Need to have GET at first, POST afterward.
    }
  });

  setHandlers();
});

// function checkForChanges() {
//   if ($('.t402-elided').length > 0) {
//     setTimeout(checkForChanges, 1000);
//     console.log('Trying again in one second.');
//   } else {
//     console.log('Survey completed or skipped. Adding in advancedsearch');
//     //var html = $("#blockOfStuff").html();
//     //$("#post-gcs").html(html);
//   }
// }
