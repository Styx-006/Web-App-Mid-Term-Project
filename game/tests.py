from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from game.models import PlayerProgress


class StarterApiTests(APITestCase):
    def test_registration_login_and_private_state(self):
        credentials = {'username': 'test_tycoon', 'password': 'River!Company73Strong'}
        response = self.client.post('/api/accounts/register/', credentials)
        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.data)
        self.assertEqual(self.client.get('/api/game/state/').status_code, 401)
        response = self.client.post('/api/accounts/login/', credentials)
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        other = User.objects.create_user(username='other', password='Other!Strong73')
        PlayerProgress.objects.create(user=other, money=900)
        response = self.client.get('/api/game/state/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'test_tycoon')
        self.assertEqual(response.data['money'], '0.00')
        self.assertEqual(self.client.patch('/api/game/state/', {'money': '999'}).status_code, 405)
        self.assertEqual(PlayerProgress.objects.get(user__username='test_tycoon').money, 0)


from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
from django.utils import timezone
from game.models import Business, OwnedBusiness


class EconomyApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='Test!Pass734')
        self.player = PlayerProgress.objects.create(user=self.user)
        self.business = Business.objects.create(name='Lemonade Stand', base_price=10, income_per_second=1)
        self.client.force_authenticate(self.user)

    def test_work_awards_one_and_rejects_rapid_repeat(self):
        now = timezone.now()
        with patch('game.views.timezone.now', return_value=now):
            self.assertEqual(self.client.post('/api/game/work/').status_code, 200)
            self.assertEqual(self.client.post('/api/game/work/').status_code, 429)
        self.player.refresh_from_db()
        self.assertEqual(self.player.money, 1)
        self.assertEqual(self.player.lifetime_earnings, 1)

    def test_cannot_buy_without_money(self):
        response = self.client.post(f'/api/game/businesses/{self.business.id}/buy/')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(OwnedBusiness.objects.filter(player=self.player).exists())

    def test_purchase_scaling_and_no_retroactive_income(self):
        self.player.money = 100
        self.player.last_income_at = timezone.now() - timedelta(hours=1)
        self.player.save()
        response = self.client.post(f'/api/game/businesses/{self.business.id}/buy/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['money'], '90.00')
        self.assertEqual(response.data['businesses'][0]['next_price'], '11.50')
        self.assertEqual(response.data['income_per_second'], '1.00')
        response = self.client.post(f'/api/game/businesses/{self.business.id}/buy/')
        self.assertEqual(response.data['money'], '78.50')
        self.assertEqual(response.data['businesses'][0]['quantity'], 2)

    def test_offline_income_is_not_counted_twice(self):
        OwnedBusiness.objects.create(player=self.player, business=self.business, quantity=2)
        now = timezone.now()
        self.player.last_income_at = now - timedelta(seconds=60)
        self.player.save()
        with patch('game.views.timezone.now', return_value=now):
            first = self.client.get('/api/game/state/')
            second = self.client.get('/api/game/state/')
        self.assertEqual(first.data['money'], '120.00')
        self.assertEqual(first.data['income_earned'], '120.00')
        self.assertEqual(second.data['money'], '120.00')
        self.assertEqual(second.data['income_earned'], '0.00')
        self.player.refresh_from_db()
        self.assertEqual(self.player.lifetime_earnings, Decimal('120'))

    def test_actions_require_authentication(self):
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.post('/api/game/work/').status_code, 401)
        self.assertEqual(self.client.post(f'/api/game/businesses/{self.business.id}/buy/').status_code, 401)


class BulkAndRewardTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='rewards-player')
        self.player = PlayerProgress.objects.create(user=self.user, money=1000)
        self.business = Business.objects.create(name='Stand', base_price=10, income_per_second=1)
        self.client.force_authenticate(self.user)
        self.buy_url = f'/api/game/businesses/{self.business.id}/buy/'

    def test_buy_ten_uses_sum_of_scaled_prices(self):
        from game.services.economy import purchase_price
        cost = sum(purchase_price(self.business, i) for i in range(10))
        response = self.client.post(self.buy_url, {'quantity': '10'})
        self.assertEqual(response.status_code, 200)
        self.player.refresh_from_db()
        self.assertEqual(self.player.money, Decimal('1000') - cost)
        self.assertEqual(OwnedBusiness.objects.get(player=self.player).quantity, 10)

    def test_buy_max_is_affordable_and_maximal(self):
        from game.services.economy import purchase_price
        response = self.client.post(self.buy_url, {'quantity': 'max'})
        self.assertEqual(response.status_code, 200)
        self.player.refresh_from_db()
        owned = OwnedBusiness.objects.get(player=self.player)
        self.assertGreater(owned.quantity, 0)
        self.assertGreaterEqual(self.player.money, 0)
        self.assertLess(self.player.money, purchase_price(self.business, owned.quantity))

    def test_invalid_quantity_and_insufficient_bulk_do_not_purchase(self):
        for value in ('0', '-1', 'all', 10, True):
            self.assertEqual(self.client.post(self.buy_url, {'quantity': value}, format='json').status_code, 400)
        self.player.money = 10
        self.player.save()
        self.assertEqual(self.client.post(self.buy_url, {'quantity': '10'}).status_code, 400)
        self.assertFalse(OwnedBusiness.objects.filter(player=self.player).exists())
        self.player.refresh_from_db()
        self.assertEqual(self.player.money, 10)

    def test_max_with_zero_money_does_not_create_ownership(self):
        self.player.money = 0
        self.player.save()
        self.assertEqual(self.client.post(self.buy_url, {'quantity': 'max'}).status_code, 400)
        self.assertFalse(OwnedBusiness.objects.filter(player=self.player).exists())

    def test_daily_reward_once_per_24_hours(self):
        now = timezone.now()
        with patch('game.views.timezone.now', return_value=now):
            self.assertEqual(self.client.post('/api/game/rewards/daily/').status_code, 200)
            self.assertEqual(self.client.post('/api/game/rewards/daily/').status_code, 400)
        self.player.refresh_from_db()
        self.assertEqual(self.player.money, 1100)
        with patch('game.views.timezone.now', return_value=now + timedelta(hours=24) - timedelta(seconds=1)):
            self.assertEqual(self.client.post('/api/game/rewards/daily/').status_code, 400)
        with patch('game.views.timezone.now', return_value=now + timedelta(hours=24)):
            self.assertEqual(self.client.post('/api/game/rewards/daily/').status_code, 200)
        self.player.refresh_from_db()
        self.assertEqual(self.player.money, 1200)

    def test_achievement_eligibility_and_duplicate_claim(self):
        url = '/api/game/achievements/first-business/claim/'
        self.assertEqual(self.client.post(url).status_code, 400)
        OwnedBusiness.objects.create(player=self.player, business=self.business)
        now = timezone.now()
        with patch('game.views.timezone.now', return_value=now):
            self.assertEqual(self.client.post(url).status_code, 200)
            self.assertEqual(self.client.post(url).status_code, 400)
        self.player.refresh_from_db()
        self.assertEqual(self.player.money, 1000)
        self.assertEqual(self.player.achievement_points, 5)
        self.assertEqual(self.player.achievement_claims.count(), 1)
        self.assertEqual(self.client.post('/api/game/achievements/unknown/claim/').status_code, 404)

    def test_rewards_are_private_and_require_authentication(self):
        self.client.post('/api/game/rewards/daily/')
        other = User.objects.create_user(username='another-player')
        self.client.force_authenticate(other)
        response = self.client.post('/api/game/rewards/daily/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['money'], '100.00')
        self.client.force_authenticate(None)
        self.assertEqual(self.client.post('/api/game/rewards/daily/').status_code, 401)
        self.assertEqual(self.client.post('/api/game/achievements/first-business/claim/').status_code, 401)


from game.models import GlobalUpgrade
from game.services.economy import income_rate


class ProgressionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='progression-player')
        self.player = PlayerProgress.objects.create(user=self.user, money=10000)
        self.business = Business.objects.create(name='Lemonade', base_price=10, income_per_second=1)
        self.owned = OwnedBusiness.objects.create(player=self.player, business=self.business)
        self.client.force_authenticate(self.user)

    def test_achievement_awards_points_not_cash_once(self):
        now = timezone.now()
        with patch('game.views.timezone.now', return_value=now):
            response = self.client.post('/api/game/achievements/first-business/claim/', {'points': 99999})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['achievement_points'], 5)
            self.assertEqual(self.client.post('/api/game/achievements/first-business/claim/').status_code, 400)
        self.player.refresh_from_db()
        self.assertEqual(self.player.money, 10000)
        self.assertEqual(self.player.total_points_earned, 5)
        self.assertEqual(self.player.lifetime_earnings, 0)

    def test_global_upgrade_cost_and_old_rate_settlement(self):
        now = timezone.now()
        self.player.achievement_points = 50
        self.player.total_points_earned = 50
        self.player.last_income_at = now - timedelta(seconds=60)
        self.player.save()
        with patch('game.views.timezone.now', return_value=now):
            response = self.client.post('/api/game/global-upgrades/training/buy/', {'cost': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['money'], '10060.00')
        self.assertEqual(response.data['achievement_points'], 40)
        self.assertEqual(response.data['income_per_second'], '1.10')
        self.assertEqual(response.data['global_upgrades'][0]['next_cost'], 20)
        self.assertEqual(response.data['statistics']['points_spent'], 10)

    def test_global_upgrade_insufficient_points_max_level_and_unknown(self):
        url = '/api/game/global-upgrades/training/buy/'
        self.assertEqual(self.client.post(url).status_code, 400)
        self.assertFalse(GlobalUpgrade.objects.exists())
        self.player.achievement_points = 1000
        self.player.save()
        for _ in range(3):
            self.assertEqual(self.client.post(url).status_code, 200)
        self.assertEqual(self.client.post(url).status_code, 400)
        self.player.refresh_from_db()
        self.assertEqual(self.player.achievement_points, 930)
        self.assertEqual(self.client.post('/api/game/global-upgrades/made-up/buy/').status_code, 404)

    def test_individual_upgrade_doubles_all_copies_without_backpay(self):
        now = timezone.now()
        self.owned.quantity = 3
        self.owned.save()
        self.player.last_income_at = now - timedelta(seconds=10)
        self.player.save()
        with patch('game.views.timezone.now', return_value=now):
            response = self.client.post(f'/api/game/businesses/{self.business.id}/upgrade/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['money'], '9930.00')
        self.assertEqual(response.data['income_per_second'], '6.00')
        self.assertEqual(response.data['businesses'][0]['upgrade_cost'], '300.00')
        self.assertEqual(response.data['statistics']['total_upgrades_purchased'], 1)

    def test_upgrade_checks_ownership_money_and_cap(self):
        other = Business.objects.create(name='Unowned', base_price=100, income_per_second=5)
        self.assertEqual(self.client.post(f'/api/game/businesses/{other.id}/upgrade/').status_code, 404)
        self.player.money = 0
        self.player.save()
        url = f'/api/game/businesses/{self.business.id}/upgrade/'
        self.assertEqual(self.client.post(url).status_code, 400)
        self.owned.upgrade_level = 10
        self.owned.save()
        self.assertEqual(self.client.post(url).status_code, 400)

    def test_unlock_enforced_using_lifetime_earnings(self):
        business = Business.objects.create(name='Coffee', base_price=1000, income_per_second=25)
        url = f'/api/game/businesses/{business.id}/buy/'
        self.assertEqual(self.client.post(url).status_code, 403)
        self.player.lifetime_earnings = 100
        self.player.save()
        self.assertEqual(self.client.post(url).status_code, 200)
        self.player.refresh_from_db()
        self.assertEqual(self.player.total_businesses_purchased, 1)
        self.assertTrue(self.player.discovered_businesses.filter(pk=business.pk).exists())

    def test_prestige_requires_confirmation_and_run_threshold(self):
        self.assertEqual(self.client.post('/api/game/prestige/', {}, format='json').status_code, 400)
        self.assertEqual(self.client.post('/api/game/prestige/', {'confirm': 'true'}, format='json').status_code, 400)
        self.assertEqual(self.client.post('/api/game/prestige/', {'confirm': True}, format='json').status_code, 400)
        self.player.refresh_from_db()
        self.assertEqual(self.player.prestige_count, 0)
        self.assertTrue(OwnedBusiness.objects.filter(player=self.player).exists())

    def test_prestige_resets_run_preserves_permanent_progress(self):
        now = timezone.now()
        self.player.run_earnings = 1000000
        self.player.lifetime_earnings = 1000000
        self.player.achievement_points = 25
        self.player.total_points_earned = 35
        self.player.total_businesses_purchased = 12
        self.player.total_upgrades_purchased = 3
        self.player.last_daily_claim_at = now
        self.player.save()
        self.player.discovered_businesses.add(self.business)
        GlobalUpgrade.objects.create(player=self.player, code='training')
        self.client.post('/api/game/achievements/first-business/claim/')
        with patch('game.views.timezone.now', return_value=now):
            response = self.client.post('/api/game/prestige/', {'confirm': True}, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['money'], '0.00')
        self.assertEqual(data['prestige']['run_earnings'], '0.00')
        self.assertEqual(data['prestige_count'], 1)
        self.assertEqual(data['achievement_points'], 30)
        self.assertEqual(data['global_upgrades'][0]['level'], 1)
        self.assertEqual(data['statistics']['total_businesses_purchased'], 12)
        self.assertEqual(data['statistics']['total_upgrades_purchased'], 3)
        self.assertFalse(data['daily_reward']['available'])
        self.assertFalse(OwnedBusiness.objects.filter(player=self.player).exists())
        discovery = next(item for item in data['achievements'] if item['code'] == f'business-{self.business.pk}')
        self.assertTrue(discovery['eligible'])
        self.assertEqual(self.client.post('/api/game/prestige/', {'confirm': True}, format='json').status_code, 400)
        self.player.refresh_from_db()
        self.player.money = 10
        self.player.save()
        response = self.client.post(f'/api/game/businesses/{self.business.pk}/buy/')
        self.assertEqual(response.data['income_per_second'], '1.38')

    def test_achievement_count_unique_codes_and_difficulty_points(self):
        response = self.client.get('/api/game/state/')
        items = response.data['achievements']
        self.assertGreaterEqual(len(items), 50)
        self.assertEqual(len(items), len({item['code'] for item in items}))
        by_code = {item['code']: item for item in items}
        self.assertGreater(by_code['first-million']['points'], by_code['first-thousand']['points'])
        self.assertGreater(by_code['purchases-1000']['points'], by_code['first-business']['points'])

    def test_progression_endpoints_require_authentication(self):
        self.client.force_authenticate(None)
        for url in ('/api/game/prestige/', '/api/game/global-upgrades/training/buy/',
                    f'/api/game/businesses/{self.business.pk}/upgrade/'):
            self.assertEqual(self.client.post(url).status_code, 401)

    def test_income_caps_before_database_overflow(self):
        from game.services.economy import MAX_CASH
        self.player.money = MAX_CASH - 1
        self.player.last_income_at = timezone.now() - timedelta(days=100000)
        self.player.save()
        response = self.client.get('/api/game/state/')
        self.assertEqual(response.status_code, 200)
        self.player.refresh_from_db()
        self.assertEqual(self.player.money, MAX_CASH)


from django.test import TransactionTestCase
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


class ExistingSaveMigrationTests(TransactionTestCase):
    def test_existing_claims_receive_points_once_and_businesses_survive(self):
        old_target = [('game', '0004_playerprogress_last_daily_claim_at_achievementclaim')]
        new_target = [('game', '0010_alter_business_base_price_and_more')]
        executor = MigrationExecutor(connection)
        executor.migrate(old_target)
        try:
            old_apps = executor.loader.project_state(old_target).apps
            UserModel = old_apps.get_model('auth', 'User')
            OldPlayer = old_apps.get_model('game', 'PlayerProgress')
            OldBusiness = old_apps.get_model('game', 'Business')
            OldOwned = old_apps.get_model('game', 'OwnedBusiness')
            OldClaim = old_apps.get_model('game', 'AchievementClaim')
            user = UserModel.objects.create(username='old-save')
            player = OldPlayer.objects.create(user_id=user.pk, money=1234, lifetime_earnings=5000)
            business = OldBusiness.objects.create(name='Existing Stand', base_price=10, income_per_second=1)
            OldOwned.objects.create(player_id=player.pk, business_id=business.pk, quantity=7)
            OldClaim.objects.create(player_id=player.pk, code='first-business')
            OldClaim.objects.create(player_id=player.pk, code='first-thousand')
            executor = MigrationExecutor(connection)
            executor.migrate(new_target)
            migrated = PlayerProgress.objects.get(pk=player.pk)
            self.assertEqual(migrated.money, 1234)
            self.assertEqual(migrated.achievement_points, 15)
            self.assertEqual(migrated.total_points_earned, 15)
            self.assertEqual(migrated.total_businesses_purchased, 7)
            self.assertEqual(migrated.run_earnings, 5000)
            self.assertTrue(migrated.discovered_businesses.filter(pk=business.pk).exists())
            MigrationExecutor(connection).migrate(new_target)
            migrated.refresh_from_db()
            self.assertEqual(migrated.achievement_points, 15)
        finally:
            MigrationExecutor(connection).migrate(new_target)


from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test.utils import CaptureQueriesContext
from game.serializers import BusinessSerializer


class ValidationAndFlowTests(APITestCase):
    def test_invalid_business_data_is_rejected(self):
        for price, income in [(0, 1), (-1, 1), (10, -1)]:
            with self.assertRaises(ValidationError):
                Business.objects.create(name=f'Invalid {price} {income}', base_price=price, income_per_second=income)
            serializer = BusinessSerializer(data={
                'name': 'Invalid API business', 'base_price': str(price), 'income_per_second': str(income),
            })
            self.assertFalse(serializer.is_valid())

    def test_database_constraints_block_invalid_bulk_updates(self):
        business = Business.objects.create(name='Valid', base_price=10, income_per_second=1)
        for changes in ({'base_price': '-1.00'}, {'base_price': '0.00'}, {'income_per_second': '-0.01'}):
            with self.assertRaises(IntegrityError), transaction.atomic():
                Business.objects.filter(pk=business.pk).update(**changes)
        business.refresh_from_db()
        self.assertEqual(business.base_price, 10)
        self.assertEqual(business.income_per_second, 1)

    def test_registration_checks_password_similarity_and_duplicates(self):
        response = self.client.post('/api/accounts/register/', {'username': 'FlowStudent', 'password': 'FlowStudent'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        credentials = {'username': 'new-student', 'password': 'Strong!Independent74'}
        self.assertEqual(self.client.post('/api/accounts/register/', credentials).status_code, 201)
        self.assertEqual(self.client.post('/api/accounts/register/', credentials).status_code, 400)

    def test_fresh_player_can_complete_the_core_loop(self):
        business = Business.objects.create(name='Starter Stand', base_price=10, income_per_second=1)
        credentials = {'username': 'full-flow', 'password': 'Strong!Independent74'}
        self.assertEqual(self.client.post('/api/accounts/register/', credentials).status_code, 201)
        tokens = self.client.post('/api/accounts/login/', credentials).data
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])
        now = timezone.now()
        with patch('game.views.timezone.now', return_value=now):
            self.assertEqual(self.client.get('/api/game/state/').data['money'], '0.00')
            self.assertEqual(self.client.post('/api/game/rewards/daily/').status_code, 200)
            self.assertEqual(self.client.post(f'/api/game/businesses/{business.pk}/buy/').status_code, 200)
            self.assertEqual(self.client.post('/api/game/achievements/first-business/claim/').status_code, 200)
            self.assertEqual(self.client.post(f'/api/game/achievements/business-{business.pk}/claim/').status_code, 200)
            response = self.client.post('/api/game/global-upgrades/training/buy/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['achievement_points'], 0)
        with patch('game.views.timezone.now', return_value=now + timedelta(seconds=10)):
            response = self.client.post(f'/api/game/businesses/{business.pk}/upgrade/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['income_per_second'], '2.20')
        self.assertEqual(response.data['businesses'][0]['upgrade_level'], 1)

    def test_catalog_is_read_only_and_requires_login(self):
        self.assertEqual(self.client.get('/api/game/catalog/').status_code, 401)
        user = User.objects.create_user(username='catalog-reader')
        self.client.force_authenticate(user)
        self.assertEqual(self.client.get('/api/game/catalog/').status_code, 200)
        self.assertEqual(self.client.post('/api/game/catalog/', {'name': 'Cheat'}).status_code, 405)

    def test_failed_action_rolls_back_database_changes(self):
        user = User.objects.create_user(username='rollback-player')
        player = PlayerProgress.objects.create(user=user, money=10)
        self.client.force_authenticate(user)
        self.client.raise_request_exception = False
        with patch('game.views.snapshot', side_effect=RuntimeError('Test failure')):
            response = self.client.post('/api/game/work/')
        self.assertEqual(response.status_code, 500)
        player.refresh_from_db()
        self.assertEqual(player.money, 10)
        self.assertEqual(player.total_work_actions, 0)

    def test_other_players_cannot_upgrade_your_businesses(self):
        owner = User.objects.create_user(username='private-owner')
        player = PlayerProgress.objects.create(user=owner)
        business = Business.objects.create(name='Private stand')
        owned = OwnedBusiness.objects.create(player=player, business=business)
        other = User.objects.create_user(username='different-player')
        self.client.force_authenticate(other)
        self.assertEqual(self.client.post(f'/api/game/businesses/{business.pk}/upgrade/').status_code, 404)
        owned.refresh_from_db()
        self.assertEqual(owned.upgrade_level, 0)

    def test_catalog_seed_is_repeatable_and_preserves_edits(self):
        from io import StringIO
        call_command('seed_businesses', stdout=StringIO())
        self.assertEqual(Business.objects.count(), 12)
        stand = Business.objects.get(name='Lemonade Stand')
        stand.description = 'My custom description'
        stand.save()
        call_command('seed_businesses', stdout=StringIO())
        self.assertEqual(Business.objects.count(), 12)
        stand.refresh_from_db()
        self.assertEqual(stand.description, 'My custom description')

    def test_queries_do_not_grow_for_each_business(self):
        user = User.objects.create_user(username='query-player')
        PlayerProgress.objects.create(user=user)
        self.client.force_authenticate(user)
        Business.objects.create(name='One stand')
        with CaptureQueriesContext(connection) as small:
            self.assertEqual(self.client.get('/api/game/state/').status_code, 200)
        for number in range(11):
            Business.objects.create(name=f'Extra business {number}')
        with CaptureQueriesContext(connection) as large:
            self.assertEqual(self.client.get('/api/game/state/').status_code, 200)
        self.assertLessEqual(len(large), len(small) + 2)
