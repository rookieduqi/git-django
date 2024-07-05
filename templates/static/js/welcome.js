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
            </div>
        </div>
    `);
}
