from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
import json
from django.http import HttpResponse
from py2neo import Graph
import grpc
from . import msg_pb2
from . import msg_pb2_grpc
import re

# Create your views here.

g = Graph("bolt://localhost:7475", password='123')
style_dict = {
    "Person": "rgba(111,200,184,1)",
    "Interview": "rgba(255,214,24,1)",
    "Activity": "rgba(47,195,47,1)",
    "Meeting": "rgba(86,185,247,1)",
    "Talking": "rgba(234,180,4,1)",
    "Org": "rgba(222,103,44,1)",
    "Area": "rgba(222,103,44,1)",
    "Adminregion": "rgba(222,103,44,1)",
    "Autoregion": "rgba(222,103,44,1)",
    "Convention": "rgba(222,103,44,1)",
    "Country": "rgba(222,103,44,1)",
    "Municipality": "rgba(222,103,44,1)",
    "Personnel": "rgba(222,103,44,1)",
    "Province": "rgba(222,103,44,1)",
    "Report": "rgba(222,103,44,1)",
    "SubOrg": "rgba(222,103,44,1)",
    "Session": "rgba(222,103,44,1)",
}


def index(request):
    return render(request, 'index.html')

def req_recommand(request):
    question = request.GET.get('input_text')

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = msg_pb2_grpc.MsgServiceStub(channel)
        response = stub.GetMsg(msg_pb2.MsgRequest(question=question))

    print("Client received: " + response.answer)
    if response.answer == 'not found':
        return HttpResponse('not found')

    answer = json.loads(response.answer)
    answer_ret = answer['answer']
    try:
        for i in range(len(answer_ret)):
            for k, v in answer_ret[i].items():
                for j in range(len(v)):
                    res = v[j].split('|||')
                    if len(res) > 1:
                        answer_ret[i][k][j] = "<a href='" + res[1] + "' target='_blank'>" + res[0] + "</a>"
    except Exception as e:
        pass

    msg = json.dumps({
        'entities': answer['entities'],
        'recommand': answer_ret,
    })

    return HttpResponse(msg)

def req_search(request):
    value = request.GET.get('input_text')
    query = "MATCH (e) where e.value = '{0}'return e".format(value)
    res = g.run(query).data()
    entities = {}

    for item in res:
        node = item['e']
        props = dict(node)
        label = list(node.labels)[0]
        entities[node.identity] = {'value': props['value'], 'label': label}

    msg = json.dumps({'entities': entities})
    return HttpResponse(msg)

def req_qa(request):
    question = request.GET.get('input_text')

    with grpc.insecure_channel('localhost:50001') as channel:
        stub = msg_pb2_grpc.MsgServiceStub(channel)
        response = stub.GetMsg(msg_pb2.MsgRequest(question=question))

    print("Client received: " + response.answer)
    if response.answer == 'not found':
        return HttpResponse('not found')

    answer = json.loads(response.answer)
    print(answer)

    msg = json.dumps({
        'entities': answer['entities'],
        'recommand': answer['answer'],
    })
    return HttpResponse(msg)

def entity_graph(request):
    value = request.GET.get('value')
    label = request.GET.get('label')
    label = label[0].upper() + label[1:]
    query1 = "MATCH (e:{0}) where e.value = '{1}' return e".format(label,value)
    query2 = "MATCH (h)-[r]->(e:{0}) where e.value = '{1}' return h,type(r) as r,r.name as n limit 50".format(label,value)
    query3 = "MATCH (e:{0})-[r]->(t) where e.value = '{1}' return t,type(r) as r,r.name as n limit 50".format(label,value)

    res1 = g.run(query1).data()
    res2 = g.run(query2).data()
    res3 = g.run(query3).data()

    res = {
        "nodes": [],
        "links": [],
    }
    e_id = None

    for item in res1:
        node = item['e']
        props = dict(node)
        label = list(node.labels)[0]
        label_split = '\n'.join(re.findall(r'.{3}', label))
        e_id = node.identity
        res["nodes"].append({
            "id": node.identity,
            "label": label_split,
            "props": props,
            "style": {"label": node["value"],"fillColor": style_dict[label]},
        })

    for item in res2:
        node = item['h']
        rel = item['r']
        rel_name = item['n']
        props = dict(node)
        label = list(node.labels)[0]
        res["nodes"].append({
            "id": node.identity,
            "label": label,
            "props": props,
            "style": {"label": node["value"], "fillColor": style_dict[label]},
        })
        res["links"].append({
            "id": str(node.identity) + '-' + str(e_id),
            "from": node.identity,
            "to": e_id,
            "style": {"fillColor":"red", "toDecoration":"arrow", "label": rel},
            "name": rel_name,
        })

    for item in res3:
        node = item['t']
        rel = item['r']
        rel_name = item['n']
        print(rel_name)
        props = dict(node)
        label = list(node.labels)[0]
        res["nodes"].append({
            "id": node.identity,
            "label": label,
            "props": props,
            "style": {"label": node["value"],"fillColor": style_dict[label]},
        })
        res["links"].append({
            "id": str(e_id) + '-' + str(node.identity),
            "from": e_id,
            "to": node.identity,
            "style": {"fillColor": "red", "toDecoration": "arrow", "label": rel},
            "name": rel_name,
        })

    msg = json.dumps(res)
    return HttpResponse(msg)
