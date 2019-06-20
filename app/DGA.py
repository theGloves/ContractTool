## python 3.6.1
import json
import numpy as np
import operator
import time
from app.CNF.CNF import *
import copy
import re

class GNode:
    def __init__(self):
        self.id = 0
        self.data = []
        self.edge = []
        self.children = []
    
    def addEdge(self, edge):
        for i in range(len(self.edge)):
            if self.edge[i] == edge:
                return
        self.edge.append(edge)

    def addChild(self, child):
        for i in range(len(self.children)):
            if self.children[i] == child:
                return 
        self.children.append(child)
    
    def getId(self):
        return self.id

    def getchildren(self):
        return self.children

class St_node:                                       # 定义了状态机中一个合理状态节点
    def __init__(self, Id, state, graph):
        self.Id = Id               
        self.state = state
        self.graph = graph
    def print_content(self):
        print(self.Id)
        print(self.state)

class Transfer:
    def __init__(self, current, action, newS):
        self.current = current
        self.action = action
        self.newS = newS
    def print_content(self):
        print("==========Transfer==========")
        print(self.current)
        print(self.action)
        print(self.newS)


class GraphNode:
    def __init__(self, title):
        self.premise = CNF() # 逻辑表达式
        self.title = title
        self.flag = True
        self.ActionInPre = False

    def buildPremise(self, premise):
        clause = re.split('[||&&]',premise)
        for t in range(len(clause)):
            if "Term" not in clause[t]:
                print(clause[t])
                self.ActionInPre = True
        self.premise.build(premise)

class Graph:
    def __init__(self, n):
        # 图采用邻接矩阵来保存，
        # 矩阵matrix的元素是edge结构体的list
        # matrix[i][t]表示vertex[i]到vertex[t]的边
        # vertexList和matrix的顺序一一对应
        self.matrix = [[[]*n for i in range(n)] for _ in range(n)]
        self.vertexList = []
        self.valueMap = {}
    def addNode(self, graphNode):
        self.vertexList.append(graphNode)
        postfix=[".Sat",".Exp",".Vio"]
        for i in range(len(postfix)):
            key = graphNode.title+postfix[i]
            self.valueMap[key]=False

def getPerson(jsondata):
    actperson = []
    stateNum = len(jsondata)
    for i in range(stateNum):
        actperson.append(jsondata[i]["Obligor"])
    return actperson

def generate(inputdate):
    jsondata = json2python(inputdate)
    # state num
    StateNum = len(jsondata)
    actperson = getPerson(jsondata)
    print(actperson)
    # =======================Step 1================================
    # initial state - 1*n vector
    initState = np.ones(StateNum)#.astype(int)
    for i in range(StateNum):
        # no dependence with others
        if jsondata[i]['premise'] == None or jsondata[i]['premise'] =="":
            initState[i] = 2
    print("initial state:", initState)

    # =======================Step 2================================
    # 根据前提构建有向无环图
    graph = BuildGraph(jsondata, StateNum)
    print("matrix:")
    print(graph.matrix)
    # =======================Step 3================================
    # 广度优先搜索（队列辅助实现），寻找所有合理的状态机节点
    id = 0    
    chmap = {2:'Bas', 3:'Sat', 4:'Exp', 5:'Vio'}
    st = St_node(0, initState, graph)
    queue = []
    transfer = []
    queue.append(st)
    gnodelist = []
    # BFS
    while len(queue):
        # input("按任意键继续")

        st = queue.pop(0)
        # 直接复制，防止浅拷贝错误
        state = st.state.copy()
        graph = copy.deepcopy(st.graph)

        print("####################################################")
        print("current state:")
        print(state)

        # =======================Step 3.1================================
        # 更新图和边
        graph = updateGraph(graph, state)
        done = 0
        for i in range(StateNum):
            if state[i] >= 3:
                done+=1
        # 迭代边界-所有承诺状态处于终态(3,4,5)
        if done == StateNum:
            continue

        # =======================Step 3.2================================
        # 得到不相关承诺集合的变化组合
        uclist = getUcList(state, graph, graph.valueMap)

        # 严重错误，不应该出现
        if len(uclist)==0:
            print("[fatal_error] func getUncorrelated return nil! check logic")
            continue
        print(uclist)
        # =======================Step 3.3================================
        # 生成新的状态
        # class Gnode:
        #     currentState - self.data
        #     edge - { ([pid], [ [person, action], ... ] ), ...  } - self.edge
        #     child - self.children
        for i in range(len(uclist)):
            # id = id + 1
            newState = st.state.copy()
            newGraph = copy.deepcopy(graph)

            action = "("
            currentAction = []
            for t in range(len(uclist[i])):
                index = uclist[i][t][0]
                change = uclist[i][t][1]
                newState[index] = change
                action = action+chmap[change]+str(index)+", "
                currentAction.append([actperson[index], chmap[change], index])
            action = action[:-2] + ')'
            newGraph = updateGraph(newGraph, newState)
            for t in range(StateNum):
                if newState[t] == 1 and newGraph.vertexList[t].premise.getValue(newGraph.valueMap) == True:
                    newState[t] = 2
            # Generate Game Tree Node ==================================
            gnodelist, pnode, id = findGnode(gnodelist, state, id)
            gnodelist, cnode, id = findGnode(gnodelist, newState, id)
            pid = pnode.getId()
            edge = [ [pid], currentAction ]
            print(edge)
            pnode.addChild(cnode)
            cnode.addEdge(edge)
            # ==========================================================
            newSt = St_node(id, newState, newGraph)
            queue.append(newSt)
            tran = Transfer(state, action, newState)
            transfer.append(tran)

    for i in range(len(gnodelist)):
            print(gnodelist[i], " id: ",gnodelist[i].id, " Gnodestate: ", gnodelist[i].data, " edge:",gnodelist[i].edge, " child:", gnodelist[i].children)

    return (initState, transfer, gnodelist[0])

