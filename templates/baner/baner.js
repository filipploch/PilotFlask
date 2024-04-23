function start(){        
var slideIndex = 0;
//        sleep(4000);
        showSlides();

        function showSlides() {
            var i;
            var slides = document.getElementsByClassName("baner_element");
            for (i = 0; i < slides.length; i++) {
                slides[i].style.display = "none";
            }
            slideIndex++;
            if (slideIndex > slides.length) {
                slideIndex = 1
            }
            
            slides[slideIndex - 1].style.display = "block";
            animation_duration = 25000
            start_slide_duration = 5000
            other_slides_duration = (animation_duration - start_slide_duration)/(slides.length + 1)
            
            if (slideIndex == slides.length){
                //pass
            }
            else if (slideIndex == 1) {
                first_slide_duration = start_slide_duration + other_slides_duration
                setTimeout(showSlides, first_slide_duration);
                }
            else {
                setTimeout(showSlides, (other_slides_duration));
            }
        }
}