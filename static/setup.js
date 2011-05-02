function rewriteWikiLinksToThisSite() {
  // The Mozilla wiki generates links that point to 
  // http and then redirect to https.
  var baseContent = config.baseContent.replace('https:', 'http:');
  $('a[href^="' + baseContent + '"]').each(function() {
    var href = $(this).attr("href");
    var newHref = href.slice(config.baseContent.length);
    $(this).attr("href", newHref);
  });
}

$(window).ready(redirectWikiLinksToThisSite);
