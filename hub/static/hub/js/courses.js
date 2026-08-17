/* Course catalog filter for the Academy section */
(function () {
  'use strict';
  var filters = document.querySelectorAll('#courseFilters .filter-btn');
  var items = document.querySelectorAll('#courseGrid .course-item');
  var empty = document.getElementById('courseEmpty');
  if (!filters.length || !items.length) return;

  filters.forEach(function (btn) {
    btn.addEventListener('click', function () {
      filters.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      var filter = btn.getAttribute('data-filter');
      var visible = 0;
      items.forEach(function (item) {
        var match = filter === 'all' || item.getAttribute('data-category') === filter;
        item.style.display = match ? '' : 'none';
        if (match) visible++;
      });
      if (empty) empty.style.display = visible === 0 ? 'block' : 'none';
    });
  });
})();
