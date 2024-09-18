var swiper = new Swiper(".mySwiper", {
    slidesPerView: "auto",
    spaceBetween: 10,
    
    loop: true,
    autoplay: {
        delay: 4000, 
        disableOnInteraction: true, 
     },
  });



  var admin=document.querySelector(".prt3 i");

  admin.addEventListener("click",function(){

    document.querySelector(".admin").style.opacity="1";
    
   
    })

    var adminp =document.querySelector(".admin");
    adminp.addEventListener("click",function(){
        adminp.style.opacity="0";
    admin.style.opacity=1;


    })



  