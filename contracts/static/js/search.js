$(document).ready(function() {
  $(document).keypress(function(e) {
    if (e.which == 13) {
      getSearch();  // todo: Need to have GET at first, POST afterward.
    }
  });

  setHandlers();
  checkPagerButtons();
});

function populateSearchParameters(data) {
  console.log(data);

  document.getElementById('text-box').value = data.search_input;
  document.getElementById('vendors').value = data.vendors;
  document.getElementById('departments').value = data.departments;
  document.getElementById('officers').value = data.officers;

  // if (data.name_address === '') {
  //   if (data.neighborhood !== '') {
  //     document.getElementById('name-address-box').value = data.neighborhood;
  //   } else {
  //     document.getElementById('name-address-box').value = data.zip_code;
  //   }
  // }
  // if (data.amount_low !== '' || data.amount_high !== '' || data.begin_date !== '' || data.end_date !== '') {
  //   document.getElementById('filters').style.display = 'block';
  //   document.getElementById('advanced-search').innerHTML = '<a>Hide advanced search <i class="fa fa-caret-up"></i></a>';
  // }
}