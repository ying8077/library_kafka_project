const contentContainer = document.getElementById("btn_container");
const reader = localStorage.getItem('rname');

document.addEventListener("DOMContentLoaded", function () {
    if (reader === null) {
        contentContainer.innerHTML = '<a href="/login" class="btn_login">登入</a>';
    } else {
        contentContainer.innerHTML = `
			<button class='btn_login'>黃金會員</button>
			<div class="hover px-4 py-6 space-y-2">
				<a href="/r_borrowed">借書紀錄</a>
				<div>個人資料</div>
				<div class="btn_logout" onclick="signout()">登出</div>
			</div>`;
    }
});

function signout() {
	localStorage.removeItem("rname");
	location.href='/r_signout';
}