const laptop_select = document.querySelector('option[value="lapcomp"]')
const phonetab_select = document.querySelector('option[value="phonetab"]')
const laptop_device_select = document.querySelectorAll('option[value^="l_"]')
const phonetab_device_select = document.querySelectorAll('option[value^="p_"]')

function change_display(elements, display) {
    elements.forEach(function (elem) {
        elem.style.display = display;
    })
}

const dynamic_devices = function () {
    laptop_select.addEventListener("click", function () {
        change_display(phonetab_device_select, "none");
        change_display(laptop_device_select, "inline");
    })
    phonetab_select.addEventListener("click", function () {
        change_display(phonetab_device_select, "inline");
        change_display(laptop_device_select, "none");
    })
    document.querySelector('select[name="device_os"]').addEventListener("change", function() {
        this.parentElement.submit();
    })
}

dynamic_devices()
