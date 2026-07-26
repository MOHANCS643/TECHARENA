const toggle = document.getElementById("theme-toggle");

if(localStorage.getItem("theme") === "dark"){
    document.body.classList.add("dark");
    toggle.textContent = "☀️";
}

toggle.onclick = () =>{

    document.body.classList.toggle("dark");

    if(document.body.classList.contains("dark")){
        toggle.textContent="☀️";
        localStorage.setItem("theme","dark");
    }else{
        toggle.textContent="🌙";
        localStorage.setItem("theme","light");
    }

};