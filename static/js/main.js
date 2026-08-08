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

// ==========================
// ROUND 3 CONTROLS
// ==========================

const enableRound3Btn = document.getElementById("enableRound3Btn");

if(enableRound3Btn){

    enableRound3Btn.onclick = function(){

        fetch("/admin/enable_round3",{

            method:"POST"

        }).then(()=>{

            alert("✅ Round 3 Enabled");

        });

    };

}

const disableRound3Btn = document.getElementById("disableRound3Btn");

if(disableRound3Btn){

    disableRound3Btn.onclick=function(){

        fetch("/admin/disable_round3",{

            method:"POST"

        }).then(()=>{

            alert("🔒 Round 3 Disabled");

        });

    };

}