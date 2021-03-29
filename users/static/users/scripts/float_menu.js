$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('collapsed');
        const CSRFToken = Cookies.get('csrftoken')
        const request = new Request(
        '/users/preferences/menu-expansion/',
        {headers: {'X-CSRFToken': CSRFToken}}
        );
        fetch(request, {
            method: 'POST',
            mode: 'same-origin',
        }).then(function(response) {console.log(response)})
    });
});
