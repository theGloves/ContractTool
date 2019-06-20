$(document).ready(function () {
  var contracId = window.location.pathname.substr(5, window.location.pathname.length);
  $.ajax({
    async: false,    //表示请求是否异步处理
    type: "post",    //请求类型
    url: "/getDGA",//请求的 URL地址
    dataType: "json",//返回的数据类型
    data: {
      'contractId': contracId
    },
    success: function (data) {
      console.log(data.fsm);  //在控制台打印服务器端返回的数据
      // /let content = JSON.parse(data)
      fsm = data.fsm
      create()
    },
    error: function (data) {
    }
  });
});

function create() {
  let state_array = fsm['FsmArray']

  let size = state_array.length
  var g = new dagreD3.graphlib.Graph().setGraph({ directed: true });
  var state_ar = [];
  let InitStatus = fsm['InitStatus'];
  console.log(InitStatus);
  var j = 0;
  for (let i = 0; i < size; i++) {
    state_ar[j] = state_array[i]['CurrentStatus']
    j = j + 1;
    state_ar[j] = state_array[i]['NewStatus']
    j = j + 1;
  }
  state_enum = { '1': 'Act', '2': 'Bas', '3': 'Sat', '4': 'Exp', '5': 'Vio' }
  num = { '0': '1', '1': '2', '2': '3', '3': '4', '4': '5', '5': '6', '6': '7', '7': '8', '8': '9', '9': '10' }
  let len = state_ar.length

  let color = ['', '#e0ffff', '#ADFF2F', '#00CD00', '#FFD700', '#FF6347']
  for (let i = 0; i < len; i++) {
    let state_list = JSON.parse(state_ar[i])
    des = ""
    for (let s in state_list) {
      des = des + "<br>Term" + num[String(s)]
      des = des + ' ' + state_enum[state_list[s]]
    }
    g.setNode(state_ar[i], {
      label: function () {
        let table = document.createElement("table");
        let tr = document.createElement('tr')
        table.style.cssText = 'border-style:hidden;color:#333;font-size:17px'
        for (let j = 0; j < state_list.length; j++) {
          td = document.createElement("td");
          td.innerText = String(state_list[j])
          if (j == 0) {
            td.style.cssText = "background-color:" + color[state_list[j]] + "; border-top: 1.5px solid #333; border-left: 1.5px solid #333; border-bottom: 1.5px solid #333; border-radius: 5px 0 0 5px;"
          } else if (j == state_list.length - 1) {
            td.style.cssText = "background-color:" + color[state_list[j]] + "; border-top: 1.5px solid #333; border-bottom: 1.5px solid #333; border-right: 1.5px solid #333;border-radius: 0 5px 5px 0;"
          } else {
            td.style.cssText = "background-color:" + color[state_list[j]] + "; border-top: 1.5px solid #333; border-bottom: 1.5px solid #333;"
          }
          tr.append(td)
        }
        table.append(tr)
        return table;
      },
      padding: 0,
      rx: 5,
      ry: 5,
      description: des
    })
  }
  //alert(td_set['td_31'])
  for (let i = 0; i < size; i++) {
    g.setEdge(state_array[i]['CurrentStatus'], state_array[i]['NewStatus'], { label: state_array[i]['Action'] });
  }
  $("#DGAgraph").css('border-style', 'hidden')
  $("#DGAgraph").css('overflow', 'visible')
  // document.getElementById("right").innerHTML = "<svg width=1140 height=560><g/></svg>";
  var svg = d3.select("svg"), inner = svg.select("g");
  var zoom = d3.zoom().on("zoom", function () {
    inner.attr("transform", d3.event.transform);
  });
  svg.call(zoom);
  // Set up zoom support
  // Create the renderer
  var render = new dagreD3.render();
  // Run the renderer. This is what draws the final graph.
  render(inner, g);
  var styleTooltip = function (name, description) {
    return "<p class='name'>" + name + "</p><p class='description'>" + description + "</p>";
  };

  // All Paths
  function weight(e) {
    return 1;
  }
  AllPaths = dagreD3.graphlib.alg.dijkstra(g, InitStatus, weight)

  inner.selectAll("g.node")
    .on("click", function (d) {
      console.log(d);
      console.log(g.edge("[2, 1, 1, 1, 1, 1, 1, 1, 1]","[3, 2, 1, 1, 1, 1, 1, 1, 1]").label);
      console.log(AllPaths);
      console.log(AllPaths["[3, 2, 1, 1, 1, 1, 1, 1, 1]"].predecessor);
      currentStatus = d;
      path = "";
      while (currentStatus!=InitStatus) {
        pre = AllPaths[currentStatus].predecessor;
        padding = path.length==0?"":" -> " 
        path = g.edge(pre, currentStatus).label + padding + path;
        currentStatus = pre;
      }
      console.log(path);
    })
    .attr("title", function (v) { return styleTooltip(v, g.node(v).description) });

  var initialScale = 0.7;
  //alert(svg.attr("width"))
  //alert(g.graph().width)
  svg.call(zoom.transform, d3.zoomIdentity.translate((svg.attr("width") - g.graph().width * initialScale) / 2 + 5, 50).scale(initialScale));
  //svg.attr('height', g.graph().height * initialScale + 40);
}

// function Vertex() {
//   if (!(this instanceof Vertex))
//     return new Vertex();
//   this.color = this.WHITE; //初始为 白色
//   this.pi = null; //初始为 无前驱
//   this.d = null; //时间戳 发现时
//   this.f = null; //时间戳 邻接链表扫描完成时
//   this.edges = null; //由顶点发出的所有边
//   this.value = null; //节点的值 默认为空
// }
// Vertex.prototype = {
//   constructor: Vertex,
//   WHITE: 'white', //白色
//   GRAY: 'gray', //灰色
//   BLACK: 'black', //黑色
// }

// function DFS(g) {
//   let t = 0; //时间戳
//   for (let v of g.vertexs) { //让每个节点都作为一次源节点
//     if (v.color == v.WHITE) DFSVisit(g, v);
//   }
//   function DFSVisit(g, v) {
//     t = t + 1; //时间戳加一
//     v.d = t;
//     v.color = v.GRAY;
//     let sibling = v.edges;
//     while (sibling != null) {
//       let index = sibling.index;
//       let n = g.getNode(index);
//       if (n.color == n.WHITE) {
//         n.pi = v;
//         DFSVisit(g, n); //先纵向找
//       }
//       sibling = sibling.sibling; //利用递归的特性来回溯
//     }
//     v.color = v.BLACK;
//     t = t + 1; //时间戳加一
//     v.f = t;
//   }
// }