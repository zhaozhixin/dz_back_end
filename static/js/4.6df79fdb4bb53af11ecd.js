webpackJsonp([4],{"8A3x":function(t,e,a){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var n=a("c2Ch"),r={name:"recommand",components:{},data:function(){return{input_text:"",recommand_text:"",entities:{},activeNames:null}},mounted:function(){},methods:{openGraph:function(t,e){var a=this;Object(n.a)(t,e).then(function(t){a.$store.state.graph_data=t.data}),console.log(this.activeNames),this.$store.dispatch("dialogshowGraph")},reqRecommand:function(){var t=this,e=this.$refs.input_box.$refs.textarea.selectionStart,a=this.input_text.split(/[。|!|?|;|.|；|？|！]/),r=[];for(var s in a)r.push(a[s].length+1);var i=0,o=0;for(var c in r)if(e<(i+=r[c])){o=c;break}for(;0==a[o]&&o>0;)o-=1;console.log(a[o]),Object(n.e)(a[o]).then(function(e){if(200===e.status){if("not found"==e.data||0==e.data.found&&""!=t.recommand_text)return;t.activeNames=0,t.entities=e.data.entities,t.recommand_text=e.data.recommand}})}}},s={render:function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",{staticClass:"order-receivable"},[[a("el-row",{attrs:{gutter:20}},[a("el-col",{attrs:{span:12}},[a("el-card",{staticClass:"box-card"},[a("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[a("span",[t._v("用户输入")]),t._v(" "),a("el-button",{staticStyle:{float:"right",padding:"3px 0"},attrs:{type:"text"},on:{click:function(e){t.reqRecommand()}}},[t._v("生成推荐")])],1),t._v(" "),a("div",[a("el-input",{ref:"input_box",attrs:{type:"textarea",rows:20,placeholder:"请输入内容"},nativeOn:{keyup:function(e){return("button"in e||!t._k(e.keyCode,"enter",13,e.key,"Enter"))&&e.ctrlKey?void t.reqRecommand():null}},model:{value:t.input_text,callback:function(e){t.input_text=e},expression:"input_text"}})],1)]),t._v(" "),a("br"),t._v(" "),a("el-card",{staticClass:"box-card"},[a("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[a("span",[t._v("实体识别")])]),t._v(" "),a("el-row",t._l(t.entities,function(e,n){return a("el-button",{attrs:{size:"small",type:"primary"},on:{click:function(a){t.openGraph(n,e[0])}}},[t._v("\n                "+t._s(n)+":"+t._s(e[0])+"\n            ")])}))],1)],1),t._v(" "),a("el-col",{attrs:{span:12,offset:0}},[a("el-card",{staticClass:"box-card"},[a("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[a("span",[t._v("推荐内容")])]),t._v(" "),a("el-col",[t.recommand_text?a("el-collapse",{staticStyle:{"margin-top":"-21px"},model:{value:t.activeNames,callback:function(e){t.activeNames=e},expression:"activeNames"}},[t._l(t.recommand_text,function(e,n){return t._l(e,function(e,r,s){return a("el-collapse-item",{attrs:{title:r,name:n+s}},t._l(e,function(e,n){return a("div",{domProps:{innerHTML:t._s(e+"&nbsp")}})}))})})],2):t._e()],1)],1)],1)],1)]],2)},staticRenderFns:[]};var i=a("VU/8")(r,s,!1,function(t){a("ASPI")},"data-v-5f3c2e0f",null);e.default=i.exports},ASPI:function(t,e){}});
//# sourceMappingURL=4.6df79fdb4bb53af11ecd.js.map