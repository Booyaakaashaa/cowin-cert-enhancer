/*const script = document.createElement('script');
script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);*/

const container = document.querySelector(".container"),
    dropArea = container.querySelector(".drop_area"),
    form = container.querySelector("form"),
    button = container.querySelector(".pic_btn_container"),
    btn = button.querySelector(".pic_btn"),
    input = container.querySelector("input"),
    dropInfo = dropArea.querySelector(".drop_info"),
    body = document.querySelector("body"),
    icon = dropArea.querySelector(".icon"),
    loading = dropArea.querySelector(".loading"),
    orSpan = dropArea.querySelector(".or_span");

let file;
let ajaxData;

container.onclick = (e) => {
    e.stopPropagation();
    input.click();
}
btn.onclick = (e) => {
    e.stopPropagation();
}

dropArea.addEventListener("dragover", (e) => {
    e.stopPropagation();
    e.preventDefault();
    dropArea.classList.add("drop_area--drag");
    container.classList.add("container--drag");
    orSpan.classList.add("or_span--drag");
    dropInfo.classList.add("drop_info--drag");
    btn.classList.add("pic_btn--drag")
    icon.classList.add("icon--drag");
    button.classList.add("pic_btn_container--drag");
});

["dragleave", "dragend"].forEach(action => {
    dropArea.addEventListener(action, () => {
        dropArea.classList.remove("drop_area--drag");
        container.classList.remove("container--drag");
        orSpan.classList.remove("or_span--drag");
        dropInfo.classList.remove("drop_info--drag");
        btn.classList.remove("pic_btn--drag")
        icon.classList.remove("icon--drag");
        button.classList.remove("pic_btn_container--drag");
    });
});

dropArea.addEventListener("drop", (e) => {
    e.stopPropagation();
    e.preventDefault();
    dropArea.classList.add("drop_area--drag");
    container.classList.add("container--drag");
    orSpan.classList.add("or_span--drag");
    dropInfo.classList.add("drop_info--drag");
    btn.classList.add("pic_btn--drag");
    icon.classList.add("icon--drop");
    loading.classList.remove("loading");
    loading.classList.add("loading--drop");
    button.classList.add("pic_btn_container--drag");
    /*reader.onload = ()=>{

    };*/
    file = e.dataTransfer.files;
    //let $form = $('form');
    //$form.trigger('submit');
    console.log(file);
    if (file.length > 1 || file.length === 0) {
        alert("Multiple files selected!");
        dropArea.classList.remove("drop_area--drag");
        container.classList.remove("container--drag");
        orSpan.classList.remove("or_span--drag");
        dropInfo.classList.remove("drop_info--drag");
        btn.classList.remove("pic_btn--drag")
        loading.classList.add("loading");
        loading.classList.remove("loading--drop");
        button.classList.remove("pic_btn_container--drag");
        icon.classList.remove("icon--drag");
        icon.classList.remove("icon--drop");
    } else {
        file = file[0];
        //console.log(file);
        $(function(){

            let $form = $("form");
            //$form.trigger('submit');
            ajaxData = new FormData();
            console.log(1,file);
            ajaxData.append($('input').attr('name'), file);
            console.log(2,file);
            console.log(ajaxData);
            $.ajax({
                url: $form.attr('action'),
                type: $form.attr('method'),
                data: ajaxData,
                //dataType: 'json',
                cache: false,
                contentType: false,
                processData: false,
                success: function (data){
                    console.log(data, "Success");
                },
            });
            //$form.trigger('submit');
        });
    }
});

document.getElementById("pic").onchange = function () {
    console.log("Le bhai main bhi chal gya!");
    dropArea.classList.add("drop_area--drag");
    container.classList.add("container--drag");
    orSpan.classList.add("or_span--drag");
    dropInfo.classList.add("drop_info--drag");
    btn.classList.add("pic_btn--drag");
    icon.classList.add("icon--drop");
    loading.classList.remove("loading");
    loading.classList.add("loading--drop");
    button.classList.add("pic_btn_container--drag");
    console.log(document.getElementById("pic").value);
    document.getElementsByTagName("form")[0].submit();
}
