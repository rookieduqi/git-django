function loadRepositoryGroupManagement() {
    $('#content-container').html(`
        <div class="ui container">
            <h2>仓库组管理
                <button class="ui button" id="add-group-button" style="margin-left: 20px;">新增仓库组</button>
            </h2>
            <div class="ui segment">
                <h3>仓库组列表</h3>
                <table class="ui celled table">
                    <thead>
                        <tr>
                            <th>组名</th>
                            <th>备注</th>
                            <th>创建时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="group-list">
                        <!-- 仓库组数据将通过AJAX加载 -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Modals -->
        <div class="ui modal" id="add-group-modal">
            <div class="header">新增仓库组</div>
            <div class="content">
                <form id="add-group-form" method="post" class="ui form">
                    <div class="field">
                        <label>组名</label>
                        <input type="text" name="name" placeholder="组名">
                    </div>
                    <div class="field">
                        <label>备注</label>
                        <input type="text" name="remark" placeholder="备注">
                    </div>
                </form>
                <button type="button" class="ui button" id="add-group-submit">提交</button>
                <button type="button" class="ui button" id="add-group-cancel">取消</button>
            </div>
        </div>
        
        <!-- Edit Group Modal -->
        <div class="ui modal" id="edit-group-modal">
            <div class="header">编辑仓库组</div>
            <div class="content">
                <form id="edit-group-form" method="post" class="ui form">
                    <div class="field">
                        <label>组名</label>
                        <input type="text" name="name" id="edit-group-name" placeholder="组名">
                    </div>
                    <div class="field">
                        <label>备注</label>
                        <input type="text" name="remark" id="edit-group-remark" placeholder="备注">
                    </div>
                </form>
                <button type="button" class="ui button" id="edit-group-submit">提交</button>
                <button type="button" class="ui button" id="edit-group-cancel">取消</button>
            </div>
        </div>
    `);

    $('#add-group-button').click(function () {
        $('#add-group-modal').modal('show');
    });

    $('#add-group-submit').click(function () {
        var formData = $('#add-group-form').serializeArray();
        var data = {};
        $(formData).each(function (index, obj) {
            data[obj.name] = obj.value;
        });
        $.ajax({
            url: '/api/repository_groups/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (response) {
                if (response.success) {
                    $('#add-group-modal').modal('hide').remove();
                    loadRepositoryGroupManagement();
                } else {
                    alert('新增仓库组失败: ' + response.message);
                }
            },
            error: function (xhr, status, error) {
                alert('新增仓库组失败: ' + xhr.responseText);
            }
        });
    });


    $('#add-group-cancel').click(function () {
        $('#add-group-modal').modal('hide').remove();
    });

    $.get('/api/repository_groups/', function (response) {
        var groups = response.groups;
        var groupList = '';
        groups.forEach(function (group) {
            groupList += `
                <tr>
                    <td>${group.name}</td>
                    <td>${group.remark}</td>
                    <td>${group.created_at}</td>
                    <td>
                        <button class="ui button edit-button" data-id="${group.id}">编辑</button>
                        <button class="ui button delete-button" data-id="${group.id}">删除</button>
                        <button class="ui button view-members-button" data-id="${group.id}">查看成员</button>
                    </td>
                </tr>
            `;
        });
        $('#group-list').html(groupList);

        // 绑定编辑按钮点击事件
        $('.edit-button').click(function () {
            var groupId = $(this).data('id');
            $.get(`/api/repository_groups/${groupId}/`, function (response) {
                console.log(response)
                if (response.success) {
                    $('#edit-group-name').val(response.group.name);
                    $('#edit-group-remark').val(response.group.remark);
                    $('#edit-group-modal').modal('show');

                    $('#edit-group-submit').click(function () {
                        var formData = {
                            name: $('#edit-group-name').val(),
                            remark: $('#edit-group-remark').val()
                        };
                        $.ajax({
                            url: `/api/repository_groups/${groupId}/`,
                            type: 'PUT',
                            contentType: 'application/json',
                            data: JSON.stringify(formData),
                            success: function (response) {
                                if (response.success) {
                                    $('#edit-group-modal').modal('hide').remove();
                                    loadRepositoryGroupManagement();
                                } else {
                                    alert('编辑仓库组失败: ' + response.message);
                                }
                            },
                            error: function (xhr, status, error) {
                                alert('编辑仓库组失败: ' + xhr.responseText);
                            }
                        });
                    });

                    $('#edit-group-cancel').click(function () {
                        $('#edit-group-modal').modal('hide').remove();
                    });
                } else {
                    alert('加载仓库组信息失败: ' + response.message);
                }
            });
        });

        $('.delete-button').click(function () {
            var groupId = $(this).data('id');
            if (confirm('确认删除该仓库组吗？')) {
                $.ajax({
                    url: '/api/repository_groups/' + groupId + '/',
                    type: 'DELETE',
                    success: function (response) {
                        if (response.success) {
                            loadRepositoryGroupManagement();
                        } else {
                            alert('删除仓库组失败: ' + response.message);
                        }
                    }
                });
            }
        });

        $('.view-members-button').click(function () {
            var groupId = $(this).data('id');
            loadGroupMembers(groupId);
        });
    });
}

