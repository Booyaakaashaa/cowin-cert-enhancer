const body = document.querySelector("body"),
    input = document.querySelector("input")
    click = document.querySelector(".click"),
    tap = document.querySelector(".tap"),
    to_up = document.querySelector(".to"),
    cert = document.querySelector(".cert"),
    load = document.querySelector(".load");

body.onclick = (e) => {
    e.stopPropagation();
    input.click();
}
if(document.getElementById("certificate")){
    document.getElementById("certificate").onchange = function () {
        load.classList.remove("load");
        click.classList.add("click--load");
        tap.classList.add("tap--load");
        to_up.classList.add("to--load");
        cert.classList.add("cert--load");
        load.classList.add("load--load");
        body.onclick = (e) => {
            e.stopPropagation();
            e.preventDefault();
        }
        document.getElementsByTagName("form")[0].submit();
    }
}
if(document.getElementById("pic")) {
    document.getElementById("pic").onchange = function () {
        load.classList.remove("load");
        click.classList.add("click--load");
        tap.classList.add("tap--load");
        to_up.classList.add("to--load");
        cert.classList.add("cert--load");
        load.classList.add("load--load");
        body.classList.add("body--load");
        body.onclick = (e) => {
            e.stopPropagation();
            e.preventDefault();
        }
        document.getElementsByTagName("form")[0].submit();
    }
}