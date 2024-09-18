var pass= document.querySelector(".pass");
var conf=document.querySelector(".confirm");



var bt=document.querySelector(".submit")
bt.addEventListener("click",function(){
    var p=pass.value;
    var c=conf.value;
if(p===c){
   document.querySelector(".formsignup").action="/studentSignupOTP/";
}
else{
    alert("Rewrite Password")
    document.querySelector(".formsignup").action="/studentSignupPage/";
}
   
})