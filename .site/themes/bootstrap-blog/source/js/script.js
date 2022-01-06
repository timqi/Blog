(function($){
  // Caption
  $('.article-entry').each(function(i){
    $(this).find('img').each(function(){
      if ($(this).parent().hasClass('image-link')) return;

      var alt = this.alt;
      if (alt) $(this).after('<span class="caption">' + alt + '</span>');

      $(this).wrap('<a href="' + this.src + '" title="' + alt + '" class="image-link"></a>');
    });

    $(this).find('.image-link').each(function(){
      $(this).attr('rel', 'article' + i);
    });
  });

  // Bootstrap table style
  $('.article-entry table').each(function(i, table)  {
    if ($(this).parent().hasClass('table-responsive')) return;
    $(this).addClass('table');
    $(this).wrap('<div class="table-responsive"></div>');
  });

})(jQuery);
