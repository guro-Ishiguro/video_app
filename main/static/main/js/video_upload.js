"use strict";

function thumbnailPreview(obj) {
    const fileReader = new FileReader();
    fileReader.onload = function () {
        document.getElementById("thumbnail-preview").src = fileReader.result;
    };
    fileReader.readAsDataURL(obj.files[0]);
}

function showTitleLength(str) {
    document.getElementById("title-form-length").textContent = str.length;
}

function showDescriptionLength(str) {
    document.getElementById("description-form-length").textContent = str.length;
}