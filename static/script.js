
(function(){
  function two(n){return (n<10?'0':'')+n;}
  function toLocalDatetimeValue(d){
    return d.getFullYear()+"-"+two(d.getMonth()+1)+"-"+two(d.getDate())+"T"+two(d.getHours())+":"+two(d.getMinutes());
  }
  function roundTo15(d){
    const m = Math.round((d.getTime()/60000)/15)*15;
    return new Date(m*60000);
  }
  function setNowRounded(id){
    var el=document.getElementById(id);
    if(!el) return;
    var v=toLocalDatetimeValue(roundTo15(new Date()));
    el.value=v;
    el.dispatchEvent(new Event('change'));
  }
  window.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('input[type="datetime-local"]').forEach(function(inp){
      inp.setAttribute('step','900');
    });
    document.querySelectorAll('[data-now]').forEach(function(btn){
      btn.addEventListener('click', function(e){
        e.preventDefault();
        setNowRounded(btn.getAttribute('data-now'));
      });
    });
  });
})(); 


(function(){
  window.addEventListener('DOMContentLoaded', function(){
    var btnOpen = document.getElementById('btnMobileMenu');
    var btnClose = document.getElementById('btnMobileMenuClose');
    var menu = document.getElementById('mobileMenu');
    function closeMenu(){
      if(menu){ menu.classList.remove('open'); }
    }
    function openMenu(){
      if(menu){ menu.classList.add('open'); }
    }
    if(btnOpen){
      btnOpen.addEventListener('click', function(e){
        e.preventDefault();
        if(menu && menu.classList.contains('open')){ closeMenu(); } else { openMenu(); }
      });
    }
    if(btnClose){
      btnClose.addEventListener('click', function(e){
        e.preventDefault();
        closeMenu();
      });
    }
    // close when clicking outside
    document.addEventListener('click', function(e){
      if(!menu) return;
      if(!menu.classList.contains('open')) return;
      var target = e.target;
      if(target===menu || target===btnOpen || menu.contains(target)) return;
      closeMenu();
    });
  });
})();
