// static/js/service.js

function loadServiceOperations() {
    $('#content-container').html(`
        <div class="ui container">
            <h2>服务操作</h2>
            <div class="ui segment">
                <h3>服务状态: <span id="service-status">未知</span></h3>
                <h4>端口号: <span id="service-port">8000</span></h4>
                <button class="ui primary button" id="start-service">启动服务</button>
                <button class="ui primary button" id="stop-service">停止服务</button>
                <button class="ui primary button" id="refresh-service-status">刷新状态</button>
            </div>
        </div>
    `);

    function refreshServiceStatus() {
        $.ajax({
            url: '/serviceops/refresh/',
            method: 'GET',
            success: function (response) {
                console.log(response);
                $('#service-status').text(response.service_status);
                $('#service-port').text(response.port);
            },
            error: function () {
                alert('刷新服务状态失败');
            }
        });
    }

    $('#start-service').click(function () {
        $.ajax({
            url: '/serviceops/start/',
            method: 'POST',
            success: function (response) {
                alert(response.message);
                refreshServiceStatus();
            },
            error: function () {
                alert('启动服务失败');
            }
        });
    });

    $('#stop-service').click(function () {
        $.ajax({
            url: '/serviceops/stop/',
            method: 'POST',
            success: function (response) {
                alert(response.message);
                refreshServiceStatus();
            },
            error: function () {
                alert('停止服务失败');
            }
        });
    });

    $('#refresh-service-status').click(function () {
        refreshServiceStatus();
    });

    // 初始加载时刷新服务状态
    refreshServiceStatus();
}