def isequle(list1, list2):
    n = len(list1)
    for i in range(n):
        if list1[i] != list2[i]:
            return False
    return True

def findGnode(NodeList, state_np, id):
    state = state_np.astype(int).tolist()
    for i in range(len(NodeList)):
        if isequle(NodeList[i].data, state) == True:
            return (NodeList, NodeList[i], id)
    node = GNode()
    node.data = state
    node.edge = []
    node.id = id
    NodeList.append(node)
    return (NodeList, node, id+1)

def updateGraph(graph, state):
    chmap = {2:'Bas', 3:'Sat', 4:'Exp', 5:'Vio'}
    stateNum = len(state)
    for i in range(stateNum):
        if state[i]>=3:
            for t in range(len(graph.vertexList)):
                key = "Term"+str(i+1)+"."+chmap[state[i]]
                # graph.vertexList[t].premise.deleteLiteral(key)
                graph.valueMap[key] = True
        # 从状态开始，检查哪些节点的前提已经不可能满足
    return graph

# 构建有向无环图

def BuildGraph(jsondata, StateNum):
    chmap = {'Sat':3, "Exp":4, "Vio":5}
    graph = Graph(StateNum)

    # 生成GraphNode
    for i in range(StateNum):
        title = "Term"+str(i+1)
        node = GraphNode(title)
        premise = jsondata[i]['premise']
        print("commitment premise: ", premise)
        if premise == None:
            premise = ""
        # 根据前提构建CNF表达式
        node.buildPremise(premise)
        # 加入graph
        graph.addNode(node)
    
    # 生成matrix矩阵
    for i in range(StateNum):
        premise = jsondata[i]['premise']
        if premise == None:
            print("None")
            premise = ""
        clause = re.split('[||&&]',premise)
        for t in range(len(clause)):
            if "Term" not in clause[t]:
                continue
            tmp = clause[t].split('.')
            index = int(tmp[0][4:]) - 1
            state = chmap[tmp[1]]
            graph.matrix[i][index].append(state)
    return graph
        
# middleware
def combination(res, ith, tmplist, nextState, index):
    if ith == len(nextState) and len(tmplist):
        res.append(tmplist)
        return res

    for t in range(len(nextState[ith])):
        tmp = tmplist.copy()
        
        tmp.append([index[ith], nextState[ith][t]])
        res = combination(res, ith+1, tmp, nextState, index)
    return res

