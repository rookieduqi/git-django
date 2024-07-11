function loadHookManagement() {
    $('#content-container').html(`
        <div class="ui container">
            <h2>Hook管理
                <button class="ui button" id="add-hook-button" style="margin-left: 20px;">新增Hook</button>
            </h2>
            <div class="ui segment">
                <h3>Hook列表</h3>
                <table class="ui celled table">
                    <thead>
                        <tr>
                            <th>仓库组</th>
                            <th>仓库名</th>
                            <th>分支名</th>
                            <th>Hook URL</th>
                            <th>备注</th>
                            <th>触发事件</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="hook-list">
                        <!-- Hook 数据将通过AJAX加载 -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Modals -->
        <div class="ui modal" id="add-hook-modal">
            <div class="header">新增Hook</div>
            <div class="content">
                <form id="add-hook-form" method="post" class="ui form">
                    <div class="field">
                        <label>仓库组</label>
                        <input type="text" name="repository_group_name" placeholder="仓库组名">
                    </div>
                    <div class="field">
                        <label>仓库</label>
                        <input type="text" name="repository_name" placeholder="仓库名">
                    </div>
                    <div class="field">
                        <label>分支名</label>
                        <input type="text" name="branch_name" placeholder="分支名">
                    </div>
                    <div class="field">
                        <label>Hook URL</label>
                        <input type="url" name="hook_url" placeholder="Hook URL">
                    </div>
                    <div class="field">
                        <label>备注</label>
                        <input type="text" name="remark" placeholder="备注">
                    </div>
                    <div class="field">
                        <label>触发事件</label>
                        <select name="trigger_event">
                            <option value="push">Push</option>
                            <option value="pull">Pull Request</option>
                        </select>
                    </div>
                </form>
                <button type="button" class="ui button" id="add-hook-submit">提交</button>
                <button type="button" class="ui button" id="add-hook-cancel">取消</button>
            </div>
        </div>

        <div class="ui modal" id="edit-hook-modal">
            <div class="header">编辑Hook</div>
            <div class="content">
                <form id="edit-hook-form" method="post" class="ui form">
                    <div class="field">
                        <label>仓库组</label>
                        <input type="text" name="repository_group_name" id="edit-repo-group-input" readonly>
                    </div>
                    <div class="field">
                        <label>仓库</label>
                        <input type="text" name="repository_name" id="edit-repo-input" readonly>
                    </div>
                    <div class="field">
                        <label>分支名</label>
                        <input type="text" name="branch_name" id="edit-branch-input" readonly>
                    </div>
                    <div class="field">
                        <label>Hook URL</label>
                        <input type="url" name="hook_url" placeholder="Hook URL">
                    </div>
                    <div class="field">
                        <label>备注</label>
                        <input type="text" name="remark" placeholder="备注">
                    </div>
                    <div class="field">
                        <label>触发事件</label>
                        <select name="trigger_event">
                            <option value="push">Push</option>
                            <option value="pull">Pull Request</option>
                        </select>
                    </div>
                </form>
                <button type="button" class="ui button" id="edit-hook-submit">提交</button>
                <button type="button" class="ui button" id="edit-hook-cancel">取消</button>
            </div>
        </div>
    `);

    // 绑定新增Hook按钮点击事件
    $('#add-hook-button').click(function () {
        $('#add-hook-modal').modal('show');
    });

    // 绑定新增Hook提交按钮点击事件
    $('#add-hook-submit').click(function () {
        var formData = getFormData('#add-hook-form');
        $.ajax({
            url: '/api/hooks/',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function (response) {
                if (response.success) {
                    $('#add-hook-modal').modal('hide').remove();
                    loadHookManagement();
                } else {
                    alert('新增Hook失败: ' + response.message);
                }
            },
            error: function (xhr, status, error) {
                alert('请求失败: ' + error);
            }
        });
    });

    // 绑定新增Hook取消按钮点击事件
    $('#add-hook-cancel').click(function () {
        $('#add-hook-modal').modal('hide').remove();
    });

    // 绑定编辑Hook取消按钮点击事件
    $('#edit-hook-cancel').click(function () {
        $('#edit-hook-modal').modal('hide').remove();
    });

    // 加载Hook列表
    $.get('/api/hooks/', function (response) {
        if (response.success) {
            var hooks = response.hooks;
            var hookList = '';
            hooks.forEach(function (hook) {
                hookList += `
                    <tr>
                        <td>${hook.repository_group_name}</td>
                        <td>${hook.repository_name}</td>
                        <td>${hook.branch_name}</td>
                        <td>${hook.hook_url}</td>
                        <td>${hook.remark}</td>
                        <td>${hook.trigger_event}</td>
                        <td>
                            <button class="ui button edit-button" data-id="${hook.id}">编辑</button>
                            <button class="ui button delete-button" data-id="${hook.id}">删除</button>
                            <button class="ui button test-button" data-id="${hook.id}">测试Hook</button>
                        </td>
                    </tr>
                `;
            });
            $('#hook-list').html(hookList);

            // 绑定编辑按钮事件
            $('.edit-button').click(function () {
                var hookId = $(this).data('id');
                $.get('/api/hooks/' + hookId + '/', function (response) {
                    if (response.success) {
                        var hook = response.hook;
                        $('#edit-repo-group-input').val(hook.repository_group_name);
                        $('#edit-repo-input').val(hook.repository_name);
                        $('#edit-branch-input').val(hook.branch_name);
                        $('#edit-hook-form input[name="hook_url"]').val(hook.hook_url);
                        $('#edit-hook-form input[name="remark"]').val(hook.remark);
                        $('#edit-hook-form select[name="trigger_event"]').val(hook.trigger_event);
                        $('#edit-hook-modal').modal('show');
                    } else {
                        alert('加载Hook信息失败: ' + response.message);
                    }
                });

                // 绑定编辑Hook提交按钮点击事件
                $('#edit-hook-submit').click(function () {
                    var formData = getFormData('#edit-hook-form');
                    $.ajax({
                        url: '/api/hooks/' + hookId + '/',
                        type: 'PUT',
                        data: JSON.stringify(formData),
                        contentType: 'application/json',
                        success: function (response) {
                            if (response.success) {
                                $('#edit-hook-modal').modal('hide').remove();
                                loadHookManagement();
                            } else {
                                alert('编辑Hook失败: ' + response.message);
                            }
                        },
                        error: function (xhr, status, error) {
                            alert('请求失败: ' + error);
                        }
                    });
                });
            });

            // 绑定删除按钮事件
            $('.delete-button').click(function () {
                var hookId = $(this).data('id');
                if (confirm('确认删除该Hook吗？')) {
                    $.ajax({
                        url: '/api/hooks/' + hookId + '/',
                        type: 'DELETE',
                        success: function (response) {
                            if (response.success) {
                                loadHookManagement();
                            } else {
                                alert('删除Hook失败: ' + response.message);
                            }
                        },
                        error: function (xhr, status, error) {
                            alert('请求失败: ' + error);
                        }
                    });
                }
            });

            // 绑定测试按钮事件
            $('.test-button').click(function () {
                var hookId = $(this).data('id');
                $.post('/api/hooks/' + hookId + '/test_hook/', function (response) {
                    if (response.success) {
                        alert('Hook测试成功: ' + response.message);
                    } else {
                        alert('Hook测试失败: ' + response.message);
                    }
                }).fail(function (xhr, status, error) {
                    alert('请求失败: ' + error);
                });
            });
        } else {
            alert('加载Hook列表失败: ' + response.message);
        }
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

loadHookManagement();
