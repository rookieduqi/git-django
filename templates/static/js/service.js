function loadServiceOperations() {
    const serviceOperationsHTML = `
        <div class="ui segment">
            <h2>服务操作</h2>
            <p>服务状态：<span id="service-status">未知</span></p>
            <p>端口号：<span id="service-port">8000</span></p>
            <button class="ui button" id="start-service-button">启动服务</button>
            <button class="ui button" id="stop-service-button">停止服务</button>
            <button class="ui button" id="refresh-service-status-button">刷新服务状态</button>
        </div>
    `;

    $('#content-container').html(serviceOperationsHTML);

    $('#start-service-button').click(function () {
        // Add logic to start service
        alert('Service started!');
        $('#service-status').text('运行中');
    });

    $('#stop-service-button').click(function () {
        // Add logic to stop service
        alert('Service stopped!');
        $('#service-status').text('已停止');
    });

    $('#refresh-service-status-button').click(function () {
        // Add logic to refresh service status
        alert('Service status refreshed!');
        $('#service-status').text('未知');
    });
}
