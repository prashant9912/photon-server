

document.getElementById("butt").addEventListener("click", camera);

function camera(){
    console.log(1);
    document.getElementById("qrsuccess").style.display="none";
    document.getElementById("qrfail").style.display="none";
    // show the camera element
    document.getElementById("preview").style.display="block";

let scanner = new Instascan.Scanner(
    {
        video: document.getElementById('preview')
    }
);
scanner.addListener('scan', function(content) {
    
    console.log(content);
    decode(content);

    document.getElementById("preview").style.display="none";// stop showing camera once you get the value
    scanner.stop(); //stop the camera request

});
Instascan.Camera.getCameras().then(cameras => 
{
    if(cameras.length > 0){
        scanner.start(cameras[0]);
    } else {
        console.error("Error with camera request");
    }
});


}


function decode(url){

    let vars = {};
    let parts = url.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });

console.log(vars);

if(vars.pa!=undefined || vars.pn!=undefined){

    document.getElementById("pa").value = vars.pa;
    document.getElementById("pn").value = vars.pn;
    document.getElementById("qrsuccess").style.display="block";

}
else{
    document.getElementById("qrfail").style.display="block";


}

//set the inputs AUTOFILL


}