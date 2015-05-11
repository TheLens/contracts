window.downloadFile = function (sUrl) {
  console.log('downloadFile');

  // iOS devices do not support downloading.
  if (/(iP)/g.test(navigator.userAgent)) {
    console.log('iOS alert');

    alert('Your device does not support files downloading. Please try again in desktop browser.');
    return false;
  }

  // If in Chrome or Safari - download via virtual link click
  if (window.downloadFile.isChrome || window.downloadFile.isSafari) {
    console.log('In Chrome or Safari');

    // Creating new link node.
    var link = document.createElement('a');
    link.href = sUrl;

    if (link.download !== undefined) {
      console.log('Link is undefined');

      // Set HTML5 download attribute. This will prevent file from opening if supported.
      var fileName = sUrl.substring(sUrl.lastIndexOf('/') + 1, sUrl.length);
      link.download = fileName;
    }

    // Dispatching click event.
    if (document.createEvent) {
      console.log('Dispatching click event');

      var e = document.createEvent('MouseEvents');
      e.initEvent('click', true, true);
      link.dispatchEvent(e);
      return true;
    }
  }

  // Force file download (whether supported by server).
  if (sUrl.indexOf('?') === -1) {
    console.log('Force file download');

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
  data.current_page = document.querySelector('#pagination');

  console.log(document.querySelector('#pagination'));
  console.log(typeof document.querySelector('#pagination'));

  if (data.current_page === null) {
    console.log(data.current_page);
    console.log(typeof data.current_page);
    data.current_page = 1;
  } else {
    console.log(data.current_page);
    console.log(typeof data.current_page);
    data.current_page = document.querySelector('#pagination').getAttribute('data-current-page');
  }

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

  if (data.current_page !== '' && data.current_page !== "1") {
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

  $(".open-button").on("click", function() {
    var id = $(this).parents(".contract-preview").attr("id");
    window.location.href = '/contracts/contract/' + id;
  });

  $(".download").on("click", function() {
    var id = $(this).parents(".contract-preview").attr("id");
    downloadFile("/contracts/download/" + id);
  });
}

function previous() {
  var new_current_page = parseInt($("#pagination").attr("data-current-page"), 10) - 1;
  document.querySelector('#pagination').setAttribute('data-current-page', new_current_page);
  
  getSearch();
}

function next() {
  var new_current_page = parseInt($("#pagination").attr("data-current-page"), 10) + 1;
  document.querySelector('#pagination').setAttribute('data-current-page', new_current_page);
  
  getSearch();
}

function getSearch() {
  var data = prepareData();

  var query_string = buildSearch(data);
  console.log(query_string);
  
  window.location.href = '/contracts/search/' + query_string;
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
  $(document).keypress(function(e) {
    if (e.which == 13) {
      getSearch();  // todo: Need to have GET at first, POST afterward.
    }
  });

  setHandlers();
});

window.downloadFile.isChrome = navigator.userAgent.toLowerCase().indexOf('chrome') > -1;
window.downloadFile.isSafari = navigator.userAgent.toLowerCase().indexOf('safari') > -1;
