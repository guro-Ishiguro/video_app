"use strict";

// 設定の表示切り替え
const settings_target = document.querySelector(".settings");
const settings_button = document.querySelector(".account-settings-btn");
const settings_close = document.querySelector(".settings-close");
settings_button.addEventListener("click", function () {
    settings_target.classList.toggle("page-visible");
});
settings_close.addEventListener("click", function () {
    settings_target.classList.toggle("page-visible");
});