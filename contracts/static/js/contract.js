$(".download").on("click", function() {
  // var id = $(this).parents(".contract-row").attr("id");
  var id = document.querySelector('#download').getAttribute('data-id');
  downloadFile("/contracts/download/" + id);
});