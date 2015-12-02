function changeBannerImage() {
  // console.log('changeBannerImage');
  var header_img;
  var screenWidth = document.documentElement.clientWidth;

  if (screenWidth <= 500) {
    header_img = 'https://s3-us-west-2.amazonaws.com/lensnola/realestate/css/images/lens-logo-magnifying-glass-only.png';
    document.getElementById('banner-image').src = header_img;
    document.getElementById('banner-image').width = '35';
    document.getElementById('banner-logo').style.width = '40px';
    document.getElementById('banner-logo').style.marginTop = '0px';
  } else {
    header_img = 'https://s3-us-west-2.amazonaws.com/lensnola/realestate/css/images/lens-logo-retina.png';
    document.getElementById('banner-image').src = header_img;
    document.getElementById('banner-image').width = '100';
    document.getElementById('banner-logo').style.width = '100px';
    document.getElementById('banner-logo').style.marginTop = '5px';
  }

  if (screenWidth <= 600) {
    document.getElementById('banner-title').innerHTML = 'City contracts';
  } else {
    document.getElementById('banner-title').innerHTML = 'City of New Orleans contracts';
  }
}

var window_resize_timeout;

window.addEventListener('resize', function(e) {
  clearTimeout(window_resize_timeout);
  window_resize_timeout = setTimeout(changeBannerImage, 100);
});

changeBannerImage();


window.downloadFile = function (sUrl) {

  // iOS devices do not support downloading.
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

window.downloadFile.isChrome = navigator.userAgent.toLowerCase().indexOf('chrome') > -1;
window.downloadFile.isSafari = navigator.userAgent.toLowerCase().indexOf('safari') > -1;

$(".download").on("click", function(event) {
  var id = $(this).parents(".contract-row").attr("id");
  downloadFile("/contracts/download/" + id);
});

function previous() {
  var current_page = $('#pagination').attr('data-current-page');
  current_page = current_page.toString();

  var number_of_pages = $('#pagination').attr('data-number-of-pages');
  number_of_pages = number_of_pages.toString();

  if (current_page === '1' || current_page === '0') {
    return;
  }

  var new_current_page = parseInt($("#pagination").attr("data-current-page"), 10) - 1;
  document.querySelector('#pagination').setAttribute('data-current-page', new_current_page);

  getSearch(1); // keep_current_page == 1 tells getSearch reset to page 1
}

function next() {
  var current_page = $('#pagination').attr('data-current-page');
  current_page = current_page.toString();

  var number_of_pages = $('#pagination').attr('data-number-of-pages');
  number_of_pages = number_of_pages.toString();

  if (current_page === number_of_pages) {
    return;
  }

  var new_current_page = parseInt($("#pagination").attr("data-current-page"), 10) + 1;
  document.querySelector('#pagination').setAttribute('data-current-page', new_current_page);

  getSearch(1); // keep_current_page == 1 tells getSearch reset to page 1
}

function checkPagerButtons() {//current_page, number_of_pages) {
  var current_page;
  var number_of_pages;

  if (typeof current_page === 'undefined') {
    current_page = $('#pagination').attr('data-current-page');
  }

  if (typeof number_of_pages === 'undefined') {
    number_of_pages = $('#pagination').attr('data-number-of-pages');
  }

  current_page = current_page.toString();
  number_of_pages = number_of_pages.toString();

  if (current_page === '1' || current_page === '0') {
    document.getElementById('previous').style.color = 'gray';
    document.getElementById('previous').style.cursor = 'default';
  } else {
    document.getElementById('previous').style.color = '#222';
    document.getElementById('previous').style.cursor = 'pointer';
  }

  if (current_page === number_of_pages) {
    document.getElementById('next').style.color = 'gray';
    document.getElementById('next').style.cursor = 'default';
  } else {
    document.getElementById('next').style.color = '#222';
    document.getElementById('next').style.cursor = 'pointer';
  }
}

function checkNumberOfResults() {
  var number_of_results = $('#pagination').attr('data-number-of-documents');
  var number_of_pages = $('#pagination').attr('data-number-of-pages');

  if (number_of_results !== '0') {
    document.getElementById('pagination').style.display = 'block';
  }

  if (number_of_pages !== '1') {
    document.getElementById('previous').style.display = 'block';
    document.getElementById('next').style.display = 'block';
  }
}

$(document).ready(function() {
  checkPagerButtons();
  checkNumberOfResults();
});


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
      getSearch();
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
