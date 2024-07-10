function loadImportRepository() {
    $('#content-container').html(`
        <div class="ui container">
            <h2>导入仓库</h2>
            <div class="ui segment">
                <form id="import-repo-form" class="ui form">
                    <div class="field">
                        <label>URL地址</label>
                        <input type="url" name="url" placeholder="仓库URL" required>
                    </div>
                    <div class="field">
                        <label>是否认证</label>
                        <div class="ui toggle checkbox">
                            <input type="checkbox" name="authenticated" id="authenticated-checkbox">
                            <label>是</label>
                        </div>
                    </div>
                    <div class="field">
                        <label>用户名</label>
                        <input type="text" name="username" id="username" placeholder="用户名">
                    </div>
                    <div class="field">
                        <label>用户密码</label>
                        <input type="password" name="password" id="password" placeholder="用户密码">
                    </div>
                    <div class="field">
                        <label>备注</label>
                        <input type="text" name="remark" placeholder="备注">
                    </div>
                    <button type="button" class="ui button" id="import-repo-submit">导入仓库</button>
                </form>
            </div>
        </div>
    `);

    // 初始化UI组件
    $('.ui.checkbox').checkbox();

    // 绑定提交按钮事件
    $('#import-repo-submit').click(function () {
        var authenticated = $('#authenticated-checkbox').is(':checked');
        var username = $('#username').val().trim();
        var password = $('#password').val().trim();

        if (authenticated && (!username || !password)) {
            alert('请填写用户名和密码');
            return;
        }

        var formData = getFormData('#import-repo-form');
        formData.authenticated = authenticated; // 添加是否认证的值

        $.ajax({
            url: '/api/import-repository/',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function (response) {
                if (response.success) {
                    alert('仓库导入成功');
                    $('#import-repo-form')[0].reset(); // 清空输入框
                    $('.ui.checkbox').checkbox('uncheck'); // 取消选中复选框
                } else {
                    alert('仓库导入失败: ' + response.message);
                }
            },
            error: function (xhr, status, error) {
                alert('请求失败: ' + error);
            }
        });
    });
}

function getFormData(formSelector) {
    var unindexed_array = $(formSelector).serializeArray();
    var indexed_array = {};

    $.map(unindexed_array, function (n, i) {
        indexed_array[n['name']] = n['value'];
    });

    return indexed_array;
}

loadImportRepository();
