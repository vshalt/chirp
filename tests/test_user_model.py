import time
from datetime import datetime
import unittest
from flask import current_app
from app import create_app, db
from app.models import User, Role, AnonymousUser, Permission, Follow

class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        user = User(password='password')
        self.assertTrue(user.password_hash is not None)

    def test_no_password_getter(self):
        user = User(password='password')
        with self.assertRaises(AttributeError):
            user.password

    def test_password_verification(self):
        user = User(password='password')
        self.assertTrue(user.verify_password('password'))
        self.assertFalse(user.verify_password('new_password'))

    def test_password_salts_are_random(self):
        user = User(password='password')
        user1 = User(password='password')
        self.assertTrue(user.password_hash != user1.password_hash)

    def test_valid_confirmation_token(self):
        user = User(password='password')
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        self.assertTrue(user.confirm(token))

    def test_invalid_confirmation_token(self):
        user = User(password='password')
        user1 = User(password='passwords')
        db.session.add(user)
        db.session.add(user1)
        db.session.commit()
        token = user.generate_confirmation_token()
        self.assertFalse(user1.confirm(token))

    def test_expired_confirmation_token(self):
        user = User(password='password')
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(user.confirm(token))

    def test_valid_reset_token(self):
        user = User(password='password')
        db.session.add(user)
        db.session.commit()
        token = user.generate_reset_token()
        self.assertTrue(user.reset_password(token, 'new_password'))
        self.assertTrue(user.verify_password('new_password'))

    def test_invalid_reset_token(self):
        user = User(password='password')
        db.session.add(user)
        db.session.commit()
        token = user.generate_reset_token()
        self.assertFalse(User.reset_password(token+'a', 'new_password'))
        self.assertTrue(user.verify_password('password'))

    def test_valid_email_change_token(self):
        user = User(password='password')
        db.session.add(user)
        db.session.commit()
        token = user.generate_email_update_token('example@mail.com')
        self.assertTrue(user.update_email(token))
        self.assertTrue(user.email=='example@mail.com')

    def test_invalid_email_change_token(self):
        user = User(email='name@mail.com', password='password')
        user1 = User(email='mail@mail.com', password='password1')
        db.session.add(user)
        db.session.add(user1)
        db.session.commit()
        token = user.generate_email_update_token('new@mail.com')
        self.assertFalse(user1.update_email(token))
        self.assertTrue(user.email == 'name@mail.com')

    def test_duplicate_email(self):
        user = User(email='sername@mail.com', password='password')
        user1 = User(email='ail@mail.com', password='password1')
        db.session.add(user)
        db.session.add(user1)
        db.session.commit()
        token = user.generate_email_update_token('ail@mail.com')
        self.assertFalse(user.update_email(token))
        self.assertTrue(user.email == 'sername@mail.com')

    def test_user_roles(self):
        user = User(email='username@mail.com', password='password')
        self.assertTrue(user.can(Permission.FOLLOW))
        self.assertTrue(user.can(Permission.WRITE))
        self.assertTrue(user.can(Permission.COMMENT))
        self.assertFalse(user.can(Permission.MODERATE))
        self.assertFalse(user.can(Permission.ADMIN))

    def test_moderator_roles(self):
        role = Role.query.filter_by(name='Moderator').first()
        user = User(email='username@mail.com', password='password', role=role)
        self.assertTrue(user.can(Permission.FOLLOW))
        self.assertTrue(user.can(Permission.WRITE))
        self.assertTrue(user.can(Permission.COMMENT))
        self.assertTrue(user.can(Permission.MODERATE))
        self.assertFalse(user.can(Permission.ADMIN))

    def test_admin_roles(self):
        role = Role.query.filter_by(name='Administrator').first()
        user = User(email='username@mail.com', password='password', role=role)
        self.assertTrue(user.can(Permission.WRITE))
        self.assertTrue(user.can(Permission.FOLLOW))
        self.assertTrue(user.can(Permission.COMMENT))
        self.assertTrue(user.can(Permission.MODERATE))
        self.assertTrue(user.can(Permission.ADMIN))

    def test_anonymous_user(self):
        user = AnonymousUser()
        self.assertFalse(user.can(Permission.FOLLOW))
        self.assertFalse(user.can(Permission.WRITE))
        self.assertFalse(user.can(Permission.COMMENT))
        self.assertFalse(user.can(Permission.MODERATE))
        self.assertFalse(user.can(Permission.ADMIN))

    def test_timestamps(self):
        user = User(password='password')
        db.session.add(user)
        db.session.commit()
        self.assertTrue((datetime.utcnow() - user.member_since).total_seconds() < 3)
        self.assertTrue((datetime.utcnow() - user.last_seen).total_seconds() < 3)

    def test_ping(self):
        user = User(password='password')
        db.session.add(user)
        db.session.commit()
        last_seen_before = user.last_seen
        user.ping()
        self.assertTrue(user.last_seen > last_seen_before)

    def test_gravatar(self):
        user = User(email='john@example.com', password='catdog')
        with self.app.test_request_context('/'):
            gravatar = user.gravatar()
            gravatar_256 = user.gravatar(size=256)
            gravatar_pg = user.gravatar(rating='pg')
            gravatar_retro = user.gravatar(default='retro')
        self.assertTrue('https://www.gravatar.com/avatar/' + 'd4c74594d841139328695756648b6bd6'in gravatar)
        self.assertTrue('s=256' in gravatar_256)
        self.assertTrue('r=pg' in gravatar_pg)
        self.assertTrue('d=retro' in gravatar_retro)

    def test_follows(self):
        user1 = User(email='john@example.com', password='cat')
        user2 = User(email='susan@example.org', password='dog')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        self.assertFalse(user1.is_following(user2))
        self.assertFalse(user1.is_followed_by(user2))
        timestamp_before = datetime.utcnow()
        user1.follow(user2)
        db.session.add(user1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(user1.is_following(user2))
        self.assertFalse(user1.is_followed_by(user2))
        self.assertTrue(user2.is_followed_by(user1))
        self.assertTrue(user1.followed.count() == 2)
        self.assertTrue(user2.followers.count() == 2)
        f = user1.followed.all()[-1]
        self.assertTrue(f.followed == user2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        f = user2.followers.all()[-1]
        self.assertTrue(f.follower == user1)
        user1.unfollow(user2)
        db.session.add(user1)
        db.session.commit()
        self.assertTrue(user1.followed.count() == 1)
        self.assertTrue(user2.followers.count() == 1)
        self.assertTrue(Follow.query.count() == 2)
        user2.follow(user1)
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        db.session.delete(user2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 1)

    def test_to_json(self):
        user = User(email='john@example.com', password='cat')
        db.session.add(user)
        db.session.commit()
        with self.app.test_request_context('/'):
            json_user = user.to_json()
        expected_keys = ['user_url', 'username', 'member_since', 'last_seen',
                         'posts', 'followed_posts', 'posts_count']
        self.assertEqual(sorted(json_user.keys()), sorted(expected_keys))
        self.assertEqual('/api/v1/users/' + str(user.id), json_user['user_url'])

