from rest_framework import serializers
from .models import Product, Comment, Category, Cart

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'price', 'description', 'made_in', 'image')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.category:
            representation['category'] = instance.category.name
        representation['likes'] = instance.likes.all().count()
        action = self.context.get('action')
        if action == 'retrieve':
            representation['comments'] = CommentSerializer(instance.comments.all(), many=True).data
        else:
            representation['comments'] = instance.comments.all().count()
        return representation


    def validate_name(self, name):
        if Product.objects.filter(slug=name.lower().replace(' ', '-')).exists():
            raise serializers.ValidationError('Product with such name already exists')
        return name

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ('user',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.email
        return representation
    
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ('product', 'quantity')

    # def validate(self, attrs):

    def create(self, validated_data):
        # VALIDATED_DATA -> VALIDATED_DATA {'product': <Product: samsung note 20 ultra>, 'quantity': 1}
        user = self.context.get('request').user
        validated_data['user'] = user
        return super().create(validated_data)