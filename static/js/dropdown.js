(function($) {

  // Reverse
  // =============================================
  $.fn.reverse = [].reverse;

  // jQuery Extended Family Selectors
  // =============================================
  $.fn.cousins = function(filter) {
    return $(this).parent().siblings().children(filter);
  };

  $.fn.piblings = function(filter) {
    return $(this).parent().siblings(filter);
  };

  $.fn.niblings = function(filter) {
    return $(this).siblings().children(filter);
  };

  // Update
  // =============================================
  $.fn.update = function() {
    return $(this);
  };

  // Dropdown
  // =============================================
  $.fn.dropdown = function(options) {

    // Store object
    var $this = $(this);

    // Settings
    var settings = $.extend({
      className : 'toggled',
    }, options);

    // Simplify variable names
    var className = settings.className;

    // List selectors
    var $ul = $this.find('ul'),
        $li = $this.find('li'),
        $a  = $this.find('a');

    // Menu selectors
    var $drawers = $a.next($ul),      // All unordered lists after anchors are drawers
        $buttons = $drawers.prev($a), // All anchors previous to drawers are buttons
        $links   = $a.not($buttons);  // All anchors that are not buttons are links

    // Toggle menu on-click
    $buttons.on('click', function() {
      console.log("I clicked on button!")
      var $button = $(this),
          $drawer = $button.next($drawers),
          $piblingDrawers = $button.piblings($drawers);

      // Toggle button and drawer
      $button.toggleClass(className);
      $drawer.toggleClass(className).css('height', '');

      // Reset children
      $drawer.find($buttons).removeClass(className);
      $drawer.find($drawers).removeClass(className).css('height', '');

      // Reset cousins
      $piblingDrawers.find($buttons).removeClass(className);
      $piblingDrawers.find($drawers).removeClass(className).css('height', '');

      // Animate height auto
      $drawers.update().reverse().each(function() {
        var $drawer = $(this);
        if($drawer.hasClass(className)) {
          var $clone = $drawer.clone().css('display', 'none').appendTo($drawer.parent()),
              height = $clone.css('height', 'auto').height() + 'px';
          $clone.remove();
          $drawer.css('height', '').css('height', height);
        }
        else {
          $drawer.css('height', '');
        }
      });
    });

    // Close menu
    function closeMenu() {
      $buttons.removeClass(className);
      $drawers.removeClass(className).css('height', '');
    }

    // Close menu after link is clicked
    $links.click(function() {
      closeMenu();
    });

    // Close menu when off-click and focus-in
    $(document).on('click focusin', function(event) {
      if(!$(event.target).closest($buttons.parent()).length) {
        closeMenu();
      }
    });
  };
})(jQuery);

