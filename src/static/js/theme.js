$(document).on('change', '#theme-toggle', function (e) {
    var style = $('#bootstrap-theme').attr('href')
    var mode;
    if (style.includes('dark')) {
        style = style.replace('dark', 'light')
        mode = "light"
    } else {
        style = style.replace('light', 'dark')
        mode = "dark"
    }
    $.post('/theme/toggle', {mode: mode}, function () {
        $('#bootstrap-theme').attr('href', style)
    })
})

$.ready(function () {
    var blue = getComputedStyle(document.documentElement)
    .getPropertyValue('--blue');

    console.log({blue})
})