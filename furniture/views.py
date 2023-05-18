from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.generics import ListCreateAPIView, DestroyAPIView

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import Product, Like, Comment, Category, Cart
from .serializers import ProductSerializer, CommentSerializer, CategorySerializer, CartSerializer
from .permissions import IsCommentAuthor


class MyPaginationView(PageNumberPagination):
    page_size = 6
    def get_paginated_response(self, data):
        return super().get_paginated_response(data)

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'create']:
            permissions = [IsAdminUser]
        else:
            permissions = [AllowAny, ]
        return [permission() for permission in permissions]

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = MyPaginationView
    permission_classes = [IsAdminUser, ]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'create']:
            permissions = [IsAdminUser, ]
        else:
            permissions = [AllowAny, ]
        return [permission() for permission in permissions]


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        return context

    @action(detail=False, methods=['get'])
    def search(self, request, pk=None):
        print(request.query_params)
        q = request.query_params.get('q')
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(name__icontains=q) |
                                   Q(description__icontains=q) |
                                   Q(made_in__icontains=q))
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def filter(self, request):
        queryset = self.queryset

        price = request.query_params.get('price')
        category = request.query_params.get('category')
        made_in = request.query_params.get('made_in')
        print(request.query_params)
        if category:
            queryset = queryset.filter(category=category)
        elif made_in:
            queryset = queryset.filter(made_in=made_in)
        elif price == 'asc':
            queryset = queryset.order_by('price')
        elif price == 'desc':
            queryset = queryset.order_by('-price')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@login_required
def toggle_like(request, id):
    product = Product.objects.get(id=id)
    if Like.objects.filter(user=request.user, product=product):
        Like.objects.get(user=request.user, product=product).delete()
    else:
        Like.objects.create(user=request.user, product=product)
    serializer = ProductSerializer(product)
    return Response(serializer.data)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsCommentAuthor, ]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

def write_db(request):
    import csv
    import os
    open('db.csv', 'w').close()
    products = Product.objects.all()
    with open('db.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(('category', 'name', 'price', 'description', 'made_in', 'image'))
        for product in products:
            writer.writerow((product.category, product.name, product.price, product.description, product.made_in, product.image))
    with open('db.csv') as f:
        db = f.read()
    os.remove('db.csv')
    return HttpResponse(db, content_type='application/csv')


class CartGenericApiView(ListCreateAPIView):

    serializer_class = CartSerializer
    
    def get_queryset(self):    
        user = self.request.user
        return Cart.objects.filter(user=user)


class CartDestroyGenericView(DestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer