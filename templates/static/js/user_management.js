function loadUserManagement() {
    $('#content-container').html(`
        <div class="ui container">
            <h2>用户管理
                <button class="ui button" id="add-user-button" style="margin-left: 20px;">新增用户</button>
            </h2>
            <div class="ui segment">
                <h3>用户列表</h3>
                <table class="ui celled table">
                    <thead>
                        <tr>
                            <th>用户名</th>
                            <th>备注</th>
                            <th>创建时间</th>
                            <th>状态</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="user-list">
                        <!-- 用户数据将通过AJAX加载 -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Add User Modal -->
        <div class="ui modal" id="add-user-modal">
            <div class="header">新增用户</div>
            <div class="content">
                <form id="add-user-form" method="post" class="ui form">
                    <div class="field">
                        <label>用户名</label>
                        <input type="text" name="username" placeholder="用户名">
                    </div>
                    <div class="field">
                        <label>密码</label>
                        <input type="password" name="password" placeholder="密码">
                    </div>
                    <div class="field">
                        <label>备注</label>
                        <input type="text" name="remark" placeholder="备注">
                    </div>
                </form>
                <button type="button" class="ui button" id="add-user-submit">提交</button>
                <button type="button" class="ui button" id="add-user-cancel">取消</button>
            </div>
        </div>

        <!-- Edit User Modal -->
        <div class="ui modal" id="edit-user-modal">
            <div class="header">编辑用户</div>
            <div class="content">
                <form id="edit-user-form" method="post" class="ui form">
                    <input type="hidden" name="user_id" id="edit-user-id">
                    <div class="field">
                        <label>备注</label>
                        <input type="text" name="remark" id="edit-user-remark" placeholder="备注">
                    </div>
                    <div class="field">
                        <label>状态</label>
                        <select name="is_disabled" id="edit-user-status">
                            <option value="false">正常</option>
                            <option value="true">禁用</option>
                        </select>
                    </div>
                </form>
                <button type="button" class="ui button" id="edit-user-submit">提交</button>
                <button type="button" class="ui button" id="edit-user-cancel">取消</button>
            </div>
        </div>

        <!-- Reset Password Modal -->
        <div class="ui modal" id="reset-password-modal">
            <div class="header">重置密码</div>
            <div class="content">
                <form id="reset-password-form" method="post" class="ui form">
                    <input type="hidden" name="user_id" id="reset-password-user-id">
                    <div class="field">
                        <label>新密码</label>
                        <input type="password" name="new_password" placeholder="新密码">
                    </div>
                </form>
                <button type="button" class="ui button" id="reset-password-submit">提交</button>
                <button type="button" class="ui button" id="reset-password-cancel">取消</button>
            </div>
        </div>
    `);

    // 绑定新增用户按钮点击事件
    $('#add-user-button').click(function () {
        $('#add-user-form')[0].reset();
        $('#add-user-modal').modal('show');
    });

    // 绑定新增用户提交按钮点击事件
    $('#add-user-submit').click(function () {
        var formData = $('#add-user-form').serialize();
        $.post('/user/add/', formData, function (response) {
            if (response.success) {
                $('#add-user-modal').modal('hide');
                $('#add-user-form')[0].reset();
                loadUserManagement();
            } else {
                alert('新增用户失败: ' + response.message);
            }
        });
    });

    // 绑定新增用户取消按钮点击事件
    $('#add-user-cancel').click(function () {
        $('#add-user-modal').modal('hide');
    });

    // 绑定编辑用户提交按钮点击事件
    $('#edit-user-submit').click(function () {
        var formData = $('#edit-user-form').serialize();
        var userId = $('#edit-user-id').val();
        $.post('/user/edit/' + userId + '/', formData, function (response) {
            if (response.success) {
                $('#edit-user-modal').modal('hide');
                $('#edit-user-form')[0].reset();
                loadUserManagement();
            } else {
                alert('编辑用户失败: ' + response.message);
            }
        });
    });

    // 绑定编辑用户取消按钮点击事件
    $('#edit-user-cancel').click(function () {
        $('#edit-user-modal').modal('hide');
    });

    // 绑定重置密码提交按钮点击事件
    $('#reset-password-submit').click(function () {
        var formData = $('#reset-password-form').serialize();
        var userId = $('#reset-password-user-id').val();
        $.post('/user/reset_password/' + userId + '/', formData, function (response) {
            if (response.success) {
                $('#reset-password-modal').modal('hide');
                $('#reset-password-form')[0].reset();
                loadUserManagement();
            } else {
                alert('重置密码失败: ' + response.message);
            }
        });
    });

    // 绑定重置密码取消按钮点击事件
    $('#reset-password-cancel').click(function () {
        $('#reset-password-modal').modal('hide');
    });

    // 加载用户列表
    $.get('/user/list/', function (response) {
        if (response.success) {
            var users = response.users;
            var userList = '';
            users.forEach(function (user) {
                userList += `
                    <tr>
                        <td>${user.username}</td>
                        <td>${user.remark}</td>
                        <td>${user.created_at}</td>
                        <td>${user.is_disabled ? '禁用' : '正常'}</td>
                        <td>
                            <button class="ui button" onclick="editUser(${user.id}, '${user.remark}', ${user.is_disabled})">编辑</button>
                            <button class="ui button" onclick="resetPassword(${user.id})">重置密码</button>
                            <button class="ui button" onclick="deleteUser(${user.id})">删除</button>
                        </td>
                    </tr>
                `;
            });
            $('#user-list').html(userList);
        } else {
            alert('加载用户列表失败: ' + response.message);
        }
    });
}

function editUser(user_id, remark, is_disabled) {
    $('#edit-user-id').val(user_id);
    $('#edit-user-remark').val(remark);
    $('#edit-user-status').val(is_disabled.toString());
    $('#edit-user-modal').modal('show');
}

function resetPassword(user_id) {
    $('#reset-password-user-id').val(user_id);
    $('#reset-password-modal').modal('show');
}

function deleteUser(user_id) {
    if (confirm('确定要删除该用户吗？')) {
        $.post('/user/delete/' + user_id + '/', function (response) {
            if (response.success) {
                loadUserManagement();
            } else {
                alert('删除用户失败: ' + response.message);
            }
        });
    }
}
