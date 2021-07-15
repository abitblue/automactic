const deviceSelection = document.querySelector("select[name='device_os']")

deviceSelection.addEventListener('change', function() {
    this.parentElement.submit();
})