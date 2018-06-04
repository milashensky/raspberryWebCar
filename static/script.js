window.addEventListener("load", function() {
    var sendPosition = function (data) {
        console.log(data);
        var xhr = new XMLHttpRequest();
        xhr.open("POST", '/control/', true);
        xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
        // xhr.onreadystatechange = function() {//Вызывает функцию при смене состояния.
        //     console.log('sended');
        //     if(xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
        //         console.log('done!');
        //     }
        // }
        xhr.send(JSON.stringify(data));
    }
    var last_speed = last_ang = 0,
        speedT = 0.3,
        angT = 5;
    var timerId = '';
    var dynamic = nipplejs.create({
            zone: document.getElementById('controller'),
            color: 'blue',
    });
    let getSpeed = (x)=>(x > 3? 3: Math.round(x*100)/100);
    dynamic.on('start end', function(evt, data) {
        if (evt.type == 'end') {
            sendPosition({left: 0, right: 0, speed: 0});
            console.log('se', evt.type);
        }
    }).on('move', function(evt, data) {
        if (data && data.direction){
            // console.log('move', data);
            ang = -1 * (Math.abs(data.angle.degree) - 180) / 2;
            speed = getSpeed(data.force);
            if(Math.abs(last_speed - speed) > speedT || Math.abs(last_ang - ang) > angT){
                last_speed = speed;
                last_ang = ang;
                direction = (Math.abs(data.angle.degree) < 180)
                // console.log('speed: ' + speed + '; ang: '+ ang);
                clearTimeout(timerId);
                timerId = setTimeout(function() {
                    sendPosition({
                        left: Math.round(Math.sin(ang*3.14/180) * 100)/100,
                        right: Math.round(Math.cos(ang*3.14/180) * 100)/100,
                        speed: speed,
                        direction: direction,
                    })
                }, 100);
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
