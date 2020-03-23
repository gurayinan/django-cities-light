"""
Couple djangorestframework and cities_light.

It defines a urlpatterns variables, with the following urls:

- cities-light-api-city-list
- cities-light-api-city-detail
- cities-light-api-region-list
- cities-light-api-region-detail
- cities-light-api-country-list
- cities-light-api-country-detail

If rest_framework (v3) is installed, all you have to do is add this url
include::

    url(r'^cities_light/api/', include('cities_light.contrib.restframework3')),

And that's all !
"""
from rest_framework import viewsets, relations
from rest_framework.serializers import HyperlinkedModelSerializer, IntegerField
from rest_framework import routers

from django.conf.urls import url, include

from ..loading import get_cities_models

Country, Region, City = get_cities_models()


class CitySerializer(HyperlinkedModelSerializer):
    """
    HyperlinkedModelSerializer for City.
    """
    url = relations.HyperlinkedIdentityField(
        view_name='cities-light-api-city-detail')
    country = relations.HyperlinkedRelatedField(
        view_name='cities-light-api-country-detail', read_only=True)
    region = relations.HyperlinkedRelatedField(
        view_name='cities-light-api-region-detail', read_only=True)
    id = IntegerField(read_only=True)

    class Meta:
        model = City
        exclude = ('slug',)


class RegionSerializer(HyperlinkedModelSerializer):
    """
    HyperlinkedModelSerializer for Region.
    """
    url = relations.HyperlinkedIdentityField(
        view_name='cities-light-api-region-detail')
    country = relations.HyperlinkedRelatedField(
        view_name='cities-light-api-country-detail', read_only=True)
    id = IntegerField(read_only=True)

    class Meta:
        model = Region
        exclude = ('slug',)


class CountrySerializer(HyperlinkedModelSerializer):
    """
    HyperlinkedModelSerializer for Country.
    """
    url = relations.HyperlinkedIdentityField(
        view_name='cities-light-api-country-detail')
    id = IntegerField(read_only=True)

    class Meta:
        model = Country
        fields = '__all__'


class CitiesLightListModelViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        """
        Allows a GET param, 'q', to be used against name_ascii.
        """
        queryset = super(CitiesLightListModelViewSet, self).get_queryset()

        if self.request.GET.get('q', None):
            return queryset.filter(name_ascii__icontains=self.request.GET['q'])

        return queryset


class RegionListModelViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        """
        Allows a GET param, 'q', to be used against name_ascii.
        Allows a GET param 'country_id', to be used against filter out country parents.
        """
        queryset = super(RegionListModelViewSet, self).get_queryset()

        if self.request.GET.get('q', None):
            queryset = queryset.filter(name_ascii__icontains=self.request.GET['q'])
        if self.request.GET.get('country_id', None):
            queryset = queryset.filter(country_id=int(self.request.GET['country_id']))

        return queryset


class CityListModelViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        """
        Allows a GET param, 'q', to be used against name_ascii.
        Allows a GET param 'region_id', to be used against filter out region parents.
        """
        queryset = super(CityListModelViewSet, self).get_queryset()

        if self.request.GET.get('q', None):
            queryset = queryset.filter(name_ascii__icontains=self.request.GET['q'])
        if self.request.GET.get('region_id', None):
            queryset = queryset.filter(region_id=int(self.request.GET['region_id']))

        return queryset

class CountryModelViewSet(CitiesLightListModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class RegionModelViewSet(RegionListModelViewSet):
    serializer_class = RegionSerializer
    queryset = Region.objects.all()


class CityModelViewSet(CityListModelViewSet):
    serializer_class = CitySerializer
    queryset = City.objects.all()


router = routers.SimpleRouter()
router.register(r'cities', CityModelViewSet, basename='cities-light-api-city')
router.register(r'countries', CountryModelViewSet,
                basename='cities-light-api-country')
router.register(r'regions', RegionModelViewSet,
                basename='cities-light-api-region')


urlpatterns = [
    url(r'^', include(router.urls)),
]