function loadGroupMembers(groupId) {
    $('#content-container').html(`
        <div class="ui container">
            <h2>仓库组管理 > group${groupId}
                <button class="ui button" id="add-member-button" style="margin-left: 20px;">添加成员</button>
                <button class="ui button" id="back-to-groups" style="margin-left: 20px;">返回仓库组管理</button>
            </h2>
            <div class="ui segment">
                <h3>成员列表</h3>
                <table class="ui celled table">
                    <thead>
                        <tr>
                            <th>用户名</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="member-list">
                        <!-- 成员数据将通过AJAX加载 -->
                    </tbody>
                </table>
            </div>
        </div>

        <div class="ui modal" id="add-member-modal">
            <div class="header">添加成员</div>
            <div class="content">
                <form id="add-member-form" method="post" class="ui form">
                    <div class="field">
                        <label>用户名</label>
                        <input type="text" name="username" placeholder="用户名">
                    </div>
                    <input type="hidden" name="group" value="${groupId}">
                </form>
                <button type="button" class="ui button" id="add-member-submit">提交</button>
                <button type="button" class="ui button" id="add-member-cancel">取消</button>
            </div>
        </div>
    `);

    $('#back-to-groups').click(function () {
        loadRepositoryGroupManagement();
    });

    $('#add-member-button').click(function () {
        $('#add-member-modal').modal('show');
    });

    $('#add-member-submit').click(function () {
        var formData = $('#add-member-form').serializeArray();
        var data = {};
        $(formData).each(function (index, obj) {
            data[obj.name] = obj.value;
        });
        $.ajax({
            url: `/api/repository_groups/${groupId}/members/`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (response) {
                if (response.success) {
                    $('#add-member-modal').modal('hide').remove();
                    loadGroupMembers(groupId);
                } else {
                    alert('添加成员失败: ' + response.message);
                }
            },
            error: function (xhr, status, error) {
                alert('添加成员失败: ' + xhr.responseText);
            }
        });
    });


    $('#add-member-cancel').click(function () {
        $('#add-member-modal').modal('hide').remove();
    });

    $.get(`/api/repository_groups/${groupId}/members/`, function (response) {
        if (response.success) {
            var members = response.members;
            var memberList = '';
            members.forEach(function (member) {
                memberList += `
                    <tr>
                        <td>${member.username}</td>
                        <td>
                            <button class="ui button remove-button" data-id="${member.id}">移除</button>
                        </td>
                    </tr>
                `;
            });
            $('#member-list').html(memberList);

            $('.remove-button').click(function () {
                var memberId = $(this).data('id');
                if (confirm('确认移除该成员吗？')) {
                    $.ajax({
                        url: `/api/repository_groups/${groupId}/members/remove/${memberId}/`,
                        type: 'DELETE',
                        success: function (response) {
                            if (response.success) {
                                loadGroupMembers(groupId);
                            } else {
                                alert('移除成员失败: ' + response.message);
                            }
                        }
                    });
                }
            });
        } else {
            alert('加载成员列表失败: ' + response.message);
        }
    });
}

// 加载仓库组列表
function loadRepositoryGroups() {
    $.get('/api/repository_groups/', function (response) {
        if (response.success) {
            var groups = response.groups;
            var options = '';
            groups.forEach(function (group) {
                options += `<option value="${group.id}">${group.name}</option>`;
            });
            $('select[name="group_id"]').html(options);
        } else {
            alert('加载仓库组列表失败: ' + response.message);
        }
    });
}

// 加载仓库组详情（用于编辑）
function loadRepositoryGroupDetails(groupId) {
    $.get(`/api/repository_groups/${groupId}/`, function (response) {
        if (response.success) {
            var group = response.group;
            $('input[name="name"]').val(group.name);
            $('input[name="remark"]').val(group.remark);
            // 显示编辑表单
            $('#edit-group-modal').modal('show');
        } else {
            alert('加载仓库组信息失败: ' + response.message);
        }
    });
}