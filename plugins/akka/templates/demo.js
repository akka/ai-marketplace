/* ---- DEMO SECTION JS ---- */
/* Reads window.DEMO_SEQUENCE_DATA injected by demo.html */
(function() {
  var demoTabs = document.querySelectorAll('#demo-section .nav-tab');
  var demoPanels = document.querySelectorAll('#demo-section .tab-panel');

  function switchDemoTab(idx) {
    demoTabs.forEach(function(t, i) { t.classList.toggle('active', i === idx); });
    demoPanels.forEach(function(p, i) { p.classList.toggle('active', i === idx); });
  }

  demoTabs.forEach(function(tab) {
    tab.addEventListener('click', function() { switchDemoTab(+this.dataset.tab); });
  });

  /* Expandable row toggle */
  var demoCompRows = document.querySelectorAll('#demo-section .comp-row');
  demoCompRows.forEach(function(row) {
    var chev = document.createElement('span');
    chev.className = 'comp-row-chevron';
    chev.innerHTML = '&#9654;';
    row.appendChild(chev);
  });
  demoCompRows.forEach(function(row) {
    row.addEventListener('click', function() {
      var key = this.dataset.comp;
      var detail = document.querySelector('#demo-section [data-detail="' + key + '"]');
      var isExpanded = this.classList.contains('expanded');
      demoCompRows.forEach(function(r) { r.classList.remove('expanded'); });
      document.querySelectorAll('#demo-section .comp-detail').forEach(function(d) { d.classList.remove('open'); });
      if (!isExpanded && detail) {
        this.classList.add('expanded');
        detail.classList.add('open');
        detail.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
  });

  /* Tool tab switching (Try It Yourself step 1) */
  document.querySelectorAll('#demo-section [data-tool]').forEach(function(tab) {
    tab.addEventListener('click', function() {
      var tool = this.dataset.tool;
      var parent = this.closest('.try-step-content');
      if (!parent) return;
      parent.querySelectorAll('.try-os-tab[data-tool]').forEach(function(t) { t.classList.remove('active'); });
      parent.querySelectorAll('.try-tool-content').forEach(function(p) { p.classList.remove('active'); });
      this.classList.add('active');
      var target = parent.querySelector('[data-tool-panel="' + tool + '"]');
      if (target) target.classList.add('active');
    });
  });

  /* Install method tab switching (Try It Yourself step 2) */
  document.querySelectorAll('#demo-section [data-os]').forEach(function(tab) {
    tab.addEventListener('click', function() {
      var os = this.dataset.os;
      var parent = this.closest('.try-step-content');
      if (!parent) return;
      parent.querySelectorAll('.try-os-tab[data-os]').forEach(function(t) { t.classList.remove('active'); });
      parent.querySelectorAll('.try-os-content').forEach(function(p) { p.classList.remove('active'); });
      this.classList.add('active');
      var target = parent.querySelector('[data-os-panel="' + os + '"]');
      if (target) target.classList.add('active');
    });
  });

  /* SVG connector lines for component graph */
  function drawDemoConnectors() {
    document.querySelectorAll('#demo-section .dg-conn-tree svg.dg-lines').forEach(function(s) { s.remove(); });
    document.querySelectorAll('#demo-section .dg-conn-tree').forEach(function(tree) {
      var branches = tree.querySelectorAll('.dg-conn-branch');
      var n = branches.length;
      if (n === 0) return;
      var ROW = 24, MID = ROW / 2, TRUNK_X = 12, ARROW_X = 28;
      var svgH = n * ROW;
      var ns = 'http://www.w3.org/2000/svg';
      var svg = document.createElementNS(ns, 'svg');
      svg.setAttribute('class', 'dg-lines');
      svg.setAttribute('height', svgH);
      svg.style.left = '0px';
      svg.style.width = (ARROW_X + 8) + 'px';
      function line(x1,y1,x2,y2) {
        var l = document.createElementNS(ns,'line');
        l.setAttribute('x1',x1); l.setAttribute('y1',y1);
        l.setAttribute('x2',x2); l.setAttribute('y2',y2);
        l.setAttribute('stroke','#444'); l.setAttribute('stroke-width','1');
        l.setAttribute('shape-rendering','crispEdges');
        svg.appendChild(l);
      }
      function arrow(x,y) {
        var p = document.createElementNS(ns,'polygon');
        p.setAttribute('points',(x-4)+','+(y-3)+' '+x+','+y+' '+(x-4)+','+(y+3));
        p.setAttribute('fill','#444');
        svg.appendChild(p);
      }
      line(0, MID, TRUNK_X, MID);
      if (n === 1) { line(TRUNK_X, MID, ARROW_X, MID); arrow(ARROW_X, MID); }
      else {
        var lastY = (n-1)*ROW + MID;
        line(TRUNK_X, MID, TRUNK_X, lastY);
        for (var i = 0; i < n; i++) { var y = i*ROW+MID; line(TRUNK_X,y,ARROW_X,y); arrow(ARROW_X,y); }
      }
      tree.insertBefore(svg, tree.firstChild);
    });
  }
  drawDemoConnectors();

  /* Auto-expand sequence diagram row by default */
  var seqRow    = document.querySelector('#demo-section .comp-row[data-comp="dv-sequence"]');
  var seqDetail = document.querySelector('#demo-section [data-detail="dv-sequence"]');
  if (seqRow && seqDetail) {
    seqRow.classList.add('expanded');
    seqDetail.classList.add('open');
  }

  /* Re-draw lines when detail panels open */
  var demoCompObserver = new MutationObserver(function() {
    setTimeout(drawDemoConnectors, 50);
  });
  document.querySelectorAll('#demo-section .comp-detail').forEach(function(d) {
    demoCompObserver.observe(d, { attributes: true, attributeFilter: ['class'] });
  });

  /* Sequence diagram SVG — reads window.DEMO_SEQUENCE_DATA */
  (function() {
    var data = window.DEMO_SEQUENCE_DATA;
    if (!data) return;
    var participants = data.participants;
    var messages = data.messages;
    var N = participants.length;
    var container = document.querySelector('#demo-section #seqDiagram');
    if (!container) return;
    var availW = container.offsetWidth || 900;
    if (availW < 600) availW = 900;
    var COL_W = Math.floor(availW / N);
    var W = N * COL_W;
    var HDR_H = 48, ROW_H = 32, REGION_GAP = 14, REGION_TITLE_H = 22;
    var PAD_X = COL_W / 2;
    var y = HDR_H + 8;
    messages.forEach(function(m) { if (m.region) y += REGION_GAP + REGION_TITLE_H; else y += ROW_H; });
    var TOTAL_H = y + 20;
    var ns = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('width', W); svg.setAttribute('height', TOTAL_H);
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + TOTAL_H);
    svg.style.fontFamily = "'Instrument Sans', sans-serif";
    function text(x, yy, str, size, color, anchor, weight) {
      var lines = str.split('\n');
      lines.forEach(function(line, i) {
        var t = document.createElementNS(ns, 'text');
        t.setAttribute('x', x); t.setAttribute('y', yy + i * (size + 2));
        t.setAttribute('text-anchor', anchor || 'middle');
        t.setAttribute('fill', color); t.setAttribute('font-size', size);
        if (weight) t.setAttribute('font-weight', weight);
        t.textContent = line;
        svg.appendChild(t);
      });
    }
    function colX(i) { return i * COL_W + PAD_X; }
    participants.forEach(function(p, i) {
      var x = colX(i);
      var rect = document.createElementNS(ns, 'rect');
      var boxW = Math.min(COL_W - 12, 120);
      rect.setAttribute('x', x - boxW/2); rect.setAttribute('y', 4);
      rect.setAttribute('width', boxW); rect.setAttribute('height', HDR_H - 8);
      rect.setAttribute('rx', 4);
      rect.setAttribute('fill', p.ext ? '#1A1A1A' : '#141414');
      rect.setAttribute('stroke', p.ext ? '#666' : (p.color || '#555'));
      rect.setAttribute('stroke-width', '1');
      if (p.ext) rect.setAttribute('stroke-dasharray', '4 3');
      svg.appendChild(rect);
      var lines = p.name.split('\n');
      var textY = lines.length > 1 ? 24 : 30;
      text(x, textY, p.name, 11, p.ext ? '#999' : (p.color || '#fff'), 'middle', '700');
    });
    participants.forEach(function(p, i) {
      var x = colX(i);
      var l = document.createElementNS(ns, 'line');
      l.setAttribute('x1', x); l.setAttribute('y1', HDR_H);
      l.setAttribute('x2', x); l.setAttribute('y2', TOTAL_H - 10);
      l.setAttribute('stroke', '#222'); l.setAttribute('stroke-width', '1');
      l.setAttribute('stroke-dasharray', '3 3');
      svg.appendChild(l);
    });
    var curY = HDR_H + 8;
    messages.forEach(function(m) {
      if (m.region) {
        curY += REGION_GAP;
        text(8, curY + 12, m.region, 10, m.color, 'start', '700');
        var rline = document.createElementNS(ns, 'line');
        rline.setAttribute('x1', 0); rline.setAttribute('y1', curY + 14);
        rline.setAttribute('x2', W); rline.setAttribute('y2', curY + 14);
        rline.setAttribute('stroke', m.color); rline.setAttribute('stroke-width', '0.5');
        rline.setAttribute('opacity', '0.2');
        svg.appendChild(rline);
        curY += REGION_TITLE_H;
        return;
      }
      curY += ROW_H;
      var fromX = colX(m.from), toX = colX(m.to);
      var aline = document.createElementNS(ns, 'line');
      aline.setAttribute('x1', fromX); aline.setAttribute('y1', curY);
      aline.setAttribute('x2', toX); aline.setAttribute('y2', curY);
      aline.setAttribute('stroke', '#555'); aline.setAttribute('stroke-width', '1');
      if (m.dashed) aline.setAttribute('stroke-dasharray', '4 3');
      svg.appendChild(aline);
      var head = document.createElementNS(ns, 'polygon');
      if (toX > fromX) head.setAttribute('points', (toX-5)+','+(curY-3)+' '+toX+','+curY+' '+(toX-5)+','+(curY+3));
      else head.setAttribute('points', (toX+5)+','+(curY-3)+' '+toX+','+curY+' '+(toX+5)+','+(curY+3));
      head.setAttribute('fill', '#555');
      svg.appendChild(head);
      var midX = (fromX + toX) / 2;
      var bg = document.createElementNS(ns, 'rect');
      var labelLen = m.label.length * 5.5 + 12;
      bg.setAttribute('x', midX - labelLen/2); bg.setAttribute('y', curY - 14);
      bg.setAttribute('width', labelLen); bg.setAttribute('height', 14);
      bg.setAttribute('fill', '#070707'); bg.setAttribute('rx', 2);
      svg.appendChild(bg);
      text(midX, curY - 3, m.label, 10, '#B8B8B8', 'middle', '500');
    });
    container.appendChild(svg);
  })();
})();

/* ---- Demo keyboard: 1-6 switch tabs when demo is in view ---- */
(function() {
  var demoWrapper = document.getElementById('demo-wrapper');
  var demoTabs = document.querySelectorAll('#demo-section .nav-tab');
  var demoPanels = document.querySelectorAll('#demo-section .tab-panel');
  function isDemoActive() {
    if (!demoWrapper) return false;
    var rect = demoWrapper.getBoundingClientRect();
    return rect.top < window.innerHeight * 0.5 && rect.bottom > window.innerHeight * 0.5;
  }
  function switchDemoTab(idx) {
    demoTabs.forEach(function(t, i) { t.classList.toggle('active', i === idx); });
    demoPanels.forEach(function(p, i) { p.classList.toggle('active', i === idx); });
  }
  document.addEventListener('keydown', function(e) {
    if (!isDemoActive()) return;
    if (e.key >= '1' && e.key <= '6') {
      e.preventDefault();
      e.stopPropagation();
      switchDemoTab(+e.key - 1);
    }
  }, true);
})();
