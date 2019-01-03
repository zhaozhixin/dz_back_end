from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^$',views.index,name='index'),
    url(r'req_recommand',views.req_recommand,name='req_recommand'),
    url(r'entity_graph', views.entity_graph, name='entity_graph'),
    url(r'req_search', views.req_search, name='req_search'),
    url(r'req_qa', views.req_qa, name='req_qa'),
]