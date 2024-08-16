  window.onload = function() {
    const parent = document.getElementById('substitutions-container');
    const children = parent.getElementsByClassName('substitution');
    let maxWidth = 0;
    let totalHeight = 0;

    for (let i = 0; i < children.length; i++) {
      const childWidth = children[i].offsetWidth;
      const childHeight = children[i].offsetHeight;

      if (childWidth > maxWidth) {
        maxWidth = childWidth;
      }
      totalHeight += childHeight;
    }

    parent.style.width = maxWidth * 1 + 'px';
    parent.style.height = totalHeight * 1 + 'px';
  };