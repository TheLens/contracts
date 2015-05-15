$(document).ready(function() {
  $(document).keypress(function(e) {
    if (e.which == 13) {
      getSearch();  // todo: Need to have GET at first, POST afterward.
    }
  });

  setHandlers();
  checkPagerButtons();
});
