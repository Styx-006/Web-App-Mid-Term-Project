from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
from .serializers import BusinessSerializer, GameStateSerializer, PurchaseSerializer, PrestigeSerializer
from .models import AchievementClaim, GlobalUpgrade, Business, OwnedBusiness, PlayerProgress
from .services.progression import is_unlocked, upgrade_cost, MAX_UPGRADE_LEVEL, global_status, prestige_status
from .services.rewards import DAILY_REWARD, daily_status, achievement_status
from .services.economy import bulk_quote, credit_cash, settle_income, snapshot


def locked_player(user):
    PlayerProgress.objects.get_or_create(user=user)
    return PlayerProgress.objects.select_for_update().get(user=user)


class BusinessViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer


class GameViewSet(viewsets.ViewSet):


    @action(detail=False, methods=['get'], url_path='state')
    @transaction.atomic
    def state(self, request):
        player = locked_player(request.user)
        earned = settle_income(player, timezone.now())
        player.save()
        data = snapshot(player)
        data['income_earned'] = format(earned, '.2f')
        return Response(GameStateSerializer(data).data)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def work(self, request):
        player = locked_player(request.user)
        now = timezone.now()

        if player.last_work_at and (now - player.last_work_at).total_seconds() < 1:
            return Response({'detail': 'Wait one second between work actions.'}, status=429)
        settle_income(player, now)
        credit_cash(player, Decimal(1))
        player.total_work_actions += 1
        player.last_work_at = now
        player.save()
        data = snapshot(player)
        return Response(GameStateSerializer(data).data)

    @action(detail=False, methods=['post'], url_path=r'businesses/(?P<business_id>[0-9]+)/buy')
    @transaction.atomic
    def buy_business(self, request, business_id):
        serializer = PurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mode = serializer.validated_data['quantity']
        player = locked_player(request.user)
        business = get_object_or_404(Business, pk=business_id)
        now = timezone.now()
        settle_income(player, now)
        if not is_unlocked(player, business):
            return Response({'detail': 'Reach the lifetime earnings requirement to unlock this business.'}, status=403)
        owned = OwnedBusiness.objects.filter(player=player, business=business).first()
        quantity = owned.quantity if owned else 0
        if business.base_price <= 0 or business.income_per_second < 0:
            return Response({'detail': 'This business has invalid pricing or income.'}, status=400)
        quote = bulk_quote(business, quantity, player.money, mode)
        price = Decimal(quote['cost'])
        count = quote['quantity']
        if count == 0 or player.money < price:
            player.save()
            return Response({'detail': 'You do not have enough money.'}, status=400)
        player.money -= price


        player.last_income_at = now
        player.save()
        if owned:
            owned.quantity += count
            owned.save(update_fields=['quantity'])
        else:
            OwnedBusiness.objects.create(player=player, business=business, quantity=count)
        player.discovered_businesses.add(business)
        player.total_businesses_purchased += count
        player.most_business_types = max(player.most_business_types, player.owned_businesses.count())
        player.save()
        data = snapshot(player)
        return Response(GameStateSerializer(data).data)

    @action(detail=False, methods=['post'], url_path=r'rewards/daily')
    @transaction.atomic
    def claim_daily(self, request):
        player = locked_player(request.user)
        now = timezone.now()
        if not daily_status(player)['available']:
            return Response({'detail': 'Your daily reward is available 24 hours after your last claim.'}, status=400)
        settle_income(player, now)
        credit_cash(player, DAILY_REWARD)
        player.total_daily_claims += 1
        player.last_daily_claim_at = now
        player.save()
        data = snapshot(player)
        return Response(GameStateSerializer(data).data)

    @action(detail=False, methods=['post'], url_path=r'achievements/(?P<code>[-a-zA-Z0-9_]+)/claim')
    @transaction.atomic
    def claim_achievement(self, request, code):
        player = locked_player(request.user)
        settle_income(player, timezone.now())
        achievement = next((item for item in achievement_status(player) if item['code'] == code), None)
        if achievement is None:
            return Response({'detail': 'Achievement not found.'}, status=404)
        if achievement['claimed'] or not achievement['eligible']:
            return Response({'detail': 'This achievement is already claimed or not yet earned.'}, status=400)
        AchievementClaim.objects.create(player=player, code=code)
        player.achievement_points += achievement['points']
        player.total_points_earned += achievement['points']
        player.save()
        data = snapshot(player)
        return Response(GameStateSerializer(data).data)

    @action(detail=False, methods=['post'], url_path=r'businesses/(?P<business_id>[0-9]+)/upgrade')
    @transaction.atomic
    def upgrade_business(self, request, business_id):
        player = locked_player(request.user)
        owned = get_object_or_404(OwnedBusiness.objects.select_related('business'), player=player, business_id=business_id)
        now = timezone.now()
        settle_income(player, now)
        if owned.upgrade_level >= MAX_UPGRADE_LEVEL:
            return Response({'detail': 'This business is fully upgraded.'}, status=400)
        cost = upgrade_cost(owned)
        if cost <= 0 or player.money < cost:
            return Response({'detail': 'You do not have enough cash for this upgrade.'}, status=400)
        player.money -= cost
        player.last_income_at = now
        player.total_upgrades_purchased += 1
        player.save()
        owned.upgrade_level += 1
        owned.save(update_fields=['upgrade_level'])
        data = snapshot(player)
        return Response(GameStateSerializer(data).data)

    @action(detail=False, methods=['post'], url_path=r'global-upgrades/(?P<code>[-a-zA-Z0-9_]+)/buy')
    @transaction.atomic
    def buy_global_upgrade(self, request, code):
        player = locked_player(request.user)
        item = next((item for item in global_status(player) if item['code'] == code), None)
        if item is None:
            return Response({'detail': 'Global upgrade not found.'}, status=404)
        if item['level'] >= item['max_level']:
            return Response({'detail': 'This global upgrade is maxed out.'}, status=400)
        if player.achievement_points < item['next_cost']:
            return Response({'detail': 'Earn and claim more achievement points first.'}, status=400)
        now = timezone.now()
        settle_income(player, now)
        player.achievement_points -= item['next_cost']
        player.last_income_at = now
        player.save()
        upgrade, created = GlobalUpgrade.objects.get_or_create(player=player, code=code)
        if not created:
            upgrade.level += 1
            upgrade.save(update_fields=['level'])
        data = snapshot(player)
        return Response(GameStateSerializer(data).data)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def prestige(self, request):
        serializer = PrestigeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        player = locked_player(request.user)
        now = timezone.now()
        settle_income(player, now)
        if not prestige_status(player)['available']:
            return Response({'detail': 'Earn the required cash during this run before prestiging.'}, status=400)
        player.most_business_types = max(player.most_business_types, player.owned_businesses.count())
        player.owned_businesses.all().delete()
        player.money = 0
        player.run_earnings = 0
        player.prestige_count += 1
        player.last_income_at = now
        player.save()
        data = snapshot(player)
        return Response(GameStateSerializer(data).data)
