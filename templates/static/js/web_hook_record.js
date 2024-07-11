function loadWebhookManagement() {
    $('#content-container').html(`
        <div class="ui container">
            <h2>Webhook管理</h2>
            <div class="ui segment">
                <h3>触发记录列表</h3>
                <table class="ui celled table">
                    <thead>
                        <tr>
                            <th>Hook URL</th>
                            <th>事件类型</th>
                            <th>分支</th>
                            <th>状态</th>
                            <th>触发时间</th>
                            <th>响应内容</th>
                        </tr>
                    </thead>
                    <tbody id="webhook-trigger-list">
                        <!-- 触发记录数据将通过AJAX加载 -->
                    </tbody>
                </table>
                <button class="ui button" id="refresh-button">刷新</button>
            </div>
        </div>
    `);

    loadWebhookTriggerRecords();

    // 绑定刷新按钮点击事件
    $('#refresh-button').click(function () {
        loadWebhookTriggerRecords();
    });
}

function loadWebhookTriggerRecords() {
    $.get('/api/webhook-trigger-records/', function (response) {
        if (response.success) {
            var records = response.hooks;
            var recordList = '';
            records.forEach(function (record) {
                recordList += `
                    <tr>
                        <td>${record.hook_url}</td>
                        <td>${record.event}</td>
                        <td>${record.branch}</td>
                        <td>${record.status}</td>
                        <td>${record.trigger_time}</td>
                        <td>${record.response_content}</td>
                    </tr>
                `;
            });
            $('#webhook-trigger-list').html(recordList);
        } else {
            alert('加载触发记录列表失败: ' + response.message);
        }
    }).fail(function (xhr, status, error) {
        alert('请求失败: ' + error);
    });
}

loadWebhookManagement();
