!function (t) { Array.indexOf || (Array.prototype.indexOf = function (t) { for (var e = 0; e < this.length; e++)if (this[e] == t) return e; return -1 }); var e, i = t(document), r = t("head"), o = null, s = {}, d = 0, a = "px", n = "JColResizer", l = "JCLRFlex", c = parseInt, f = Math, h = navigator.userAgent.indexOf("Trident/4.0") > 0; r.append("<style type='text/css'>  .JColResizer{table-layout:fixed;} .JColResizer > tbody > tr > td, .JColResizer > tbody > tr > th{overflow:hidden}  .JPadding > tbody > tr > td, .JPadding > tbody > tr > th{padding-left:0!important; padding-right:0!important;} .JCLRgrips{ height:0px; position:relative;} .JCLRgrip{margin-left:-5px; position:absolute; z-index:5; } .JCLRgrip .JColResizer{position:absolute;background-color:red;filter:alpha(opacity=1);opacity:0;width:10px;height:100%;cursor: col-resize;top:0px} .JCLRLastGrip{position:absolute; width:1px; } .JCLRgripDrag{ border-left:1px dotted black;\t} .JCLRFlex{width:auto!important;} .JCLRgrip.JCLRdisabledGrip .JColResizer{cursor:default; display:none;}</style>"); var p = function (t) { var e = t.attr("id"); (t = s[e]) && t.is("table") && (t.removeClass(n + " " + l).gc.remove(), delete s[e]) }, g = function (i) { var r = i.find(">thead>tr:first>th,>thead>tr:first>td"); r.length || (r = i.find(">tbody>tr:first>th,>tr:first>th,>tbody>tr:first>td, >tr:first>td")), r = r.filter(":visible"), i.cg = i.find("col"), i.ln = r.length, i.p && e && e[i.id] && u(i, r), r.each((function (e) { var r = t(this), o = -1 != i.dc.indexOf(e), s = t(i.gc.append('<div class="JCLRgrip"></div>')[0].lastChild); s.append(o ? "" : i.opt.gripInnerHtml).append('<div class="' + n + '"></div>'), e == i.ln - 1 && (s.addClass("JCLRLastGrip"), i.f && s.html("")), s.on("touchstart mousedown", x), o ? s.addClass("JCLRdisabledGrip") : s.removeClass("JCLRdisabledGrip").on("touchstart mousedown", x), s.t = i, s.i = e, s.c = r, r.w = r.width(), i.g.push(s), i.c.push(r), r.width(r.w).removeAttr("width"), s.data(n, { i: e, t: i.attr("id"), last: e == i.ln - 1 }) })), i.cg.removeAttr("width"), i.find("td, th").not(r).not("table th, table td").each((function () { t(this).removeAttr("width") })), i.f || i.removeAttr("width").addClass(l), w(i) }, u = function (t, i) { var r, o, s = 0, d = 0, n = []; if (i) { if (t.cg.removeAttr("width"), t.opt.flush) return void (e[t.id] = ""); for (o = (r = e[t.id].split(";"))[t.ln + 1], !t.f && o && (t.width(o *= 1), t.opt.overflow && (t.css("min-width", o + a), t.w = o)); d < t.ln; d++)n.push(100 * r[d] / r[t.ln] + "%"), i.eq(d).css("width", n[d]); for (d = 0; d < t.ln; d++)t.cg.eq(d).css("width", n[d]) } else { for (e[t.id] = ""; d < t.c.length; d++)r = t.c[d].width(), e[t.id] += r + ";", s += r; e[t.id] += s, t.f || (e[t.id] += ";" + t.width()) } }, w = function (t) { t.gc.width(t.w); for (var e = 0; e < t.ln; e++) { var i = t.c[e]; t.g[e].css({ left: i.offset().left - t.offset().left + i.outerWidth(!1) + t.cs / 2 + a, height: t.opt.headerOnly ? t.c[0].outerHeight(!1) : t.outerHeight(!1) }) } }, v = function (t, e, i) { var r = o.x - o.l, s = t.c[e], d = t.c[e + 1], n = s.w + r, l = d.w - r; s.width(n + a), t.cg.eq(e).width(n + a), t.f ? (d.width(l + a), t.cg.eq(e + 1).width(l + a)) : t.opt.overflow && t.css("min-width", t.w + r), i && (s.w = n, d.w = t.f ? l : d.w) }, m = function (e) { var i = t.map(e.c, (function (t) { return t.width() })); e.width(e.w = e.width()).removeClass(l), t.each(e.c, (function (t, e) { e.width(i[t]).w = i[t] })), e.addClass(l) }, C = function (t) { if (o) { var e = o.t, i = t.originalEvent.touches, r = (i ? i[0].pageX : t.pageX) - o.ox + o.l, s = e.opt.minWidth, d = o.i, n = 1.5 * e.cs + s + e.b, l = d == e.ln - 1, c = d ? e.g[d - 1].position().left + e.cs + s : n, h = e.f ? d == e.ln - 1 ? e.w - n : e.g[d + 1].position().left - e.cs - s : 1 / 0; if (r = f.max(c, f.min(h, r)), o.x = r, o.css("left", r + a), l) { var p = e.c[o.i]; o.w = p.w + r - o.l } if (e.opt.liveDrag) { l ? (p.width(o.w), !e.f && e.opt.overflow ? e.css("min-width", e.w + r - o.l) : e.w = e.width()) : v(e, d), w(e); var g = e.opt.onDrag; g && (t.currentTarget = e[0], g(t)) } return !1 } }, b = function (r) { if (i.off("touchend." + n + " mouseup." + n).off("touchmove." + n + " mousemove." + n), t("head :last-child").remove(), o) { if (o.removeClass(o.t.opt.draggingClass), o.x - o.l != 0) { var s = o.t, d = s.opt.onResize, a = o.i, l = a == s.ln - 1, c = s.g[a].c; l ? (c.width(o.w), c.w = o.w) : v(s, a, !0), s.f || m(s), w(s), d && (r.currentTarget = s[0], d(r)), s.p && e && u(s) } o = null } }, x = function (e) { var d = t(this).data(n), a = s[d.t], l = a.g[d.i], c = e.originalEvent.touches; if (l.ox = c ? c[0].pageX : e.pageX, l.l = l.position().left, l.x = l.l, i.on("touchmove." + n + " mousemove." + n, C).on("touchend." + n + " mouseup." + n, b), r.append("<style type='text/css'>*{cursor:" + a.opt.dragCursor + "!important}</style>"), l.addClass(a.opt.draggingClass), o = l, a.c[d.i].l) for (var f, h = 0; h < a.ln; h++)(f = a.c[h]).l = !1, f.w = f.width(); return !1 }; t(window).on("resize." + n, (function () { for (var t in s) if (s.hasOwnProperty(t)) { var i, r = 0; if ((t = s[t]).removeClass(n), t.f) { for (t.w = t.width(), i = 0; i < t.ln; i++)r += t.c[i].w; for (i = 0; i < t.ln; i++)t.c[i].css("width", f.round(1e3 * t.c[i].w / r) / 10 + "%").l = !0 } else m(t), "flex" == t.mode && t.p && e && u(t); w(t.addClass(n)) } })), t.fn.extend({ colResizable: function (i) { switch ((i = t.extend({ resizeMode: "fit", draggingClass: "JCLRgripDrag", gripInnerHtml: "", liveDrag: !1, minWidth: 15, headerOnly: !1, hoverCursor: "col-resize", dragCursor: "col-resize", postbackSafe: !1, flush: !1, marginLeft: null, marginRight: null, disable: !1, partialRefresh: !1, useLocalStorage: !1, disabledColumns: [], removePadding: !0, onDrag: null, onResize: null }, i)).fixed = !0, i.overflow = !1, i.resizeMode) { case "flex": i.fixed = !1; break; case "overflow": i.fixed = !1, i.overflow = !0 }return this.each((function () { !function (i, o) { var a = t(i); a.opt = o, a.mode = o.resizeMode, a.dc = a.opt.disabledColumns, a.opt.removePadding && a.addClass("JPadding"); try { e = a.opt.useLocalStorage ? localStorage : sessionStorage } catch (t) { } if (a.opt.disable) return p(a); var l = a.id = a.attr("id") || n + d++; a.p = a.opt.postbackSafe, !a.is("table") || s[l] && !a.opt.partialRefresh || ("col-resize" !== a.opt.hoverCursor && r.append("<style type='text/css'>.JCLRgrip .JColResizer:hover{cursor:" + a.opt.hoverCursor + "!important}</style>"), a.addClass(n).attr("id", l).before('<div class="JCLRgrips"/>'), a.g = [], a.c = [], a.w = a.width(), a.gc = a.prev(), a.f = a.opt.fixed, o.marginLeft && a.gc.css("marginLeft", o.marginLeft), o.marginRight && a.gc.css("marginRight", o.marginRight), a.cs = c(h ? i.cellSpacing || i.currentStyle.borderSpacing : a.css("border-spacing")) || 2, a.b = c(h ? i.border || i.currentStyle.borderLeftWidth : a.css("border-left-width")) || 1, s[l] = a, g(a)) }(this, i) })) } }) }(jQuery);



// alert('js working');


$(function () {
    $(".test").colResizable({

        // 'fit', 'flex' or 'overflow'
        resizeMode: 'overflow',
        fixed: false,
        liveDrag: true


    })
});





    // project filter data
    $(document).ready(function(){
        $("#projectinput").on("keyup", function() {
          var value = $(this).val().toLowerCase();
          
          $("#projectlist tr").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
          });
        });
    });

    // item filter data
    $(document).ready(function(){
        $("#iteminput").on("keyup", function() {
          var value = $(this).val().toLowerCase();
          
          $("#itemlist tr").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
          });
        });
    });