def recursion(cnf, valueMap, TermFlag, index):
    if index == len(TermFlag):
        return cnf.getValue(valueMap)
    if TermFlag[index] == True:
        return recursion(cnf, valueMap, TermFlag, index+1)
    
    res = False
    postfix=[".Sat",".Exp",".Vio"]
    for i in range(len(postfix)):
        key = "Term"+str(index+1)+postfix[i]
        valueMap[key] = True
        res = res or recursion(cnf, valueMap, TermFlag, index+1)
        valueMap[key] = False
    return res

# 暴力求解
def isContradiction(cnf, valueMap, stateNum):
    postfix=[".Sat",".Exp",".Vio"]
    cnf_tmp = copy.deepcopy(cnf)
    isTrue = [False] * stateNum

    for i in range(stateNum):
        flag = False
        for t in range(len(postfix)):
            key = "Term"+str(i+1)+postfix[t]
            flag = flag or valueMap[key]
        isTrue[i] = flag
    
    return not recursion(cnf_tmp, valueMap, isTrue, 0)

def getUcList(state, graph, valueMap):    
    stateNum = len(state)
    # 得到每一个承诺的次态
    nextStates = []
    print(valueMap)
    for i in range(stateNum):
        tmp = []
        preRes = graph.vertexList[i].premise.getValue(valueMap)
        if state[i] == 1 :
            # if graph.vertexList[i].flag == False: # 前提无法满足了
            if isContradiction(graph.vertexList[i].premise, valueMap, stateNum)==True:
                tmp.append(4)
            if preRes == True: #前提为满足式
                if graph.vertexList[i].ActionInPre == True:
                    tmp.append(4)
                tmp.append(2)
        elif state[i] == 2:
            tmp.append(3)
            tmp.append(5)
        nextStates.append(tmp)

    zeroslist = []
    # 找到所有的不相关承诺,入度为0的点\入度不为0但是前提满足
    for i in range(stateNum):
        if state[i]==1 and graph.vertexList[i].premise.getValue(valueMap) == True:
            zeroslist.append(i)
            continue
        # 判断是不是矛盾式，如果是矛盾式。那么就只能向4变化
        elif state[i]==1 and isContradiction(graph.vertexList[i].premise, valueMap, stateNum) == True:
            zeroslist.append(i)
        if state[i] == 2:
            zeroslist.append(i)
            continue
        
        flag = True
        for t in range(stateNum):
            if len(graph.matrix[i][t])>0:
                flag = False
        if flag == True and state[i]<3:
            zeroslist.append(i)
    print(zeroslist)
    currentChange = []
    for index in zeroslist:
        currentChange.append(nextStates[index])
    # combination
    res = []
    tmp = []
    print("currentChange: ", currentChange)
    print("index: ", zeroslist)
    res = combination(res, 0, tmp, currentChange, zeroslist)
    return res

def json2python(JsonData):
    print ("before decoding:")
    print (JsonData)
    data = json.loads(JsonData)

    print ("after decoding:")
    print (data)
    return data

def save_transfer(initState, DGA, contract_id):
    gt_file = {"FsmArray": []}

    transfer_file = {'InitStatus':str(initState.astype(int).tolist()), "FsmArray":[]}
    
    for i in range(0, len(DGA)):
        current_status = str(DGA[i].current.astype(int).tolist())
        new_status = str(DGA[i].newS.astype(int).tolist())
        action = str(DGA[i].action)
        t = {'CurrentStatus': str(current_status), 'Action': action, 'NewStatus': str(new_status)}
        #print(transfers)
        transfer_file['FsmArray'].append(t)
    
    with open('./DGA/'+contract_id, 'w') as fs:
        fs.write(json.dumps(transfer_file, indent=2))

def GenerateDGA(contract, contract_id):
    time_start=time.time()
    initState, DGA, _ = generate(contract)
    time_end=time.time()
    with open('times.log', 'a') as f:
        f.write(str(contract_id)+": " + str(time_end-time_start))
        f.write("\n")

    save_transfer(initState,DGA,contract_id)

if __name__ == '__main__':

    data = input("jsonData")
    initState, transfer, DFA= generate(data)
    save_transfer(initState, transfer,"tmp")
    #painting2(DFA)

