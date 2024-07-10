// static/js/repository_management.js

function loadRepositoryManagement() {
    $('#content-container').html(`
        <div class="ui container">
            <h2>仓库管理
                <button class="ui button" id="add-repo-button" style="margin-left: 20px;">新增仓库</button>
            </h2>
            <div class="ui segment">
                <h3>仓库列表</h3>
                <table class="ui celled table">
                    <thead>
                        <tr>
                            <th>仓库名</th>
                            <th>URL</th>
                            <th>备注</th>
                            <th>仓库组</th>
                            <th>创建时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="repo-list">
                        <!-- 仓库数据将通过AJAX加载 -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Modals -->
        <div class="ui modal" id="add-repo-modal">
            <div class="header">新增仓库</div>
            <div class="content">
                <form id="add-repo-form" method="post" class="ui form">
                    <div class="field">
                        <label>仓库名</label>
                        <input type="text" name="name" placeholder="仓库名">
                    </div>
                    <div class="field">
                        <label>备注</label>
                        <input type="text" name="remark" placeholder="备注">
                    </div>
                    <div class="field">
                        <label>仓库组</label>
                        <select name="group_id">
                            <!-- 仓库组选项将通过AJAX加载 -->
                        </select>
                    </div>
                    <div class="field">
                        <label>仓库链接</label>
                        <input type="text" name="url" id="repo-url" placeholder="仓库链接">
<!--                        <input type="text" name="url" id="repo-url" placeholder="仓库链接" readonly>-->
                    </div>
                </form>
                <button type="button" class="ui button" id="add-repo-submit">提交</button>
                <button type="button" class="ui button" id="add-repo-cancel">取消</button>
            </div>
        </div>

        <div class="ui modal" id="edit-repo-modal">
            <div class="header">编辑仓库</div>
            <div class="content">
                <form id="edit-repo-form" method="post" class="ui form">
                    <div class="field">
                        <label>仓库名</label>
                        <input type="text" name="name" placeholder="仓库名">
                    </div>
                    <div class="field">
                        <label>备注</label>
                        <input type="text" name="remark" placeholder="备注">
                    </div>
                    <div class="field">
                        <label>仓库组</label>
                        <select name="group_id" id="edit-repo-group" readonly>
                            <!-- 仓库组选项将通过AJAX加载 -->
                        </select>
                    </div>
                    <div class="field">
                        <label>仓库链接</label>
                        <input type="text" name="url" id="edit-repo-url" placeholder="仓库链接" readonly>
                    </div>
                </form>
                <button type="button" class="ui button" id="edit-repo-submit">提交</button>
                <button type="button" class="ui button" id="edit-repo-cancel">取消</button>
            </div>
        </div>
    `);

    // 绑定新增仓库按钮点击事件
    $('#add-repo-button').click(function () {
        loadRepositoryGroups();
        $('#add-repo-modal').modal('show');
        bindFormEvents();
    });

    // 绑定新增仓库提交按钮点击事件
    $('#add-repo-submit').click(function () {
        var formData = getFormData('#add-repo-form');
        $.ajax({
            url: '/api/repositories/',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function (response) {
                if (response.success) {
                    $('#add-repo-modal').modal('hide').remove();
                    loadRepositoryManagement();
                } else {
                    alert('新增仓库失败: ' + response.message);
                }
            },
            error: function (xhr, status, error) {
                alert('请求失败: ' + error);
            }
        });
    });

    // 绑定新增仓库取消按钮点击事件
    $('#add-repo-cancel').click(function () {
        $('#add-repo-modal').modal('hide').remove();
    });

    // 绑定编辑仓库取消按钮点击事件
    $('#edit-repo-cancel').click(function () {
        $('#edit-repo-modal').modal('hide').remove();
    });

    // 加载仓库列表
    $.get('/api/repositories/', function (response) {
        if (response.success) {
            var repos = response.repositories;
            var repoList = '';
            repos.forEach(function (repo) {
                repoList += `
                    <tr>
                        <td>${repo.name}</td>
                        <td>${repo.url}</td>
                        <td>${repo.remark}</td>
                        <td>${repo.group_name}</td>
                        <td>${repo.created_at}</td>
                        <td>
                            <button class="ui button edit-button" data-id="${repo.id}">编辑</button>
                            <button class="ui button delete-button" data-id="${repo.id}">删除</button>
                            <button class="ui button view-members-button" data-id="${repo.id}">查看成员</button>
                        </td>
                    </tr>
                `;
            });
            $('#repo-list').html(repoList);

            // 绑定编辑按钮事件
            $('.edit-button').click(function () {
                var repoId = $(this).data('id');
                loadRepositoryGroups(function () {
                    // 获取仓库信息并加载到编辑表单
                    $.get('/api/repositories/' + repoId + '/', function (response) {
                        if (response.success) {
                            var repo = response.repository;
                            $('#edit-repo-form input[name="name"]').val(repo.name);
                            $('#edit-repo-form input[name="remark"]').val(repo.remark);
                            $('#edit-repo-form select[name="group_id"]').val(repo.group_id);
                            $('#edit-repo-form input[name="url"]').val(repo.url);
                            $('#edit-repo-modal').modal('show');
                            bindEditFormEvents();
                        } else {
                            alert('加载仓库信息失败: ' + response.message);
                        }
                    });

                    // 绑定编辑仓库提交按钮点击事件
                    $('#edit-repo-submit').click(function () {
                        var formData = getFormData('#edit-repo-form');
                        $.ajax({
                            url: '/api/repositories/' + repoId + '/',
                            type: 'PUT',
                            data: JSON.stringify(formData),
                            contentType: 'application/json',
                            success: function (response) {
                                if (response.success) {
                                    $('#edit-repo-modal').modal('hide').remove();
                                    loadRepositoryManagement();
                                } else {
                                    alert('编辑仓库失败: ' + response.message);
                                }
                            },
                            error: function (xhr, status, error) {
                                alert('请求失败: ' + error);
                            }
                        });
                    });
                });
            });

            // 绑定删除按钮事件
            $('.delete-button').click(function () {
                var repoId = $(this).data('id');
                if (confirm('确认删除该仓库吗？')) {
                    $.ajax({
                        url: '/api/repositories/' + repoId + '/',
                        type: 'DELETE',
                        success: function (response) {
                            if (response.success) {
                                loadRepositoryManagement();
                            } else {
                                alert('删除仓库失败: ' + response.message);
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
                var repoId = $(this).data('id');
                loadRepositoryMembers(repoId);
            });
        } else {
            alert('加载仓库列表失败: ' + response.message);
        }
    });
}

function loadRepositoryGroups(callback) {
    $.get('/api/repository_groups/', function (response) {
        console.log("/api/repository_groups/");
        if (response.success) {
            var groups = response.groups;
            var options = '';
            groups.forEach(function (group) {
                options += `<option value="${group.id}">${group.name}</option>`;
            });
            $('select[name="group_id"]').html(options);
            if (callback) callback();
        } else {
            alert('加载仓库组列表失败: ' + response.message);
        }
    });
}


function bindFormEvents() {
    $('input[name="name"], select[name="group_id"]').on('change', generateRepositoryUrl);
}

function generateRepositoryUrl() {
    $.get('/api/get_server_ip/', function (response) {
        if (response.success) {
            var serverIp = response.ip;
            // var groupName = $('select[name="group_id"] option:selected').text().trim();
            var groupName = $('#add-repo-form select[name="group_id"] option:selected').text();
            var repoName = $('#add-repo-form input[name="name"]').val();
            var repoUrl = `http://${serverIp}/git/${groupName}/${repoName}.git`;
            console.log("groupName:", groupName);
            console.log("repoName:", repoName);
            $('#repo-url').val(repoUrl);
        } else {
            alert('获取服务器IP失败: ' + response.message);
        }
    });
}


function bindEditFormEvents() {
    $('input[name="name"], select[name="group_id"]').on('change', function () {
        var serverIp = $('#edit-repo-url').val().split('/')[2];
        var groupName = $('#edit-repo-form select[name="group_id"] option:selected').text();
        var repoName = $('#edit-repo-form input[name="name"]').val();
        console.log("groupName:", groupName);
        console.log("repoName:", repoName);
        // var groupName = $('select[name="group_id"] option:selected').text();
        // var repoName = $('input[name="name"]').val().trim().replace(/\s+/g, '-');
        var repoUrl = `http://${serverIp}/git/${groupName}/${repoName}.git`;
        $('#edit-repo-url').val(repoUrl);
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

function loadUsers() {
    $.get('/api/users/list_usernames/', function (response) {
        if (response.success) {
            var users = response.users;
            var options = '';
            users.forEach(function (user) {
                options += `<option value="${user}">${user}</option>`;
            });
            $('select[name="username"]').html(options);
        } else {
            alert('加载用户列表失败: ' + response.message);
        }
    });
}

function loadRoles() {
    $.get('/api/roles/', function (response) {
        if (response.success) {
            var roles = response.roles;
            var options = '';
            roles.forEach(function (role) {
                options += `<option value="${role.id}">${role.name}</option>`;
            });
            $('select[name="role_id"]').html(options);
        } else {
            alert('加载角色列表失败: ' + response.message);
        }
    });
}


function loadRepositoryMembers(repoId) {
    $('#content-container').html(`
        <div class="ui container">
            <h2>仓库成员管理
                <button class="ui button" id="add-member-button" style="margin-left: 20px;">添加成员</button>
                <button class="ui button" id="back-to-repos" style="margin-left: 20px;">返回仓库管理</button>
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

    // 绑定返回仓库管理按钮点击事件
    $('#back-to-repos').click(function () {
        loadRepositoryManagement();
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
            url: `/api/repositories/${repoId}/members/`,
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function (response) {
                if (response.success) {
                    $('#add-member-modal').modal('hide').remove();
                    loadRepositoryMembers(repoId);
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
    $.get(`/api/repositories/${repoId}/members/`, function (response) {
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
                        url: `/api/repositories/${repoId}/members/remove/${memberId}/`,
                        type: 'DELETE',
                        success: function (response) {
                            if (response.success) {
                                loadRepositoryMembers(repoId);
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

loadRepositoryManagement();
