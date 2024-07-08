function loadHomePage() {
    $('#content-container').html(`
        <div class="ui segment">
            <h2 class="ui center aligned icon header">
                <i class="circular users icon"></i>
                欢迎来到管理系统
            </h2>
            <div class="ui center aligned container">
                <button class="ui primary button" onclick="loadServiceOperations()">服务操作</button>
                <button class="ui primary button" onclick="loadUserManagement()">用户管理</button>
                <button class="ui primary button" onclick="loadRepositoryGroupManagement()">仓库组管理</button>
                <button class="ui primary button" onclick="loadRepositoryManagement()">仓库管理</button>
                <button class="ui primary button" onclick="loadBranchManagement()">分支管理</button>
                <button class="ui primary button" onclick="loadHookManagement()">HOOK管理</button>
                <button class="ui primary button" onclick="loadImportRepository()">导入仓库</button>
                <button class="ui primary button" onclick="loadWebhookManagement()">Webhook管理</button>
            </div>
        </div>
    `);
}
