jQuery(document).ready(function(){

jQuery('#subscribe-bottom').submit(function(e){
  jQuery.ajax({type:'POST', url: 'https://platzi.com/blog/wp-content/themes/platzi-blog/newsletter.php', data:jQuery('#subscribe-bottom').serialize(), success: function(response) {
  }});
  e.preventDefault();
});
   

  jQuery('.header-mobileMenu').click(function(){
    
    jQuery('.nav-primary').slideToggle(function(){return 0;},function(){
          if(jQuery('.login').hasClass('menu-expanded')){
            jQuery('.login').removeClass('menu-expanded');
          }
          else{
            jQuery('.login').addClass('menu-expanded')
          }
        });
  });
  
  jQuery('.header-login').click(function(){
    jQuery('.login').slideToggle('medium');
  });
  
	var _fbq = window._fbq || (window._fbq = []);
	if (!_fbq.loaded) {
		var fbds = document.createElement('script');
		fbds.async = true;
		fbds.src = '//connect.facebook.net/en_US/fbds.js';
		var s = document.getElementsByTagName('script')[0];
		s.parentNode.insertBefore(fbds, s);
		_fbq.loaded = true;
	};
  
  jQuery('#subscribe-bottom').validate({
	  messages: {
		  name: "Por favor pon tu nombre",
		  email: "Por favor pon tu correo electrónico"
	  },
	  
		submitHandler: function(form) {
			
			jQuery("#subscribe-bottom").remove();
			jQuery(".email-bottom h4").remove();
			jQuery(".email-bottom").append("<h4 class='succeed'>Gracias por suscribirte, pronto empezarás a recibir las buenas nuevas.</h4>");
			
			twttr.conversion.trackPid('l6fey', { tw_sale_amount: 0, tw_order_quantity: 0 });
			window._fbq = window._fbq || [];
			window._fbq.push(['track', '6028337997147', {'value':'0.00','currency':'USD'}]);
			ga('send', 'event', 'blog', 'platzi-blog', 'Email blog adquisition - ES');
			
		}
  });
  
});
