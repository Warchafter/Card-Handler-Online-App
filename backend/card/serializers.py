from django.db.models.fields.related import ManyToManyField
from rest_framework import serializers

from core.models import Card, CardCategory, CardColor, CardStatus


class CardCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = CardCategory
        fields = ('id', 'name')
        read_only_fields = ('id',)


class CardColorSerializer(serializers.ModelSerializer):

    class Meta:
        model = CardColor
        fields = ('id', 'name')


class CardStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = CardStatus
        fields = ('id', 'name')
        read_only_fields = ('id',)


class CardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Card
        fields = ('id', 'title', 'text', 'creation_date',
                  'category', 'status', 'color', 'user')
        read_only_fields = ('id', 'user')
        ordering = ('id',)


class CardListSerializer(CardSerializer):
    category = CardCategorySerializer(many=False, read_only=True)
    color = CardColorSerializer(many=False, read_only=True)
    status = CardStatusSerializer(many=False, read_only=True)
