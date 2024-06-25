function Menu(e) {
    if (document.getElementById("nav").classList.contains("responsive")) {
        document.getElementById("nav").classList.remove("responsive");
        document.getElementById("nav-menu-hamicon").classList.remove("responsive")
    } else {
        document.getElementById("nav").classList.add("responsive");
        document.getElementById("nav-menu-hamicon").classList.add("responsive");
    }
    if (document.getElementById("nav2").classList.contains("responsive")) {
        document.getElementById('content').setAttribute("onclick", "");
        document.getElementById("nav2").setAttribute("onmouseleave", "Menu()");
        document.getElementById("nav2").classList.remove("responsive");
        document.getElementById("nav-menu-hamicon").classList.remove("responsive")
    } else {
        if (e)
            if (e.getAttribute("id") == "nav-menu") {
                document.getElementById('nav2').setAttribute("onmouseleave", "");
                document.getElementById('content').setAttribute("onclick", "Menu()");
            }
        document.getElementById("nav2").classList.add("responsive");
        document.getElementById("nav-menu-hamicon").classList.add("responsive");
    }
    if (document.getElementById("navbar").classList.contains("responsive")) {
        document.getElementById("navbar").classList.remove("responsive");
        document.getElementById("nav-menu-hamicon").classList.remove("responsive")
    } else {
        document.getElementById("navbar").classList.add("responsive");
        document.getElementById("nav-menu-hamicon").classList.add("responsive");
    }
}

var prevScrollpos = window.scrollY;
window.onscroll = function () {
    var currentScrollPos = window.scrollY;
    if (prevScrollpos > currentScrollPos) {
        document.getElementById("navbar").classList.remove("hidden");
        document.getElementById("nav").classList.remove("hidden");
        document.getElementById("nav2").classList.remove("hidden");
        if (window.innerWidth > 575) {
            document.getElementById("content").style.marginLeft = document.getElementById("nav").offsetWidth - document.querySelector(".inverted-topleft-corner").offsetWidth + "px"
        }
    } else {
        document.getElementById("navbar").classList.add("hidden");
        document.getElementById("nav").classList.add("hidden");
        document.getElementById("nav2").classList.add("hidden");
        document.getElementById("content").style.marginLeft = "0";
    }
    prevScrollpos = currentScrollPos;
}

if (window.innerWidth > 575) {
    document.getElementById("content").style.marginLeft = document.getElementById("nav").offsetWidth - document.querySelector(".inverted-topleft-corner").offsetWidth + "px"
}
document.getElementById("content").style.marginTop = document.getElementById("navbar").offsetHeight + "px"
document.querySelectorAll(".heightofnavbar").forEach(function (element) {
    element.style.height = document.getElementById("navbar").offsetHeight + "px";
});
document.querySelectorAll(".widthofnav").forEach(function (element) {
    element.style.width = document.getElementById("nav").offsetWidth - document.querySelector(".inverted-topleft-corner").offsetWidth + "px";
});
document.querySelectorAll(".widthofnav2").forEach(function (element) {
    element.style.width = document.getElementById("nav2").offsetWidth - document.querySelector(".inverted-topleft-corner").offsetWidth + "px";
});