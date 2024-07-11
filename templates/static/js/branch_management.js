// static/js/branch_management.js

function loadBranchManagement() {
    $('#content-container').html(`
        <div class="ui container">
            <h2>分支管理
                <button class="ui button" id="add-branch-button" style="margin-left: 20px;">新增分支</button>
            </h2>
            <div class="ui segment">
                <h3>分支列表</h3>
                <table class="ui celled table">
                    <thead>
                        <tr>
                            <th>分支名</th>
                            <th>同步分支</th>
                            <th>备注</th>
                            <th>所属仓库</th>
                            <th>所属仓库组</th>
                            <th>创建时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="branch-list">
                        <!-- 分支数据将通过AJAX加载 -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Modals -->
        <div class="ui modal" id="add-branch-modal">
            <div class="header">新增分支</div>
            <div class="content">
                <form id="add-branch-form" method="post" class="ui form">
                    <div class="field">
                        <label>分支名</label>
                        <input type="text" name="name" placeholder="分支名">
                    </div>
                    <div class="field">
                        <label>同步分支</label>
                        <input type="text" name="sync_branch" placeholder="同步分支">
                    </div>
                    <div class="field">
                        <label>备注</label>
                        <input type="text" name="remark" placeholder="备注">
                    </div>
                    <div class="field">
                        <label>所属仓库</label>
                        <input type="text" name="repository_name" placeholder="所属仓库">
                    </div>
                    <div class="field">
                        <label>所属仓库组</label>
                        <input type="text" name="repository_group_name" placeholder="所属仓库组">
                    </div>
                </form>
                <button type="button" class="ui button" id="add-branch-submit">提交</button>
                <button type="button" class="ui button" id="add-branch-cancel">取消</button>
            </div>
        </div>

        <div class="ui modal" id="edit-branch-modal">
            <div class="header">编辑分支</div>
            <div class="content">
                <form id="edit-branch-form" method="post" class="ui form">
                    <div class="field">
                        <label>分支名</label>
                        <input type="text" name="name" placeholder="分支名">
                    </div>
                    <div class="field">
                        <label>同步分支</label>
                        <input type="text" name="sync_branch" placeholder="同步分支">
                    </div>
                    <div class="field">
                        <label>备注</label>
                        <input type="text" name="remark" placeholder="备注">
                    </div>
                    <div class="field">
                        <label>所属仓库</label>
                        <input type="text" name="repository_name" placeholder="所属仓库" readonly>
                    </div>
                    <div class="field">
                        <label>所属仓库组</label>
                        <input type="text" name="repository_group_name" placeholder="所属仓库组" readonly>
                    </div>
                </form>
                <button type="button" class="ui button" id="edit-branch-submit">提交</button>
                <button type="button" class="ui button" id="edit-branch-cancel">取消</button>
            </div>
        </div>
    `);

    // 绑定新增分支按钮点击事件
    $('#add-branch-button').click(function () {
        $('#add-branch-modal').modal('show');
    });

    // 绑定新增分支提交按钮点击事件
    $('#add-branch-submit').click(function () {
        var formData = getFormData('#add-branch-form');
        $.ajax({
            url: '/api/branches/',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function (response) {
                if (response.success) {
                    $('#add-branch-modal').modal('hide').remove();
                    loadBranchManagement();
                } else {
                    alert('新增分支失败: ' + response.message);
                }
            },
            error: function (xhr, status, error) {
                alert('请求失败: ' + error);
            }
        });
    });

    // 绑定新增分支取消按钮点击事件
    $('#add-branch-cancel').click(function () {
        $('#add-branch-modal').modal('hide').remove();
    });

    // 绑定编辑分支取消按钮点击事件
    $('#edit-branch-cancel').click(function () {
        $('#edit-branch-modal').modal('hide').remove();
    });

    // 加载分支列表
    $.get('/api/branches/', function (response) {
        if (response.success) {
            var branches = response.branches;
            var branchList = '';
            branches.forEach(function (branch) {
                branchList += `
                    <tr>
                        <td>${branch.name}</td>
                        <td>${branch.sync_branch}</td>
                        <td>${branch.remark}</td>
                        <td>${branch.repository_name}</td>
                        <td>${branch.repository_group_name}</td>
                        <td>${branch.created_at}</td>
                        <td>
                            <button class="ui button edit-button" data-id="${branch.id}">编辑</button>
                            <button class="ui button delete-button" data-id="${branch.id}">删除</button>
                            <button class="ui button view-members-button" data-id="${branch.id}">查看成员</button>
                        </td>
                    </tr>
                `;
            });
            $('#branch-list').html(branchList);

            // 绑定编辑按钮事件
            $('.edit-button').click(function () {
                var branchId = $(this).data('id');
                $.get('/api/branches/' + branchId + '/', function (response) {
                    if (response.success) {
                        var branch = response.branch;
                        $('#edit-branch-form input[name="name"]').val(branch.name);
                        $('#edit-branch-form input[name="sync_branch"]').val(branch.sync_branch);
                        $('#edit-branch-form input[name="remark"]').val(branch.remark);
                        $('#edit-branch-form input[name="repository_name"]').val(branch.repository_name);
                        $('#edit-branch-form input[name="repository_group_name"]').val(branch.repository_group_name);
                        $('#edit-branch-modal').modal('show');
                        bindEditBranchFormEvents(branchId);
                    } else {
                        alert('加载分支信息失败: ' + response.message);
                    }
                });

                // 绑定编辑分支提交按钮点击事件
                $('#edit-branch-submit').click(function () {
                    var formData = getFormData('#edit-branch-form');
                    $.ajax({
                        url: '/api/branches/' + branchId + '/',
                        type: 'PUT',
                        data: JSON.stringify(formData),
                        contentType: 'application/json',
                        success: function (response) {
                            if (response.success) {
                                $('#edit-branch-modal').modal('hide').remove();
                                loadBranchManagement();
                            } else {
                                alert('编辑分支失败: ' + response.message);
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
                var branchId = $(this).data('id');
                if (confirm('确认删除该分支吗？')) {
                    $.ajax({
                        url: '/api/branches/' + branchId + '/',
                        type: 'DELETE',
                        success: function (response) {
                            if (response.success) {
                                loadBranchManagement();
                            } else {
                                alert('删除分支失败: ' + response.message);
                            }
                        },
                        error: function (xhr, status, error) {
                            alert('请求失败: ' + error);
                        }
                    });
                }
            });

            // 绑定查看成员按钮事件
            $('.view-members-button').click(function () {
                var branchId = $(this).data('id');
                loadBranchMembers(branchId);
            });
        } else {
            alert('加载分支列表失败: ' + response.message);
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

function loadBranchMembers(branchId) {
    $('#content-container').html(`
        <div class="ui container">
            <h2>分支成员管理
                <button class="ui button" id="add-member-button" style="margin-left: 20px;">添加成员</button>
                <button class="ui button" id="back-to-branches" style="margin-left: 20px;">返回分支管理</button>
            </h2>
            <div class="ui segment">
                <h3>成员列表</h3>
                <table class="ui celled table">
                    <thead>
                        <tr>
                            <th>用户名</th>
                            <th>角色</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="member-list">
                        <!-- 成员数据将通过AJAX加载 -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Modals -->
        <div class="ui modal" id="add-member-modal">
            <div class="header">添加成员</div>
            <div class="content">
                <form id="add-member-form" method="post" class="ui form">
                    <div class="field">
                        <label>用户名</label>
                        <select name="username">
                            <!-- 用户选项将通过AJAX加载 -->
                        </select>
                    </div>
                    <div class="field">
                        <label>角色</label>
                        <select name="role_id">
                            <!-- 角色选项将通过AJAX加载 -->
                        </select>
                    </div>
                </form>
                <button type="button" class="ui button" id="add-member-submit">提交</button>
                <button type="button" class="ui button" id="add-member-cancel">取消</button>
            </div>
        </div>
    `);

    // 绑定返回分支管理按钮点击事件
    $('#back-to-branches').click(function () {
        loadBranchManagement();
    });

    // 绑定添加成员按钮点击事件
    $('#add-member-button').click(function () {
        loadUsers();
        loadRoles();
        $('#add-member-modal').modal('show');
    });

    // 绑定添加成员提交按钮点击事件
    $('#add-member-submit').click(function () {
        var formData = getFormData('#add-member-form');
        $.ajax({
            url: `/api/branches/${branchId}/members/`,
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function (response) {
                if (response.success) {
                    $('#add-member-modal').modal('hide').remove();
                    loadBranchMembers(branchId);
                } else {
                    alert('添加成员失败: ' + response.errors);
                }
            },
            error: function (xhr, status, error) {
                alert('请求失败: ' + error);
            }
        });
    });

    // 绑定添加成员取消按钮点击事件
    $('#add-member-cancel').click(function () {
        $('#add-member-modal').modal('hide').remove();
    });

    // 加载成员列表
    $.get(`/api/branches/${branchId}/members/`, function (response) {
        if (response.success) {
            var members = response.members;
            var memberList = '';
            members.forEach(function (member) {
                memberList += `
                    <tr>
                        <td>${member.username}</td>
                        <td>${member.role_name}</td>
                        <td>
                            <button class="ui button remove-button" data-id="${member.id}">移除</button>
                        </td>
                    </tr>
                `;
            });
            $('#member-list').html(memberList);

            // 绑定移除按钮事件
            $('.remove-button').click(function () {
                var memberId = $(this).data('id');
                if (confirm('确认移除该成员吗？')) {
                    $.ajax({
                        url: `/api/branches/${branchId}/members/remove/${memberId}/`,
                        type: 'DELETE',
                        success: function (response) {
                            if (response.success) {
                                loadBranchMembers(branchId);
                            } else {
                                alert('移除成员失败: ' + response.message);
                            }
                        },
                        error: function (xhr, status, error) {
                            alert('请求失败: ' + error);
                        }
                    });
                }
            });
        } else {
            alert('加载成员列表失败: ' + response.message);
        }
    });
}

loadBranchManagement();
