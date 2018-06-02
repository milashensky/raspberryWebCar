window.addEventListener("load", function() {
    var sendPosition = function (position) {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", '/control/', true);
        xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
        // xhr.onreadystatechange = function() {//Вызывает функцию при смене состояния.
        //     console.log('sended');
        //     if(xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
        //         console.log('done!');
        //     }
        // }
        xhr.send(JSON.stringify({ direction: position }));
    }
    var last = '';
    var dynamic = nipplejs.create({
        zone: document.getElementById('controller'),
        color: 'blue'
    });
    dynamic.on('start end', function(evt, data) {
        if (evt.type == 'end') {
            sendPosition(' ');
            console.log('se', evt.type);
        }
    }).on('move', function(evt, data) {
        if (data && data.direction){
            if(last != data.direction.angle){
                console.log('move', data);
                sendPosition(data.direction.angle)
            }
            last = data.direction.angle;
        }
    })
    // .on('dir:up plain:up dir:left plain:left dir:down ' +
    //     'plain:down dir:right plain:right',
    //     function(evt, data) {
    //         console.log('dir', data);
    //     }
    // ).on('pressure', function(evt, data) {
    //     console.log('press', data);
    // });




});
